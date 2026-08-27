from __future__ import annotations

from pathlib import Path

import pytest

from cavebot.core import CaveTableError, parse_cave_table, parse_coordinate_pair


FIXTURE = Path(__file__).parent / "fixtures" / "deepest_caves_table.html"


def test_parse_coordinate_pair_supports_dms_and_hemispheres() -> None:
    latitude, longitude = parse_coordinate_pair("5°28′53″S 151°20′46″E")

    assert latitude == pytest.approx(-5.4813889)
    assert longitude == pytest.approx(151.3461111)


def test_parse_coordinate_pair_supports_decimal_degrees() -> None:
    assert parse_coordinate_pair("43.22056°N 4.86028°W") == pytest.approx(
        (43.22056, -4.86028)
    )


def test_parse_coordinate_pair_rejects_incomplete_coordinates() -> None:
    with pytest.raises(CaveTableError, match="could not parse latitude/longitude"):
        parse_coordinate_pair("43.22056°N")


def test_parse_coordinate_pair_rejects_invalid_minutes() -> None:
    with pytest.raises(CaveTableError, match="less than 60"):
        parse_coordinate_pair("43°60′00″N 4°00′00″E")


def test_parse_cave_table_uses_headers_not_column_positions() -> None:
    caves = parse_cave_table(FIXTURE.read_text(encoding="utf-8"))

    assert len(caves) == 3
    assert caves[0].name == "Krubera-Voronja Cave"
    assert caves[0].depth_m == 2224
    assert caves[0].length_km == 23.0
    assert caves[0].location == "Abkhazia / Georgia"
    assert caves[0].wikipedia_url == "https://en.wikipedia.org/wiki/Krubera_Cave"
    assert caves[1].longitude == pytest.approx(-4.8602778)
    assert caves[2].latitude == pytest.approx(-5.4813889)
    assert caves[2].wikipedia_url is None


def test_parse_cave_table_accepts_legacy_location_header() -> None:
    html = FIXTURE.read_text(encoding="utf-8").replace("Country", "Location")

    assert len(parse_cave_table(html)) == 3


def test_parse_cave_table_reports_missing_table() -> None:
    with pytest.raises(CaveTableError, match="class 'wikitable'"):
        parse_cave_table("<html><body><p>No table</p></body></html>")


def test_parse_cave_table_reports_schema_drift() -> None:
    html = FIXTURE.read_text(encoding="utf-8").replace("Coordinates", "Position")

    with pytest.raises(CaveTableError, match="missing required column 'coordinates'"):
        parse_cave_table(html)
