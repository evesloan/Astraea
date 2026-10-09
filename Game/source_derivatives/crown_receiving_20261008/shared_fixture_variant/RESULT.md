# Isolated common Crown fixture relocation: r002 source/runtime verified

Active candidate: `AST-CMD-001_crown_fixture_relocation_20261008_r002.blend` and matching `.glb`. It is not retained independently or adopted in Game/Catalogue. Parent owns retention, registration and installation. Original common assets, incoming rooms, live manifest and gameplay scripts remain untouched.

## Verified result

- Five complete fixtures move to the exact proposed positions: Navigation X15.1/X15.3, Solar X15.75, Bridge Z22.5/Z38.75. All other coordinates, roof-mount height, marker names/extras, light settings, normals, UVs and materials are preserved.
- Exactly 20 editable Housing/Lens pieces (240 triangles) and five datum objects move. The Blender save/reload snapshot preserves all other 2,797 native objects exactly. Original source data, including Communications, doors, roof and floor-bearing blades, remains unchanged.
- Native versus active runtime passes all 32,724 triangle/material/UV signatures at four decimals, plus every marker within 0.00001 m. This follows the existing source-comparison convention; native preservation is exact before/after snapshot equality outside selected transforms.
- All 729 original runtime node identities remain. Twenty explicit relocated-fixture batches preserve part identities; historical-to-active memberships are recorded. The active maximum batch extent is 13.6399999857 m, within the unchanged <16.001 m gate.
- 225 actual white-roof contact rays pass at housing-top Y111. 225 full shared-plus-incoming downward lens-footprint rays are clear to Y108.8. Incoming housing AABBs and other fixed fixture housing AABBs have no overlaps. Navigation and Solar retain cross-rib alignment; the two shifted Bridge fixtures mount directly to the unchanged roof, no longer the original cross-ribs.
- Existing 76-degree half-angle cones and all photometric values are unchanged. Sampled off-axis rays intersect normal room/coffer surfaces; counts are recorded, not treated as evidence of a clear cone or final lighting acceptance.

## Preservation chain and historical failed gate

`prepare_variant.py` produces r001 by changing only the selected POSITION components, affected accessor extrema and five datum translations. Every other binary byte/JSON field is proven unchanged. Each selected source piece requires all eight retained corners, correct material, exactly twelve triangles and no selected vertex referenced by an unrelated triangle. An initial pre-save corner-match assertion identified coincident split-face ambiguity; requiring all eight source corners resolves it without weakening checks.

r001 retains original batching and fails the unchanged size gate for two Bridge batches at 16.25 m. That rejected batching variant is preserved as history and must not be adopted. `split_fixture_batches.py` creates r002 by moving only the 240 relocated triangles into 20 compact fixture batches. All 32,724 oriented triangle POSITION/NORMAL/TEXCOORD/material byte signatures remain identical to r001; unused predecessor binary bytes are retained as well. Unrelated active triangles and attributes are unchanged. `BATCH_SPLIT_PROOF.json` distinguishes historical from active memberships.

Geometric ray checks were measured on r001. `GEOMETRY_PROVENANCE.json` transfers them to r002 through exact oriented world-triangle/attribute equality; the successor changes grouping only. No photometric claim is inferred from ray checks.

## Deliverables

- `NATIVE_RUNTIME_PROOF.json`, `BINARY_EDIT_PROOF.json`, `BATCH_SPLIT_PROOF.json`: source/runtime and preservation evidence.
- `GEOMETRY_CHECKS.json`, `GEOMETRY_PROVENANCE.json`, `OTHER_FIXTURE_CLEARANCE.json`, `MARKER_TRANSFORM_PROOF.json`: mounting, collision, optical and identity evidence.
- `CENTRAL_CROWN_RUNTIME.proposed.json`: complete runtime-manifest copy changing only five position values.
- `RUNTIME_MANIFEST_PATCH.json`: exact JSON tests/replacements and proposed r002 runtime model-name selection.
- `geometry_parts.proposed.json`, `section_contract.proposed.json`: derivative source metadata changing only the selected coordinates.
- `ORIGINALS_PRESERVED.json`, `SHA256SUMS.json`: unchanged originals and deliverable hashes.
- `save_native_verify.py`, `NATIVE_SAVE_CHECK.log`: single released CPU2 Blender save/reload/import check, completed PASS and exit0. No runtime re-export occurred.

No new catalogue ID is allocated. No live adoption, Godot job, render, independent backup or registration was performed. Common-original independent retention was identified by the parent as GitHub checkpoint b7fdf2acb6f1828cd94d474c5d729ae6083ebc2a; this scratch derivative still needs independent retention before root adoption. Installed import/collision behavior, broad illumination and visual acceptance remain parent integration gates.
