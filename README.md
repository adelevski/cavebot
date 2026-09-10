# spelunk

[Open spelunk](https://snowball-projects.github.io/spelunk/) · [snowball](https://snowball-projects.github.io/)

Explore cave locations and compare surveyed depth and passage length. Search or filter the catalogue, sort by depth or length, and select caves for a compact comparison. The map fills the screen; controls and results collapse independently, with bottom sheets on mobile.

The initial catalogue contains 45 records from a reviewed snapshot of Wikipedia's deepest-caves list. It is not a world inventory, a verified ranking, or a guide to entering caves. Locations are rounded to 0.1°; visitor access is unknown. [Data sources and updating](data/README.md).

## Run and verify

Use Node 24 and Python 3.10 or newer. There are no Node production dependencies, backend, accounts, API keys or runtime data queries. Leaflet 1.9.4 is vendored; only ordinary OpenStreetMap tile requests leave the site while browsing. Wikipedia and Google open only when their links are clicked.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
npm ci
npx playwright install chromium
npm run verify
npm run preview
```

Open `http://127.0.0.1:8770`. On Windows activate `.venv\Scripts\Activate.ps1` and use `python` if `python3` is not an alias. The build itself uses only Python's standard library: `python scripts/build.py`.

`npm run test` runs offline parser/data tests. Browser tests intercept map tiles and make no provider requests. CI repeats both checks, builds `dist/`, and deploys main to GitHub Pages. `package.json` owns the version; `dist/version.json` exposes the deployed version and catalogue date.

## Project layout

- `web/`: HTML, CSS, JavaScript, optimized icons and vendored Leaflet.
- `data/caves.json`: reviewed catalogue and provenance metadata.
- `scripts/build.py`: offline validation and static build.
- `scripts/cave_source.py`, `scripts/refresh_catalog.py`: source parsing and candidate refresh.
- `tests/`: deterministic parser, catalogue and browser behavior checks.
- [Operations](docs/OPERATIONS.md): deploy, cost, privacy, rollback and dormancy.
- [Next work](docs/ROADMAP.md): broader catalogue and optional 3D surveys.

## Licensing and continuity

Original code, documentation and project artwork use [MIT](LICENSE). Wikipedia-derived data uses CC BY-SA 4.0; Leaflet and map tiles retain their own terms. See [third-party notices](THIRD-PARTY-NOTICES.txt).

A snowball project, founded by Nas Delevski. This repository continues the original cavebot experiment; history and the v0.1.x tags are preserved. Version 0.2.0 replaces the old Python/Folium map command with the static dashboard. Its parser and relevant tests remain; the old command is available in the earlier tags.

Version 0.3.0 renames cave atlas to **spelunk**. Its identity is inspired by
digital exploration inside caves. The current app is still a map and measurement
comparison; rotatable 3D surveys are the next planned feature, only where real
measurements/models and suitable permissions are available.
