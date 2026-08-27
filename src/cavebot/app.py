from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Sequence
from urllib import error, request

import folium

from .core import Cave, CavebotError, DEFAULT_SOURCE_URL, parse_cave_table


USER_AGENT = "cavebot (+https://github.com/adelevski/cavebot)"


def fetch_html(url: str = DEFAULT_SOURCE_URL, *, timeout_seconds: float = 20.0) -> str:
    """Fetch one HTML document with a bounded direct HTTP request."""
    req = request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            payload = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
    except error.HTTPError as exc:
        raise CavebotError(f"source request returned HTTP {exc.code}") from exc
    except error.URLError as exc:
        raise CavebotError(f"source request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise CavebotError("source request timed out") from exc

    try:
        return payload.decode(charset)
    except (LookupError, UnicodeDecodeError) as exc:
        raise CavebotError(f"source response could not be decoded as {charset}") from exc


def render_map(caves: Sequence[Cave], output_path: str | Path) -> Path:
    """Render cave records to one Folium HTML map."""
    if not caves:
        raise CavebotError("cannot render a map without cave records")

    cave_map = folium.Map(location=[0.0, 0.0], zoom_start=2)
    for cave in caves:
        popup_parts = [f"Depth: {cave.depth_m} m"]
        if cave.wikipedia_url:
            popup_parts.append(f"Wiki: {escape(cave.wikipedia_url)}")
        folium.Marker(
            location=[cave.latitude, cave.longitude],
            tooltip=escape(cave.name),
            popup="<br>".join(popup_parts),
            icon=folium.Icon(color="green"),
        ).add_to(cave_map)

    destination = Path(output_path)
    try:
        cave_map.save(str(destination))
    except OSError as exc:
        raise CavebotError(f"could not write map to {destination}: {exc}") from exc
    return destination


def generate_map(
    *,
    source_url: str = DEFAULT_SOURCE_URL,
    output_path: str | Path = "caves.html",
    timeout_seconds: float = 20.0,
) -> tuple[Path, int]:
    html = fetch_html(source_url, timeout_seconds=timeout_seconds)
    caves = parse_cave_table(html, base_url=source_url)
    return render_map(caves, output_path), len(caves)
