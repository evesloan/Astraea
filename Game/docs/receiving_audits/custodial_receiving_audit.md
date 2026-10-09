# Custodial Depot D01_directory_10 receiving audit

Date:2026-10-09 UTC. Read-only receiving analysis. No Blender, Godot, build, import, backup, production edit, or external worker was run by this audit. Root owns integration and in-engine acceptance.

## Finding

The exact retained Custodial Depot source can use the proposed3,128m² room floor and16m² west connector without a static ownership, protected-void, actual-neighbour or tested-route conflict. The historical entry atZ432 is superseded by the sole current exterior entry at[8,0,460]. Retain the existing native and its corrected export; no architectural rebuild is indicated.

There is no mandatory collision exclusion equivalent to Cinema5’s explicitly visual-only floor markings. The eighty HSK meshes marked body_candidate_retained=false belong to an optional simplified geometric-body subset. They are still present in the complete precise-reference collision proposal and visible native. An early parent notification interpreted that flag too strongly; the corrected interpretation below governs this report.

Static routes are not real player/cart/species acceptance. The1.7m-radius screen fails two final work approaches at existing bearing piers, although the.3,.5 and.65m-radius screens pass. Root separately reports a passing unchanged-player test and bounded default-scene checks; this audit did not execute them.

## Verified source identity and placement

- All85 manifest entries match delivered byte counts andSHA-256. No mismatch.
- Editable nativeSHA-256:98c13dd2d18bec5c8e5cdb5f8be84b02f86e45990d4e573d96d0af1bc66d308d
- Corrected exportSHA-256:076365a7d65e5b6381799fab3cd3e3d75ad75aca4370291150dac8e78df0c299
- Predecessor exportSHA-256:46ceb4ae15f41ba4bcf34e77912efa66225753e9dc35a4bf6fcebd861857bbe7
- Exact runtime placement:translation[8,0,460],yaw0,scale[1,1,1]. The export is localY-up at the receiving portal; it is not identity world coordinates.
- Actual world bounds:[[8.0, 0.0, 398.0], [54.0, 5.699999809265137, 466.0]]
- 7400 mesh nodes,1752 unique mesh resources,169550 triangles,12 embedded images; no external image URI.
- All7,376 predecessor mesh nodes have exactly equal transformed triangle arrays. No retained mesh was removed or changed. Only the24 authored FONT signage meshes were added by the export correction.
- All35 predecessor light records, transformed positions, colors and intensities are exactly unchanged.
- All133 named native-placement roots exist as NAME_placement, with their member meshes retained and unit world scale. Maximum origin error versus instances.json:1.525878929e-06m. The initial exact-name query omitted the authored _placement suffix; the final corrected test has zero placement errors.
- All35 lights match lights.json; maximum documented position error is0.000000763m. They are raw point emitters without glTF range fields; intensity spans11957.3109–27175.7065. Use the shared bounded receiving-light adapter; do not treat these intensities as ready engine brightness.
- Source normals/positions/UVs are finite; all primitives carryPOSITION,NORMAL,TEXCOORD_0. Normal lengths span0.999999881–1.000000119. There are112 numerically degenerate triangles isolated to the24 lettering nodes. No structural receiver triangle is implicated.
- No preview floor is exported. Native reopening was not repeated; the unchanged native hash and package export-only receipt preserve that provenance without claiming a new Blender validation.

## Missing-only receiving floors

All polygon coordinates are worldXZ metres. Floor topY0. Standard0.24m receiving thickness gives undersideY−0.24. The current425 retained owners comprise303 original+116 previous+2Salon+2Stillroom+2Cinema5. Exact unioned owner triangles were used, not allocation AABBs.

Room polygon,3,128m²:

[[8,398],[54,398],[54,466],[8,466]]

Connector polygon,16m²:

[[4,458],[8,458],[8,462],[4,462]]

- Allocation area already owned atY0:0m². Both recommended polygons are entirely missing-only additions.
- Connector connection_to:D01_aft_route.
- Existing-route contact:X4,Z458..462,4m long.
- Room contact:X8,Z458..462,4m long.
- Zero positive-area same-datum overlap and zero positive-volume slab overlap against all425 retained floor owners.
- Zero intersection with applicable protectedD01 voids.
- Source west shell physically opens betweenZ458 and462. West_fore runsZ398..458;West_aft runsZ462..466. Portal_lintel occupiesX8..10.5,Y3.5..5.7,Z458..462, leaving a4m-wide,3.5m-high aperture.
- East, fore and aft shells are continuous in the actual export. No unsupported second exterior portal was found. AST-STF-008 is an interior staff threshold and must not be substituted for the main4m portal or claimed as a laundry connection.
- The receiving connector is open-sided atZ458 and462 forX4..8. The source deliberately contains no connector geometry. Centerline support passes; unrestricted side-edge/fall behavior is not accepted by this audit.

## Actual source contacts

All292 source-proposed bearing nodes exist. Their supplied footprint polygons lie entirely inside the receiving room; no unsupported proposed footprint was found. Actual lowestY across these nodes is0..0.00400000019m, reflecting the source’s slightly relieved/beveled details rather than below-floor penetration.

A stricter independent horizontal-face calculation finds229 nodes with positive-area triangles lying within0.00002m ofY0. Their union is157.258731428556m², fully covered by the receiver. The other63 nodes in the292-part proposal are wall-panel/backing profile details:60 begin atY0.004m and3 atY0.002m. They are projected lowest-face support probes, not physical zero-height contacts. These are different measurements, not a missing63-node defect. No source node extends belowY0 beyond the2e−5m float tolerance.

The package’s retained133-assembly contact report records no failed contacts and uses actual mesh distance to architectural triangles or the proposed floor plane. It is source-only evidence with a0.06m gate, not structural load certification or a new installed contact result. Machine-readable output retains exact floor-contact polygons, source bounds and all292 bearing-node records.

## Current ship geometry and upper interface

The neighbour check reads actual installed model files and current placements, including the aft public core, lower hull, lower staff network, every receivedD01 section and every receivedD02 section. Broadphase candidates are clipped using actual triangles rather than reporting overlapping multi-deck modelAABBs as collisions.

- Current aft core isassets/models/AST-CIR-005_aft_crewcare_d03.glb at[0,0,432], not the older generic spine-core filename. It ends aroundZ452.04; the receiving entry atZ460 avoids its closed east side.
- Core’s maximum side extentX7.8800001 leaves about0.12m to the source west wall atX8. No existing core wall cut is required.
- No actual neighbour triangle intrudes into the room’sX8..54,Z398..466,Y0..5.7 interior band.
- No source triangle penetrates an existing retained floor slab.
- D02_inspection_dock_source_floor overlaps1,831.8m² in projection overhead. It isY6 with undersideY5.76; source roof topY5.6999998 leaves0.0600002m. This small verified gap is not a structural allowance to raise the roof or add upward protrusions.
- TheD02 inspection enclosure and equipment begin atY6. Their horizontal overlap is expected stacking, not a room collision.

## Static routes and exact waypoints

All points below areXZ at floorY0. Actual source+neighbour triangles are clipped toY0.06..2.1, with0.0001m inflation only for line-like projections. Swept circular radii.3,.5,.65m all have zero physical obstruction and zero unsupported floor area along the following paths. This is a conservative static planar screen, not an occupied capsule, articulated cart, turn, controller or real species test.

- arrival_to_handover: [[8.6, 460], [27, 460]]. Minimum geometric centerline clearance2.011964m.
- cart_spine: [[26.5, 453], [26.5, 411]]. Minimum geometric centerline clearance3.829900m.
- workcab_approach: [[26.5, 439], [19.4, 439]]. Minimum geometric centerline clearance0.779901m.
- ready_stock_approach: [[26.5, 449], [39, 449]]. Minimum geometric centerline clearance1.944900m.
- used_hold_approach: [[26.5, 405], [19.5, 405]]. Minimum geometric centerline clearance0.779899m.
- receiving_entry_extension: [[0, 460], [4, 460], [8.6, 460], [27, 460]]. Minimum geometric centerline clearance1.999900m.
- connected_work_route: [[0, 460], [27, 460], [26.5, 453], [26.5, 439], [19.4, 439], [26.5, 439], [26.5, 405], [19.5, 405], [26.5, 405], [26.5, 449], [39, 449], [26.5, 449], [26.5, 453], [27, 460], [0, 460]]. Minimum geometric centerline clearance0.779899m.

Additional existing-core exit:

[[0,450],[0,460],[4,460],[8.6,460],[27,460]]

This passes radii.3,.5,.65 and1.7m with zero unsupported sweep; minimum clearance1.9999m. It establishes the actual aft-core opening rather than merely starting on an isolated room threshold.

The1.7m-radius workcab_approach and used_hold_approach fail atBearing_pier.021 andBearing_pier.005 respectively. Both centerlines approach withinapproximately0.7799m of the pier. The source’s reported cart check usedradius0.5m,height2.1m, not a1.7m radius. Preserve the source; if a broader species/cart use is later required, resolve the approach waypoints or use stance before changing structure.

- Bearing_pier.021 actual worldXYZ bounds:[[21.329999923706055, 0.0, 437.7800006866455], [21.670000076293945, 5.119999885559082, 438.2199993133545]]
- Bearing_pier.005 actual worldXYZ bounds:[[21.329999923706055, 0.0, 405.7799987792969], [21.670000076293945, 5.119999885559082, 406.2200012207031]]

## Collision semantics and source intent

The candidate should keep source-supported physical contacts and real shelf/cabinet/threshold openings. Never replace open shelf ranges, workcabinet approaches, the carrier liner, or lower retrieval spaces with blanket enclosing hulls. The181 source structural primitive proposals are not a complete collision set for all7,400 meshes.

Both bundled HSK manifests and native dependency hashes exactly match the retainedhousekeeping_handling family. That family’sREADME Collision roles section andcollision_proposals.json distinguish:

- AST-HSK-003:25 precise semantic reference shapes;23 optional-body shapes.
- AST-HSK-004:51 precise shapes;33 optional-body shapes.
- Four placements of each produce80 fine meshes outside the optional subset:8 bench identification plates and72 carrier fork/axle/strap/label details.
- All remain in the complete precise reference. The optional subset is not a game collider until adopted and checked; its engine_adoption isPending.
- body_candidate_retained=false therefore does not instruct the receiver to drop static collision. It is not equivalent to Cinema5’s explicit visible-only marking policy. No such mandatory mesh-level exclusion was found here.
- Nonphysical approach/bearing-axis markers are emptynodes without meshes, not hidden obstacles.
- Keep USED-only carrier identity and static retained caster geometry. No rolling, hygiene,load, stock refill or player-cart replacement is implied.

## Design review and acceptance boundary

Reviewed complete relevant master chapter prose4,5,7,11,14,21,30,32 and current-decision overrides, plus sourceBRIEF,plan/current-allocation/floor/collision/instance/light manifests and actual export/native-contact reports. These require a legible connected custodial workplace, separate ready and used handling, real support and useful clearance, source-driven cool staff lighting, editable continuity, and normal-play evidence in the existing Godot project. Historical master implementation statements remain historical; the current six-species,400-crew,1,000-unit,RMB/E andGodot4.6.3 decisions apply.

The native is already constructed and retained. Do not run the historical architectural builder or regenerate stock from a substitute. Parent/source responsibilities for exterior routes, floors, crossings and lift-stop acceptance remain separate. The source does not establish hygiene chemistry, dispatch operation, inventory/refill, clinical/species capacity, cabinet mechanisms, loaded-cart behavior, save/load or target-GPU performance.

Root reported at06:28UTC:default-scene292contacts/427static route samples pass; unchanged player208.0394m over4,197 ordinary-input frames; preceding58-section4,348samples pass; five bounded Godot images reviewed. These are reported integration evidence outside this audit’s execution. Root had not yet claimed installation completion at that message. Use root’s final matching runtime receipts for installation status.

## Deliverables and reproduction

- Human report:custodial_receiving_audit.md
- Final machine report:custodial_receiving_geometry.json
- Compatibility copy:custodial_receiving_audit.json contains the same final records.
- Read-only scratch analysis:audit_custodial_static.py,finalize_custodial_audit.py,write_custodial_report.py. Their outputs stay in scratch; no production file was written by this audit.

Pinned owner/void inputs:

- data/generated/structural_meshes.json: e7cd0cc1c3892a99cf75f2dab4c852f3e1c1864a13b81f828e2a2f93cf239e92
- data/generated/received_structural_meshes.json: e05fd27b14d97d5bdf37a6ac94bb80b1c009342d69ff90142579fe692af3a59b
- data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json: f2a04e22b2a085c6fb1c83f195031a43611402cc09eaa165ee278738fa9502dc
- data/architecture/STILLROOM_RECEIVING_FLOORS_CANDIDATE.json: 704c3cbc430dde93deee14d33f12c0220d5647183019b7e43c4c1ffec79d2755
- data/architecture/CINEMA5_RECEIVING_FLOORS_CANDIDATE.json: f50999339be030e66c27e4007c6b08e149a171c2528b715a0b360afc434ea01e
- data/spatial_layout.json: 75cc3e6259d89da873f5c2fa4fefa2e846427eeda3e5457561d785305a0471d2
