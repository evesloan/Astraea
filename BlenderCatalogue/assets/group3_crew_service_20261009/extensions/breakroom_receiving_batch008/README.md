# Group 3, batch 008: Custodian breakroom staff receiver

This is a frozen, source-only, bounded receiver proposal for the existing D03 Custodian breakroom. It contains three editable Blender sources, deterministic builders and three compact exports. It does not install a room, door, platform, floor or new identity. Group 3 remains unfinished.

## What was actually missing

The retained received section for programme `D03_directory_02` is placed at `[8,12,-466]`. Its physical outer wall is at X48, with an outer face at X48.1. The retained folded roof reaches X48, with edge underside Y15.25 and edge top Y15.45. The separate platform metadata's X50.2 receiver is the platform clear port, not the received room wall. The platform jamb's outer face is X50.02. The genuine missing enclosure is therefore 1.92 m long. The original room, furniture, roof, main inboard portal `[8,12,-432]`, programme and all save/berth identities are preserved.

## Three bounded assets

- `AST-STF-G3-009`: Eight missing collar components. Two lower wall panels, two gently graded upper panels, two cart-protection strips, a 0.1 m folded-roof edge nib and a graded roof transition. The clear mouth is centred at Z−420. The side boundaries remain Z−421.8 and Z−418.2. The bumper faces project 0.03 m into that gross width. The roof transitions from the real received edge to the existing platform underside Y15.2. The collar already has actual compiled D03 floor beneath it.
- `AST-STF-G3-010`: A subset of exactly 32 retained `AST-STF-010` branch components. Twenty-three are geometrically unchanged. Eight horizontal wall/protection components stop at the first street's outer wall X55.06, and one cap stops at the first street's roof edge X55.2. Every original semantic component and original native AABB is explicitly retained in the spec. The existing `CRW_TASK_LIGHT_DATUM_150` remains at `[52.7,15.03,-420]` with its original metadata and original housing/hangers. No full staff platform is adopted.
- `AST-STF-G3-011`: A separately held two-mesh successor for the first crew street's west wall. It removes only the turn-bay mouth, Z−422.5 through Z−417.5, Y12 through Y15.2. Four retained wall pieces are batched back into the exact two old runtime names. All 2,797 other original first-street native meshes remain unchanged.

`BREAKROOM_MISSING_SUPPORT_PROPOSAL.json` contains only 5.6816 m² of additional support after subtracting both actual compiled D03 support and the frozen first-street floor proposal. The proposed slab datum is Y12, thickness 0.24 m. Floor polygons are never exported as walkable geometry by this batch. Physical beam/bearing acceptance remains open.

## Exact future adoption contract

1. Preserve the original received breakroom export and translation. Keep its main inboard portal and source furniture. Use the pinned source and native hashes in `source/SOURCE_DEPENDENCIES.json`.
2. Adopt the missing collar at world identity, only after receiving the interface and floor/support review. These sources already use world coordinates.
3. Use only the bounded branch subset export. Do not also load the complete `AST-STF-010` or a second copy of these 32 original branch components. Its longitudinal platform wall, floor and main-street fixture are intentionally excluded because the frozen first crew street owns that corridor.
4. If and when the first crew street is adopted, omit exactly `screen_wall_staff_bluegrey_paint_6_-53` and `screen_wall_staff_white_paint_6_-53` from its original export. Substitute `AST-STF-G3-011.glb`, which contains those exact two mesh names. Never load the blocking original wall meshes alongside their successor. Keep all other first-street meshes and original light markers.
5. Compose actual floor support, the previously held first-street proposal and only this batch's missing support. Do not duplicate the original platform's much broader compiler preview floor.
6. The retained gate reservation is `[54,12,-420]`, gross width 3.6 m and nominal clear height 2.65 m. No gate or controller is instanced here. Existing service-door infrastructure, exact frame/sweep/support, light registration, cart/species passage, ordinary arrival, persistence and operational screening are root adoption gates. The 2.65 m gate reservation is not treated as the physical room ceiling.

## Validation and review

- Protected plan screen: zero intersection with the 200 proposed crew envelopes, every other D03 programme allocation, protected voids and conservative hull outside area. The Custodian breakroom's own allocation is the intended receiver owner.
- Twelve exact old/new material-height street cross-sections preserve everything outside the declared opening.
- Thirty-two pinned original native branch bounds and thirty-two derived editable bounds agree with the declared source and clipping envelope within 0.00005 m.
- Ten bounded fresh-native stationary capsule witnesses pass. Sixteen actual receiver face contacts, four preserved street surfaces, three opening witnesses and two hanger/ceiling contacts pass.
- Ten conservative stationary native cart-body/contact/driver proxies pass, with a minimum fixed-surface gap of 1.249 m. These are local poses, not continuous cart travel.
- All three compact GLBs re-export byte-identically. They contain 528 triangles across 13 mesh batches, with finite coordinates, no degenerate triangles and no opposed normals.
- Four actual source-context images were inspected, after reopening the retained staff lift reference and D03 plan. They show the existing room furniture, genuine collar, retained turn bay and bounded first-street mouth. Workbench illumination is diagnostic; actual source task-light integration, CRT presentation, target hardware and final in-engine appearance remain open. Diagnostic floors and the plan cutaway are never saved or exported.

The first native contact review failed because some contact probes were placed at the received wall's rounded bevel corners, at the retained branch's 0.03 m protection offsets, or inside the hanger solid. Its failed receipt and log are retained. Final probes lie on real shared face bands. No geometry or tolerance was changed to conceal that failed review. Original rounded edges and the existing 0.01 m hanger embed remain preserved; this is not a sealed or structural-capacity claim.

## Rebuilding the bounded slice

Run `source/prepare_receiver.py` with the retained CPython environment and `/workspace/shared/astraea_python_deps`. Reserve the serialized Blender window, then run `/usr/bin/blender --background --factory-startup --threads 2 --python source/build_source.py -- BREAKROOM_COLLAR.json`, and repeat for `BREAKROOM_REUSED_BRANCH.json` and `CREW_STREET_BREAKROOM_PATCH.json`. The builder derives its paths from its own batch folder. Run `source/check_local_cart.py` with CPython, and `source/review_native.py` with Blender for the bounded native/context review. The scripts never write to Game or shared manifests. The full catalogue is checked by exact new ID before export. Existing families and original files are never overwritten.

## Complete remaining Group 3 obligations

1. Reconcile all 400 existing berth/save keys exactly once, including the installed two-person shared home. C036 is an explicit root-review migration proposal. The 184 inferred room addresses remain held until exact placement/allocation approval. Complete the actual crew rooms and shared living/privacy/bathing/changing interfaces; a two-place template or source array is not proof that all 400 berths are built.
2. Adopt and finish the D03 crew streets, real supports and programme receivers for breakroom, dining, crew care, recreation, administration, training, briefing, uniforms/lockers and depot. This batch closes only one source enclosure gap; it does not complete the breakroom or D03 district.
3. Integrate the first starboard and independent port2 seventeen-stop sources with their explicitly retained cabin binding. Finish the seven other retained staff-riser reservations, remaining port2 deck receivers and D18 needs. Preserve original stop/save identities and the original fore-port D04–D07 blank rule and wet datum 46.2.
4. Finish actual clinical floor/support and door connections while preserving all ten original clinical junctions. The four-gate sealed-load port2 crossing, first-starboard transfer buffer, dispatch/interlock policy and operational clean/soiled segregation remain held. No sterile flow is claimed.
5. Finish supply, clean linen, used linen, sealed waste, maintenance access, cart parking and receiving equipment across all public and residential districts. D01 processing/stores, food and wet/dirty returns still need their actual interfaces. The four earlier service/depot/header source batches cover bounded receiving points, not the ship-wide network.
6. Root must resolve lawful house-side joins and supported upper landings for Tidal and the other residential houses. Keep the Tidal private window verge, finished homes, commons, five retained stop IDs and wet datum intact. External collars are not a finished local house route.
7. Bind existing stocking, door, lift, cleaning-cart, light and interaction controllers to the adopted sources. Accept actual normal arrivals, species clearances, loaded carts, door/cabinet sweeps and persistent keys without a second room, interaction or transport system.
8. Complete real hull/structural support and the supplied blueprint/material/view composition, supported hardware, CRT lighting, acoustic hierarchy and target-machine acceptance. Source-only contacts and cloud timings establish none of those final claims.

Next useful bounded candidate, after independent retention, is another exact existing D03 programme receiver, starting with the retained crew dining branch near Z−216. Its actual received wall and roof must be surveyed first; the X50.2 metadata is not automatically a room edge.
