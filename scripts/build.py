"""Validate a reviewed snapshot and build the static site without network access."""
from __future__ import annotations

import html
import json
import math
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def validate_catalog(catalog: dict) -> None:
    metadata = catalog['metadata']
    date.fromisoformat(metadata['retrieved'])
    source = urlparse(metadata['source'])
    if source.scheme != 'https' or source.hostname != 'en.wikipedia.org' or source.username:
        raise ValueError('catalogue source must be the documented Wikipedia HTTPS source')
    if metadata['license'] != 'CC-BY-SA-4.0':
        raise ValueError('review the data license before changing this catalogue')
    if metadata['coordinate_precision_degrees'] != 0.1:
        raise ValueError('coordinate precision must remain 0.1 degrees')
    caves = catalog['caves']
    if not caves:
        raise ValueError('catalogue is empty')
    ids = set()
    for cave in caves:
        for field in ('id', 'name', 'location'):
            if not isinstance(cave[field], str) or not cave[field].strip():
                raise ValueError(f'invalid {field}')
        if cave['id'] in ids:
            raise ValueError('duplicate cave id')
        ids.add(cave['id'])
        for field, maximum in [('latitude', 90), ('longitude', 180)]:
            value = cave[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value) > maximum:
                raise ValueError(f'invalid {field}')
            if abs(value - round(value, 1)) > 1e-8:
                raise ValueError('publish regional coordinates rounded to 0.1 degrees')
        for field in ('depth_m', 'length_km'):
            value = cave[field]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f'invalid {field}')
        link = cave.get('wikipedia_url')
        if link:
            parsed = urlparse(link)
            if parsed.scheme != 'https' or parsed.hostname != 'en.wikipedia.org' or parsed.username or not parsed.path.startswith('/wiki/'):
                raise ValueError('invalid article URL')


def build(destination: Path | None = None) -> Path:
    destination = destination or ROOT / 'dist'
    catalog = json.loads((ROOT / 'data/caves.json').read_text(encoding='utf-8'))
    validate_catalog(catalog)
    version = json.loads((ROOT / 'package.json').read_text())['version']
    template = (ROOT / 'web/index.html').read_text()
    replacements = {
        '__CATALOG__': json.dumps(catalog, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'),
        '__COUNT__': str(len(catalog['caves'])),
        '__DATE__': f"{date.fromisoformat(catalog['metadata']['retrieved']).day} {date.fromisoformat(catalog['metadata']['retrieved']).strftime('%B %Y')}",
        '__SOURCE__': html.escape(catalog['metadata']['source'], quote=True),
        '__VERSION__': html.escape(version),
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    if '__CATALOG__' in template:
        raise ValueError('unexpanded template')
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(ROOT / 'web', destination)
    (destination / 'index.html').write_text(template, encoding='utf-8')
    shutil.copy(ROOT / 'data/caves.json', destination / 'caves.json')
    for name in ('LICENSE', 'THIRD-PARTY-NOTICES.txt'):
        shutil.copy(ROOT / name, destination / name)
    (destination / '.nojekyll').touch()
    (destination / 'version.json').write_text(json.dumps({'version': version, 'catalogue_date': catalog['metadata']['retrieved']})+'\n')
    total = sum(p.stat().st_size for p in destination.rglob('*') if p.is_file())
    print(f'Built spelunk {version}: {len(catalog["caves"])} caves; {total:,} bytes')
    return destination


if __name__ == '__main__':
    build()
