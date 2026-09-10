# Next work

These are proposed improvements, not shipped features or dated commitments.

## Broaden the catalogue

Expand beyond the initial 45 deepest-cave records, adding well-documented caves across regions and formation types. Prefer incremental reviewed additions over a large unverified import. Evaluate Wikidata, OpenStreetMap and specialist sources; reuse suitable open data instead of building a parallel contribution system.

Before expanding: model per-record provenance and stable source IDs; distinguish entrances from cave systems; support unknown dimensions without treating them as zero; preserve measurement units, source dates and licensing. Verify appropriate location granularity and any access claims. Keep updates reproducible and easy to pause; catalogue growth is ongoing maintenance, not an automated scrape-and-publish promise.

## Optional 3D survey pilot

Explore one real, suitably licensed cave survey as the next possible interactive feature. Prefer a simple rotatable passage/shaft outline to detailed textures or photorealistic geometry. Our current location/depth/length fields cannot reconstruct a cave's shape.

Evaluate [CaveView](https://github.com/aardgoose/CaveView.js) first: it is an existing MIT-licensed browser viewer for Survex/Therion/Compass models, with a [GitHub Pages demonstration](https://aardgoose.github.io/CaveView.js/). Reuse an established library if it keeps maintenance smaller; measure its actual cost before adopting it. Viewer licensing does not grant rights to survey data.

Use an explicit 3D button only for caves with a model; double-click may be an additional shortcut. Load the viewer and model on demand, provide rotate/zoom/reset and source/date labels, offer a static fallback, and release rendering resources when closed. Self-host allowed assets without accounts, tracking or paid APIs. Measure transfer size, render time, memory and behavior on an ordinary phone before expanding. Do not add fabricated geometry, cave-navigation claims, terrain services, or a 3D dependency before the pilot justifies them.
