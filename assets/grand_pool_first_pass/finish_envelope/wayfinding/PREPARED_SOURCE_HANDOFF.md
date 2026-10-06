# Grand Pool / Orchard Market physical wayfinding source handoff

Status: scratch-only, source-authoring code and exact mount contract prepared. No Blender, Godot, render, UI, export, runtime edit, original-source edit, or commit was executed. The running full-suite engine gate remains owned by the parent. No `.blend` or `.glb` is claimed as built.

## Deliverable and identity

- `build_pool_wayfinding.py`: self-contained Blender builder using this package's pure-Python helpers. Default saves only `source/grand_pool_wayfinding.blend` plus a QA report in a new isolated output directory. It retains independent frame, backing, mount, fastener and physical glyph meshes. It does not register assets or change runtime.
- `wayfinding_contract.json`: all 11 exact source-derived boards, local viewing bases, component envelopes, 22 physical contact patches, source references, arrow projections, named materials and 47 preservation pins.
- `prepare_wayfinding_contract.py`: reproducible pure-Python preparation from retained source records and GLB triangles. Existing contracts cannot be silently overwritten or rebaselined after retained-input drift.
- `check_wayfinding.py`, `wayfinding_geometry.py`: dependency-free source-contact, preservation, mount connectivity, spatial envelope, control/motion, route and cart screens.
- `test_wayfinding_contract.py`, `PYTHON_TESTS.log`: six positive/negative control tests.
- `SOURCE_SCREEN_REPORT.json`: final source-screen result, with individual checks.
- `PROPOSAL_PIN_VERIFICATION.json`: original AST-AQU-016 and AST-RES-001 source/export hashes still match the approved proposal pins.

Ownership remains AST-RES-001 / residential_wayfinding_bay. Export identity is exactly `AST-RES-001_pool_wayfinding.glb`. No new design or programme ID. The original `RES_MapFrame` walnut body and `RES_MapBacking` ivory inset provide the construction language; original residential geometry is never loaded for modification.

## Exact receivers and board bounds

World coordinates are Godot XYZ metres. The JSON retains full source precision; values below are rounded for reading. Bounds include mounts and glyph reservations, not just board faces.

| Sign | Receiver | Complete X | Complete Y | Complete Z |
|---|---|---:|---:|---:|
| Grand Pool, D08 | GPM_CORE_PortalHeader_07 | −7.722..−7.591 | 47.450..48.050 | −433.200..−430.800 |
| Orchard Market, D09 | GPM_CORE_PortalHeader_08 | −7.722..−7.591 | 55.950..56.550 | −433.200..−430.800 |
| Pool stairs | GP_WetSealDoorHeader | −15.250..−13.850 | 55.205..55.660 | −428.259..−428.128 |
| Pool lift | GP_WetSealDoorHeader.001 | −15.250..−13.850 | 55.205..55.660 | −406.772..−406.641 |
| Orchard Market, lower lift | GP_LocalLiftHeader | −13.102..−12.971 | 49.160..49.670 | −413.100..−411.700 |
| Step-free / Grand Pool | GP_RaisedEdgeFascia | −12.600..−11.400 | 45.250..45.850 | −445.789..−445.658 |
| Step-free / Arrival | GP_RampPocketCap | −18.002..−17.871 | 47.245..47.980 | −450.350..−449.150 |
| Towels | dry_continuous_sculpted_hood, clean_towel_retrieval instance | −46.865..−46.711 | 48.018..48.330 | −454.450..−453.550 |
| Used towels | return_L/R_formed_load_cheek, used_towel_return instance | −46.925..−46.771 | 47.418..47.760 | −451.471..−450.529 |
| Staff only, wet | GP_WestDoorHeader | −53.722..−53.591 | 48.900..49.180 | −463.500..−462.500 |
| Staff only, market | GP_WestDoorHeader.001 | −53.722..−53.591 | 55.200..55.480 | −463.500..−462.500 |

Main and threshold boards use the proposed 2.4×0.6 m and 1.4×0.4 m families. Direction boards are 1.2×0.6 m. Fitted station plaques are 0.90×0.24 and 0.94×0.24 m; staff plaques are 1.0×0.28 m.

The two main receivers are the **forward-core derivative's real inner headers**, rather than the pool-shell headers behind them. Their east face is X≈−7.72. It is verified against retained GLB triangles after the exact Z−432 assembly translation, with generator names and source/export equality evidence preserved. This prevents an apparently source-mounted board being buried behind the adjoining core wall. Both main board bottoms are 3.45 m above their floors, keeping 0.25 m above the required 3.2 m opening.

Wet-door headers are only 0.16 m tall and the lower lift header only 0.13 m tall. Two separate metal pads and upstanding backstraps engage each named header, carrying its board above the moving envelope. The lowest wet-door mounting parts are 2.705 m above the floor; the lower-lift mounts begin 2.96 m above the floor. No mount uses a moving gate/door or occupies a control.

The lower-ramp east-wall candidate was rejected because an eye-height board would consume the retained 2.4 m dry approach. The selected raised-edge fascia face leaves approximately 0.811 m to the bottom landing's north limit and 0.800 m to the dry approach's west limit. The upper board projects from the east face of the west pocket guard cap, away from the separate sloping ramp handrails: its east edge remains 1.471 m west of the upper clear run and its north edge 0.150 m south of the top landing. This is a guard-cap attachment, not a mount on either ramp grip rail.

Both towel plaques are carried above the fixed housing: dry crown Y48.020 and return cheek tops Y47.420. The 2 mm root engagements are intentional. The unchanged DRY/RETURN glyphs, shelf/return mouths, restocking, rear-handle gap, full 0.92 m receiver stroke and service staging remain outside every new part. The return sign attaches to both fixed cheeks, never the removable container. Nothing is attached to glass.

## Route-arrow calculation

For each board, right = world-up × outward-normal. Project the actual route tangent onto the board's right/up plane and normalize; fail if the planar component is less than 0.25. Arrow mesh orientation uses that result.

- Lower decision: route (−9.4,44,−447.8) → (−12,44,−447.8), tangent (−1,0,0). Board normal (0,0,−1), right (−1,0,0). Projection **(+1,0)**: viewer-right, toward the ramp entrance. It does not imply that the following switchback continues straight.
- Upper landing: route (−15.2,46.2,−447.8) → (−15.2,46.2,−449), tangent (0,0,−1). Board normal (+1,0,0), right (0,0,−1). Projection **(+1,0)**: viewer-right, into the descending upper ramp run.

Both vectors are checked again against the current retained route records, not merely against the stored arrow claim. Named approach eye positions and exact viewing distances are in the JSON for later 640×360 capture.

## Checks actually completed

- 231 pure-Python checks pass, with zero source-screen issues.
- 47 retained catalogue/runtime inputs match their pinned hashes.
- 550 contact samples on 22 mount patches pass. Section box patches use the recorded eight actual vertices; towel feet use evaluated source triangles; core-header contacts use independently decoded retained GLB triangles.
- Current adopted section route, door, lift, staff and source-part records agree with retained source records. Five relevant runtime GLBs match their retained catalogue exports. Compiler/spatial files are additionally pinned.
- Every pad/strap/foot, frame, backing and fastener belongs to a physical connected mount graph.
- No unapproved source/furnishing envelope overlap. Core surviving geometry is screened separately.
- Public apertures, complete lower/top landing and dry bypass volumes, four doors' motion/call regions, local lift gate/call regions, towel clear volumes and both source/runtime return reservations remain clear.
- 10,639 samples of retained arrival, ramp, market, lift, staff and furnishing approach routes pass a conservative 0.32 m radius, 1.9 m high envelope screen.
- All 532 retained cart/operator poses on each of the two staff levels pass a conservative loaded cart/operator envelope screen: 1,064 poses total. These are not force-driven cart results.
- Palette inputs are unchanged. Ivory backing / walnut glyph nominal sRGB contrast is 5.46:1. Texture-pixel, lighting and effects legibility remain untested.
- Six unit tests pass: valid contract, hash drift, disconnected mount, reversed arrow, public-aperture intrusion and unresolved mounting compromise. The intrusion negative test initially exposed a too-shallow aperture test volume; it was extended through the physical board projection and the full tests reran successfully.
- All five Python files compile. No Blender import or engine process was used in any completed check.

## Controlled next steps and stop conditions

1. Parent first clears the running full-suite engine gate. Do not start a second engine job from this handoff.
2. Run the builder only into a new isolated output directory. Default saves the editable source and source-build report; there is no export by default. It fails on source-pin drift, ownership conflict, unresolved compromise, failed mount screen, degenerate geometry, invalid UV, glyph overflow or a letter cap below its minimum.
3. Inspect the actual saved source: glyph outlines and face normals, full contact mesh fit, body/frame hierarchy, source support relationships, material graphs/images/metric scale and all eleven approaches. This source build has not run, so API execution and evaluated output remain unverified.
4. Root reviews any mounting/interface compromise if one appears. Do not widen scope, shrink a protected route or move an original to make it fit. The prepared contract currently declares no unresolved mounting compromise.
5. Export requires a **separate invocation** and explicit receipt matching the exact source and contract hashes. Required receipt fields are documented in `export_reviewed()`; notably source_review_passed, no_unresolved_mounting_compromises and parent_export_approved must all be true. The export is new, same-family, additive and unregistered. Independently compare evaluated source and GLB, including all packed texture hashes and UVs.
6. Parent owns runtime adoption and focused test registration. Check both normal and effects-off 640×360 approaches and short pans; physical text size, contrast, occlusion, framing and both arrows are acceptance gates. Preserve original collision/motion/controller identities and the 51-item assembly.
7. Run imports, original/new capsule, floor, gate, controls and local lift checks; actual loaded-cart forward/reverse/regrip and towel retrieval/extraction; then matched full regression. Check interactions with the separate finish architecture and added stock/fixtures before acceptance.

No low-resolution legibility, Blender source build, export equality, Godot behavior, aggregate regression or occupied/species acceptance is claimed by this package.
