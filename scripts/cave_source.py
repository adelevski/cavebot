from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag


DEFAULT_SOURCE_URL = "https://en.wikipedia.org/wiki/List_of_deepest_caves"


class CaveAtlasError(RuntimeError):
    """Base error for expected spelunk failures."""


class CaveTableError(CaveAtlasError):
    """Raised when the source table is missing or has an unsupported shape."""


@dataclass(frozen=True)
class Cave:
    name: str
    depth_m: int
    length_km: float
    location: str
    latitude: float
    longitude: float
    wikipedia_url: str | None = None


_NUMBER_RE = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
_COORDINATE_RE = re.compile(
    r"(?P<degrees>\d{1,3}(?:\.\d+)?)\s*[°º]\s*"
    r"(?:(?P<minutes>\d{1,2}(?:\.\d+)?)\s*[′'])?\s*"
    r"(?:(?P<seconds>\d{1,2}(?:\.\d+)?)\s*[″\"])?\s*"
    r"(?P<direction>[NSEW])",
    flags=re.IGNORECASE,
)


def _coordinate_component(match: re.Match[str]) -> tuple[float, str]:
    degrees = float(match.group("degrees"))
    minutes = float(match.group("minutes") or 0.0)
    seconds = float(match.group("seconds") or 0.0)
    direction = match.group("direction").upper()

    if minutes >= 60 or seconds >= 60:
        raise CaveTableError("coordinate minutes and seconds must be less than 60")

    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if direction in {"S", "W"}:
        decimal *= -1
    return decimal, direction


def parse_coordinate_pair(value: str) -> tuple[float, float]:
    """Parse the first directional latitude/longitude pair in decimal or DMS form."""
    components = [_coordinate_component(match) for match in _COORDINATE_RE.finditer(value)]
    latitude = next((number for number, direction in components if direction in {"N", "S"}), None)
    longitude = next((number for number, direction in components if direction in {"E", "W"}), None)

    if latitude is None or longitude is None:
        raise CaveTableError(f"could not parse latitude/longitude from {value!r}")
    if not -90 <= latitude <= 90:
        raise CaveTableError(f"latitude is outside [-90, 90]: {latitude}")
    if not -180 <= longitude <= 180:
        raise CaveTableError(f"longitude is outside [-180, 180]: {longitude}")
    return latitude, longitude


def _number(value: str, *, field: str, integer: bool = False) -> int | float:
    match = _NUMBER_RE.search(value.replace("\xa0", " "))
    if match is None:
        raise CaveTableError(f"{field} does not contain a number: {value!r}")

    parsed = float(match.group(0).replace(",", ""))
    if parsed < 0:
        raise CaveTableError(f"{field} must not be negative: {value!r}")
    if integer:
        if not parsed.is_integer():
            raise CaveTableError(f"{field} must be a whole number: {value!r}")
        return int(parsed)
    return parsed


def _header(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def _column_index(headers: list[str], *names: str) -> int:
    normalized_names = tuple(name.casefold() for name in names)
    for index, header in enumerate(headers):
        if any(header == name or header.startswith(f"{name} ") for name in normalized_names):
            return index
    expected = " or ".join(repr(name) for name in names)
    raise CaveTableError(f"source table is missing required column {expected}")


def _article_url(name_cell: Tag, *, base_url: str) -> str | None:
    link = name_cell.find("a", href=True)
    if not isinstance(link, Tag):
        return None
    href = str(link.get("href") or "").strip()
    if not href or "index.php" in href:
        return None

    absolute = urljoin(base_url, href)
    if urlparse(absolute).scheme not in {"http", "https"}:
        return None
    return absolute


def parse_cave_table(html: str, *, base_url: str = DEFAULT_SOURCE_URL) -> tuple[Cave, ...]:
    """Parse the first Wikipedia-style cave table without performing network I/O."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.wikitable")
    if not isinstance(table, Tag):
        raise CaveTableError("source page does not contain a table with class 'wikitable'")

    rows = table.find_all("tr")
    if not rows:
        raise CaveTableError("source cave table has no rows")

    header_cells = rows[0].find_all(["th", "td"], recursive=False)
    headers = [_header(cell.get_text(" ", strip=True)) for cell in header_cells]
    indexes = {
        "name": _column_index(headers, "name"),
        "depth": _column_index(headers, "depth"),
        "length": _column_index(headers, "length (km)"),
        "location": _column_index(headers, "country", "location"),
        "coordinates": _column_index(headers, "coordinates"),
    }
    required_cell_count = max(indexes.values()) + 1

    caves: list[Cave] = []
    for row_number, row in enumerate(rows[1:], start=2):
        cells = row.find_all(["th", "td"], recursive=False)
        if not cells:
            continue
        if len(cells) < required_cell_count:
            raise CaveTableError(
                f"source table row {row_number} has {len(cells)} cells; "
                f"expected at least {required_cell_count}"
            )

        name_cell = cells[indexes["name"]]
        name = name_cell.get_text(" ", strip=True)
        if not name:
            raise CaveTableError(f"source table row {row_number} has no cave name")

        try:
            depth_m = _number(
                cells[indexes["depth"]].get_text(" ", strip=True),
                field="depth",
                integer=True,
            )
            length_km = _number(
                cells[indexes["length"]].get_text(" ", strip=True),
                field="length",
            )
            latitude, longitude = parse_coordinate_pair(
                cells[indexes["coordinates"]].get_text(" ", strip=True)
            )
        except CaveTableError as exc:
            raise CaveTableError(f"could not parse row {row_number} ({name}): {exc}") from exc

        caves.append(
            Cave(
                name=name,
                depth_m=int(depth_m),
                length_km=float(length_km),
                location=cells[indexes["location"]].get_text(" ", strip=True),
                latitude=latitude,
                longitude=longitude,
                wikipedia_url=_article_url(name_cell, base_url=base_url),
            )
        )

    if not caves:
        raise CaveTableError("source cave table contains no data rows")
    return tuple(caves)
