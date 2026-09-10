# Operating cave atlas

## Deployment and release

Canonical source: https://github.com/snowball-projects/cave-atlas

Live interface: https://snowball-projects.github.io/cave-atlas/

GitHub Pages is configured to use GitHub Actions. `.github/workflows/pages.yml` tests changes and deploys successful main builds. PR checks cannot deploy. Static output is `dist/`; relative asset paths support the repository subpath and local previews. No custom domain or runtime secret is required.

For a release, update `package.json`, synchronize the lockfile, write release notes, run `npm run verify` and formatting, inspect the diff and push main. Confirm the successful Pages workflow, live interface and `version.json`; tag that exact commit and publish release notes. To roll back, revert the unwanted commit and let Pages deploy the revert. Do not force-push history or move release tags.

## Costs and third parties

GitHub Free supports Pages from this public repository. There is no paid backend, API plan or domain attached to this project. GitHub currently limits published Pages sites to 1 GB and has a soft bandwidth limit of 100 GB/month; [check current limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) before materially increasing assets or traffic. The build reports total published bytes. Maintainer time, user bandwidth and device computation remain real costs.

Leaflet 1.9.4 is bundled under BSD-2-Clause. OpenStreetMap supplies ordinary interactive raster tiles; browsers use normal HTTP caching and send an origin referrer. Follow the [tile policy](https://operations.osmfoundation.org/policies/tiles/): no prefetch/offline downloads, no forced cache bypass, visible attribution, and no assumed SLA. The tile URL is in `web/app.js`; change the provider, CSP and attribution together if needed. No terrain or geocoding service is used.

## Privacy and failure behavior

The app does not collect accounts, telemetry, advertising identifiers, searches or selections. They stay in memory and reset on reload. GitHub handles hosting logs under its policies; OSM sees IP addresses and tile requests. Google and Wikipedia receive a request only when a person follows the corresponding link. No claim of zero third-party data processing is made.

If tiles fail, the list, filters and comparisons remain usable. If the map library cannot load, the app explains that and keeps those controls. Without JavaScript, a catalogue download and source documentation are available. Future unknown measurements must be explicitly represented rather than silently omitted or filled with zero.

## Dormancy and revival

There are no scheduled catalogue refreshes or runtime source queries. A dormant site retains its dated reviewed snapshot. Rebuild using the committed catalogue, pinned frontend tooling and vendored Leaflet; Python's standard library is sufficient for the build. Development dependencies are only required to test or refresh data. No historical browser environment, external database, or paid account is needed to revive the static site.

Monitor deployment failures when making changes. Before reactivating maintenance, verify source coverage, links, map-provider terms and dependency updates, then make a reviewed release. Keep detailed project documentation here rather than copying it into snowball's project card.
