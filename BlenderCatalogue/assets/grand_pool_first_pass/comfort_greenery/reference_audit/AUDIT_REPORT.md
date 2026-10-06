# Grand Pool seating views and fuller planting: read-only source audit

## Result and scope

The three market benches truly face nearby blank architecture. Three shallow, physically mounted framed-display derivatives have bounded fitting candidates on their actual forward-facing supports. The seven loungers face the water and should keep that view. The lower pool-end bench faces beyond the pool, so a separate floor-supported display has a clear candidate beyond, rather than within, its existing approaches.

All six major market beds can receive full, layered planting within conservative envelopes. The bed between market_rest_0 and its display has a dense low carpet across its full breadth, with its taller foliage shifted outside the viewing cone. That joint layout is screened now, not deferred to a vague future check.

This is a scratch audit only. No Blender or Godot process was run. No Game or catalogue file was edited, no asset or export authored, and no commit made. The ongoing signfix is untouched and remains a separate gate. The 51 installed furnishings and the 48 source-only planned additions are not described as room completion or final visual acceptance.

## Evidence and method

- Read the requested VISUAL_REVIEW.json, then reopened and inspected all four named market/long-view PNGs, the actual retro_atrium_quality_benchmark, and the aquatic reference. Also inspected retained canopy and cluster QA pixels. Full paths, actual SHA-256 hashes, sizes and observations are in INSPECTED_IMAGES.json.
- Read the complete 170-entry catalogue manifest by exact catalogue ID, and checked the actual source/export hashes of all 16 investigated assets against its records. All matched. SOURCE_INVENTORY.json contains ownership, paths, hashes and bounds computed from actual GLB POSITION buffers plus scene-node transforms.
- Read the source and runtime furnishing contracts; the current seat positions and orientations agree. Used source construction, seat datums and retained front-axis evidence, rather than apparent camera orientation.
- Read actual AST-AQU-016 and retained-furnishing GLB triangles. Current baseline rays are in SEAT_SIGHTLINES.json. Proposed upright eye heights are human-scale audit poses, not universal-species or ergonomic acceptance.
- Screen fitting additionally includes all 48 staged retained additions, exact triangles for retained inputs, and conservative full envelopes of the staged finish parts. Finish faces include non-convex polygons, so this audit does not falsely fan-triangulate them. A rejected exploratory convex-face assertion was corrected to fail-closed envelope checks; no geometry change resulted.
- The four media candidate envelopes have zero strict overlap with other source/furnishing/planned-finish/retained48 envelopes and zero protected-route overlaps. Each candidate has 30 clear eye-to-image probes: two seat positions, three eye heights, four image corners plus centre. Their analytic envelopes remain proposals, not source-authored or runtime-approved objects.

## Actual seat-facing audit

The furniture source defines front as Blender -Y, which exports to glTF +Z. The bench's two source seat centres are X -0.548 and +0.548, forward Z +0.11, seat crown Y 0.475. Its back is on local -Z. The lounger head/back is on local -Z, and its feet/front on +Z. A world yaw of pi/2 therefore faces +X, not -X.

- market_rest_0: root (-50.4, 52.5, -448.9), yaw 0, forward +Z. Seated eye proposals (-50.948 or -49.852, 53.68, -448.79) hit the actual terracotta surface at Z -446.100006, 2.689994 m away. The named source support is GP_OrangeReveal_0_-444.6. Its genuinely flat south face spans X -53.6..-49.05 at Z -446.1; the east end is bevelled and is not a flat mounting surface.
- market_rest_1: root (-50.4, 52.5, -436.5), forward +Z. The two eyes encounter the south face/chamfer of GP_UpperPier_1 at Z about -434.26, 2.13 m away. Flat central face X -51.545..-49.855, Y 53.05..59.0, Z -434.26. Do not mount a full-width panel across the chamfer as though it were planar.
- market_rest_2: root (-50.4, 52.5, -419.5), same basis. GP_UpperPier_2 has the same face dimensions at Z -417.26, again about 2.13 m away.
- wet_rest_448, _444, _440, _436, _429, _425, _421: roots X -47.5, Y 46.2, named Z, yaw pi/2, forward +X. Their current view crosses the wet apron and pool. Some centre rays eventually encounter the far-side gallery/rail or east wall at 30–40 m. That does not make them close-wall-facing seats; do not obscure the water with added monitors or turn them around.
- wet_end_rest: root (-47,46.2,-402.5), yaw pi/2, forward +X. Its two eye axes at Z -401.952 and -403.048 lie beyond the pool's aft edge Z -406.6, and terminate on GP_EastWall.001 at X -8.2, 38.69 m away. It needs a deliberate distant view or a separate local display. The pool is not directly ahead of this bench.

Protected existing seat approaches are retained unchanged. Market front approach centreline Z values are -447.95, -435.55 and -418.55, from X -45.9 to each seat. wet_end_rest has two approaches from X -43 to -46.05 at Z -401.952 and -403.048. Lounger side-entry approaches remain the source/runtime positions, including the continuous X -45.9 walk.

## Recommended media candidates

MEDIA_FITTING_CANDIDATES.json carries exact full bounds and image rectangles. Coordinates below are world X/Y/Z metres.

1. market_rest_0_screen: full body X -52.05..-50.35, Y 54.03..55.03, Z -446.30..-446.10. Image face Z -446.28, image X -51.97..-50.43, Y 54.11..54.95, facing -Z. Attach a real backplate to the flat GP_OrangeReveal_0_-444.6 south face at Z -446.1. This is intentionally on the west portion of the return, clear of its bevel and shifted away from the taller planting.
2. market_rest_1_screen: full body X -51.48..-49.92, Y 53.68..54.58, Z -434.44..-434.26. Image face Z -434.42, image X -51.40..-50.00, Y 53.76..54.50, facing -Z. Backplate fits the 1.69 m-wide flat face of GP_UpperPier_1 with approximately 65 mm margin per side.
3. market_rest_2_screen: same dimensions and X/Y as candidate 2; full Z -417.44..-417.26 and image face Z -417.42. Actual support GP_UpperPier_2.
4. wet_end_rest_floor_display: total stand/body envelope X -41.35..-40.88, Y 46.2..48.6, Z -403.6..-401.4. Image plane X -41.35, normal -X; image Z -403.48..-401.52, Y 47.12..48.38. Real feet/bearings on D08_grand_pool_wet at Y 46.2, with visible supporting spines and plinth. It is 1.65 m beyond the nearest X -43 approach start, and its nearest edge is 0.60 m outside the protected wet-aft apron boundary Z -404.2. All 552 sampled footprint positions are on the actual compiler floor triangles. This location is a fitted candidate, not permission to block wider informal circulation; loaded runtime circulation remains a gate.

The market candidates retain the seats and their approaches. Panel fixtures must have attachment witnesses, a closed backed housing, restrained bezel, fasteners/service access and a legible mounting relationship. Avoid opaque floating rectangles. Candidate 4 must visibly bear on the floor; do not silently convert it to a hanging panel without a separately verified ceiling support and headroom assessment.

### Exact source ownership

Preferred electronic display derivative: AST-LIB-010, existing family library_use, source assets/library_use/source/AST-LIB-010.blend, export assets/library_use/exports/AST-LIB-010.glb. Its retained source contains TERM_shaped_back_shell, TERM_walnut_display_frame, TERM_recessed_inner_gasket, TERM_recessed_display_glazing, TERM_original_catalogue_display and a proper bearing/service construction. Derive a new pool-specific representation from these editable construction ideas, reshaping/reorienting for the stated panel bounds. Do not scale the complete stand onto a wall or retain misleading FIND A BOOK artwork. The floor-mounted candidate can derive the paired feet/load-spine support vocabulary with new span/contact verification.

Parent ownership proposal: keep the new pool media derivative under AST-LIB-010/library_use and record physical wall interface pieces against the existing AST-AQU-016/grand_pool_orchard_section supports. Keep named source objects and parent_design_id provenance for each retained construction. Use a separately named source/export such as AST-LIB-010_pool_leisure_display; do not overwrite AST-LIB-010.glb or invent/claim a new catalogue ID. The parent must accept this representation ownership before authoring if the current production boundary does not already cover it.

Alternative frame-only passive display: AST-RES-001/residential_wayfinding_bay has RES_MapFrame and RES_MapBacking. Its exact 3.12 x 1.45 m frame is a useful source for a non-electronic scenic panel, but it contains no actual TV or projector system. Reusing that construction must be a separate media representation, never bundled into or allowed to disturb AST-RES-001_pool_wayfinding or its signfix. Preferred electronic lineage remains AST-LIB-010.

Avoid AST-ENG-003 as a ready-made entertainment TV: it is a water-recovery utility console. Likewise, AST-LND-001 is arrival-directory furniture. No retained entertainment projector or hologram family was verified in the complete manifest. A projector/hologram would require additional optical/emitter/mount geometry and ownership, so it is not the minimal bounded solution.

Use a broad, original aquatic/natural vista or calm abstract planetary scene that reads from both seats at 640x360 presentation resolution. Meaningful imagery is the point; a tiny label, black blank display, safety-text board or fake active control is not a viewing accommodation. A static authored image can be honest static leisure display dressing; do not claim streaming/video/interactive functions. Reuse source-backed ivory, walnut, restrained champagne trim and display glass/material construction. Keep all shared renderer/palette files and existing shader defaults unchanged. Do not add Light3D instances or exceed the approved section fixture/shadow budgets. Any display emission must remain locally bounded and cannot be used as a lighting-budget bypass.

## Fuller six-bed planting treatment

The six real supports are GP_PlantSoil_0_-454.7; GP_PlantSoil_0_-446.70000000000005; GP_PlantSoil_1_-440.9; GP_PlantSoil_1_-429.40000000000003; GP_PlantSoil_2_-423.7; GP_PlantSoil_2_-411.1. Each soil top is Y 53.2 with a chamfered 2.21 x 0.96 m overall footprint, X -50.58..-48.37 and Z centre +/-0.48. Use its actual octagonal polygon for roots, not just the bounding rectangle. The current three individual planted elements do not visually fill these beds.

PLANTING_ENVELOPE_CANDIDATES.json supplies a low and an upper reservation per bed. The complete reservation clears all non-botanical source/finish/retained48 envelopes and media bodies. Existing planted source instances stay intact. Botanical-to-botanical visual overlap is purposeful crown composition, not permission for crossing walls or unrooted floating leaves.

For all beds, use a dense low basal layer within X -50.55..-48.35, Y 53.20..53.62, Z centre +/-0.44. Roots remain inside the actual soil polygon; the minor foliage overhang remains within the planter surround. Create broad, opaque, sculpted leaf masses with linked crowns and a few readable flower tufts. The result should hide most exposed soil from standing and seated viewpoints without becoming a uniformly flat green carpet.

For the five ordinary beds, mid/upper foliage remains within X -50.55..-48.35, Y 53.62..55.20, Z centre +/-0.40. Shape this into unequal low/middle/high silhouettes with breathing space around stems, a substantial broad-leaf middle, and a connected asymmetric crown. The box is a maximum reservation, not a solid rectangular hedge or a new collision hull.

For GP_PlantSoil_0_-446.70000000000005 specifically:
- Full low foliage reservation: X -50.55..-48.35, Y 53.20..53.62, Z -447.14..-446.26.
- Shifted upper foliage reservation: X -49.60..-48.35, Y 53.62..55.20, Z -447.10..-446.30. Put the fuller crown and middle leaf fans on this outer/east side; continue dense low planting across the west side beneath the image sightline.
- This is not merely a sampled coincidence. Every viewing segment to the image remains at X <= -49.852, while upper foliage starts at X -49.60, leaving at least 0.252 m lateral separation. The lowest proposed eye is Y 53.50; the image's lowest point is Y 54.11. At the nearer bed face Z -447.14, the lowest connecting segment is already Y 53.901, 0.281 m above the low layer's cap. Thus the entire image rectangle clears both conservative envelopes for both source seat X positions over the proposed Y 53.50..53.90 eye interval, not only the five sampled points. Broader species/head motion still needs its own assessment.

### Exact botanical lineages

- AST-BOT-003 / botanical_understory: assets/botanical_understory/source/AST-BOT-003.blend. Preferred dense basal spoon-leaf/flower tuft derivative, retaining root/leaf construction and connected opaque geometry. Raw asset bounds are only 0.546 x 0.338 x 0.514 m (X/Y/Z); spreading more isolated raw copies is not the visual target.
- AST-BOT-002 / botanical_understory: assets/botanical_understory/source/AST-BOT-002.blend. Preferred broad cupped-leaf middle layer. Raw bounds 1.011 x 0.926 x 0.701 m. Compose substantial overlapping middle crowns, with their stems visibly attached to soil-supported root groups.
- AST-BOT-007 / botanical_cluster: assets/botanical_cluster/source/AST-BOT-007.blend. Preferred fitted high fan/crown derivative. Actual raw bounds 2.284 x 2.530 x 1.718 m; unchanged raw depth would intrude into the return beyond these narrow beds. Recompose the editable fans/stems within the specified width/depth/height reservation. Do not globally squash the original export or let oversized fans disappear into the wall.
- AST-BOT-009 / botanical_cluster: assets/botanical_cluster/source/AST-BOT-009.blend. Optional clustered flower accent. Raw upright bank is 0.996 x 1.127 x 0.484 m, but its actual reference QA is stem-heavy; a few more tall pins will not create the requested lushness. Keep flowers as clustered accents supported by broader middle foliage.
- AST-BOT-001 / botanical_canopy: assets/botanical_canopy/AST-BOT-001.blend. Optional asymmetric branching crown language. Its actual 2.394 x 2.693 x 2.006 m envelope is too deep unchanged. Use a separately fitted derivative only when that silhouette improves a selected bed; it is not necessary in all six.
- AST-BOT-008 / botanical_cluster: trailing lineage only if a real coping and trailing clearance are verified. Raw glTF tails extend down to Y -0.571 and along -Z to -0.887. They are not a generic ground shrub. No raw vines across seat approach strips, glazing, open voids or the screen viewing cone. The full/mid/low treatment above is viable without trailing foliage.
- AST-BOT-011 / atrium_canopy is a 16 m-scale conservatory tree and is inappropriate here unchanged.

Use distinct, derivative filenames under the existing botanical source owners, with explicit parent IDs. A mixed planted assembly may reference several IDs, but must not claim all of its components as AST-AQU-016 or overwrite a botanical family export. Retain original sources, scripts, materials and runtime variants unchanged. The construction must remain editable and painterly/chunky, with opaque broad leaf silhouettes and restrained jade/olive/sage face variation. Use the existing botanical material vocabulary and planned real light first. Do not change the shared palette, switch renderer, add global saturation or make leaves emissive to fake vibrancy.

## Wet-zone greenery and the tiny-pot distinction

The five existing AST-BOT-012 nursery pots are only 0.30 m across and 0.22 m tall. Their little AST-BOT-003 plants are secondary accents and cannot satisfy the large-bed treatment above or carry the long-pool composition. Do not place a full 2 m fan crown in a tiny nursery pot and call that properly rooted planting.

A small companion treatment for all five pots is included in the bounded proposal: one additive AST-BOT-003 full leaf/flower whorl per existing wet_pot_rosette, with the original rosette, root and AST-BOT-012 vessel preserved. For each original centre (-47,46.4,Z), where Z is -455, -443, -432, -416 or -409, the complete permitted plant envelope is X -47.29..-46.71, Y 46.40..46.88, Z centre +/-0.28. The new connected leaf/petal whorl attaches to the actual retained rosette_basal_crown at about 25–45 mm above its original root plane; it does not introduce an oversized tree root into the tiny pot. The original basal crown has a 35 mm physical root-contact radius and remains the soil contact. Final source attachment/leaf-to-rim triangle tests must establish the join. This complete envelope clears unrelated architecture, furnishings, staged finish, planned48, protected routes and all proposed screen sightlines. WET_POT_FULLNESS_CANDIDATES.json records each separate placement and check.

The visible goal for these five companions is a rounded, leafy, coherent potted tuft with readable coloured flower accents and less bare thin-stem character. At close/medium range it should feel fuller and healthier while remaining appropriately small for its vessel. It is not a substitute for major planting and is not claimed to solve the long-view hierarchy by itself. Use only the existing botanical material vocabulary and opaque source-derived leaf/petal construction. No shared palette change or emissive foliage.

The six market beds remain the major treatment. If stronger lower-level botanical rhythm is also included later, two additional bounded wet-backdrop planting candidates are available behind the loungers, without moving them: X -51.10..-49.15, Y 46.20..48.25; one at Z -446.40..-445.20, the other at Z -410.60..-409.40. Both full reservations clear retained source/furnishings, staged finish, retained48 stock and protected route boxes. These optional candidates are outside the existing planned48 additions and need an explicit source-design/floor-support scope decision. They are not silently included as accepted objects.

For those optional beds, derive a properly enlarged planted vessel from AST-BOT-012/nursery_pottery (source assets/nursery_pottery/source/AST-BOT-012.blend), with real base, rim, soil top around Y 46.72 and body contact, plus the same fitted BOT-002/003/007 planting lineages. Do not replace or overwrite the existing tiny pots. Their broad silhouette should frame the rest groups from behind and preserve the direct +X water views. OPTIONAL_WET_BED_CANDIDATES.json records conservative bounds; full actual-floor/support/maintenance and source geometry gates remain pending.

## Explicit instance budget for parent review

This is a real expansion of the earlier furnishing plan, and is not hidden by calling multiple placed assets one bed.

- Existing installed placements retained: 51
- Earlier source-only retained additions retained as planned: 48; earlier prospective total: 99
- Three new separately placed botanical derivatives per major bed: one AST-BOT-003 basal bank, one AST-BOT-002 middle bank, one AST-BOT-007 fitted crown. Six beds therefore add 18 derivative instances, even if their source organization groups them under six bed roots.
- Five additive wet-pot AST-BOT-003 companion whorls: 5 further derivative instances. The original five rosettes remain counted within the 51.
- Three complete market wall-display assemblies and one complete wet-end floor-display assembly: 4 further derivative instances. Each contains its own native frame/body/mount or feet; if authoring instead splits a physical mount into another separately placed export, that is an additional instance and must be reported.
- New requested adjustment above the earlier plan: 27 instances. Revised prospective additions: 75, revised prospective furnishing total: 126.
- New unique catalogue designs/IDs requested: 0. Derivative lineage, mesh parts, materials, draw calls and triangles must still be tracked; zero new IDs is not a zero-cost claim.
- The optional two larger wet-backdrop beds are NOT included in 126. If later selected with one vessel and the same three separate botanical derivatives per bed, they add another 8 instances, taking the total to 134. They require their own bounded source/floor/support review.

No extra AST-BOT-009 flower-bank or AST-BOT-008 trailing instances are in the 126 cap. Flowers within the low AST-BOT-003 derivative use its existing folded flower vocabulary. If another derivative is added, exchange an explicitly named layer/instance within this cap or revise the declared budget. Do not inflate or collapse a count by renaming an assembly. A direct replacement alternative could avoid some net instance growth, but would require an explicit replacement list and new retained-runtime pins; it is not silently assumed here.

The count is a scope ceiling for review only. Acceptance depends on the matched visual comparison and functional gates below, not reaching 126.

## Acceptance gates, expressed as visible outcomes

1. Seated viewing: both actual bench seat positions see a full, purposeful image without leaning around a column, looking at a display's edge/back, or craning upward. The panel reads as housed and supported. Recheck corners/centre over required actor eye/pose envelopes against FINAL leaf vertices, screen bezel and mounting hardware, not merely the current planning boxes.
2. Lushness: at the ordinary market camera and seated camera, the trough reads as one composed living bed with broad upper/middle/low masses, connected stems and flower accents. It no longer reads as a black tray holding three isolated twigs. At normal 640x360 presentation and in an unzoomed long-pool view, green masses remain visible and have varied silhouette and tonal separation. A vegetation count is not acceptance.
3. Style and vibrancy: foliage is chunky, painterly and source-consistent; leaf faces are readable under the existing/planned real lighting. Reject wire-thin crowns, repeated clone patterns, fluorescent/emissive green, reference-photo billboards, or purely sharpened/brightened screenshots. Inspect source export and actual normal/effects-off engine pixels separately.
4. Composition: fuller growth softens the existing planted pockets and frames space while retaining the windows, wet/dry glazing, structural pier forms, water vistas and central void. The market_rest_0 display and adjacent crown both read naturally; neither looks shoved aside to satisfy a technical probe.
5. Rooted construction and contacts: all root reservations use the actual chamfered soil top and named planter support; crowns remain attached through coherent stems. The modeled 50 mm soil cap is not proof of horticultural soil depth. Do not claim biological, drainage, load or all-species certification. Media feet/brackets need actual surface contacts and non-floating joins; protect original support meshes.
6. Circulation: full new envelopes, screen supports, foliage, collision geometry and maintenance poses stay outside the existing wet walk, dry loop, display browsing paths, all seat approaches, doors/lift movement, towel extraction and loaded-cart routes. No moving a route or seat to make the test pass. Foliage remains appropriately non-colliding; never add a solid canopy AABB collision.
7. Integration: keep original hashes/IDs and source ownership; validate new editable sources and GLB equivalence, UV/material/image packing and imported marker transforms; independently retain the work before adoption. Then rerun affected and required aggregate checks and inspect matched ordinary/effects-off views and short pans. New screen and planting geometry must not expand the shared lighting/shadow budget or alter the shared renderer/palette.

The intended stopping point of this audit is a safely bounded authoring proposal. None of these screens, new leafy derivatives, optional wet planters, or their runtime/visual acceptance is claimed complete.
