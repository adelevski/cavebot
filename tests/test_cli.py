from __future__ import annotations

from pathlib import Path

from cavebot import cli
from cavebot.core import CavebotError


def test_cli_reports_generated_output(monkeypatch, capsys, tmp_path: Path) -> None:
    destination = tmp_path / "caves.html"

    def _generate_map(*, source_url: str, output_path: Path, timeout_seconds: float):
        assert source_url == "https://example.test/caves"
        assert output_path == destination
        assert timeout_seconds == 4.0
        return destination, 3

    monkeypatch.setattr(cli, "generate_map", _generate_map)

    result = cli.main(
        [
            "--source-url",
            "https://example.test/caves",
            "--output",
            str(destination),
            "--timeout",
            "4",
        ]
    )

    assert result == 0
    assert capsys.readouterr().out == f"wrote 3 cave markers to {destination}\n"


def test_cli_reports_expected_failure(monkeypatch, capsys) -> None:
    def _generate_map(**kwargs):
        raise CavebotError("source table changed")

    monkeypatch.setattr(cli, "generate_map", _generate_map)

    assert cli.main([]) == 1
    assert capsys.readouterr().err == "cavebot failed: source table changed\n"
