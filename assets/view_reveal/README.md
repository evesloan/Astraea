# Astraea deep reveal kit 01

New independent architectural component assets, authored 2 October 2026. This is Blender component inspection evidence. It is not a recovered game scene, room installation, hull opening, glass system, playable prototype, or physics/performance acceptance.

The three supplied references were inspected directly. The design follows their generous rounded openings, substantial warm ivory architecture, material-separated timber return and restrained residential detail. It does not reproduce their room size, exterior/court image, glazing, railings or suite arrangement.

## Four unique source pieces

| ID | Piece | Local pivot and use | Evaluated triangles |
|---|---|---|---:|
| AST-VR-01-H | Straight crown/header | Left nominal seam at `(0,0,0)`; other seam at X2.2 | 412 |
| AST-VR-01-S | Deep sill/plinth | Left opening-edge seam at `(0,0,0)`; nominal foot Z−0.7 | 412 |
| AST-VR-01-J | Handed jamb/corners | Upper header seam at origin; lower sill seam Z−2.2 | 2,608 |
| AST-VR-01-T | Closed crown termination | Crown seam at origin; full eased/capped end at X0.24 | 842 |

The closed assembly uses H + S + two instances of J, totaling 6,040 triangles. The left J is a baked X reflection with recalculated outward normals and positive object scale. T is a separate genuine crown-to-wall termination demonstration, not an added decoration on the closed perimeter. It supports only the crown profile; a sill terminal is not claimed.

## Shape, dimensions and interfaces

The nominal assembly envelope is 3.35 m wide × 3.25 m high × 0.43 m deep, with a rounded 2.80 m × 2.20 m aperture from Z0.70 to Z2.90. Inner corner radius is 0.30 m. Evaluated dimensions and bounds appear in `manifest.json`; the 1.2 mm retained bevel eases the foremost point to an actual 0.42995 m depth. The straight sill reaches exactly world Z0.

The ivory perimeter has a shaped shoulder, crowned front lip and substantial body. The timber throat is 0.347 m deep, with a shaped mouth and a 3 mm radial material joint. There is no added thin outline strip or emissive material. Optional pane datum is Y+0.145 m only; no glass or distant view is supplied. Front is −Y, width is X, up is Z, and units are metres.

H and S sit at `(-1.1,0,2.9)` and `(-1.1,0,0.7)`. Right J sits at `(1.1,0,2.9)`; reflected left J sits at `(-1.1,0,2.9)`. Nominal joining profiles match exactly. Each cap is set back 1 mm from its nominal seam, producing an explicit 2 mm joint. Header and sill straight runs can be resized in the generator while preserving their profile; jamb height and radii are intentional fixed parameters for this batch.

The T shoulder eases inward and back over 0.24 m, with a full watertight distal cap. Its local depth is approximately 0.495 m because the closed back end returns an additional 65 mm. This is documented geometry, not an assembly envelope change. `qa/join_validation.json` compares actual reloaded source cross sections and seam gaps, while exploded and front/rear terminal views demonstrate the joins and ends.

## Editable source and runtime distinction

Each source `.blend` retains two named semantic meshes, separate ivory/walnut roles, metric UVs, an editable Bevel modifier and Weighted Normal modifier. The source generator intentionally authors the profile/rings; this is disclosed script-assisted modelling. Side UV grain follows each part's path, at the shared material scale (walnut U0.65 m / V1.3 m). Caps use independent planar metric UVs. Runtime export evaluates modifiers and repairs only microscopic bevel UV slivers with a metric planar projection.

Each GLB has two material-role meshes/primitives and two embedded 256 px PNG textures. The GLB assembly is likewise consolidated to two meshes; editable assembly parts remain separate in Blender. Textures and ordinary Principled materials come from the common material library. GLB uses the standard Blender Y-up conversion; the source uses Z up.

## Verification and evidence

- `qa/glb_validation.json`: independent binary glTF parser checks dimensions/transforms, finite positions/UVs, indices, nonzero triangle areas, unit normals, normal/winding consistency, metric-cap UV noncollapse, and embedded material textures
- `qa/source_reload_validation.json`: a fresh Blender process reloads all seven source/QA files, verifying retained modifiers, packed images, positive scale, finite geometry, manifold evaluated meshes and positive volume
- `qa/join_validation.json`: source ring correspondence and measured 2 mm joining gaps
- `qa/neutral_640.png`, `standing_640.png`, `seated_640.png`: neutral complete component and ordinary 1.65 m / 1.15 m eye positions
- `qa/detail_1280.png`, `join_exploded_1280.png`, `terminal_closed_1280.png`, `terminal_rear_1280.png`: higher-resolution profile, join and cap evidence

Final evidence uses Blender Eevee at 128 samples with bounded four-thread invocation. The system's Cycles build lacks OpenImageDenoise, and the noisy initial Cycles inspection was replaced. Nonfatal EGL/cache warnings may appear during successful Eevee headless initialization. The renderer is recorded in the source and logs.

`collision_proposals.json` contains separate perimeter convex-segment proposals. It does not fill the aperture with a single hull. Collision, actor approach, original room fit, game lighting/material response, visibility/culling, motion, target-PC performance and contact remain pending in the original project. The separate bench is not included or claimed to fit here.

## Reproduction

From any working directory:

`blender -b -t 4 --python /absolute/path/to/view_reveal/source/build_reveal.py`

Append `-- --no-render` for geometry/source/export only. To repeat renders from saved sources, run `qa/render_clean.py`. Run `qa/reload_sources.py` with Blender and `qa/validate_glb.py` with ordinary Python. `qa/finalize_records.py` labels final evidence and records hashes after the render/validation passes. Parent-managed durable batch backup is required before expansion.
