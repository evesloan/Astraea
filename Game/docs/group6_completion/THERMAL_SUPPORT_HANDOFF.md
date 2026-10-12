# Four retained thermal transfer provisions — r004

The additive r004 package follows the r003 entry complements in D08_directory_02 and D08_directory_03. It supplies four anchored masts/parked arms, fixed dock seats/pads/backs/legs, returned grips, source slings, capped control interfaces, towel cradles and mounted task fittings. Tidal stations sit laterally outside the central entries on the original wet landing. Mineral stations sit at the outer edges of the already supported r003 dry bridges. Original rooms, entries, compiler floors and capacity remain intact.

The two immutable r004 natives preserve all 288 r003 context meshes (212 original room meshes plus 76 prior entry meshes) and 32 packed context image resources. The additions have 160 meshes and four physical task lights. Fresh reopen verification checks 23,040 new/context solid pairs, 80 exact original/prior-bridge landing contacts, four crown mounts and 16 carrier-corner water/bed witnesses. The current entry001 room exports stay pinned, and both support exports reproduce byte-identically from reopened natives. The missing later entrance native remains missing and is not reconstructed.

THERMAL_SUPPORT_LOCAL003 passes 104 checks/16 original-player legs. THERMAL_SUPPORT_MAIN004 passes 5,328 focused checks and the same 16 legs in the actual baseline main. These cover four retained entry descents/returns and four dry support approaches/returns with eight declared independent supported starts. The original walker sets facing yaw and uses normal KEY_W; no traversal position/velocity writes occur. The persistent player, original room IDs, all original mesh instances/transforms and four floor owners remain. Dry-support witnesses contain 675 physics samples, max frame displacement below 0.052 m and minimum Y44.8991. Main counts include source shadow/visibility invariants across the existing ship.

Each dry turn capsule proposal is clear at 1.5 m diameter. Each task fitting has a real seat-surface path, reaches an actual body sample and respects the original eight-shadow budget. The held r003 Tidal0 body ray hits its hanging sling at 0.3299 m; independent saved-source ray proof identifies it. R004 adds a real forward cantilever for the fixture. Light checks and collision criteria are unchanged.

Four unoccupied geometry reservations pass 6,672 sampled lift/arm-yaw/carrier-yaw/wet-lower queries against actual source contacts. The conservative carrier box is 0.95×0.67×0.85 m; arm boxes include the crown, knee and new cantilever. Only the actual player, listed future-moving source parts and their fixed pivot connectors are excluded. Dock legs and every original obstacle remain. The initial 0..0.04 m dock departure is not certified. These are shape-query reservations with no production motion, force/load, avatar or cable simulation; dynamic and occupied operation remain held.

The exact future seat targets are (40,44.48,-436.7), (30,44.48,-427.3), (-37.7,44.48,-223.2) and (-30.3,44.48,-207.8). All carrier corners fit the original visual water faces and beds. Nominal water is Y44.9 (source visual top44.92), bed44.3. The arm reaches these targets geometrically after a proposed 0.72 m lift and yaw; the contract names exact joints/part groups. No player or shared controller is edited or activated.

Adopt once after the entry complement and before residency/light-budget setup:

```gdscript
for key in ["D08_directory_02", "D08_directory_03"]:
    var room = ship.get_node("ShipSpace/Districts/ReceivedSections/" + key)
    load("res://scripts/group6_completion/thermal_entries.gd").build(room)
    load("res://scripts/group6_completion/thermal_support.gd").build(room)
```

If thermal_entries.gd is already called, add only thermal_support.gd afterward. Select Group6ThermalSupport_02_r004.glb and Group6ThermalSupport_03_r004.glb through THERMAL_SUPPORT_CONTRACT.json. Restart after changing a selected revision; do not build twice on an existing Group6ThermalSupport root. Preserve all original floors, controller, IDs and budget. Tests register lights late only to inspect the existing main; production adoption belongs before its original configure step. Do not copy this branch's old shared root. See interfaces/THERMAL_TRANSFER_INTERFACE001.json for the shared-owner contract.

Four wide/court saved-source views and four local default/comfort captures are retained. Source studio views add only render-time original compiler context, never resaved/exported. Local ordinary views use actual materials, original player camera, 0.2 ambient, GL Compatibility/retro shader and the shared budget on Mesa llvmpipe. Wider ship/sky is omitted. The Library overview stays version6 (r018/WIDE020), pending parent review.

R002 dry stations/tests remain valid historical dry-scope evidence; their water reach was unfinished. R003 source/first envelope passed but its body-light check was held. The first source receipt-key failure, stopped wrong-node main startup and first ray diagnostic error remain. Corrected completed logs have no engine/script errors; EGL/V-Sync setup warnings remain visible. Occupied mount/support/dock release, actual hoist/cable motion and forces, water/AFK/slide integration, thermal/gravity/species/chair/engineering, whole-main graphics and final art remain unaccepted. Group 6 is not accepted as a whole.
