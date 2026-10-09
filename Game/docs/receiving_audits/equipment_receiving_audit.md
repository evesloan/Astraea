# Equipment Depot D03_directory_03 receiving audit

Date: 2026-10-09 UTC. Read-only source/actual-installed geometry audit. Root owns integration. No source or production edits, Blender/Godot builds, imports, backups, or external workers were run.

## Finding

The unchanged Equipment Depot export fits its allocation and needs one 2,720 m² missing-only floor at Y12. No additional connector is needed: the existing 6 m-wide depot threshold floor meets the new room edge. All54 source bearing nodes are supported. There are no incompatible floor overlaps, protected-void conflicts, or true interior triangle intrusions from nearby installed geometry.

A real receiving blocker remains: the currently installed lower staff network has a solid legacy cap across the reserved depot entrance. Source-only route evidence does not include this cap. The smallest reversible fix is a new receiving variant opening only four retained cap solids to the existing3.6 m by2.65 m gate reservation. Keep the source depot, all other lower-network geometry, crew-home gate, controllers and player cart unchanged. No new dynamic gate is required to establish the geometric receiving connection; whether to add one later remains a separate root-owned decision.

## Source identity and native placement

- All67 manifest entries match byte counts andSHA-256. No failure.
- Editable nativeSHA-256: 78beb0bb0a0a32c77565a17fc9f9bf3045e43a43894f9e10000629e81dcb242e
- ExportSHA-256: 75b158772963f78eedd2e1a5391580267d7ca009e734dcb978cb507046758c22
- Runtime placement is identity: translation[0,0,0], yaw0, unit scale. The source already contains worldY12, not localY0.
- ActualXYZ bounds: [[-47.80000076442957, 11.999999962747097, -249.6900061070919], [-8.200000189244747, 15.340000458061695, -182.3099938929081]]
- 447 mesh nodes, 447 unique mesh resources, 29252 triangles; 12 embedded images, no external image URI; zeroKHR lights.
- No shared floor or source-only preview floor is exported.
- All five registered placement roots exist at their documented world origins with zero measured origin error. Workcab world scales differ from1 only by glTF quaternion float error, approximately1.34e−7.

  - A_Workcab_0_placement (AST-STF-007): [-44.5, 12, -244], yaw-1.5707963267948966, sourceSHA-256 b1705b3e5d7a48f4d28765a26b7c9f60fe4aa61df3b593ba4f35861125cf8edb
  - A_Workcab_1_placement (AST-STF-007): [-44.5, 12, -235], yaw-1.5707963267948966, sourceSHA-256 b1705b3e5d7a48f4d28765a26b7c9f60fe4aa61df3b593ba4f35861125cf8edb
  - A_Workcab_2_placement (AST-STF-007): [-44.5, 12, -203], yaw-1.5707963267948966, sourceSHA-256 b1705b3e5d7a48f4d28765a26b7c9f60fe4aa61df3b593ba4f35861125cf8edb
  - A_Equipment_care_station_placement (AST-HSK-003): [-12, 12, -193], yaw0, sourceSHA-256 d0d952f890868d2234ececa0e80b19d7df681bb557a152590d76a9510bc6c47c
  - A_Used_only_return_placement (AST-HSK-004): [-13, 12, -187], yaw0, sourceSHA-256 73ea7b4ceb77ec583c072f5e4147a09436883836bcb1d72ef7568e33e5f75489

Native reopening was not repeated. The retained native geometry report records182 supported authored parts, five floor-supported assemblies, no failed contacts, no authored inward solids and no external libraries. Those source-only assertions remain bounded; the actual export and receiver checks below were calculated independently.

## Exact missing-only receiving floor

All polygon coordinates are worldXZ metres. Floor topY12, thickness0.24, undersideY11.76.

Room boundary: [[-48,-250],[-8,-250],[-8,-182],[-48,-182]]

- Required and missing-only area:2,720 m². Existing floor owns0 m² inside this room rectangle.
- Do not floor the entire wider allocationX[-54,-8]. Its6 m western strip is retained interface territory, not a new room floor request.
- Existing ownerD03_port_forward_staff_floor_0 already supplies the6×6 m thresholdX[-54,-48],Z[-219,-213]. It contacts the new room alongX−48,Z−219..−213, length6 m.
- New connector area:0 m². Preserve all427 floor owners (303 original+116 prior receiving+8 recent receiving).
- Zero positive-area same-datum overlap and zero positive-volume slab overlap; zero applicableD03 protected-void overlap.
- The source package split its additive rectangle into five arbitrary polygons against an older262-owner snapshot. Their union is exactly this rectangle. The current live427-owner calculation, not the old snapshot, determines missing-only receipt.
- D02_directory_03_authored_floor overlaps2,551.3345 m² in projection atY6, far below the depot. No nearby floor atY16.5 overlaps this allocation in the current owner set. Neither observation implies a floor should be added elsewhere.

## Supported source contacts and enclosure

- All54 actual positive-area datum-contact nodes are covered. Their union is54.257619176 m²; unsupported area0.
- This also agrees with the package’s54 source-bearing proposal parts. No actual source vertex lies belowY12 beyond2e−5 m tolerance.
- West source partition lies atX−47.8..−47.6. Its sole opening isZ−217.8..−214.2 andY12..14.65, matching the3.6 m×2.65 m reservation. The0.2 m room-floor interval between retained capX−48 and source west faceX−47.8 is supported by the new floor.
- East, fore and aft source skins are continuous; there is no unsupported second source exit. Source walls lie inside the floor boundary. The roof underside isY15.2 and topY15.34000046.
- Source does not enter the protected approach prismX[-54,-48],Z[-217.8,-214.2],Y12..14.65.
- No source triangle penetrates a retained floor slab. All applicable source bearings remain on the new receiver, not on arbitrary underside or a neighbouring floor.

## Actual retained crew-platform and gate interface

The installed lower network isassets/models/AST-STF-009_pool_market_home.glb at identity, as selected byscripts/lower_staff_network.gd. The home component isAST-STF-010_home_dogleg_labels002.glb, also identity; it has no geometry in the depot neighbourhood. The full crew-service-platform proposal is not the same as that installed bounded home component and must not be assumed installed.

The retained crew-platform contract reserves the Equipment Depot interface at[-48,12,-216], clearwidth3.6 m, clearheight2.65 m. It explicitly assigns future dynamic door integration to the parent and sayscontroller_created=false. The lower-network README calls the depot a closed, bounded6×6 m threshold. There is no existing dynamic depot gate/controller to duplicate or replace.

The current actual export has these four legacy cap solids, fromlower_staff_network/source/geometry_parts.json. Bounds use[x0,x1,y0,y1,z0,z1]:

- STF_D03_Wall_00_21_00_Wainscot: [-48.12, -48, 12, 13.03, -219, -213]
  - Replacement boxes: [[-48.12, -48, 12, 13.03, -219, -217.8], [-48.12, -48, 12, 13.03, -214.2, -213]]
- STF_D03_Wall_00_21_00_Enamel: [-48.12, -48, 13.03, 15.2, -219, -213]
  - Replacement boxes: [[-48.12, -48, 13.03, 15.2, -219, -217.8], [-48.12, -48, 13.03, 15.2, -214.2, -213], [-48.12, -48, 14.65, 15.2, -217.8, -214.2]]
- STF_D03_Wall_00_21_00_CartBumper: [-48.144999999999996, -48.12, 12.73, 12.86, -219, -213]
  - Replacement boxes: [[-48.144999999999996, -48.12, 12.73, 12.86, -219, -217.8], [-48.144999999999996, -48.12, 12.73, 12.86, -214.2, -213]]
- STF_D03_Wall_00_21_00_PanelJoint: [-48.126, -48.12, 13.04, 15.14, -216.008, -215.992]
  - Replacement boxes: [[-48.126, -48.12, 14.65, 15.14, -216.008, -215.992]]

These replacements total eight boxes, all inside the corresponding original solid. The opening isZ[-217.8,-214.2],Y[12,14.65], through the original thicknessX[-48.145,-48]. Retain the two side returns, upper enamel lintel, upper panel joint and every unrelated triangle. The four actual batched source witnesses each contain exactly12 outward box triangles; the machine report records all48 target triangles and their batch names. Oppositely wound coincident faces from adjacent retained boxes are explicitly preserved.

Affected runtime batches areHOME_BATCH_031_ASTRAEA_staff_bluegrey_paint, HOME_BATCH_196_ASTRAEA_staff_white_paint, HOME_BATCH_147_ASTRAEA_staff_rubber andHOME_BATCH_259_ASTRAEA_staff_zinc. They contain other architecture, so never remove an entire batch or turn off its collision. Rebuild a new receiver-specific native/export variant from the retained editable source, preserving the old assets and existing home opening. Changing only a collision mask would leave a visible solid wall and is not an acceptable receiving fix.

This audit performed only a read-only hypothetical triangle substitution. No modified native orGLB was generated. Root must decide/apply the variant under its development scope and validate the final native/export and actual installed collision. The existing gate reservation and all original assets stay preserved.

## Actual surrounding geometry and static routes

Neighbour broadphase inspected actual installed lower hull, lower staff network, bounded crew-home component, and all current receivedD02/D03/D04 sections with their current placements. The only relevant source nodes within the local12..18 m height band were two lower-hull nodes and15 lower-network batches; no received neighbouring room reaches into the depot. Large modelAABBs were filtered using triangles. Three tiny nominal “overlaps” atX−48 were caused only by0.1 mm inflation of line-like boundary projections; with a0.2 mm interior inset no actual neighbouring triangle intrudes.

Routes use actual triangles clipped toY12.06..14.1 and swept circles. Values below are post-hypothetical-cap-opening geometric centerline clearances, not capsule/cart/controller acceptance. All listed routes pass radii0.3,0.5 and0.65 m with zero obstacle overlap and zero unsupported swept area. Before the cap opening, every entry-containing route fails at the four legacy wall materials; the four wholly internal work routes already pass.

- retained_gate_to_issue: [[-48, -216], [-33, -216]]. Minimum clearance1.799897 m.
- depot_work_spine: [[-33, -247], [-33, -186]]. Minimum clearance1.199901 m.
- stock_retrieval: [[-33, -235], [-20, -235]]. Minimum clearance1.619907 m.
- assessment_approach: [[-33, -216], [-33, -209], [-22, -209]]. Minimum clearance2.819900 m.
- care_approach: [[-33, -186], [-17, -186], [-17, -193]]. Minimum clearance0.819900 m.
- receiving_entry_extension: [[-57, -222], [-57, -216], [-51, -216], [-48, -216], [-33, -216]]. Minimum clearance1.654899 m.
- connected_work_route: [[-57, -222], [-57, -216], [-51, -216], [-33, -216], [-33, -247], [-33, -235], [-20, -235], [-33, -235], [-33, -209], [-22, -209], [-33, -209], [-33, -186], [-17, -186], [-17, -193]]. Minimum clearance0.819900 m.

The1.7 m-radius screen is not accepted: the staff entry extension encounters retained corridor/bumper clearances, the spine reaches the staff table, stock retrieval nears the shelf task body, and care approach hits the bearing-foot/furniture region. Source cart evidence used0.5 m radius and2.1 m height. Do not promote a0.5 m cart screen to every species or a loaded articulated cart turn.

## Source-fixture emitter fit

All19 documented preview fixtures have an exact deliveredA_<fixture>_lens mesh. The preview records are[name,[x,localY,z],width,length,watts]; add12 only toY.

- Fifteen main fixtures: X−38,−22,−12 crossed withZ−243,−230,−216,−202,−188. World emitterY14.89. Lens undersideY14.912500305, gap22.5003 mm.
- Three stock-shelf fixtures: X−21,Z−241.18,−233.18,−225.18. World emitterY13.93. Lens undersideY13.952500267, gap22.5003 mm.
- Repair shelf fixture: X−43,Z−197.98, world emitterY13.93, same22.5003 mm gap.
- Every emitter falls within the corresponding lensXZ footprint. These are source-backed light origins beneath real lenses. ZeroKHR lights are present, so an explicit receiving adapter is needed.
- Preview300 W main and70 W shelf values are source-render power, not Godot light_energy. Use the existing bounded receiving light policy and existing8/32 budget. No ambient wash or camera inspection lamp can substitute for source lighting acceptance.

## Collision, design, and acceptance limits

There are20 meshes withbody_candidate_retained=false: twoHSK-003 identification plates and18HSK-004 fork/axle/strap/label details. This flag concerns only an optional simplified-body subset. It is not a collision exclusion; all source geometry was retained in this audit’s conservative physical screen. No explicit per-mesh collision policy/exclude directive was found in this export. Keep real shelf openings, workcabinet approaches, carrier liner and low retrieval areas; do not substitute enclosing convex hulls. TheUSED-only return carrier is static source furnishing, not a second player cart.

Reviewed current master application and complete relevant chapters4,5,7,11,14,21,28,30,32, source contract/authoring logic, receiving proposals, retained interface contract and actual export/native QA. Current six-species,400-crew,1,000-unit, RMB/E andGodot4.6.3 decisions govern; historical October1 implementation assertions do not establish today’s feature completion.

Inspected suppliedimage8.png andimage10.jpg references plus the authored arrival view. They call for readable source bulbs, deep shelves, supported work edges and a humane cool staff environment. The arrival source render remains conspicuously sparse and cannot establish finished inventory, capacity, art or current Godot presentation. No architecture rebuild is needed to resolve this receiving blocker.

Unaccepted by this audit: native reopening, actual engine import/collision, ordinary player movement, loaded-cart guidance/turning, species fit, door mechanism, stock/refill, clinical operation, occupancy, save/load, D03–D05 service lift stops, final light response and target-GPU performance. Root should preserve the current player/cart/controllers and verify its final connected candidate through existing runtime tests and actual views.

## Reproduction and pinned inputs

- equipment_receiving_geometry.json: exact floors, contact polygons, actual source/surrounding bounds, source/native pins,48 retained cap triangle witnesses,eight replacement boxes, pre/post hypothetical routes and19 fixture fits.
- Read-only scratch scripts: equipment_audit_helpers.py, audit_equipment_static.py, finalize_equipment_audit.py, write_equipment_report.py.
- Final hypothetical fix selection identifies the original box corner sets and outward winding. Early contained-triangle/face-only scratch selections were overbroad and were corrected before this report; only the final12 triangles per original cap solid govern.

- data/generated/structural_meshes.json: e7cd0cc1c3892a99cf75f2dab4c852f3e1c1864a13b81f828e2a2f93cf239e92
- data/generated/received_structural_meshes.json: e05fd27b14d97d5bdf37a6ac94bb80b1c009342d69ff90142579fe692af3a59b
- data/architecture/CINEMA5_RECEIVING_FLOORS_CANDIDATE.json: f50999339be030e66c27e4007c6b08e149a171c2528b715a0b360afc434ea01e
- data/architecture/CUSTODIAL_RECEIVING_FLOORS_CANDIDATE.json: 546853ed61f2e2ff69101ad8bfacd789819be550a77c650efa8761d1a26b5cd1
- data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json: f2a04e22b2a085c6fb1c83f195031a43611402cc09eaa165ee278738fa9502dc
- data/architecture/STILLROOM_RECEIVING_FLOORS_CANDIDATE.json: 704c3cbc430dde93deee14d33f12c0220d5647183019b7e43c4c1ffec79d2755
- data/spatial_layout.json: 75cc3e6259d89da873f5c2fa4fefa2e846427eeda3e5457561d785305a0471d2
- assets/models/AST-HUL-001.glb: 0a53fd2357fe1ca24b350bf53f0ee9bc2d495e8306f581c1ac13bfb685cd7fd0
- assets/models/AST-STF-009_pool_market_home.glb: ab47a5fe0cc1ba858777d8ac91ae8f7bf54729df19bfb6a9ec8af31beccff7b4
