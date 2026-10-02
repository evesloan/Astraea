# Aquatic lounge furniture

Two original independent catalogue designs, authored in Blender 4.3.2 on 2 October 2026. This is new script-assisted geometry, not recovery or reconstruction of the original game. The supplied aquatic image informed the warm clay/ivory/teal hierarchy, curved supported lounging shape and useful drained surfaces. No image pixels or third-party models are included in the art.

| Asset | Measured size, X/Y/Z metres | Evaluated triangles | Runtime material meshes |
|---|---:|---:|---:|
| AST-AQU-001 sculpted wet-area lounger | 0.827 / 1.980 / 0.993619 | 9,960 | 4 |
| AST-AQU-002 companion drained tray table | 0.666 / 0.564986 / 0.453 | 4,284 | 5 |

Both origins are on the floor at Z0. X is width; the lounger head is +Y and feet/front are -Y. GLBs use the normal glTF Y-up conversion. Sources contain editable named semantic meshes, edge modifiers and packed textures; evaluated exports are consolidated by semantic material role. Source files contain no QA cameras, lights, floor or scene context.

The lounger has six shaped clay contact panels with five real 8 mm longitudinal drainage slots, a pelvic dip, rising knee support and reclined back. Two continuous ivory side rails, six slope-aligned alloy cross supports, four shaped load legs and paired sled runners carry the contact surfaces to four floor grips. The table uses an interrupted raised rim, four separate stone panels, a lowered teal center channel, 8 mm slots, two open bowed trestles and four floor grips.

Measured lounger contact samples at X0.055 avoid the central drain slot: pelvis Z0.441893, thigh Z0.455947, shoulder Z0.842866 and foot Z0.356436 metres. The table's stone surface is Z0.438, center channel Z0.431 and rim Z0.453. These are human-scale proposals; species contact, wet grip, comfort, tip/load stability, drainage performance and safety are not certified.

Keep one transfer side clear. Proposed lounger transfer rectangles are X[-1.15,-0.43] or X[0.43,1.15], Y[-0.55,0.25]. A proposed foot approach is X[-0.44,0.44], Y[-1.70,-1.10]. A companion table can sit beside the hip on the opposite side. These local-coordinate envelopes require real actor/room validation before use.

## Verification and corrections

- Both saved .blend files reload with all used textures packed, identity object scales, UVs and closed source solids
- Independent GLB accessor checks pass dimensions, finite coordinates, normals/winding, normalized UV sets, nonzero UV triangle area, semantic materials and exact embedded texture hashes
- All declared support interfaces have evaluated surface intersections, and all four grip bottoms on each asset reach exactly Z0
- Eighteen rays on the actual imported lounger GLB find the metal support tops at least 10.043 mm below the clay contact surface
- Camera preflight passes for whole components; the joint detail is an explicitly cropped view
- Actual-GLB images include three 640x360 views, 960x720 table/support details, and a labelled 640x360 table legibility card downsampled from the detail

Two issues were found and corrected. A scoped editable 1 micrometre post-bevel weld removes nanometre duplicate vertices at the table trestle shoulders; export-only metric UV reprojection repairs those welded corner faces without changing the visible design. The first actual-GLB lounger image exposed flat cross supports cutting through inclined contact panels. Aligning the cross supports to the local recline slope removed that defect while retaining all joints. Initial rejected numerical evidence and the first failed contact image remain clearly marked under qa/initial_rejected for traceability; they are not final review media.

Final review files are listed in qa/review_media_manifest.json. See qa/render_evidence.json for actual export hashes, camera plans, stage scope and correction provenance; qa/glb_independent_validation.json for binary checks; qa/source_reload_checks.json for source verification; and qa/actual_glb_contact_clearance.json for the final contact samples.

## Reproduction and adoption

Run Blender from the catalogue environment with:

    blender -b -t 2 --python source/build_aquatic_lounge.py
    python qa/validate_glb.py
    blender -b -t 2 --python qa/check_sources.py
    blender -b -t 2 --python qa/check_contact_clearance.py
    blender -b -t 2 --python qa/render_imported.py -- --preflight

Render only after reserving the shared heavy-render slot. qa/render_imported.py uses EEVEE_NEXT, 48 samples, two CPU threads and no denoiser. QA floors, lights and cameras exist only in that inspection script.

Numerical compound collision proposals are separate JSON data. They preserve the open underside and side approaches; segmental contact boxes intentionally bridge narrow drainage slots. They are not instantiated or tested in an engine. The top table proposal is conservative around its curved corners. No LOD has been supplied; per-part triangle costs are retained for later profiling. Original-engine integration, water simulation, species rigs, actual ship fit and target-PC performance remain pending recovery of the original project.

Existing shared materials were not changed. dependency_manifest.json records all used texture dependencies, which are also packed in the sources and embedded in the GLBs. SHA256SUMS.txt records this family package. The lead owns independent review, whole-batch assembly and restored durable backup before further expansion.
