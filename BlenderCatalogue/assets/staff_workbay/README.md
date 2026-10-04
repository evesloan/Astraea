# AST-STF-007 — staff supply / work cabinet

One new independent editable design. The cabinet uses cooler painted metal, a rolled zinc worktop, C-shaped side channels, folded shelf trays, a washable splashboard and four grounded feet. The left locker has a real perforated leaf, separate pull assembly and a bored hinge. The right compartments remain open. No supplies, chores, roommate story, room/crew allocation or runtime interaction were added.

- Closed outside dimensions: **1.800 × 0.665 × 1.150 m** (X width, Y depth, Z height)
- Counter: **1.800 × 0.620 m**, top at **Z 0.940 m**
- Front: **Blender −Y**. Floor origin: **(0, 0, 0)**
- Editable source: `AST-STF-007_supply_work_cabinet.blend`
- Portable exchange: `AST-STF-007_supply_work_cabinet.glb`
- Reproduce: `blender --background --threads 1 --python build_staff_workbay.py`
- Dependencies: `../../standards/staff_materials.py` and the original staff colour tiles in `../../materials/staff/`; ordinary base colour maps are embedded in the Blender and GLB files
- Geometry: **11,060 evaluated triangles**. Static material-role meshes, leaf material-role meshes and handle material-role meshes are separate in GLB. Source keeps semantic parts and editable bevel modifiers
- UVs: metric projection, one active `UV_Metric_Metres` layer. Evaluated bevel/corner UVs are refreshed before export consolidation. Independent GLB parsing reports zero missing/collapsed UV area, degenerate triangles, or opposed normals

## Articulation coordinate contract

The genuine parent node is `AST-STF-007_door_hinge_pivot`. Closed pose is 0°. Normal opening is **−105°** around the declared positive axis.

| Coordinate space | Pivot in metres | Positive hinge axis | Front |
| --- | --- | --- | --- |
| Blender editable source / Blender reimport | (−0.837, −0.317, 0.200) | +Z | −Y |
| Standard Y-up GLB | (−0.837, 0.200, 0.317) | +Y | +Z |

The conversion is **(X, Y, Z) → (X, Z, −Y)**. Preserve the signed angle around the converted axis. Blender's importer converts the GLB back to its Z-up frame; the inspection script explicitly uses XYZ rotation mode and checks the full world pivot matrix before each final open render.

Leaf nodes:
- `AST-STF-007_door_leaf_staff_bluegrey_paint`
- `AST-STF-007_door_leaf_staff_zinc`

Handle nodes:
- `AST-STF-007_door_handle_staff_rubber`
- `AST-STF-007_door_handle_staff_zinc`

No animation/controller is included. Godot import, physical response, input, actor reach and scene placement remain pending.

## Component evidence and limits

`qa/door_sweep_report.json` records **421 actual-geometry poses** at 0.25° intervals, for both the evaluated source and actual imported GLB. Both have zero visual triangle intersections. The leaf and handle geometry agree exactly between source and GLB (0 m bidirectional vertex difference and matching triangle counts).

The report separately gives continuous conservative bounds across the full angle interval: **15 mm** main leaf/body plane separation, **202 mm** floor clearance, positive fixed/moving hinge mount/ear/pin clearances, and a **0.443 mm** conservative pin-to-bore radial bound. These are rigid component geometry proofs only. They do not establish game controller behavior, physics tolerances, actor reach, installed route clearance, or engine performance.

`AST-STF-007_supply_work_cabinet.collision_proposal.json` supplies individual numeric box proposals for formed-sheet regions and real solid door cells. It never fills the hollow cabinet with a whole-body convex shape. Proposed approach/target/contact data are unaccepted installation data. The overall locker cavity envelope is explicitly distinct from its two wholly clear lower/upper storage volumes.

`qa/RENDER_MANIFEST.json` identifies source/export hashes, cameras, intended angles, actual pivot matrices and handle landmarks. QA views are labelled **Blender imported-GLB component evidence**. The 1.65 m eye-height image is an ordinary standing view. Inspection floor and lighting are not source/game geometry.

The initial intended-open images were invalid because the importer selected quaternion rotation mode and ignored Euler edits. Their exact old hashes are labelled invalid in `qa/invalid_pose_history/invalid_pose_manifest.json`; the root QA images supersede them. Optional history is not part of the active deliverable and adds no unique designs.

## Coordinate metadata revision 02

The current `.blend` and `.glb` use **hinge-frame-metadata-02**. Their actual hinge node has no unqualified `axis` field. `hinge_axis_blender_source` is `[0, 0, 1]`, and `hinge_axis_gltf_yup` is `[0, 1, 0]`. Each frame has its own numeric pivot and explicit opening hint. The signed opening remains 0° through −105° about its stated positive axis. Exported extras are copied verbatim, so their names identify the frame of each value.

The generator writes the same fields. An isolated reconstruction with copied shared dependencies produces exactly equal GLB JSON values and a byte-identical BIN chunk. The reviewed production geometry was retained; the current GLB was changed only by replacing the hinge extras in its JSON chunk.

Exact pre-revision source, export, generator, manifests and checksums are preserved under `../../qa/batch05/cabinet_metadata_revision/original_inputs/`. Existing Batch03 sweep, render and validation records retain those historical hashes and were not rerendered or rewritten. `../../qa/batch05/cabinet_metadata_revision/verification_report.json` records the current source reload comparison, GLB invariants and generator check. All 63 base/evaluated meshes, 65 objects and their hierarchy/transforms/modifiers, four material graphs, all nine packed images and scene units match. Blender editor window/layout state is outside that asset-data comparison.
