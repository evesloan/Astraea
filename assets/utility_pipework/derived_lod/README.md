# Bounded economical shared utility flange

This is a derived repeated/distant representation of the existing `utility-port-01` flange, not another artistic design or an accepted whole-family/ship LOD system. Original six utility sources/GLBs and their original helpers remain unchanged against accepted Batch07 commit `66dcaf10f105958c5cadb421d5aca15b054b98ed`. See `qa/original_preservation.json`.

## Actual exported cost

| Representation | Triangles per flange | Used geometry buffer-view bytes | Used / serialized materials |
|---|---:|---:|---:|
| Immutable original inlet, extracted from actual AST-ENG-004 GLB | 2,327 | 141,300 | 2 / 4 |
| Exact front/hole profile baseline | 1,608 | 89,520 | 2 / 2 |
| Economical repeated/distant derivative | 1,320 | 73,968 | 2 / 2 |

The economical flange saves 1,007 triangles (43.27%) against the actual selected original inlet. The earlier general helper reference was 2,328 triangles; the selected original inward-facing inlet has 2,327 in both its original source and actual GLB. `qa/near_extraction.json` binds every comparison triangle to the original GLB with exact native triangle-position hashes. It excludes the straight pipe shell and its annular cap.

The 12-flange, six-pair exported context contains 17,760 triangles: 15,840 flange triangles plus 1,920 in five identical hollow links. The matching near arrangement would contain 29,844 triangles. This saves 12,084 triangles in this bounded fixture. Geometry buffer-view bytes describe the actual serialized attributes/indices only, not GPU allocation. The near comparison retains four original serialized images/materials, of which two are used; the derivative carries two. Whole-file byte differences therefore include removal of unused original texture payload and are not a mesh-only or runtime-memory claim. Standalone role-consolidated exports both use two mesh primitives; this work does not reduce their primitive count.

## What changes

- The full 48-sided 0.320 m front outline and 0.160 m bore stay unchanged, including the actual approximately 0.159657 m minimum bore diameter between polygon flats
- The flange remains 0.035 m thick with the same bare front mating plane, six centres on the 0.260 m circle and original zero phase
- The economical holes use 12 sides in place of 24, retaining 0.018 m diameter at vertices. Their measured minimum clearance diameter is approximately 0.0173866 m, compared with 0.0178460 m near. The minimum radius decreases by approximately 0.230 mm; maximum near-profile-to-economical-flat deviation is approximately 0.307 mm
- The original rear 2 mm edge easing is omitted. The neck’s outer profile uses 24 sides, while its bore still uses 48. Redundant axial bore rings are removed; the exterior neck stations remain at their original axial positions
- Captive shanks use six sides in place of twelve. The original six rear hex-head silhouettes remain. All hardware stays behind the mating face
- Shared zinc and blue-grey paint roles and embedded texture pixels are unchanged. UVs are metric dominant-face projections. Mesh normals remain explicit, outward and unit length

The 1,608-triangle baseline preserves all original front and hole profiles and provides a bounded comparison for the extra 288-triangle hole reduction. It is a comparison option, not a second newly accepted design or a universal transition recommendation.

## Frames and interface evidence

The standalone datum is the inlet bare front mating-face centre at (0,0,0) m; source outward normal is −X. Source is Blender Z-up; native GLB is Y-up with source (x,y,z) → (x,z,−y). Actual `PORT_INLET` nodes retain both positions, outward normals, radial-zero direction, bolt centres, dimensions and marker-axis convention. Marker local axes remain source aligned; their explicit normal field defines port direction.

The repeated context has six seams at source (0,0.8i,0.7) m, i=0…5, with opposed ±Y outward normals. Corresponding native centres are (0,0.7,−0.8i) m with opposed ∓Z normals. Thus these actual nonzero node transforms make an unconverted source-as-GLB control sensitive.

`qa/actual_glb_validation.json` parses native binary accessors and resolves node hierarchy. It checks finite vertices/UVs, unit normals and winding, noncollapsed metric UV triangles, positive transform determinants, actual material pixels, exact front boundary loops, source/native node positions and both-frame direction records. Actual geometry tests retain open bore and hole samples, blocked annulus samples and deliberately wrong 30-degree hole-phase samples. The actual paired context passes 864 through-plate clearance samples at 0.0086 m from each bolt centre, and all six paired bores stay open. The 0.006 m captive shank radius leaves at least approximately 0.002693 m radial clearance inside the 12-sided hole polygon. These are finite geometric tests, not engineering tolerances or device-operation approval.

## Editable source and reproduction

- `source/utility_flange_economical.blend`: fourteen separately named, closed editable mesh parts plus the port marker
- `source/utility_flange_exact_profile_baseline.blend`: editable comparison preserving the original 24-sided hole profiles
- `source/utility_flange_repeated_context.blend`: twelve economical flanges, five open links and twelve actual port markers; a bounded inspection fixture
- `source/utility_flange_economical.py`: separate derivative helper; original `standards/utility_ports.py` is only imported and is never rewritten
- `source/build_flange_derivative.py`: reproducible source/export generator

From the catalogue root, run:

```
blender -b -t 1 --python assets/utility_pipework/derived_lod/source/build_flange_derivative.py
python assets/utility_pipework/derived_lod/qa/extract_near_comparison.py
python assets/utility_pipework/derived_lod/qa/validate_derivative.py
python assets/utility_pipework/derived_lod/qa/check_preservation.py
blender -b -t 1 --python assets/utility_pipework/derived_lod/qa/render_comparison.py -- --preflight
blender -b -t 2 --python assets/utility_pipework/derived_lod/qa/render_comparison.py
```

Dependencies: Blender 4.3.2 with NumPy and SciPy (Delaunay triangulates exact planar loops without Boolean phase slivers); the unchanged catalogue-relative port/material helpers, shared staff material manifest/PNGs; and Python NumPy/Pillow for independent GLB evidence. Materials are packed into editable sources and embedded in GLBs. Full reproduction of the immutable near extraction also needs the original AST-ENG-004 GLB. No external reference pixels become textures or geometry.

## Visual acceptance scope

Matched actual-GLB near/repeated camera preflight and pixel review pass in `qa/camera_preflight.json`, `qa/render_evidence.json` and `qa/visual_review.json`. All fourteen captures were inspected. The roughly0.95m near view exposes coarser economical hole edges/highlights; the detailed original stays. At the repeated fixture’s4.6–7.1m seam distances (roughly33–51pixel rim heights), the economical variant retains the useful paired-flange silhouette, open bores and material identity across all three controlled camera poses. No universal switch distance follows from this fixture. The comparison keeps 640×360 resolution, lighting, camera distances and material roles constant, with a small −4/0/+4 degree camera orbit. Original near inspection remains appropriate for closer views; actual transition distance, material sharing/batching, shadow/pass costs and performance must be chosen and tested in the receiving game. This fixture does not establish pressure/load ratings, operation, species fit, collision behavior or target-PC performance.

## Compact source restoration correction

The generator explicitly creates its source, export and QA output directories. The original missing-QA-directory failure and pre-fix generator are preserved under `qa/source_restore/`. A corrected isolated build started with only Python sources and shared material dependencies, no existing Blender/GLB outputs and no QA/export directories. It generated all three GLBs byte-for-byte identical to the frozen exports and an identical source geometry report. Current Blender, GLB and rendered evidence bytes remain unchanged. See `qa/source_restore/restoration_report.json`; no rerender was needed.
