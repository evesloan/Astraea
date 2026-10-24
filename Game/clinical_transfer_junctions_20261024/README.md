# Paired clinical transfer junctions — unfinished physical successor

This package coordinates the existing D01 Pool and D06 Royalty clinical transfer layouts with the retained longitudinal through routes. It reuses source gate parts, materials, room allocations and floor owners; it does not create clinical operating identities or admit operation.

D06's transfer buffer moves forward to Z22 and its clean approach moves to X102.6 around the western Royalty pier. The existing room receiver turns at X95.1 and joins the outer return at X110.6. The two obsolete spur approaches receive physical closures. All four original D06 gate identities and84 mesh/contact nodes are reused at the successor positions. The five earlier canonical gate-reference bindings remain valid.

D01 uses an offset transfer buffer: fore clean gate(-57.45,-406.4), aft clean(-57,-396), room gate(-53.05,-402) and return gate(-61.3,-400), all at Y21. The Pool bearing and the room's original back-edge support remain intact. Four source-derived cassettes fill the previously absent Pool fittings. Six named room partition jamb/head skins provide a3.7m-wide/3.3m-high receiving opening; the existing stream installs these successors before constructing its contacts and occluders, and reinstalls them on later loads. No replacement residency manager is introduced.

The original gate aperture is3.6×2.4m, insufficient for the prior3.6m-wide/3.2m-high corridor envelope. A named3.7×3.3m successor preserves the21-part composition, source materials, base/top details and1.9m pocket length. The two leaves become1.85m wide. All eight cassettes share21 mesh and21 contact resources. The original GLBs/native assets remain immutable; other installed gates are unchanged. The old slider's hard-coded collision/sweep dimensions are not compatible without a separately reviewed operating successor.

`PLAN.json` records exact original source hashes, changed owner preimages, gate transforms, missing-only floor and authored parts. Public receiving work is under `ShipSpace/ClinicalTransferJunctions20261024/{D01_Pool,D06_Royalty}`. Existing D06 fittings keep their original `Group3CompleteClinical/AST-MED-G3-010` node paths. Source-skin successors preserve the rest of each loaded owner's vertices, UVs and materials. No protected bearing, hull, room identity or capacity is changed.

The actual-ship check deliberately distinguishes physical construction from operation: every gate must remain closed. Architectural-clearance queries exclude the80 closed leaf-part contacts only; fixed jambs, pockets, bearings, walls and other architecture remain included. This establishes potential architectural clearance, not a moving loaded-cart test or interlock/inside-egress acceptance. The existing eight-source light selector remains unchanged.

## Operating source status

The full-clinical builder names runtime `sliding_gate.gd` and `crossing_buffer.gd` paths that are not installed in the current runtime folder. A slider is retained under `RetainedConstruction/group3/payloads/Game/scripts/group3_clinical_full_20261011/sliding_gate.gd`; the located full-crossing controller is inside `qa/rejected_runtime_contract_candidate003`. Neither is silently adopted or treated as an accepted provider. The retained port2 supervisor/gate and dispatch source remain history. Authoritative IDs, mutual exclusion, sealed-load/stock/sterility and inside-egress criteria are held.

The package is not final engineering, clinical operation, visual, whole-gameplay/performance or Windows acceptance. No graphical capture, export, permission change, denied-route retry or workspace rebuild is part of this work.

## Precision and native provenance

The captured production arrays exposed two different degeneracies: exact-zero fragments produced by clipping, and97 additional collapsed triangles produced by Godot's0.1mm TriangleMesh snapping. The adapter discards only exact-zero triangles in the stored surface arrays and creates precise contact shapes from their unchanged indices/vertices. The resident mesh owns a strong shape lease while the existing cache holds a weak reference; no global retention pool is added. See `evidence/CONTACT_ARRAY_PROOF.json` and the [Godot4.6.3 TriangleMesh source](https://raw.githubusercontent.com/godotengine/godot/4.6.3-stable/core/math/triangle_mesh.cpp).

The historical D01 native package named in `REMAINING_BATCH_SECTIONS.json` is absent locally. This package does not claim its original Blender file was recovered. Its new editable receiver skins preserve the actual retained GLB arrays, material parameters and embedded PNG bytes. The three staff source libraries remain linked by relative paths. The saved successor is a new native revision, not an overwrite of any original.

## Selected integration and evidence

The selected main is `scenes/bootstrap_clinical_transfer_junctions_integrated_20261024.tscn`, retaining the existing launcher/menu/settings chain. The hook runs after `remaining_batch_receiving.gd`, before final occlusion/residency registration.

The actual complete ship reaches readiness and passes902 changed-work checks with clean exit0:125 route samples,375 floor rays, eight closed gates, all protected supports, exact contact triangles, existing light selection and D01 release/reload.317 authored parts use10 local material batches and add59.661687m² of missing-only floor. Eight closed cassettes use168 instances sharing21 mesh/shape resources;84 D06 instances are reused,84 Pool parts are newly installed. The six earlier failed attempts and the initial environment-only launch failure remain separately recorded. No failed attempt is relabelled as a pass.

`BlenderCatalogue/assets/clinical_transfer_junctions_20261024/ClinicalTransferJunctions_r001.blend` reopens with353 checks and zero measured position difference, including23 exact owner skins, three relative source libraries and both original embedded texture hashes. This is editable source integrity, not inspected final artwork. Open `Game/project.godot` after repository-root `python PREPARE_EDITOR.py --check-only`.
