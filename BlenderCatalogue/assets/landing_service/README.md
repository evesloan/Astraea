# Staff landing interfaces · Batch11

Two original script-assisted editable component designs, independently authored from the supplied staff corridor references. The images informed washable broad fields, deliberate impact protection and organized service mounts. No photographic pixels or prior game geometry were copied.

AST-LND-003 is a protected arrival/control return, 1.30 × 0.45 × 2.50m in Blender X/Y/Z. Its sloped service cassette retains each actual control surface as an individual GLB mesh. Original local graphics identify SERVICE, attention/request (bell), inspection (wrench) and an inactive status (circle/dash). These are purpose cues, not functional deck or lift controls. Four small local texture/material roles leave every shared staff material unchanged. The folded receiver supports the unchanged AST-STF-006 fixture as QA context. Its complete brackets, housing, lens guard and label fit the proposed component envelope. The fixture is excluded from the new production .blend and GLB, and adds no new fixture count.

AST-LND-004 is a fixed inspection/retrieval edge, 1.50 × 0.75 × 1.05m. Its work contact is Z0.925m; the lower retrieval contact is Z0.250m. Two folded frames support the top and fixed tray. The front mouth and toe region remain geometrically open. There is no moving tray, player cart or travel envelope.

## Editable and native handoff

- source/AST-LND-003.blend and source/AST-LND-004.blend contain named semantic meshes, physical surface markers, explicit datum roots, and retained small editable bevel/normal modifiers
- exports/AST-LND-003.glb and exports/AST-LND-004.glb contain evaluated meshes, normalized active UV layers, embedded shared staff textures, explicit datum roots and marker hierarchies; controls remain separate nodes
- source/build_landing_service.py regenerates the two components from the fully declared inputs in dependency_manifest.json
- interface_api.json records physical surfaces, opposing join witnesses, floor contacts, source/GLB points and normals, the exact reused fixture matrix, and paired mount points
- collision_proposals.json contains structural-only compounds, separate from visual exports; collision_approximation_notes.json clarifies the numerical allowances and measured undercapture

Source units are metres, X across, Y depth, Z up, front −Y. Native GLB is Y-up with source point (x,y,z) mapped to (x,z,−y), front +Z. Source pivots remain the floor datum at (0,0,0). In the proposed ship placement, source Z yaw is −90 degrees and ship point is (originX+sourceY, originY+sourceZ, originZ+sourceX). 003 origin is (−48.55,0,−377.05); 004 origin is (−48.95,0,−375.55). Heights are component targets, not recovered host headroom. Neither component crosses the proposed east band, the west arrival/turn reservation, or the cross-street. Lead independently screens the combined assembly.

The reused fixture transform relative to 003 is translation (−0.6,0.20,2.47), identity rotation/scale. The receiver underside and both fixture plate tops coincide at Z2.470m with opposing normals. Actual imported full fixture bounds are approximately X[−0.560,0.560], Y[0.025,0.373], Z[1.8625,2.470]. Receiver normal and source lens aim are recorded separately despite both pointing down in this installation.

## Evidence and scope

qa/component_checks.json reloads actual sources and imported GLBs: positive closed source meshes, exact physical marker normals, four real opposing joins, source/native bounds, all-fixture bounds/mounts and an advisory axial finish overlap screen. The only remaining fixture intersection candidates are the intended receiver/top-plate contacts. The earlier guard-plane issue and high-hatch fixture interference were fixed before final capture; earlier source/export evidence is retained under qa/revision01_before_surface_datum_fix.

qa/glb_validation.json independently resolves native hierarchy, checks finite geometry, winding, normal lengths, nonzero UV triangle area and embedded texture pixels. Counts are 1,192 triangles for 003 and 984 for 004. Normalized UV means one consistent active semantic UV layer before consolidation, with metric repeat coordinates; it does not mean clamping every coordinate into [0,1].

qa/collision_checks.json tests 343 points per declared void against native visual and proposed structural geometry, checks positive hull centers and rejects an intentionally incorrect enclosing AABB. The compounds have 10 and 16 structural convex shapes respectively. The 004 concave side frames use three exact convex sections per side to retain their inset profile and the retrieval mouth. These are component proposals, not accepted collision settings.

Per-shape conservative_empty_corner_limit_m values in the generated proposal are axial/profile allowances or bevel widths, despite the historic key wording. They are not maximum Euclidean distance claims. collision_approximation_notes.json supplies sqrt(3)-scaled padded Euclidean allowances and the independent finite surface-screen limits. Structural compounds intentionally omit small relief: maximum sampled visual-to-proposal undercapture is 54.0mm for 003 (service hatch/bolts) and 40.72mm for 004 (identification hanger). Keep this limitation if evaluating them in the original engine.

qa/render_evidence.json indexes four actual imported-GLB captures across exact original and revised evidence receipts. The revised 003-only capture adds service symbols with the same two cameras; original accepted 004 source/export/image bytes are retained. Each capture receipt binds its images to exact source/export/helper/script hashes before and after, camera transforms/lenses, frame checks and image hashes. Ordinary views use a 1.65m eye height. The control/fixture detail is an intentional service crop; the lower 004 service view uses a 1.20m eye. Neutral studio floor/lights/cameras are inspection aids only. Fixture lens is an unlit opaque shared material. No photometric or game lighting claims follow from these images.

qa/source_only_rebuild.json records a fresh initially output-free staging run from the eighteen declared inputs, including all nine staff texture roles loaded by the material helper and the four family-local graphic PNGs, their manifest and original no-font drawing script. Both production GLBs are byte-identical. Reopened editable geometry, topology, UVs, material assignments, hierarchy, transforms, custom properties and relevant modifiers have identical semantic signatures. The saved .blend containers are not byte-identical across the different staging path; that limitation is explicit. The closed source-only archive and actual build/signature logs are retained. Exact runner/checker hashes are bound before and after execution, together with their actual execution logs. No prior new output or QA input was used to generate the fresh components.

No room, body/cart fit, shaft, door stroke, headroom, load/support, working control, lift, electrical, light, route or native engine acceptance is claimed. The missing original ship remains necessary for those tests.

The first four-image acceptance, original no-symbol 003 sources and receipts are preserved under qa/revision02_before_service_symbols. That historical 003 source is superseded; its 004 source and images remain current. No additional geometry or material work was done to 004 for this revision.
