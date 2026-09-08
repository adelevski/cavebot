# Cavebot

Cavebot builds an interactive HTML map from the first `wikitable` on Wikipedia's
[`List of deepest caves`](https://en.wikipedia.org/wiki/List_of_deepest_caves).

It performs one bounded HTTP request, finds columns by header name, parses decimal or
degrees/minutes/seconds coordinates with standard-library math, and gives the resulting
records to Folium for map rendering. It does not launch a browser or require Firefox,
Geckodriver, Selenium, pandas, or `latlon`.

## Install

Cavebot requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On PowerShell, activate with `.\.venv\Scripts\Activate.ps1`; the remaining commands are
the same.

## Generate a map

```bash
cavebot --output caves.html
```

Equivalent module invocation:

```bash
python -m cavebot --output caves.html
```

Options:

- `--source-url`: page containing the cave table; defaults to the Wikipedia page above.
- `--output`: destination HTML file; defaults to `caves.html`.
- `--timeout`: positive HTTP timeout in seconds; defaults to `20`.

On success the command reports the marker count and output path. The generated HTML is
ignored by Git because it is a derived snapshot of a mutable source. Open it in a browser
to load the Folium/Leaflet map; displaying the map also requests third-party map tiles and
frontend assets referenced by Folium.

## Failures

Cavebot exits nonzero with a concise message when the source request fails, the response
cannot be decoded, the expected table or headers are missing, a row cannot be parsed, or
the output file cannot be written. It does not silently skip malformed source rows.

Wikipedia can change its table schema or data at any time. Header-based parsing avoids
the previous column-position bug, but a future incompatible schema change will still
require a code update.

## Development and packaging

```bash
python -m pytest -q
python -m build
```

Tests use a three-row local fixture and mocked HTTP responses; they never access the
network. CI runs the test suite on Python 3.10 and 3.12, checks installed dependencies,
builds wheel/source distributions, and smoke-tests the wheel outside the checkout.

The package version has one source of truth in `src/cavebot/__init__.py`. Runtime
dependencies are declared in `pyproject.toml`; the old unbounded `requirements.txt` was
removed.

## Data provenance and licensing

The live data comes from the linked Wikipedia page and remains subject to that page's
accuracy, provenance, attribution, and licensing terms. The deterministic test fixture is
a minimal hand-authored transcription of three factual rows, documented in
`tests/fixtures/README.md`; it is not a full Wikipedia snapshot.

Project-authored code and documentation are licensed under [MIT](LICENSE).
This does not relicense Wikipedia-derived records, including
`tests/fixtures/deepest_caves_table.html`, or map tiles and other third-party assets.
Preserve the applicable source terms and attribution when redistributing data or
generated maps. Dependencies retain their own licenses.
