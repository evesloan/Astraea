# AST-AQU-006 — Cove leisure seating float

An original script-assisted single-occupant leisure float proposal, authored in Blender 4.3.2 after inspecting the actual supplied aquatic reference. The warm orange/pearl/teal hierarchy translates the resort character without copying its ship layout or float pixels. A continuously shaped oval coaming rises into a rear back/head cradle. The recessed teal seat membrane has a small open drain and a flexible edge binding. Two continuous arched grips terminate in four closed reinforcement saddles. There are no default torus/cube furniture assemblies.

## Files

- Editable source: `source/AST-AQU-006.blend`
- Reproducible authoring generator: `source/build_float.py`
- Role-consolidated standard Y-up export: `exports/AST-AQU-006.glb`
- Full dimensions, contacts, costs and connections: `AST-AQU-006.manifest.json`
- Exact shared texture references: `dependency_manifest.json`
- Separate open-well collision proposals: `collision_proposals.json`
- Actual imported-GLB views: `qa/standing_labelled.png`, `qa/silhouette_labelled.png`, `qa/handle_labelled.png`, `qa/seat_labelled.png`

## Coordinates and design proposals

Authoring units are metres, Z up, front -Y, rear +Y. Origin `(0,0,0)` is the XY design centre on the proposed calm-waterline plane, not a computed flotation result or floor contact. Standard GLB conversion gives `(X,Y,Z)_GLB = (X,Z,-Y)_Blender`.

The measured external envelope is 1.4161 m wide × 1.6414 m deep × 0.7057 m tall, from local Z -0.1620 to +0.5437 m. The nominal well spans about 0.61 m across × 0.795 m front to back. The front coaming crown is Z +0.206 m, rising to the rear coaming crown around +0.540 m. These are intentional body-scale design dimensions, not a universal species claim.

The seat centre datum `(0,-0.06,-0.064)` falls inside the central drain and is explicitly not a contact point. Saved-source downward raycasts provide actual nearby membrane contacts at approximately `(-0.12,-0.06,-0.05099)` and `(0.12,-0.06,-0.05096)`. The proposed back/head contact is a saved-source ray intersection on the pearl-skin mesh around `(0,0.47675,0.48478)`. A reclining posture, species reach and comfort remain unverified. Grip centres and all four saddle positions are in the manifest. The 46 mm grips have measured mid-arch lower-surface clearance of about 121 mm to the coaming.

## Geometry and material cost

The asset contains 16 editable semantic meshes, 12,576 evaluated triangles, and four exported meshes/primitives/material roles. The export is about 374 KiB. Each of the four ordinary opaque Principled material roles references an original 256 × 256 PNG with metric UVs, packed into the source and embedded in the GLB:

- `aquatic_orange_float`: soft orange float skin
- `aquatic_pearl_float`: soft pearl accent skin and flexible reinforcement, not hard enamel
- `aquatic_teal_sling`: textured flexible seating membrane
- `aquatic_dark_grip`: dark grips, soft drain binding and valve boss

UV layer names are normalized before material-role consolidation. The export includes no water material, light, camera, game controller or collider. Collision data proposes 24 separate coaming wedges with explicit convex input points, local membrane patches, and grip capsule chains, preserving the open well and hand openings. It does not propose one whole-float convex collider.

## Verification and reproduction

From the catalogue root:

1. `blender --background --threads 2 --python assets/aquatic_float/source/build_float.py`
2. `python assets/aquatic_float/qa/validate_glb.py`
3. `blender --background --threads 1 --python assets/aquatic_float/qa/inspect_source.py`
4. `blender --background --threads 1 --python assets/aquatic_float/qa/measure_contacts.py`
5. `blender --background --threads 1 --python assets/aquatic_float/qa/render_imported.py -- --preflight`
6. Reserve the shared heavy-render slot, then run `blender --background --threads 4 --python assets/aquatic_float/qa/render_imported.py`
7. `python assets/aquatic_float/qa/label_qa.py`
8. `python assets/aquatic_float/qa/finalize_records.py`
9. `python assets/aquatic_float/qa/validate_collision_proposals.py`

The independent GLB parser verifies 12,576 triangles, finite positions/normals/UVs, positive transforms, no collapsed UV triangles, no winding opposed to normals, and exact pixel identity of all four embedded textures. Reloaded source inspection verifies all 16 meshes closed with positive signed volume, all recorded joined-part surface intersections, packed textures, and both palm openings. A separate ray confirms the drain centre is open. Numeric collision-proposal checks verify the five sampled well points lie outside every separate coaming wedge, all 96 sampled seat triangles face upward, the drain stays open and both grip capsule chains are continuous; this is not a physics or engine test. Full silhouette and standing camera preflight passes; detail crops are intentional. Rendering uses EEVEE_NEXT, 64 samples, no denoising. All evidence binds exact source and GLB hashes; caption strips preserve every raw render pixel.

## Limits

This is an authored catalogue component and Blender inspection evidence. No real-world buoyancy, stability, inflation pressure, material suitability, load rating, rescue function or safety certification is claimed. No new water simulation, controller, shader, district or route was made. Engine collision selection, actor/rig contact, waterline behavior and target-PC performance remain pending recovery of the original project. QA floor, lighting and camera are inspection aids only and are absent from the GLB.
