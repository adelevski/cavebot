# spelunk icon

Canonical artwork: `assets/icon.png`. Generated with the built-in image-generation tool on September 10, 2026, replacing the cave atlas map/entrance artwork. The PNG has real transparency and subtle green tonal variation; it is retained without background removal or hand-drawn replacement geometry. It is an abstract identity mark, not a rendering of a surveyed cave.

Two nested, irregular contours suggest a passage receding into depth. No route line, map pin, stalactite or text is used. The direction anticipates digital cave exploration; it does not imply that a 3D viewer is already implemented.

Deployment derivatives use Lanczos downsampling with alpha preserved: `web/icon.png` (96px), `web/favicon.png` (32px), and `web/apple-touch-icon.png` (180px). The snowball card uses a 256px derivative. The full source image is not shipped with the dashboard. Original artwork uses MIT. Earlier artwork and its prompt remain in Git history and prior release tags.

## Generation prompt

```text
Use case: logo-brand
Asset type: standalone square logo icon for spelunk, a cave atlas.
Primary request: Create ONE original minimalist cave-passage mark. Two or three irregular nested and slightly offset contours suggest looking into an underground chamber receding into depth. Depth must come entirely from broad negative-space gaps, never shading.
Style/medium: Flat, crisp, vector-like logo artwork. Bold simple contours, compact balanced squarish silhouette. Designed to remain clearly legible at 32 pixels, with generous separation between contours.
Color palette: Exactly one solid deep forest green ink, #173e39. Anti-aliased edges may use partial alpha.
Scene/backdrop: Genuinely transparent background, actual PNG alpha transparency, including the negative spaces inside the icon. No white or colored backdrop and no simulated checkerboard.
Composition/framing: A single centered icon with comfortable transparent margin on a square canvas.
Constraints: Original abstract art, not actual cave geometry. No text or lettering. No stalactite silhouette, map pin, route line, compass, ants, gradients, shadows, lighting effects, texture, mockup, or extra decoration. Deliver only the one standalone green icon on true transparency.
```
