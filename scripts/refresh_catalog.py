"""Prepare a candidate snapshot; never overwrite or publish the reviewed catalogue."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from scripts.cave_source import parse_cave_table
from scripts.build import validate_catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=int, required=True, help='Reviewed Wikipedia revision ID')
    parser.add_argument('--output', type=Path, default=Path('candidate-caves.json'))
    args = parser.parse_args()
    source = f'https://en.wikipedia.org/w/index.php?title=List_of_deepest_caves&oldid={args.revision}'
    req = Request(source, headers={'User-Agent': 'cave-atlas (+https://github.com/snowball-projects/cave-atlas)', 'Accept': 'text/html'})
    with urlopen(req, timeout=20) as response:
        raw = response.read(5_000_001)
    if len(raw) > 5_000_000:
        raise ValueError('source exceeds 5 MB limit')
    caves = []
    for row in parse_cave_table(raw.decode('utf-8'), base_url=source):
        cave = asdict(row)
        cave['id'] = 'wiki-' + re.sub(r'[^a-z0-9]+', '-', row.name.lower()).strip('-')
        cave['name'] = re.sub(r'\s*\[\s*[a-z]{2,3}\s*\]', '', row.name).strip()
        cave['location'] = row.location.replace(' ,', ',')
        cave['latitude'] = round(row.latitude, 1)
        cave['longitude'] = round(row.longitude, 1)
        caves.append(cave)
    catalog = {'metadata': {'source': source, 'retrieved': datetime.now(timezone.utc).date().isoformat(), 'license': 'CC-BY-SA-4.0', 'coordinate_precision_degrees': 0.1, 'source_sha256': hashlib.sha256(raw).hexdigest()}, 'caves': caves}
    validate_catalog(catalog)
    with args.output.open('x', encoding='utf-8') as file:
        json.dump(catalog, file, ensure_ascii=False, indent=2)
        file.write('\n')
    print(f'Wrote {len(caves)} candidate records to {args.output}; review before replacing data/caves.json.')


if __name__ == '__main__':
    main()
