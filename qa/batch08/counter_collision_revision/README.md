# Hospitality collision revision03

Final frozen proposal: `assets/hospitality_counters/collision_proposals.json`, SHA256 `b37c063ac25d0c926d278c5ba2085833ab2f94c632b3b0f1018be7ddb1ec953c`.

| Scope | Batch07 baseline | Final |
|---|---:|---:|
| AST-HSP-001 | 26 | 34 |
| AST-HSP-002 | 263 | 121 |
| Counter family | 289 | 155 |
| All six hospitality designs | 399 | 265 |

The curved return loses 142 pieces (54.0%). The straight counter gains 8 pieces because preserving its real fascia and toe/terminal profile required a correction. Across hospitality, 134 pieces are removed (33.6%). This is a bounded geometric simplification, not a measured engine-cost result.

## Source-backed choice

Contiguous source rows form convex arc sections within a 5 mm radial chord limit; the upper ivory rail uses 2.5 mm to preserve the measured thin deep-shelf clearance. Actual maximum arc chord bound is 4.8744 mm. Low front shelf lips merge into their own shelves; taller rear upstands remain separate. Separate shell/rails/top, floor plinths, base shelf, supports and drawer remain intact. Decorative ribs, thin reveal and grip stay omitted as in Batch07.

The first 60-piece/79-piece curved candidates retained a real inherited flaw: one convex fascia profile filled 9–23mm of supported lower-shelf depth. Final fascia uses five meaningful height bands with an exact authored profile-depth infill bound of 3.984 mm. The original closed terminal hull also filled a small toe recess; final terminals split at source Z0.124, 0.164 and 0.580 m. The last two curvature cuts cost four pieces per asset beyond the toe-only candidate, reducing about 21.6 mm guest-terminal excess to at most 3.19 mm at independent samples. Intermediate candidates remain archived as comparisons and are not accepted proposals.

Final independent sampled outward source-solid errors are 8.37 mm straight and 9.65 mm curved, both on merged front shelf lips. Fascia maxima are 3.77/7.82 mm; terminal maxima are 2.76/3.19 mm. Exact halfspace/polygon-union coverage leaves no uncovered represented source triangle area above 1e-10m². Source/GLB point conversion is exact to the stored values (maximum error 0).

## Evidence

- `baseline_receipt.json` and `original_inputs/` preserve original collision/generator/manifest/README/dependency inputs and hashes of 108 earlier evidence/visual files
- `validation_report.json`: source-triangle union coverage, exact source/GLB frames, all legacy probes including the twelve curved samples, blocked structural controls, continuous convex drawer translation, and 25 mm service-sphere corridors with explicit continuum covering bounds
- `deep_corridor_report.json`: 10,430 deep lower-shelf paths; radius inflation proves a 3 mm storage-depth proxy clear throughout bounded coordinate/height regions. All old whole-fascia controls block the corresponding source-clear centrelines
- `final_detail_report.json`: 10 mm spheres in actual toe recesses, old-filled negative controls, floor/worktop contact, 2 mm joint, metadata and source/export hashes
- `reproduction_report.json`: the final generator's collision-only source reload reproduces the final JSON byte-for-byte without saving .blend files or exporting GLBs
- `../independent_collision_report.json`: 19,879 actual-source/compound clear and blocked paths with zero mismatches; actual named-solid winding and Euclidean distance for signed outward overreach, plus coverage and deliberate enclosing-hull negative controls

The author hull-face diagnostic includes internal partition faces and material-interior points. Its unsigned distance-to-source-surface maxima are conservative diagnostics and must not be confused with the independent signed outward-overfill measurement. Cached surface measurements are keyed to exact hull points, source-cache bytes and sample spacing; actual-GLB clearance caches are keyed to the precise parameter grid and GLB hash.

`conservative_halfspace_diagnostic.json` preserves a failed proof attempt: expanded convex planes around corners produced false positives. The final proof retains that broad phase and uses exact Euclidean segment-to-hull distance for its candidates. Geometry and meaningful corridor regions were not narrowed to hide the failure. The higher-resolution parameter grid retains the same 25 mm proxy and regions.

## Reproduction and limits

Run from catalogue root:

```text
blender --background --threads 2 --python-exit-code 1 --python assets/hospitality_counters/source/build_hospitality_counters.py -- --collision-only
python qa/batch08/counter_collision_revision/validate_collision_revision.py
python qa/batch08/counter_collision_revision/validate_deep_corridors.py
python qa/batch08/counter_collision_revision/validate_final_details.py
```

`--collision-output <path.json>` creates a separate comparison output without replacing current collision data. `--collision-chord-limit-m 0.010` changes only the arc limit (the final source-backed fascia and terminal decomposition remains); the archived rejected arc-only comparison files preserve the earlier data exactly.

The existing two .blend masters and two visual GLBs remain byte-identical. No scene, room, original-game project, render, engine collider or physics solver was created. No actor/species/accessibility, native performance, structural load or mechanical certification is implied. The 25 mm and 3 mm spheres are explicit bounded geometric proxies. Surface samples do not establish a global Hausdorff maximum. Continuous drawer tests cover the five proposed drawer hulls against every stationary proposal for 0.320 m source +Y travel, allowing 1 µm contact tolerance; the wrong +Z axis is blocked. Omitted decorative geometry remains outside that compound test.
