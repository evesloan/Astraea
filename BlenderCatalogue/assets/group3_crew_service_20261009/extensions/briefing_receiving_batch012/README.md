# Group 3, batch 012: Missing-only crew briefing staff receiver

Frozen source-only construction for the existing D03 briefing programme. Two editable Blender sources, deterministic builders, compact exports and bounded QA are supplied. The original room, fitted gate reservation, piers, header, reveals, roof, furniture, programme and all occupancy/save identities remain unchanged. Group 3 is unfinished.

## Actual installed source and missing interface

D03_directory_08 is already represented by crew_batch_receiving.gd at world identity, using D03_directory_08_runtime_names001.glb. Its 346 original meshes come from the retained briefing source. The installed runtime's binary geometry chunk is byte-identical to that source; only node names and provenance extras differ. The original room's inboard/public approach, fitted furniture and four received preparation lights remain untouched.

The east opening is centred at Z216. The retained fitted pier's outer east face is X53.875; its nominal clear opening is Z213.9..218.1 beneath the Y14.65 header. The exact native reveal coordinates, rather than rounded metadata, govern the final flare. The roof outer edge is X53.8 with underside Y15.2 and top Y15.34. Its actual native edge is rounded over 0.03 m.

The old AST-STF-010 briefing endpoint [50.2,216] and its five-metre turn bay lie inside this existing room and cross the received frame/ceiling. No old briefing branch geometry is adopted in this slice. The retained original platform remains unchanged. A second room, duplicate turn bay, duplicate roof or full platform adoption would be incorrect here.

The real missing receiver is only the short gap between the first-street outer face X55.06 and the fitted original pier face. Its street-side gross mouth is 3.6 m, Z214.2..217.8; it flares to the original approximately 4.2 m doorway. The floor is Y12 and the receiver ceiling remains Y15.2. Standard 0.03 m cart-protection strips project into the gross clear width. The exact existing gate reservation stays [54,12,216]. No door or stable gate identity is generated.

## Two assets and exact original preservation

- AST-STF-G3-020 has 16 editable components and eight runtime mesh batches. Two flared painted wall bands on each side, two bumpers, two upper service lips, the missing roof, one receiver-side upper-slot closure above the original fitted header, two exact rounded-roof edge complements, and four pieces of the retained supported task-fixture profile. The original header itself is never cut, moved or replaced. The source-only fixture datum is [54.65,15.03,216], with both hangers physically contacting the new roof.
- AST-STF-G3-021 has four preserved first-street semantic fragments and four runtime meshes. It opens only X[55.06,55.2], Z[214.2,217.8], Y[12,15.2] across the two original 8 m cells. All 2,795 other first-street meshes remain unchanged.

The main new roof ends at the original roof's exact native outer plane. A plain AABB join would leave the old rounded edge's empty corners. Two tiny profile-matched complements fill only those corner spaces across the original header span. Their cross-sections have zero overlap with the original roof's convex native profile, and six fresh-native shared profile points pass. Neither the original roof nor the old room is rebuilt. The existing ceiling is still a proposed structural receiver; this fit is not bearing acceptance.

## Exact root adoption contract

1. Keep the installed briefing source at identity, its existing room/root, all 346 meshes, original furniture, floor owners and programme/save identities. Reuse the pinned original source and runtime; no duplicate room export is supplied.
2. Receive AST-STF-G3-020 at world identity only after approving its exact supports and actual gate/frame/service use. Do not also adopt the old AST-STF-010 briefing branch, its shifted endpoint, terminal bay, room-side walls/caps or fixture. No platform component is reused as a room-side branch here; only the existing task-fixture profile is reused at its explicitly new source datum.
3. Omit exactly these original first-street native mesh nodes while adopting AST-STF-G3-021: screen_wall_staff_bluegrey_paint_6_26, screen_wall_staff_bluegrey_paint_6_27, screen_wall_staff_white_paint_6_26 and screen_wall_staff_white_paint_6_27. The new export contains those same exact names. Preserve every other original mesh. Compose this omission set with the distinct, explicit sets from earlier protected receiver slices.
4. Compose the actual baseline/additive floor and previously held first-street support with only BRIEFING_MISSING_SUPPORT_PROPOSAL.json. The exact request is 6.0583313465 m²: 1.0821535179 m² already has actual floor, 0.5482897503 m² belongs to the prior held street proposal, and 4.4278880784 m² is new missing-only support. No walkable floor is exported or installed. Structural bearing and receiver supports remain held.
5. Use existing received/staff, service-door, light-budget, cleaning-cart, stock and interaction infrastructure. The existing service_door.gd uses two 1.13 m leaves and a 2.5 by 2.65 m sweep. A 3.6 m source gate reservation is not an operating 3.6 m door. Root must fit the existing controller/visual/contact/frame contract and verify its sweep without inventing a second transport or interaction system.
6. Gate binding, continuous loaded turns, actual stock access, cupboard/door sweeps, species clearance, privacy/acoustics, normal arrivals, persistence and final game/CRT/target-machine appearance are still open. This is one source gap correction, not completion of briefing or Group 3.

## Bounded source QA

- Protected-plan pass: zero overlap with the 200 proposed crew envelopes, other D03 programme allocations, protected voids or conservative hull outside area. Exact missing-floor duplication is zero.
- Twenty-four old/new material-height/cell cross-sections preserve all original wall surface outside the mouth.
- Twenty derived editable component bounds match their declared source geometry within 0.00005 m. The existing 346-mesh room is imported fresh at its exact original world placement.
- Six native capsule witnesses, 13 receiver/frame/street contacts, six exact rounded-roof profile points, four unchanged street faces, five original/new opening witnesses, two supported hanger contacts and one source-only fixture datum pass.
- Six conservative native-cart/contact/driver stationary proxies pass, with a minimum fixed-surface gap of 0.23 m. They do not establish driven loaded travel, a continuous turn, a gate sweep or species movement.
- Both fresh deterministic native exports repeat byte-identically. Their combined runtime geometry is 240 triangles in 12 meshes. No degenerate triangles, opposed normals, nonfinite vertices or exported walkable floor meshes are present.
- Three actual source-context views were inspected after reopening the retained staff-lift pixels and D03 plan. They show the original dimensional fitted frame, missing short flare, supported task fixture and plan-side relation to the first street. Workbench shadows/illumination and diagnostic floors/cutaway are source review aids, never saved or exported. Final game views and CRT art remain open.

The successor explicitly checks that the four selected native batches contain exactly the four disclosed original semantic wall parts. No unselected native-cell member is discarded. The actual east pier and rounded roof are independently read from the briefing source; recreation geometry is only the deterministic helper pattern, never a substitute room export. The first street camera was too oblique and mostly showed the intervening wall. Its image and log are retained. A camera-only revision gives the final centred doorway view, with unchanged geometry, export hashes and tolerances. The optional shader-cache warning did not prevent the review images or native checks.

## Rebuild

Run prepare_receiver.py and check_local_cart.py with the retained CPython environment and /workspace/shared/astraea_python_deps. Reserve the serialized Blender window. Run /usr/bin/blender --background --factory-startup --threads 2 --python-exit-code 1 --python source/build_source.py -- BRIEFING_RECEIVER.json, then the same command with CREW_STREET_BRIEFING_PATCH.json. Supply only the spec filename after --. Run review_native.py through Blender for the bounded fresh-native checks and three views; run check_compact.py through CPython for compact geometry, repeat hashes and exact original dependencies. No original source, Game file, global manifest or ledger is written by these builders.

## Complete remaining Group 3 obligations

1. Reconcile all 400 existing berth/save keys exactly once, including the installed two-person shared home. C036 stays an explicit root-review migration proposal. The 184 inferred addresses need exact placement/allocation acceptance. Finish the actual crew interiors and shared living/privacy/bathing/changing interfaces, including species-compatible crew homes. A two-place template or source array is not proof that all 400 berths are constructed.
2. Adopt and finish D03 streets, real supports and programme receivers for breakroom, dining, care, briefing, administration, training, briefing, uniforms/lockers and depot. Care010 connects the existing forward quiet pod in source only; the aft pod retains its original inboard entry and its actual service arrangements remain open. Dining's retained cupboard bypass is still an explicit movement hold. Neither this batch nor previous receiver slices complete the district.
3. Integrate the first-starboard and independent port2 seventeen-stop sources using the exact retained cabin binding. Finish seven other retained staff-riser reservations, remaining port2 deck receivers and D18 needs. Preserve all original stop/save identities and the original fore-port D04-D07 blank rule and wet datum 46.2.
4. Finish real clinical support, doors and connections, preserving all ten original junctions. The four-gate sealed-load port2 crossing, first-starboard transfer buffer, dispatch/interlock policy and operational clean/soiled segregation remain held. No sterile flow is claimed.
5. Finish supply, clean/used linen, sealed waste, maintenance access, cart parking and receiving equipment across all public and residential districts. D01 processing/stores, food and wet/dirty returns still need real interfaces. The earlier equipment/header/depot slices cover bounded points rather than a ship-wide network.
6. Root must resolve lawful house-side joins and supported upper landings for Tidal and other residential houses. Preserve the private window verge, finished homes/commons, five retained lift IDs and wet datum. External collars are not finished local house routes.
7. Bind existing stock, door, lift, cart, light and interaction systems. Accept real normal arrivals, species clearances, loaded carts, cupboard/gate sweeps and persistence without a second room, interaction or transport system.
8. Complete real hull/structural bearing and master/reference composition, supported hardware, CRT lighting, acoustic hierarchy and target-hardware acceptance. Bounded source contacts and cloud timings establish none of those final claims.

After parent independently retains this slice, the next useful source candidate is a remaining exact D03 programme receiver such as uniforms/lockers, administration or training. Only lightweight surveying is permitted until that retention gate is confirmed.
