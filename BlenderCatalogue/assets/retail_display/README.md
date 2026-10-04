# Batch18 retail display components

Two original, editable component designs translate the supplied promenade's joined pale structure, orange recess, dark inset field and tactile display surfaces. Both actual reference images were inspected before authoring. No reference pixels are used as textures.

| ID | Design | Actual full source XYZ envelope | Source parts | Triangles | Runtime material groups |
| --- | --- | --- | ---: | ---: | ---: |
| AST-RTL-001 | Rising recessed retail display bay | 3.40 × 0.90 × 2.90 m | 40 | 552 | 5 |
| AST-RTL-002 | Offset stepped merchandise island | 1.90 × 1.40 × 1.05 m | 12 | 256 | 5 |

The bay's continuous plinth supports a rising asymmetric pale surround. The recessed terracotta returns meet the full arch-shaped dark back, while differently sized upper display alcoves and permanently open lower storage explain its use without inventory clutter. Its source −X end contains a real side-facing display recess with a tactile sill, dark back and orange return, useful for the proposed entry-facing placement. The upper contour rises from shaped side returns to the central canopy; it is not a rectangular cabinet with applied decoration. A 3 mm ornamental metal strip ends on a real wood face, and two physical rear mount pads provide proposed contact datums.

The island's long, low faceted display terrace and smaller offset upper tier provide surfaces at source Z = 0.69 and 1.05 m. A pale grounded pedestal has an actual front storage/retrieval pocket. The upper terracotta mass is supported by a pale foot and lower terrace. Every primary top and storage support patch is included in the manifests and marker API.

## Coordinates and authority

Source coordinates are metres, Blender XYZ, Z up, front −Y. Native GLB coordinates are `(x, z, −y)` with a proper rotation, never reflection. All source/native markers and support polygons are explicit. Floor origins are datums; rear wall pads on AST-RTL-001 are proposed physical contact faces, not approved drilled anchors.

For the separate proposed R070 study, the source-to-ship map remains `ship = (78 − sourceY, 52.5 + sourceZ, 236 − sourceX)`. R070 / Kind Curios /070 is a historical 12 × 12 m allocation, not a recovered finished room. These components make no host, local ceiling, door, moving pocket, activity-slot, reach, species-fit, load, inventory, visitor-capacity, payment or runtime adoption claim.

## Editable source and economical exchange

`source/AST-RTL-001.blend` and `source/AST-RTL-002.blend` retain separate semantic editable solids. The original generator is `source/build_retail_display.py`. All parts have authored metric UVs; top wood grain follows longitudinal X. Export does not repair or substitute UVs. The grouped GLBs embed all five used original/shared material textures. There are no moving mechanisms or state-only artistic counts.

`collision_proposals.json` contains a literal `detail` role for each exact convex authored part. `actor_proxies/body_collision_subset.json` contains an optional literal `body` role: 31 shapes for the bay, 11 for the island. The bay's compound surround merges material-layer construction and conservatively occupies at most the documented shallow 90 mm finish setback; no useful opening is enclosed. Thin ornamental metal details are omitted by 3 mm and 5 mm respectively, separately from material thickness. These are source-level choices, not measured engine cost or collision adoption.

## Rebuild from original inputs

`source_input_manifest.json` is the complete original-input closure. It includes every image loaded by the common helper, including unused palette roles. The new terracotta PNG and manifest must be generated from `materials/retail/draw_textures.py` before the retail material helper loads. The actual clean test copies no pre-existing new blend, GLB, manifest, QA input or generated retail artwork.

From a catalogue root with these declared original inputs:

1. Run `python3 materials/retail/draw_textures.py`
2. Run `blender --background --threads 2 --python assets/retail_display/source/build_retail_display.py`

`qa/source_only_rebuild.json` records byte-identical reconstruction of both GLBs and of the original terracotta artwork. Blender source file hashes may differ because packed image origin paths differ in the isolated stage; source geometry, markers, material roles and all other manifest fields match.

## Evidence and its limits

- `qa/source_checks.json`: all whole convex profiles, noncollapsed UVs, packed images, physical marker surfaces/normals, joins and complete horizontal support polygons
- `qa/geometry_checks.json`: actual native geometry/marker/bounds correspondence with wrong-axis controls, full solid overlap checks, useful-volume checks against both detail and body roles, and inserted-solid blocked controls
- `qa/001_neutral_actual_glb_section.png`: source X = 0 cut of actual exported GLB triangles, all materials neutral grey; backed by `qa/neutral_section_evidence.json`
- `qa/all_camera_preflight.json`: all imported camera bounds checked before any heavy capture
- `qa/review_media_manifest.json`: exact imported capture, camera and frozen source/export/script hash scope once capture completes

Neutral floor, lighting, camera and section presentation are inspection aids only. They are not runtime assets, a finished R070 shop or proof of the original game's renderer or target-PC performance.
