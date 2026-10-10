# Group 3, batch 009: Crew dining staff receiver

Frozen, source-only, bounded construction for the existing D03 Crew dining programme. Three editable Blender sources, deterministic builders and compact exports are supplied. The retained room, cupboard, tables, benches, source roof, portals and all occupancy/save identities remain unchanged. Group 3 is unfinished.

## Verified real interfaces

`D03_directory_04` is received at `[8,12,-250]`, yaw zero. Its inboard portal remains `[8,12,-216]`. Its actual outer wall face is X48.1; its folded roof edge is X48, underside Y15.25, top Y15.45. The retained `AST-STF-010` platform clear port is X50.2, with its outer jamb at X50.02. The missing enclosure is 1.92 m long and centred at Z−216. The nominal external gate reservation remains `[54,12,-216]`, gross width 3.6 m, nominal clear height 2.65 m. No gate, controller, stock or occupancy is installed here.

The baseline structural compilation and the additive received-section compilation are both pinned. The received bootstrap actually builds the retained dining interior floor from the additive compilation. Neither compilation supports the exterior collar/branch envelope. After subtracting the frozen first-street proposal, exactly 35.0136 m² of new missing-only floor support remains a held proposal. It is never exported as walkable geometry, and its structural bearing is unaccepted.

## Three small assets

- `AST-STF-G3-012`: Eight missing collar components. Two lower panels, two graded upper panels, two cart-protection strips, a 0.1 m folded-roof nib and the graded roof transition. The gross mouth spans Z−217.8 to Z−214.2. The bumper faces project 0.03 m into that gross width. The physical roof transitions from the actual received section to the existing platform underside Y15.2.
- `AST-STF-G3-013`: Exactly 40 retained platform components. Twenty-nine remain geometrically unchanged. Eight horizontal wall/protection pieces are explicitly clipped at X55.06, the first street's outer wall; three caps stop at X55.2, the first street's roof edge. Every original semantic name and native source AABB is recorded. The retained fixture datum `CRW_TASK_LIGHT_DATUM_151` remains exactly `[52.7,15.03,-216]` with its original housing, hangers and metadata. This is a selected branch subset, not a full platform adoption.
- `AST-STF-G3-014`: Four exact first-street wall mesh successors across the two 8 m cells at the receiver. Four retained semantic parts become four runtime meshes with the original names. Only the mouth Z−218.5 to Z−213.5, Y12 to Y15.2 is removed. All 2,795 other first-street runtime meshes are preserved.

## Exact duplicate-prevention adoption contract

1. Keep the original received dining export at its exact translation. Do not replace its furniture, cupboard, folded roof or inboard portal. All source/native/material/controller dependencies are pinned in `source/SOURCE_DEPENDENCIES.json`.
2. The three new assets already use world coordinates. Their eventual root placement is identity. Receive their exact floors and structural supports before normal use.
3. Use only the bounded 40-component branch subset. Do not also load the full `AST-STF-010` or another copy of these original branch meshes. Its longitudinal wall and broad compiler-preview floor are intentionally excluded. The frozen first street owns that main corridor and its existing roof/light markers.
4. When adopting this successor, omit exactly these four original first-street native meshes: `screen_wall_staff_bluegrey_paint_6_-28`, `screen_wall_staff_bluegrey_paint_6_-27`, `screen_wall_staff_white_paint_6_-28`, and `screen_wall_staff_white_paint_6_-27`. Substitute `AST-STF-G3-014.glb`, which contains those exact names. Keep every other original mesh. Do not load the old blocking wall meshes alongside the successor.
5. Compose the actual baseline/additive interior floors, the previously held first-street support and only `DINING_MISSING_SUPPORT_PROPOSAL.json`. Do not install duplicate platform preview floors or silently expand an existing owner.
6. Existing service-door, staff/received-section, light-budget, cleaning-cart and interaction infrastructure must receive the eventual root bindings. No second room, interaction or transport system is supplied. The gate reservation's 2.65 m nominal height does not redefine the physical ceiling. Door/frame/sweep, continuous loaded-cart travel, cupboard sweep, species access, persistence, lighting and normal arrival remain open.

## Retained cupboard conflict and proposed bypass

The original `AST-STF-007` care cupboard occupies the straight inside approach. Its retained worktop native bounds are approximately X45.6..47.4, Z−216.3325..−215.7125, Y12.893..12.94. A centreline cart/driver pose at `[47.5,12,-216]`, yaw −90 degrees, overlaps retained cupboard components by 0.6210 m². A fresh native capsule witness at that point independently confirms the blockage. Both the failed conservative proxy receipt and the native rejected witness are preserved.

A straight cart pose at `[49,12,-216]` is technically non-overlapping but leaves only 0.0300 m to the cupboard/driver boundary, so it is not used as a proposed approach. The bounded alternative uses northern offset poses `[47.5,12,-217.1]` and `[49,12,-217.1]`, yaw −90 degrees, within the original mouth. Together with eight exterior poses, these ten conservative cart/contact/driver witnesses have zero overlap and explicit support coverage, with a minimum gap of 0.2600 m. The source cupboard stays untouched. These stationary alternatives do not establish a continuous bypass, turning sequence, loaded steering, cupboard-door sweep or operational route. Root must accept the real movement before adopting the connection.

## Bounded source QA

- Protected plan: zero overlap with the 200 proposed crew envelopes, other D03 programme allocations, protected voids and conservative hull outside area.
- Twenty-four exact old/new material-height/cell cross-sections preserve the retained walls outside the opening.
- Forty original native branch bounds and forty derived editable component bounds match the declared original/clipped envelopes within 0.00005 m.
- Ten proposed stationary native capsule points, sixteen receiver face contacts, four unchanged street surface points, three opening witnesses and two retained hanger/ceiling contacts pass. The blocked straight interior witness remains separately rejected.
- Ten proposed stationary conservative native-cart/contact/driver poses pass; the rejected straight inside pose remains in its own failed receipt. No original furniture moves.
- Three fresh native builder exports repeat byte-identically. Total runtime geometry is 624 triangles in 15 mesh batches. No degenerate triangles, opposed normals, nonfinite vertices or exported walkable floor meshes are present.
- Four actual source-context views were inspected after reopening the retained staff lift reference and D03 plan. They show the genuine mouth, unchanged care cupboard and dining benches, retained branch and exact street opening. Workbench light is diagnostic; visible fixture integration, CRT appearance and target-hardware/final game acceptance remain open. Diagnostic floors and the plan cutaway are never saved or exported.

An initial review-script placement error stopped before the native checks; its log is retained. The final corrected review performs all named checks. Geometry was not changed to hide either that script error or the genuine cupboard conflict.

## Rebuild

Run `source/prepare_receiver.py` and `source/check_local_cart.py` with the retained CPython environment and `/workspace/shared/astraea_python_deps`. Reserve the serialized Blender window. Run `/usr/bin/blender --background --factory-startup --threads 2 --python source/build_source.py -- DINING_COLLAR.json`, then repeat for `DINING_REUSED_BRANCH.json` and `CREW_STREET_DINING_PATCH.json`. Run `source/review_native.py` in Blender for the bounded native source/context check and four views. The builder supports exact material-and-cell runtime name overrides so the two cells cannot collapse into a duplicate mesh name. The complete catalogue is checked by exact new ID before export. Scripts never edit Game, shared manifests or original assets.

## Complete remaining Group 3 obligations

1. Reconcile all 400 existing berth/save keys exactly once, including the installed two-person shared home. C036 is an explicit root-review migration proposal. The 184 inferred room addresses remain held until exact placement/allocation approval. Complete the actual crew rooms and shared living/privacy/bathing/changing interfaces; a two-place template or source array is not proof that all 400 berths are built.
2. Adopt and finish the D03 crew streets, real supports and programme receivers for breakroom, dining, crew care, recreation, administration, training, briefing, uniforms/lockers and depot. This batch closes only one source enclosure gap; it does not complete the breakroom or D03 district.
3. Integrate the first starboard and independent port2 seventeen-stop sources with their explicitly retained cabin binding. Finish the seven other retained staff-riser reservations, remaining port2 deck receivers and D18 needs. Preserve original stop/save identities and the original fore-port D04–D07 blank rule and wet datum 46.2.
4. Finish actual clinical floor/support and door connections while preserving all ten original clinical junctions. The four-gate sealed-load port2 crossing, first-starboard transfer buffer, dispatch/interlock policy and operational clean/soiled segregation remain held. No sterile flow is claimed.
5. Finish supply, clean linen, used linen, sealed waste, maintenance access, cart parking and receiving equipment across all public and residential districts. D01 processing/stores, food and wet/dirty returns still need their actual interfaces. The four earlier service/depot/header source batches cover bounded receiving points, not the ship-wide network.
6. Root must resolve lawful house-side joins and supported upper landings for Tidal and the other residential houses. Keep the Tidal private window verge, finished homes, commons, five retained stop IDs and wet datum intact. External collars are not a finished local house route.
7. Bind existing stocking, door, lift, cleaning-cart, light and interaction controllers to the adopted sources. Accept actual normal arrivals, species clearances, loaded carts, door/cabinet sweeps and persistent keys without a second room, interaction or transport system.
8. Complete real hull/structural support and the supplied blueprint/material/view composition, supported hardware, CRT lighting, acoustic hierarchy and target-machine acceptance. Source-only contacts and cloud timings establish none of those final claims.


After independent retention, the next useful source candidate is another verified D03 programme receiving edge, such as crew care. Its unusual X−12 platform metadata must first be checked against actual source walls, roof, interior furniture and protected allocations. No next batch is built or implied here.
