# Group 4 boarding and destination milestone

This additive handoff builds on verified commit `02a25202c1331f7db0ea9834ccec468b12ba5fbb` / tree `2cd9adda88ed2138987c565150e39cd83c6862e7`. The original 185-file checkpoint and the retained baseline remain unchanged. Production `active` and independent `terminal_active` flags are false. No shared root, registry, capacity, room identity, cart, stock or main/checkpoint ref is edited. Group 4 remains unfinished.

## Construction supplied

- **Slotted tram body024:** 31 original car011 meshes remain exact. Eight pocket/post successors contain two narrow sliding-leaf channels on each side; actual octagonal source profiles and exterior UVs are retained. The selected editable source uses 88 closed, touching convex prism cells with no positive volume overlap. Internal cell-interface faces remain explicitly retained; the failed consolidated surface is not selected. Two powered portals reuse original `AST-DOR-003` / `lift_gate.gd`. Original011 is immutable.
- **Five station barrier receivers025 r003:** 40 new receiver meshes. Original powered gates sit 0.32 m inboard of the retained bridges, within the original 2.22 m portal and 2.41 m header. Header shoulders meet the retained source. R003 lowers the footcaps after actual moving-leaf contacts rejected r002; r001/r002 and their failed evidence remain available.
- **Restraint hardware026 r003:** 24 new meshes, four fixed pods and four physical moving clamps on the existing car anchor positions. The empty mechanisms complete 0.139 m closing/return strokes. Open inner faces at X ±0.490 preserve the 0.82 m caster entry; nominal closed faces at ±0.351 leave 1 mm to the original ±0.350 chassis sides. **No physical restraint joint, loaded-cart operation or transport acceptance is supplied.** The single original cart and four products are unchanged.
- **Two terminal branches027:** Paper Moon and Post & Parcels retain their existing 4 m corridors, floor/room owners and portals. New outboard ledges add exactly 8 m² missing-only floor, with guards, positive floor-depth receivers and four rigid original lanterns outside the retained clear route. All 32 lantern mesh payloads, UVs and material graphs are exact copies. No lower-programme support column is introduced.

Native files and GLBs are source candidates. Source IDs024–027 are reserved locally and unregistered. Select only the names in `GROUP4_BOARDING_SAFETY_CANDIDATE.json`; retained failed alternatives and audit re-exports are not runtime choices.

## Tested and reviewed

| Evidence | Result | Practical boundary |
| --- | --- | --- |
| `GEOMETRY_AUDIT.json` | 872 checks | Actual exports, missing-only floor, exact cell/slot separation; no capacity acceptance |
| `NATIVE_AUDIT.json` | 164 checks | 31 exact original car payloads; eight closed-cell successors; four byte-identical fresh native exports; 32 exact original fixture copies |
| `MATERIAL_FIDELITY.json` | 71 checks | All 39 car and 32 fixture material graphs; original packed texture bytes, interpolation and color spaces |
| `SAFETY_RUN003.log` / `Game/artifacts/group4_boarding_safety.json` | 656 checks | 588 actual moving-leaf poses, five independent physical dock fixtures, ordered bridge/barrier/car-door operation, occupied threshold hold, off-dock refusal, pause, four empty clamp close/return strokes |
| `TERMINALS_CONNECTION002.log` / `Game/artifacts/group4_terminals_connection.json` | 2,648 checks | 12 original-player W-input legs on unchanged affc5c8 main plus the terminal child; two supported initial fixtures, zero within-route teleports; 2,626 original room meshes/poses and original cart/product identities preserved |

The terminal test prepares both actual room arrivals before snapshotting, as the existing residency controller initially detaches distant rooms. It uses the original player controller and preserved global lighting budget. The original physical bottle has no fill/consumption property; this test does not invent or certify one. Door/bridge tests use independent stationary source fixtures and a capsule, not a tram trip or ordinary player/cart boarding. The full validation suite is not claimed.

Reviewed wide real-source views are [boarding and hardware](SOURCE_G4_BOARDING_AND_RESTRAINT_CONTEXT002.png) and [furnished Paper Moon approach](SOURCE_G4_PAPERMOON_TERMINAL_CONTEXT001.png), both 1920×1080. `SOURCE_PHOTO_RECEIPT.json` and `SOURCE_VISUAL_REVIEW.json` bind the assembly, poses and limitations. No retained source was hidden, cut or saved for composition. Workbench material averages omit texture detail, game lighting and CRT. The boarding image includes one unsaved original cart mesh as a fit reference, and depicts separately tested open gate poses; runtime opens only the dock side. It is not a loaded operating scene. Four wide context images, including the prior north/forward views, are saved in Library; `LIBRARY_SCREENSHOT_DELIVERY.json` records their identities and byte hashes.

Failed build, manifold, triangulation, runtime and obscured-view attempts remain retained. A PASS string is insufficient if the same run contains engine/script errors. Accepted log hashes and scope are recorded in `ENGINE_TEST_EVIDENCE.json`.

## Integration owner contract

Construction thread `01a11d7f-8ef6-70bc-858d-bdf8deb7000b` owns shared integration. See `INTEGRATION_OWNER_CONTRACT.json` here and the preceding milestone's pit-cut contract. The complete 16-item criteria are preserved in the new local `REMAINING_GROUP4_CHECKLIST.json`; the first checkpoint's record is not rewritten.

1. Cherry-pick both handoff commits in order into an isolated integration worktree. Verify all pinned source bytes and current shared preimages. This only adds files and leaves production inactive. Current `ship.gd` has advanced externally; derive insertion in its actual current structure.
2. The **terminal branches can be adopted independently** of tram pits/north docking. Set only `terminal_active` after current-source checks, and call `load("res://scripts/group4_boarding_safety.gd").build_terminals($ShipSpace/Districts)` once, before the existing global `lighting_budget.configure(self,player)`. New source027 meshes own the 8 m² ledges; do not compile duplicate generic slabs. For an already configured candidate, `register_lights_with_budget` appends the four lights without resetting the existing budget. It is not a second lighting controller.
3. The **boarding assembly depends on** the preceding four bounded pit cuts, exact station/floor adoption and explicit north physical stop decision. `FORE_MIDSHIP` and master catchment −216 remain stable; candidate docking −241 is not adopted here. Never activate both old010 and candidate020 as the same station.
4. Supply the existing base from `group4_completion.gd` and exactly one shared root-owned `AnimatableBody3D` with source024 visual/contact geometry, metadata `source_vehicle_model = "AST-TRM-G4-024_powered_portal_body_r001.glb"`, and the pinned cell contact recipe. Call `group4_boarding_safety.gd.build(parent, base, vehicle)` once after the owned manifest is adopted. `create_candidate_vehicle` is a construction-test factory, not a production motor, cart or transport controller.
5. Connect the existing E/RMB control path to `request_boarding(station)` / `request_secure()`. Docking checks require the exact retained port track/dock, zero yaw and 15 stationary physics frames. Closed portals precede bridge deployment; full deployment precedes portal opening; closed clear portals precede bridge stow. **The root must suppress its single tram motor throughout this sequence.** `unloaded_clear_to_depart()` is unloaded mechanical clearance only, not a loaded or certified departure predicate. Add the real cart-restraint joint, original cart/stock continuity, loaded-motion protection, source capacity and source-exact motors/bogies in the shared owner's existing transport architecture. No root motor or duplicate input stack exists in this package.
6. Resolve the new `_proposal` component identities through the existing persistent world state. Test ordinary player/cart boarding, full travel, crossings/corners/end stops, repeated dock cycles, occupancy/carry, pause/save/load and original consumable continuity. Four empty clamp strokes do not bind a cart. Existing rooms, source variants, capacities and routes remain protected.
7. Group 4 continues to own exterior neighborhood/destination/theater/service connections. Group 8 owns theater/cinema interiors, Group 1 owns homes/courts/shared roots, Group 3 owns staff lanes and Group 7 owns hull/gallery reservations. Request their actual receiving contracts before crossing those source boundaries; no whole-group responsibility is reassigned. Remaining destination routes, NPC finite-time transit, species/emergency stair access, structural/mechanical capacity, ordinary in-game visuals, CRT/performance/hardware and final art remain open.

Reproduction in the existing saved environment:

```sh
source /workspace/astraea-env/activate.sh
python BlenderCatalogue/assets/group4_completion_20261011/boarding_safety_009/audit_geometry.py
blender -b --threads 1 --python BlenderCatalogue/assets/group4_completion_20261011/boarding_safety_009/audit_native.py
blender -b --threads 1 --python BlenderCatalogue/assets/group4_completion_20261011/boarding_safety_009/audit_materials.py
godot --headless --path Game --fixed-fps 60 --script res://tests/validate_group4_boarding_safety.gd
godot --headless --path Game --fixed-fps 60 --script res://tests/validate_group4_terminals_connection.gd
```

Refresh imports first in a clean worktree. Geometry/native audits verify the selected outputs; build recipes can produce retained intermediate/audit files, so use an isolated reproduction directory. No spending, engine switch, credential/permission change, watcher, competing publisher or duplicate worker was introduced.
