# Four retained thermal support stations

This additive package follows the existing r003 entry complements in D08_directory_02 and D08_directory_03. It adds two source-supported stations on each original wet landing: fixed seat/pad/back/legs, returned grips, anchored mast/parked hoist arm/slings, capped control interfaces, small towel cradle and a fitted task housing. These are construction provisions. The seats remain fixed, control marks remain static and the parked hoists do not operate or carry an occupant.

The two new immutable r002 natives preserve all 288 r003 context meshes (212 original room meshes plus 76 prior entry meshes) and 32 packed context image resources. The new exchange has 156 meshes and four source-bound task lights. Fresh reopen verification checks 22,464 new/context solid pairs, 80 actual original-landing foot/anchor witnesses and four real lamp/crown contacts. Both fresh exports repeat byte-identically. The exact current entry001 room export is pinned; its original wet landing bounds match the retained source. The missing later entrance native remains missing and is not reconstructed.

THERMAL_SUPPORT_LOCAL001 passes 84 checks and 16 original-player legs. THERMAL_SUPPORT_MAIN002 passes 5,308 focused checks and the same 16 legs in the actual baseline main. Four old entry descents/returns and four dry support approaches/returns use normal KEY_W input and the original persistent player. There are eight declared independent supported starts and no traversal position/velocity writes; the existing walker sets facing yaw. Original room IDs, every original mesh instance/transform and four floor-owner identities remain. Support-route witnesses contain 320 samples, maximum frame displacement below 0.052 m and minimum Y44.8991. Entry witnesses remain separate in the receipt.

Four 1.5 m diameter source-turn capsule proposals are physically clear against original and added contacts, excluding only the actual player RID. Each fitted lamp has a clear path to its real seat surface, reaches an actual actor sample and respects the existing eight-shadow cap. The main check count includes per-source visibility/shadow invariants across the existing ship source set; it is not a new geometry count or whole-group acceptance.

Adopt after the entry complement and before the existing residency/light-budget setup:

```gdscript
for key in ["D08_directory_02", "D08_directory_03"]:
    var room = ship.get_node("ShipSpace/Districts/ReceivedSections/" + key)
    load("res://scripts/group6_completion/thermal_entries.gd").build(room)
    load("res://scripts/group6_completion/thermal_support.gd").build(room)
```

If the owner already calls thermal_entries.gd, add only thermal_support.gd immediately after it. Each builder applies once. Keep the original controller, all compiler floors, room IDs and budget; do not copy this branch's old shared root. Tests register new lights late only to inspect the original already-built main; production adoption belongs before the original configure step.

Four wide/court saved-source views and four local ordinary default/comfort images are retained. Neutral source views use render-only original compiler context and never resave/export it. Local ordinary images use actual imported materials, original player camera, original 0.2 ambient, original GL Compatibility/retro shader and shared budget on Mesa llvmpipe. Wider ship/sky is omitted. The Library image remains version 6 (r018/WIDE020), pending parent review.

The first source attempt saved only room02 before a receipt-key failure; that native/export/log/source remain incomplete. The first main startup was stopped after identifying the wrong budget node path; its source/log/interpretation remain HOLD. The corrected completed source and main checks pass without engine/script errors. EGL setup warnings in successful source rendering and graphics V-Sync warnings remain visible in logs.

Occupied hoist release/swing/lift/load/seat contacts, swimmer/current/air integration, thermal controls, gravity/species/chair compatibility, engineering, whole-main graphics/hardware and final art remain unaccepted. Group 6 is not accepted as a whole.
