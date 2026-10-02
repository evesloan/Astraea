# Compact-source generator usability sweep

Read 37 Python files: 20 primary family generators covering all 45 unique designs, 9 other family scripts, 2 new flange scripts and 6 shared standards. This is a bounded static read/AST audit; no generator, render, Blender load or rebuild was executed.

## Exact findings

- **CS-001 — guard_present_in_current_source**: `assets/botanical_canopy/source/build_canopy.py` writes `qa/support_contacts.json`. The output parent must be created before the mandatory write. Current source SHA256 `8f25dd670481663f884d8f7795bb3688ae5f12bc4c54cef3b293917596c6e4b8`. This does not require a geometry change.

- **CS-002 — guard_present_in_current_source**: `assets/aquatic_lounge/source/build_aquatic_lounge.py` writes `qa/join_checks.json`. The output parent must be created before the mandatory write. Current source SHA256 `5db2a1b1e75386d1eef3561bf65df188d936769a44aee38c3dabcd49c71fe093`. This does not require a geometry change.

- **CS-003 — guard_present_in_current_source**: `assets/library_contents/build_stock_variants.py` writes `qa/variant_source_import_audit.json`. The output parent must be created before the mandatory write. Current source SHA256 `375963140fa74c1006d72c1c270533d7a5b8b1047a80fa42f8c2b2f4e688c7a6`. This does not require a geometry change.

- **CS-004 — guard_present_in_current_source**: `assets/utility_pipework/derived_lod/source/build_flange_derivative.py` writes `qa/source_geometry.json`. The output parent must be created before the mandatory write. Current source SHA256 `d1963ce3b6531b5fea089da954e29dc6a35685ea52fad2987828c60de4b8d8d6`. This does not require a geometry change.

## Required inputs and optional review work

No production import/read from an excluded `qa/` or `renders/` path was found. Exact reviewed I/O, imports, line numbers and per-script hashes are in `interface_compact_source_static_scan.json`.

The only newly found omissions were CS-001 and CS-002; CS-003 was fixed earlier by the lead, and CS-004 was already known and is owned by the flange author. The current statuses above are recalculated from actual current source guards. Separate lead/author execution evidence must establish regeneration.

Required local helper paths are listed in the JSON and all currently exist in included source folders. Common `standards/` material/port helpers, material manifests/images and batch reference manifests remain required. No helper was moved into a missing review folder.

- build_reveal.py main couples model creation and new QA rendering; line11 creates qa/. It has no dependency on pre-existing QA media and no missing-directory defect. It is not a render-free command.
- Other excluded QA/report paths in manifests or strings are references to separate validation evidence, not generation-time reads.
- build_stock_variants.py reads the included base source .blend and manifest; botanical closure/repack scripts read included master/family records. These are expected local source dependencies.
- Texture redraw scripts need Pillow and, for the two graphic labels, system DejaVu fonts. Current PNG/JSON resources are included; primary model generators read those resources, not pre-existing renders.
- New flange helper additionally imports NumPy and SciPy Delaunay; these are environment requirements, not excluded-folder files.
- Batch reference-manifest JSONs are common source data. Furniture/reveal reference-image globbing may be empty without optional reference media; it does not supply geometry or fail on a missing QA input.
- Static absence of excluded-input dependencies does not certify arbitrary full regeneration or replace prior actual source/export/visual QA.

## Per-generator coverage

| Primary generator | Exact unique assets | Missing excluded-folder input |
|---|---|---|
| assets/aquatic_edges/source/build_aquatic_edges.py | AST-AQU-003, AST-AQU-004, AST-AQU-005 | none found |
| assets/aquatic_float/source/build_float.py | AST-AQU-006 | none found |
| assets/aquatic_lounge/source/build_aquatic_lounge.py | AST-AQU-001, AST-AQU-002 | none found |
| assets/botanical_canopy/source/build_canopy.py | AST-BOT-001 | none found |
| assets/botanical_planter/source/build_botanical_planter.py | AST-BOT-004, AST-BOT-005, AST-BOT-006 | none found |
| assets/botanical_understory/source/build_botanical_understory.py | AST-BOT-002, AST-BOT-003 | none found |
| assets/furniture/build_furniture.py | AST-FUR-001, AST-FUR-002, AST-FUR-003 | none found |
| assets/hospitality_counters/source/build_hospitality_counters.py | AST-HSP-001, AST-HSP-002 | none found |
| assets/hospitality_serviceware/source/build_serviceware.py | AST-HSP-005, AST-HSP-006 | none found |
| assets/hospitality_stations/source/build_hospitality_stations.py | AST-HSP-003, AST-HSP-004 | none found |
| assets/library_contents/build_library_contents.py | AST-LIB-006, AST-LIB-007 | none found |
| assets/library_structure/source/build_library_structure.py | AST-LIB-STR-001, AST-LIB-STR-002, AST-LIB-STR-003 | none found |
| assets/library_study/build_study.py | AST-LIB-STUDY-01, AST-LIB-STUDY-02 | none found |
| assets/staff_overhead/source/build_staff_overhead.py | AST-STF-004, AST-STF-005, AST-STF-006 | none found |
| assets/staff_wall/source/build_staff_wall.py | AST-STF-001, AST-STF-002, AST-STF-003 | none found |
| assets/staff_workbay/build_staff_workbay.py | AST-STF-007 | none found |
| assets/utility_console/source/build_utility_console.py | AST-ENG-003 | none found |
| assets/utility_machines/source/build_utility_machines.py | AST-ENG-001, AST-ENG-002 | none found |
| assets/utility_pipework/source/build_utility_pipework.py | AST-ENG-004, AST-ENG-005, AST-ENG-006 | none found |
| assets/view_reveal/source/build_reveal.py | AST-VR-01-H, AST-VR-01-S, AST-VR-01-J, AST-VR-01-T | none found |
