from __future__ import annotations

from pathlib import Path
from urllib import error

import pytest

from cavebot.app import fetch_html, render_map
from cavebot.core import Cave, CavebotError


class _Headers:
    def get_content_charset(self) -> str:
        return "utf-8"


class _Response:
    headers = _Headers()

    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


def test_fetch_html_uses_direct_bounded_request(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, float, str | None]] = []

    def _urlopen(req, timeout: float):
        calls.append((req.full_url, timeout, req.get_header("User-agent")))
        return _Response(b"<html>fixture</html>")

    monkeypatch.setattr("cavebot.app.request.urlopen", _urlopen)

    assert fetch_html("https://example.test/caves", timeout_seconds=3.0) == (
        "<html>fixture</html>"
    )
    assert calls == [
        ("https://example.test/caves", 3.0, "cavebot (+https://github.com/adelevski/cavebot)")
    ]


def test_fetch_html_wraps_network_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def _urlopen(req, timeout: float):
        raise error.URLError("offline")

    monkeypatch.setattr("cavebot.app.request.urlopen", _urlopen)

    with pytest.raises(CavebotError, match="source request failed: offline"):
        fetch_html("https://example.test/caves")


def test_render_map_writes_marker_content(tmp_path: Path) -> None:
    cave = Cave(
        name="Krubera-Voronja Cave",
        depth_m=2224,
        length_km=23.0,
        location="Abkhazia / Georgia",
        latitude=43.417778,
        longitude=40.309833,
        wikipedia_url="https://en.wikipedia.org/wiki/Krubera_Cave",
    )
    output = render_map([cave], tmp_path / "caves.html")
    rendered = output.read_text(encoding="utf-8")

    assert "Krubera-Voronja Cave" in rendered
    assert "Depth: 2224 m" in rendered
    assert "https://en.wikipedia.org/wiki/Krubera_Cave" in rendered


def test_render_map_rejects_empty_input(tmp_path: Path) -> None:
    with pytest.raises(CavebotError, match="without cave records"):
        render_map([], tmp_path / "caves.html")
