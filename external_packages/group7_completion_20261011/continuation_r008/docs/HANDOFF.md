# Group 7 R008: west theatre weatherline and owned body correction

The 170m west theatre shoulder now has a finite one-metre weather join from the actual retained skin top at Y92/X−109.6 to the owned canonical body foot at Y93/X−109.2. The first-pass owned foot had used lower theatre extents from an adjacent-height screen, displacing it out to X−118.45. This continuation corrects270 owned parts and adds217 finite weatherline/gasket parts. Original theatre skin, rooms, roofs, floor owners, audience capacity and all earlier source revisions remain immutable.

The three selected body cells are explicit successors of `Body_-1_01`, `Body_-1_02` and `Body_-1_03`. Other83 models, all39 lights and all eight doors retain their exact R007 definitions. The current opt-in selection remains86 models/39 sources/eight doors, with the original eight-source shadow budget. Shared root and registries remain untouched.

## Implemented and tested

The editable native is `source/natives/G7_TheaterWeatherline_r008.blend`, SHA256 `4ad44963ca7c498497d9f08594af73ee6a2a0cb0ac8799be07b05f01917b59cc`. It derives from immutable R005B, SHA256 `c44d92f922628ad6b88e6c678d2dbbd7aa1fc2f18c8adef4f3248495b3a5fee0`. The source audit passes46,350 checks, preserves27,758 undeclared objects and170 packed images exactly, and checks all487 corrected/new parts for closed manifold geometry, positive volume and finite UVs. Three independently decoded exports contain31,444 triangles and match native points within0.1mm.

`qa/FINITE_WEATHER_SECTIONS.json` independently measures1,395 decoded outer/inner sections through the actual new exports. Maximum section error is0.000004537m. All31 gasket projections fit inside the exact decoded old horizontal cap. Skin depth is0.18m measured normal to the sloping surface. The physical closure continues the same slope above and below Y93 instead of inserting an8.85m cantilevered roof.

`qa/RUNTIME_CHECK.json` passes1,341 focused checks in actual baseline main with the opt-in candidate:487 protected-source shape queries, zero unexpected contacts,31 deliberate gasket contacts with `HUL2_FullShoulderSkin`,651 finite weather/body surface rays,93 retained original cap witnesses and24 original D11 bridge floor/worker poses. Four walking legs use the original player controller with two fixture seeds and no position writes between legs. Receiver queries exclude only owned candidate colliders; seam surface rays, ordinary routes and walking exclude none. Actual engine triangles match native/export points within0.1mm; measured maximum import error is0.000061035m. Only the three new owned import settings disable compression.

These tests establish bounded construction/contact geometry and preservation of the original D11 worker bridge. They do not establish pressure/weatherproof engineering, primary capacity, theatre operations, closed upper/secondary joins, largest-species/cart fit or whole-group acceptance.

## Source interfaces and remaining holds

Group8 branch `688a18417b6b17cfdcf527f26c8973ed4fd1142a` was inspected read-only. Its theatre receiving contract preserves the2200 audience allocation, original source envelope ending at Y92, active D11 receiving bridge and closed upper/secondary/backstage interfaces. All24 geometry/controller/floor/native pins match this retained baseline. Only its older shared `ship.gd` pin differs; Group7 does not edit that root. The library fit-out is geographically separate. Exact candidate bounds find no protected architecture or historical guest reserve in the corrected owned foot band.

The gasket contacts a skin cap. **This supplies no primary bearing rating.** The original HUL002 skin is the only retained component with a head above Y89 in that source. Group1/Group8 must provide the primary receiver graph, true member seats, sections, connections, restraints and load cases before the upper body is accepted as supported architecture. No support capacity is inferred from a positive contact ray.

The actual width reconciliation captures251 original witness meshes/65,430 triangles and correlates them to immutable GLBs using measured old-import quantization. Among the original294 nominal-node neighbour screens, one is clear and293 retain the original0.8m reservation hold. No actual source was found outside the variable calibrated hull within the declared5mm old-import measurement allowance. This distinguishes a neighbour-band planning screen from a physical collision; it does not waive the reserve, change a criterion, trim a source floor or accept full body fit. `docs/WIDTH_RECEIVING_INTERFACE.md` gives the integration owner the exact remaining decision.

The155 historical theatre facade exclusions remain original-source ownership records. This continuation closes their measured upper weather seam; it does not overwrite the retained skin or claim all its engineering/detail acceptance.

## Visual review and attempts

`qa/views/SOURCE_R008B_THEATER_ALL_RETAINED_RECEIVERS_WIDE.png` is the directly reviewed wide real-source photograph: full theatre shoulder, corrected glazing/weatherline, retained middle frame/skin and all original compiled floor receivers. Camera/native/source hashes are recorded in `qa/SOURCE_VIEW_RECEIPT002.json`. It is a neutral Workbench source viewport with actual UV textures, not an in-game/CRT/target-hardware or final-art image. Upper floor/enclosure interfaces elsewhere remain visibly unfinished. The first source view with only theatre-floor context is retained alongside the fuller receiving context; no source native was resaved for either photograph. EGL fallback warnings remain in both successful render logs.

There were no failed native/export/runtime attempts in this continuation. Two incorrect Library-search argument shapes were corrected to the canonical schema and retained in `qa/LIBRARY_SEARCH_ARGUMENT_ATTEMPTS.json`; they were argument failures, not approval rejections. The selected screenshot is saved with its Library identity in `qa/LIBRARY_SCREENSHOT_DELIVERY.json`.

## Integration

1. Verify `RESOURCE_HASHES.json` and the exact independent remote receipt for this handoff branch. Preserve every retained original and unselected revision.
2. Apply only the three declared substitutions in `docs/RUNTIME_REPLACEMENTS.json` to `docs/PREIMAGE_GROUP7_COMPLETION.json`. Never instantiate both generations of the same body cell.
3. Keep `group7_completion.gd` opt-in. Shared source/root/registry adoption belongs only to construction thread `01a11d7f-8ef6-70bc-858d-bdf8deb7000b`. Reconcile current Group1/8 sources against the pinned contracts before shared adoption.
4. Refresh imports, then run `godot --headless --path Game --script res://tests/group7_theater_weatherline_check.gd` and the independent decoded/import checks. This evidence is baseline-topology scoped. Preserve historical earlier-phase receipts; their pinned selections are not current full-suite tests.

Group7 continues with owned D18 overhead hardware. Remaining primary structure, house/Royalty790 and wet-roof/tank-bearing decisions, complete weatherproof enclosure, service/care logistics, plant interaction/inhabitation/species and final graphical/CRT/hardware/art acceptance stay separately open. No protected luxury roof is cut or lowered, and no whole group is accepted.
