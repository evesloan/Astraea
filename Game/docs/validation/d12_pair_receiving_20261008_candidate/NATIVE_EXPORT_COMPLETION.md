# Native/export completion, 2026-10-08

This addendum supersedes only the README's statements that the deferred guard generation/native/export gates remain unrun. All live-adoption, independent-retention, structural engineering and Godot/runtime gates remain open. No live Game/Catalogue files were changed.

## Accepted isolated successor

native_attempts/build002/AST-RCV-D12-PAIR-001.blend and .glb are the final guard native/runtime candidate. There are116 named closed meshes. Each is an editable solid with ordinary retained material roles, packed images, correctly scaled UVs, support metadata and source-matched interfaces. The original corrected room files remain unchanged and retain their separate verified private-Library identities.

- Native authoring used Blender4.3.2, taskset CPU2 and two threads. No Godot, imports into Godot, renders or additional engines ran.
- verify_native.py reopened the saved native, checked each source-derived vertex, closed manifold topology, positive signed volume, unit normals and per-role UV scale. It saved a separate roundtrip native, reopened it and required exact semantic equality of every object's geometry/UV/normals/matrix/properties, used materials/node settings and packed resources. The two .blend byte hashes differ because serialization is not a semantic identity guarantee; both are retained. The accepted primary native is build002/AST-RCV-D12-PAIR-001.blend.
- verify_export.py parsed the actual GLB bytes without importing them into an engine. Each triangle was matched against native vertices, corner normals and UVs with cyclic ordering preserved. Positive exported winding volumes, all116 support/material identities, two embedded texture byte hashes, roughness/metallic factors and unit normals pass.
- All actual exported footprints have zero unsupported area and zero4m-clear-strip intrusion. All116 pieces remain floor-connected, with no positive-volume guard-to-guard overlaps. Actual exported barriers close at all piecewise-linear height events and interval midpoints. Source-jamb profiles were remeasured against the unchanged room GLBs across each terminal's full width; maximum absolute residual is0.000006356366555m. This float32 residual is reported, not described as exact physical contact.
- Native/export normal component differences reach0.000034660100937 because the exporter recomputes polygon normals on small bevel facets. A1e-4 component bound is used; unit vectors and triangle winding are separately checked. Position/source-interface tolerance is0.00002m. These numerical tolerances do not certify engine physics contact.

## Attempts retained

build001 successfully generated geometry, but its champagne_metal UVs used1m instead of the material's0.6m tile size. Its script, native/export and log remain under native_attempts. build002 corrects UV scale only; it does not change the116-solid geometry.

verify_export001 and002 used over-strict normal-delta bounds of2e-6 and2e-5. Their logs and exact script versions remain. Inspection located exporter float-normal recomputation on the terminal bevel facets. verify_export003 passes the justified1e-4 bound;004 additionally measures source-jamb residuals. Geometry was not relaxed or altered to pass these checks.

## Final evidence and activation limits

NATIVE_VERIFICATION.json, NATIVE_SNAPSHOT.json and EXPORT_VERIFICATION.json live beside the final native/export. runtime_manifest.json now pins the actual guard hashes, while operational_acceptance remains false. FINAL_CANDIDATE.json identifies the application inputs and final bytes/hashes. MANIFEST.json lists the complete scratch packet, including retained attempts and isolated compiler inputs.

The CPU2 Blender lane was released after the native process exited and raw export verification passed. No further native process is pending. Root must independently retain and verify the final transaction before live adoption. Native source parity does not replace Godot import, actual collision, loaded-cart travel, visual review, full tools/validate.py, engineering or room acceptance.
