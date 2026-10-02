# Batch08 explicit interface audit

## Result and exact scope

The exact catalogue inventory is **45 unique designs**, backed by 45 source `.blend` files, 45 master visual GLBs and 40 distinct asset/family manifests. All 90 master hashes match the current catalogue. All 45 declared material-role sets match their actual GLBs. No high-impact current frame or hierarchy defect was found. The identified library texture path-base omission is resolved in current metadata revision `library-texture-paths-02`. Outstanding required corrections: none.

Read actual native GLB accessors and composed parent transforms for **338 scene nodes / 212,215 triangles**. No orphan nodes or external GLB buffer/image URIs were found. Native dimensions agree with the catalogue's Blender-frame dimensions within 1.50e-8 m. This is a dimensional consistency check, not a fresh independent Blender-scene comparison.

Checks: **75** explicit marker-to-native-world-origin comparisons, **44** neutral-pose physical surface witnesses within 2 mm, **885** explicit source/native vector pairs, **713** normalized direction/axis/normal records, **217** resolvable dependency/path hash assertions, and **24** finite basis/hierarchy witnesses across **10** assets with real declared motion/removal interfaces. All checks pass. The 885 vector pairs include repeated exact records in different authoritative documents and GLB extras; this is not 885 independent physical tests.

No Blender scene was loaded, no render run, and no master source/export file modified by this auditor. Prior Batch05 coordinate proof and the current cabinet hinge revision remain authoritative and are hash-bound. Existing Batch06/07 source/export reports are linked per relevant asset. This pass does not execute asset generators or unknown archive code.

## Corrections and semantic distinctions

- **IF-001 resolved:** the library texture manifest now explicitly resolves eight existing PNG basenames through `textures/`, relative to that manifest. All eight current image hashes match. Lead preservation and texture-reproduction evidence is in `library_texture_path_revision/revision_report.json`. This auditor read the current files; it did not run that regeneration.

- **IF-005 resolved:** the lead isolated compact-source rebuild exposed a missing `qa/` directory assumption in the stock-variant generator. Its current explicit output-directory creation is inspected. `library_texture_path_revision/isolated_rebuild_report.json` records successful actual rebuilds of both unique library-content exports and two variants with all four GLBs byte-identical; its input hashes match current files. This is evidence supplied by the lead and verified for current-input binding, not an additional generator run by this auditor.

- **IF-002 consumer notice:** eight older origin extras describe Z-up/front −Y in unqualified prose. These are source-description text under the paired manifests and coordinate contract, while actual GLB geometry is Y-up. Frozen master bytes need not change. The staff cabinet hinge node itself already has explicit source/native axis and pivot fields; the residual text is only its floor-origin description.

- **IF-003 consumer notice:** hospitality station motion roots retain an authoring `export_group=static` tag. Their explicit proposed-motion kind, axis, travel and actual children define the movable groups. Do not interpret that tag as an engine immobility flag.

- **IF-004 known limit:** counter shelves, plate stacks and the trolley context tray have separable geometry but not a complete prescribed extraction trajectory for every group. Preserve this as unspecified; do not invent a grab point, motion limit, clearance claim or controller.

- Native marker positions and dual-frame extras are neutral asset-pose data. A marker parented below an articulated/removal node must follow the live hierarchy after motion; its initial asset-space extras are not live world transforms.

- Nozzle mouth centres, port bore centres, float drain datum and cup pose centres may intentionally lie in openings. Grip centrelines sit inside their tubes. They were not subjected to a false zero-distance surface-contact requirement. Floor/support direction does not necessarily equal outward triangle normal.

- All 34 wholly static designs have motion marked not applicable. AST-HSP-002 is separately marked separable geometry with unspecified trajectory. The other 10 have explicit component movement/removal proposals. No moving interface was demanded from a static part.

- Coping seam yaw and the documented next-origin rotation recipe explicitly define connection orientation. A second outward-normal field is not mandatory merely to duplicate that recipe. The proposed index records the existing source values; it does not relabel them native GLB.

## Deliverables and reproduction

- `interface_normalized_index_proposed.json`: complete 45-row semantic/applicability map, with exact input bindings and existing evidence pointers; proposed consumer data, not engine adoption proof

- `interface_coverage_map.json`: exact existing manifest interface records, supplemental family files, source/export/manifests and restoration-useful local script paths

- `interface_native_glb_evidence.json`: actual native node/parent/world transforms, materials, marker and surface evidence

- `interface_proposed_corrections.json`: resolved correction and remaining consumer notices, with exact per-file provenance

- `interface_input_bindings.json`, `interface_path_resolution.json`, `interface_dependency_hash_checks.json`, `interface_direction_checks.json`, `interface_dual_frame_checks.json`, `interface_motion_hierarchy_checks.json`, `interface_checks_summary.json`: reproducible evidence and scoped counts

From the catalogue root, run `OPENBLAS_NUM_THREADS=1 python qa/batch08/interface_audit.py`, then `OPENBLAS_NUM_THREADS=1 python qa/batch08/interface_semantics.py`. Both write only `qa/batch08/interface_*`. The existing read-only `qa/inspect_glb_independent.py` parser is hash-bound. Family-path resolution prefers the containing manifest folder; explicit catalogue-root references and declared texture-root rules remain intact. Prose expressions such as “matching exports/…” are retained as descriptions rather than silently treated as missing dependencies.

## Per-asset coverage

Every row has metre units, identified datum/source/exchange frames, actual GLB hierarchy evidence, source/export/manifest hashes, material-role references and restoration paths. Detailed distinctions and exact pointers are in the two index JSON files. C = declared placement/connection interface or explicitly no modular connector; P = contact/pose semantics classified. M = declared motion/removal; S = static, not applicable; U = separable geometry, trajectory unspecified.

| Asset | Family | Source / GLB hash | Native roles | C / P | Motion | Findings |
|---|---|---|---|---|---|---|
| AST-FUR-001 | view_day_furniture | match / match | match | covered / classified | S | IF-002 |
| AST-FUR-002 | view_day_furniture | match / match | match | covered / classified | S | IF-002 |
| AST-FUR-003 | view_day_furniture | match / match | match | covered / classified | S | IF-002 |
| AST-VR-01-H | deep_view_reveal | match / match | match | covered / classified | S | none |
| AST-VR-01-S | deep_view_reveal | match / match | match | covered / classified | S | none |
| AST-VR-01-J | deep_view_reveal | match / match | match | covered / classified | S | none |
| AST-VR-01-T | deep_view_reveal | match / match | match | covered / classified | S | none |
| AST-LIB-STR-001 | library_collection_structure | match / match | match | covered / classified | S | none |
| AST-LIB-STR-002 | library_collection_structure | match / match | match | covered / classified | S | none |
| AST-LIB-STR-003 | library_collection_structure | match / match | match | covered / classified | S | none |
| AST-LIB-STUDY-01 | library_study | match / match | match | covered / classified | S | IF-002 |
| AST-LIB-STUDY-02 | library_study | match / match | match | covered / classified | S | IF-002 |
| AST-LIB-006 | library_contents | match / match | match | covered / classified | S | IF-001, IF-002, IF-005 |
| AST-LIB-007 | library_contents | match / match | match | covered / classified | S | IF-001, IF-002, IF-005 |
| AST-STF-001 | staff_wall_protection | match / match | match | covered / classified | S | none |
| AST-STF-002 | staff_wall_protection | match / match | match | covered / classified | S | none |
| AST-STF-003 | staff_wall_protection | match / match | match | covered / classified | S | none |
| AST-STF-004 | staff_overhead_services | match / match | match | covered / classified | S | none |
| AST-STF-005 | staff_overhead_services | match / match | match | covered / classified | S | none |
| AST-STF-006 | staff_overhead_services | match / match | match | covered / classified | S | none |
| AST-STF-007 | staff_work_cabinet | match / match | match | covered / classified | M | IF-002 |
| AST-BOT-001 | botanical_canopy | match / match | match | covered / classified | S | IF-006 |
| AST-BOT-002 | botanical_understory | match / match | match | covered / classified | S | none |
| AST-BOT-003 | botanical_understory | match / match | match | covered / classified | S | none |
| AST-BOT-004 | botanical_planter | match / match | match | covered / classified | S | none |
| AST-BOT-005 | botanical_planter | match / match | match | covered / classified | S | none |
| AST-BOT-006 | botanical_planter | match / match | match | covered / classified | S | none |
| AST-AQU-001 | aquatic_lounge | match / match | match | covered / classified | S | IF-007 |
| AST-AQU-002 | aquatic_lounge | match / match | match | covered / classified | S | IF-007 |
| AST-AQU-003 | aquatic_edges | match / match | match | covered / classified | S | none |
| AST-AQU-004 | aquatic_edges | match / match | match | covered / classified | S | none |
| AST-AQU-005 | aquatic_edges | match / match | match | covered / classified | S | none |
| AST-AQU-006 | aquatic_float | match / match | match | covered / classified | S | none |
| AST-ENG-001 | utility_machines | match / match | match | covered / classified | M | none |
| AST-ENG-002 | utility_machines | match / match | match | covered / classified | M | none |
| AST-ENG-003 | utility_console | match / match | match | covered / classified | M | none |
| AST-ENG-004 | utility_pipework | match / match | match | covered / classified | S | none |
| AST-ENG-005 | utility_pipework | match / match | match | covered / classified | S | none |
| AST-ENG-006 | utility_pipework | match / match | match | covered / classified | M | none |
| AST-HSP-001 | hospitality_counters | match / match | match | covered / classified | M | IF-004 |
| AST-HSP-002 | hospitality_counters | match / match | match | covered / classified | U | IF-004 |
| AST-HSP-003 | hospitality_stations | match / match | match | covered / classified | M | IF-003 |
| AST-HSP-004 | hospitality_stations | match / match | match | covered / classified | M | IF-003 |
| AST-HSP-005 | hospitality_serviceware | match / match | match | covered / classified | M | IF-004 |
| AST-HSP-006 | hospitality_serviceware | match / match | match | covered / classified | M | IF-004 |



## Limits

This is an offline component-interface readiness audit. It does not prove whole-room fit, water behavior, buoyancy, physical load capacity, collision safety, continuous motion clearance, universal species fit, engine controllers, native draw calls, target-PC performance, streaming, save compatibility or use in the missing game. Game-adopted instance count remains zero. Finite motion witnesses establish native geometry/hierarchy and coordinate-basis consistency only; source coordinates in those witnesses are inverse-basis representations of the inspected native GLB vertices, not a newly sampled source scene. Earlier independent clearance/coordinate evidence remains separately scoped.

Bindings describe the inspection version. Re-run after subsequent metadata/API updates or compare the bound input hashes before reuse. Derived LODs, alternate handed versions and assembly exports are excluded from the 45-design count.

## Compact-source generator sweep

A subsequent bounded static sweep read 37 production/support scripts: 20 primary family generators covering all45 assets, nine other family scripts, two new flange scripts and six shared standards. No required import/read from excluded qa/ or renders/ folders was found. Mandatory output writes exposed missing-parent assumptions in the canopy and aquatic lounge generators, in addition to the known library/flange cases. Current source-guard statuses and exact hashes are in interface_compact_source_static_scan.json; IF-006/IF-007 carry the two newly identified issues. This audit does not execute those generators or replace separate lead/author regeneration proof.

See interface_compact_source_report.md for required local helper paths and the distinction between generation dependencies, produced QA records, coupled reveal rendering, and optional texture regeneration. Refresh that static scan before this semantic index after a generator change.
