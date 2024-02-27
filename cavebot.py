import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import folium
import latlon


def scrape_cave_table(url):
    driver = webdriver.Firefox()

    driver.get(url)
    time.sleep(3)  # Wait for page to load

    # Find the table containing the list of caves
    table = driver.find_element(By.CSS_SELECTOR, ".wikitable")

    # Extract table data
    table_rows = table.find_elements(By.TAG_NAME, "tr")
    data = []
    for row in table_rows[1:]:  # Skip header row
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 6:  # Ensure all expected columns are present
            try:
                name = cols[1].text.strip()
                link = cols[1].find_element(By.TAG_NAME, "a").get_attribute("href")
            except NoSuchElementException:
                link = None
            depth = cols[2].text.strip()
            length = cols[3].text.strip()
            location = cols[4].text.strip()
            coordinates = cols[5].text.strip()
            data.append([name, depth, length, location, coordinates, link])

    # Convert data into a pandas DataFrame
    columns = ["Name", "Depth (m)", "Length (km)", "Location", "Coordinates", "Wikipedia URL"]
    df = pd.DataFrame(data, columns=columns)

    driver.quit()
    return df

def parse_dms(dms):
    deg = float(dms.split('°')[0])
    min = float(dms.split('′')[0].split('°')[1])
    sec = float(dms.split('′')[1].split('″')[0])
    dir = dms.split('″')[1]
    if dir == 'S' or dir == 'W':
        deg *= -1
        min *= -1
        sec *= -1
    return deg, min, sec

def parse_dd(dd):
    deg = float(dd.split('°')[0])
    dir = dd.split('°')[1]
    if dir == 'S' or dir == 'W':
        deg *= -1
    return deg

def parse_func(row):
    lat, lon = row['Coordinates'].split(' ')
    if "″" in lat:
        lat_deg, lat_min, lat_sec = parse_dms(lat)
        lon_deg, lon_min, lon_sec = parse_dms(lon)
        coord = latlon.LatLon(
            lat=latlon.Latitude(degree=lat_deg, minute=lat_min, second=lat_sec), 
            lon=latlon.Longitude(degree=lon_deg, minute=lon_min, second=lon_sec)
        )
    else:
        lat_deg = parse_dd(lat)
        lon_deg = parse_dd(lon)
        coord = latlon.LatLon(
            lat=lat_deg,
            lon=lon_deg
        )
    return coord.lat, coord.lon


def clean_data(df):
    df["Depth (m)"] = df["Depth (m)"].str.split('[').str[0].astype(int)
    df["Length (km)"] = df["Length (km)"].str.split(' ').str[0].astype(float)
    df['Wikipedia URL'] = df['Wikipedia URL'].where(~df['Wikipedia URL'].str.contains('index.php', na=False), None)
    df['lat'], df['lon'] = zip(*df.apply(lambda row: parse_func(row=row), axis=1))
    return df


def add_markers(df, map):
    for _, row in df.iterrows():
        if row['Wikipedia URL'] and row['Wikipedia URL'].startswith('h'):
            popup = f"Depth: {row['Depth (m)']}, Wiki: {row['Wikipedia URL']}"
        else:
            popup = f"Depth: {row['Depth (m)']}"
        marker = folium.Marker(
            location=[row['lat'], row['lon']],
            tooltip=row['Name'],
            popup=popup,
            icon=folium.Icon(color="green")
        ).add_to(map)
    return map


if __name__ == '__main__':
    # Set URL
    url = "https://en.wikipedia.org/wiki/List_of_deepest_caves"

    # Scrape Data
    df = scrape_cave_table(url)

    # Clean 
    df = clean_data(df)

    # Make Map
    map = folium.Map(location=[0, 0], zoom_start=2)

    # Add markers
    map = add_markers(df=df, map=map)

    # Save map
    map.save("caves.html")