# spelunk working guide

Maintain a small static cave explorer. The accepted interface is a full-screen map, compact filters/list on the left, and a collapsible comparison on the right. Keep the visible name `spelunk` lowercase and the results heading `Comparison` constant. Project direction belongs to snowball's founder, Nas Delevski.

- Read README.md and data/README.md before editing. For public claims, architecture, data or operations, read the canonical principles at https://snowball-projects.github.io/principles/ (local sibling site when available). Do not duplicate or silently rewrite them.
- Preserve unrelated changes. Keep source, reviewed catalogue, behavior and styling separate. No runtime framework, backend, live database queries, tracking or credentials without demonstrated need and an owner decision.
- Python 3.10+ and Node 24. Install requirements-dev.txt and `npm ci`; run `npm run verify`. Browser tests mock tiles. Run `npm run format:check` for supported source formats. Builds and tests are offline after dependencies are installed.
- Data must carry source/revision, retrieval date, terms and explicit limits. Publish regional coordinates rounded to 0.1°. Never invent geometry, measurements, visitor access, or locations. Source-parser drift must fail clearly. Review candidate refreshes before publication; no automatic catalogue replacement.
- Keep units next to numbers. Depth and length have separate scales shared across selected caves. Filters preserve selections. Maintain keyboard access, readable small screens, visible focus, reduced motion and useful map-failure behavior.
- Original code uses MIT; preserve existing copyright and third-party notices. Data and software licenses are separate. No AI-builder labels or inflated claims.
- `package.json` owns the release version. Pushes to main deploy through `.github/workflows/pages.yml` only after checks. Inspect the staged diff, verify the remote, and confirm the deployed version and live interface before claiming publication. Preserve history; never force-push.
- Keep operations and revival instructions in docs/OPERATIONS.md. Real-survey 3D exploration is the next feature priority; broader catalogue coverage and lazy-loaded 3D surveys are documented in docs/ROADMAP.md; neither is shipped by implication.
