# Independent review — Astraea catalogue batch 01

**PASS: seven new component assets are ready to freeze and archive. No unresolved artistic or technical blocker remains within the reviewed scope.** Durable backup must be verified before expansion.

Reviewed 2 October 2026 at `/workspace/shared/astraea-catalogue-continuation-20261002`. This is new catalogue work, not restoration of the unavailable game. All renders are Blender component evidence. Engine integration, original room fit, actor/species contact, physics, motion, performance and CRT appearance remain untested.

## Reference and artistic review

Read `standards/ASSET_CONTRACT.md` and inspected all three actual reference PNGs: `references/intimate/image(20261002-000722).png`, `references/dense/image(20261002-001051).png`, and `references/premium/image(20261002-001347).png`.

The furniture passes: deliberate swept silhouettes, crowned/tapered upholstery, visible welts, recessed ivory liners, and readable runners/posts/rails. The table has a shaped inset top, waisted trestles and useful lower shelf. Broad material roles remain distinct at 640×360. Materials-02 corrects the previous overly regular wood bands. More exposed timber support than the references is a coherent interpretation; suite counts and view scale were not copied.

The reveal passes: rounded ivory shoulder, deep timber throat, differentiated modules, matching joins and visibly closed terminal. Final full-frame, detail and exploded evidence establishes its silhouette and layers.

Measured 0.475 m seat crowns, generous cushion widths and a 0.665 m table support a useful human-scale starting point. QA body proxies and eye-height views are proportion evidence, not seated-rig or all-species acceptance.

## Technical review

Independent byte-level GLB checks pass on all seven exports plus the derived reveal assembly: finite data, valid indices, unit normals, positive transforms, correct winding, no degenerate triangles, and zero collapsed UV surface. Every embedded 256×256 texture and source-packed texture matches materials-02. Separate semantic material roles are retained.

The seven unique sources, three reveal QA/assembly sources, and new combined QA scene all independently reopened in Blender 4.3.2. Before/after hashes were unchanged. Metre units and unit scales are correct. Furniture retains 36/30/15 editable named parts and 38/36/24 modifiers despite single-mesh exports; each reveal module retains two role meshes and four modifiers.

Final triangle counts: bench 4,936; chair 3,872; table 1,848; header 412; sill 412; jamb 2,608; terminal 842. These are file measurements, not performance claims. Furniture floor vertices reach Z=0 exactly. The assembled reveal also reaches Z=0; individual architecture pivots correctly use seam datums. Actual H↔J, S↔J and H↔T end gaps measure 2.000118 mm, with profile agreement within 0.000462 mm.

Final manifests match source/export hashes; furniture bounds/counts match independent measurements. Separate numeric collision proposals are supplied and clearly untested, preserving supports/openings rather than whole-chair/opening hulls.

## Evidence and resolved issues

Final evidence includes the three furniture 640 neutrals, bench detail, all seven labelled reveal views, and `qa/combined_components/{standing_640,seated_640,three_quarter_1280}.png`. The combination imports the actual final GLBs; its corrected full view includes the near chair's feet. Normal-eye crops are contextual, not whole-silhouette proof. It is an empty-opening QA arrangement, not a room or game demo.

Resolved before acceptance: reveal cap UV collapse; cropped/noisy reveal evidence; excessive wood banding; prose-only furniture collision proposals; and furniture consolidation dropping differently named UV layers. The final UV repair was independently retested. Failed-export hashes and measurements remain in `qa/resolved_issues/furniture_export_uv_failure_before_repair.json`.

Exact reviewed paths, sizes and SHA-256 hashes: `qa/independent_reviewed_files.json`. Full measurements: `qa/independent_glb_report.json`, `qa/independent_blend_report.json`, `qa/independent_reveal_joins.json`, and `qa/independent_manifest_source_check.json`. Combined saved-scene reload: `qa/independent_combined_blend_report.json`. Hash stability reports verify no reviewer source edits.

**Remaining gate: parent-owned freeze and verified durable backup. No further bounded asset fix is required.**
