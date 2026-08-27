from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .app import generate_map
from .core import CavebotError, DEFAULT_SOURCE_URL


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cavebot",
        description="Build an HTML map from Wikipedia's deepest-caves table.",
    )
    parser.add_argument(
        "--source-url",
        default=DEFAULT_SOURCE_URL,
        help="HTML page containing the cave wikitable.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("caves.html"),
        help="Output HTML path (default: caves.html).",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_float,
        default=20.0,
        help="HTTP timeout in seconds (default: 20).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output_path, cave_count = generate_map(
            source_url=args.source_url,
            output_path=args.output,
            timeout_seconds=args.timeout,
        )
    except CavebotError as exc:
        print(f"cavebot failed: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {cave_count} cave markers to {output_path}")
    return 0
