# Catalogue sources

The initial 45 entries were parsed from [Wikipedia's List of deepest caves, revision 1372337231](https://en.wikipedia.org/w/index.php?title=List_of_deepest_caves&oldid=1372337231), retrieved 9 September 2026. `caves.json` records that revision, retrieval date, source HTML SHA-256, data license, and coordinate precision.

Data is adapted from Wikipedia contributors under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Source table values were normalized, citation/language-link annotations removed from names, whitespace normalized, and locations rounded to 0.1°. The upstream revision and its history supply attribution and references. Code's MIT license does not relicense this catalogue.

This is a selected list of deep surveyed caves, with uneven geographic coverage. Dimensions and source territorial labels are reported, not independently verified. Length means surveyed passage distance; depth means vertical span. Neither indicates difficulty or public access. Map coordinates are approximate regional points, not entrance directions. Rounding is not a promise of anonymity for a known cave.

## Refresh the existing source

After installing the development requirements, identify and review a Wikipedia revision, then run:

```sh
python -m scripts.refresh_catalog --revision 1372337231 --output candidate-caves.json
```

The command refuses to overwrite a file. Compare the candidate against `data/caves.json`, inspect upstream citations, check additions/removals and surprising changes, and preserve identities where names change. Replace the reviewed file only after that review. Run `npm run verify`, update the release notes/version, and publish normally. The build fills the source/date/count in the information dialog from metadata.

Do not download a source during deployment. A source outage must not prevent rebuilding the last reviewed catalogue. The current source/parser expects complete numeric measurements; future sources with unknown values require explicit nullable data/UI support before import. Do not substitute zero or infer measurements.

## Additional sources

Expansion is a priority, described in [the roadmap](../docs/ROADMAP.md). Audit identifiers, cave-system versus entrance identity, units, coverage, access/location sensitivity and redistribution terms before importing. Wikidata structured data is CC0; OSM data is ODbL; GrottoCenter and other surveys have their own terms. Free access does not establish permission to republish. A multi-source catalogue needs per-record provenance before it ships.
