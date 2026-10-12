# Group 6 aquatic construction successor

This is an **inactive, scoped construction handoff** from retained baseline
`affc5c807087ff87da29f3642c2d6e418241b896`. It must be reviewed and adopted by
the shared integration owner, construction thread `01a11d7f-8ef6-70bc-858d-bdf8deb7000b`.
It does not modify `ship.gd`, floor registries, programme/capacity ledgers,
catalogue registries, master sources, main, or checkpoint references.

The selected source is `BlenderCatalogue/assets/group6_completion_20261011/AquaticCompletion_r019.blend`.
Its runtime export is `Game/assets/models/AquaticCompletion_r019.glb`.
The adapter consumes `Game/data/architecture/group6_completion/FIT_CONTRACT.json`
and `COLLISION_POLICY.json`. The source audit preserves all 1,640 original mesh
definitions/transforms/UVs/material assignments/modifiers and 16 packed image
resources. The immutable original native and original runtime GLB remain unchanged.

## Adoption

1. Compare the protected pins and baseline to the integrator's current branch.
   Resolve overlapping later aquatic work before adopting this adapter.
2. Bring only this handoff's Group 6 paths and uniquely named selected export into
   the integration branch. Historical failed revisions stay as evidence.
3. Immediately after the existing `aquatic_annex_receiving.gd` builder call and
   before the existing light-budget configuration, call:

   ```gdscript
   load("res://scripts/group6_completion/completion.gd").build(
       $ShipSpace/Districts/AquaticRiverSlideAnnex_WIP, self)
   ```

4. The adapter replaces only the annex's visual/contact child in memory. It keeps
   the four compiler-owned floor regions, original programme identity, original
   fourteen light sources, public seam, parent aquatic rooms, lift, stairs,
   Grand Pool, Vesper cascade and all shared builders. It asserts single application
   and an exact export hash. It supplies four moving half-leaves, two privacy
   door identities and nineteen new mounted sources. The existing `service_door.gd`
   state machine and player RMB/E interface own motion and input.
5. Refresh imports with the pinned Godot 4.6.3 and run the candidate test. That test
   adds the adapter to the actual main scene and registers its new lights late only
   for testing. After production adoption, remove the test-only adapter call and
   late light registration from the integration verification variant, and verify
   that one instance is present. Do not alter the production light budget.

## Explicit runtime substitutions

Two original continuous slide-runout north wall members are excluded from the
successor exchange and replaced by side jambs around west-offset recovery stair flights. Eight original
exit tread members are retained in the native but excluded from exchange. The retained sharp and rounded-riser attempts could not be climbed by the original
controller. The selected source supplies two visible continuous recovery ramps,
clear of the original recovery seats and flume ends; the parked seats and hoists
remain unchanged. The ramps themselves own faithful source contact. No controller
or collision-mask change, hidden walk surface or teleport is supplied. They remain untouched in the original native and retained in the
successor native. Two original full-width fixed rinse leaves are similarly retained
but excluded from exchange. Four native half-leaf derivatives split those original
meshes at their centre planes, retain their materials and outer outline, and add
closed interior seam faces. This avoids a full-width leaf sweeping the occupied
changing alcove. These are source derivatives, not a claim that the original static
leaves already operated. The original top landing and island bridge also remain preserved but excluded
from the successor exchange. Their replacements meet the existing ramp ends
without projecting a raised lip into the ascent. The top turn stays inside the
original octagonal boundary and has a guarded 2.4 m deep polygonal landing.
Three original rear-rail and three east-gallery inner-rail members are also retained but excluded from exchange;
the two replacements join at the true rear edge and leave the existing
east-gallery T junction open.
The original intersecting north/east gallery slabs remain preserved but excluded
from exchange. One continuous solid L-shaped surface replaces their union and
closes the 0.4 m seam to the new top landing; exposed guards continue around it.
Fixed controls stay attached to each doorway and can be
targeted from both sides. Saturated obstruction queries fail closed.

## Interfaces requiring coordination

| Interface | Exact retained boundary | Owner/action still required |
|---|---|---|
| Public annex arrival | X54..56, Z238..242, Y44; existing 4 m tongue | Preserve original receiving seam and step-free arrival ramp |
| Universal Changing | Existing D08 parent; historical link X-8..8/Z216/Y44 | Group 1/shared integration and Group 4: audit axial circulation and missing-only floor before a shared link |
| Annex wet service | X100/Y45.45/Z210, original 2.4 m portal | Group 3/4 and shared integration: onward service route, clean/used transfer, carts and permissions |
| Vesper cascade | Receiver X25/Z215/bottom42.8/radius1.4; existing openings, support spine and maintenance shoulder | Group 8/shared integration: restaurant finishing, pump/control/return, splash/acoustic operation; preserve existing stream clearance |
| Living Gifts overlook | Retained D09 and D10 staggered openings and guards, lift 44/52.5/61 | Group 5/8: keep both actual destinations and their protected routes |
| 50 m lane | Grand Pool X-40..-22/Z-457..-407, 18 x 50 m | Preserve exact separate lane; this annex adds no obstruction or replacement lane |
| Thermal target | Two retained D08 directory02 basins, two retained directory03 basins, original annex spa5/spa6 | Six physical source targets, zero new parents; species fit, water/temperature and gravity-adaptive operation remain open |

No reservations, physical sleeping capacity, admission count, room ID or deck datum
are added or changed. Source floor contacts and normal-player checks do not accept
steel sizing, pressure hulls, floor loading, broad species, loaded carts or final art.
The half-leaf fittings provide privacy motion, not reservations, occupation or save state.

## Evidence and limits

`BASELINE_LOCAL_VERIFICATION.json` verifies every managed baseline file;
`BASELINE_REMOTE_VERIFICATION.json` verifies the independent GitHub clone's commit,
tree and checkpoint. Native audits and fresh saved-native export verification are
in the source folder. Candidate logs/receipts distinguish all held attempts.
Source images are actual Blender source views under neutral Workbench studio light;
cutaway hiding is recorded. They do not show textures, ordinary game light, guests,
water motion, the full ship, CRT presentation or target hardware acceptance.

Swimming, buoyancy, current, mounted AFK float interruption/recovery/pause/save,
slide admission/ride physics, operating hoists, gravity adaptation, towel inventory,
water control/conservation, splash/acoustics, NPC reservations, full species and
loaded-cart access, shared service completion, engineering and final art remain
unfinished. **Group 6 is not accepted as a whole.**

The shared ship root changed on concurrent main while this branch was being built.
`CONCURRENT_MAIN_READBACK.json` records the observed main and changed protected
path; the annex builders, player, original exports, master and ledgers matched that
read-only comparison. Adopt the scoped package into the integrator's current root;
do not restore this branch's old `ship.gd`.

## r013 continuation into an already routed r010 handoff

Adopt the next commit as a scoped fast-forward/cherry-pick into the integration
owner's branch. Original r010 source and runtime files are retained; select only
`AquaticCompletion_r015.glb` through the same adapter/contract paths. Restart the
scene after changing the selected source; do not call the adapter twice on an
already constructed `Group6Completion` root. The original privacy persistent IDs,
annex programme identity, compiler floor owners, public/service boundaries and
existing adapter call interface are unchanged.

Six west wall segments, four old overlapping treads and the obstructing west
adaptive handhold are excluded for each retained spa5/spa6. Every original remains
unchanged in the native. Curved source bank joins match the exact protected island
floor-hole polygon. Two visible 1.6 m entry surfaces descend to the original basin
bed, with side rails, suspended quiet canopies/screens, reachable dry support bays
and two additional task fixtures. Original seats, hoists and east handholds remain.
Two retained rinse interiors gain mounted handset/hose/grab/control hardware;
water/temperature/gravity/hoist/inventory operation is still unimplemented.

`FOLLOWUP_MAIN001.json` records 52 focused actual-main checks/24 original-player
legs with four declared independent supported fixture starts. Per-frame witnesses
record continuous movement, no traversal position/velocity writes and no fallback
recovery. The historical r010 121-check/87-leg route is not a fresh full r013 gate.
`THERMAL001.json` separates 1.5 m dry-turn proposal geometry from wheelchair/species
acceptance. `RECOVERY005.json` proves the source-ground recovery route, not swimming
or a slide ride. `LOCAL007.json` retests rinse operation after the hardware changes.
The integrator remains responsible for current-root adoption and broader final
integration gates. No production activation, catalogue registration or shared
registry/root modification occurs in this handoff.

The existing route helper sets facing yaw per leg. Movement uses the original
player and KEY_W; no positional relocation or velocity assignment occurs during
traversal. The raw followup receipt's transform wording refers to translation.

## r015 internal care-bay continuation

Select r015 through the unchanged adapter call. The registered AST-STF-008 gate
asset is reused by hash and original service-door motion. The native contains an
exact source-only reference; it is excluded from the main export to prevent a
second static gate. The new gate adds a scoped label and fail-closed saturated
obstruction query. Two separately exported handwheel meshes use group-local
bounded object motion and the original player RMB/E interface. No player, shared
controller, collision mask, registry or water-state service is modified.

`WATER_CARE_MAIN001.json` passes 59 checks/18 legs with one declared supported
fixture start. It covers gate entry/exit, opening/closing obstruction rejection,
inside/outside controls, both mechanical isolators, the internal X99.2 approach,
and unchanged stock/refreshment stances. The X100 onward route remains untouched.
The initial zero-case raw PASS is HOLD because the engine assertion overrides it;
its interpretation/log/receipt and subsequent targeting failures remain archived.
Use `WATER_SERVICE_INTERFACE.json` for Group1/3/4/8 coordination. Supply and return
flanges end inside the original portal; pumping/filter/pressure/temperature and
cascade hydraulics are not implemented or accepted. Do not advertise their
mechanical handwheel state as a fluid simulation.

Library image identity is unchanged at version4, source r015/WIDE015. Caption:
“Astraea Group 6 r015 — actual saved-source annex overview with internal water-care
bay, service gate and mechanical isolators; neutral studio cutaway, fluid gameplay
unaccepted.” Version3 remains the older r013/WIDE010 view. The gallery/roof/near-wall
cutaway detail is staged only for source review, never saved back into the native.

## r017 river bank/bed continuation

The current adapter selects r017. Two protected original boarding bays have source-authored continuous 1.4 m entry surfaces and separate side rails/cases. `FIT_CONTRACT.json:river_entry_interfaces` gives exact bank/low/bed fixtures. Existing compiler river bed and floor owners remain; no loop replacement or capacity addition. Original tread/rim/handhold source pieces remain native and are narrowly excluded from exchange.

`RIVER_ENTRY001.json` passes ten local checks/four legs; `RIVER_ENTRY_MAIN001.json` passes 13 actual-main checks/four legs with the same original persistent player. Each independent supported dry fixture includes 204 motion samples, max frame displacement <0.060 m and minimum Y44.2994. Normal input/contact performs the paths; no traversal translation/velocity writes. Facing yaw is set by the retained walk helper. This does not accept swimming/current, a tube mount, chair/hoist operation or species/final art.

Native/repeat-export verification, current wide/source cutaway receipt and Library version5/caption are recorded in `MILESTONE.md`, `SAVED_NATIVE_VERIFICATION.json`, `RIVER_VIEW_RECEIPT019.json` and `LIBRARY_PHOTO_DELIVERY.json`. The two blank roof-occluded detail017 images remain honestly failed. No shared controller/registry/root is edited. Earlier broader validation is historical rather than freshly repeated whole-source acceptance.

## Retained Tidal / Mineral source entry package

The annex remains selected r017. After `received_sections.gd.build(ship)` and before `ReceivedRoomResidency.setup`, apply the new package to the two existing rooms:

```gdscript
for key in ["D08_directory_02", "D08_directory_03"]:
    load("res://scripts/group6_completion/thermal_entries.gd").build(
        ship.get_node("ShipSpace/Districts/ReceivedSections/" + key))
```

The adapter pins both current entry001 exports and new r003 additions, checks exact affected source bounds before modifying anything, excludes ten overlapping original bridge/tread meshes per room from runtime visibility/contact, removes only the two false water contacts per room, and adds precise contacts for visible source architecture. Grip ribbons remain visual. Beds, compiler floors, root entrance successor, room identity, furniture/lights, ledgers and capacity remain. No new floor, destination or shared registry entry. Changed water contacts are deliberately visual-only; original water appearance remains. No swimming/AFK/ride/controller acceptance.

The retained reviewed native and exact source001 export provenance are verified from archived ZIPs; listed later entrance-native paths are absent in the baseline. New entry-only exports never replace current entry001 architecture. `thermal_targets/PROVENANCE.json` records this limit; `SAVED_ENTRY_VERIFICATION.json` verifies every affected current runtime bound separately. The source views are reviewed native cutaways with the older entrance geometry explicitly identified.

`THERMAL_TARGET002.json` passes 24 local checks/eight legs. `THERMAL_TARGET_MAIN001.json` passes 30 actual-main checks/eight legs, same persistent player, both rooms and four compiler owners. Each independent supported wet-landing fixture has continuous-motion evidence; no traversal position/velocity writes. Retained facing-yaw assignment is test input. No broad shared-route, chair/hoist/species/temperature/gravity/engineering/final-art acceptance. Failed author001/002, verifier001 and local001 remain.

## r018 inlet clearance and independent float forces

Current annex selection is r018 through the same `completion.gd` call once before light-budget setup. The upper inlet rails end outside the unoccupied float corridor; low recovery grips remain under the hull. Original entry surfaces/floors/rooms/hoists/seats/eight static rings remain. Native source/source assets and historical r017 results remain immutable. Both changed entry routes pass local002 and actual-main002 with the original player.

`buoyant_float.gd` and `river_water_field.gd` provide four-point immersion forces/drag and exact protected river polygon/arc sampling with prescribed game flow. They do not auto-spawn, modify the player or replace original rack rings. `Group6LeisureFloat_r001.glb` is the exact registered AST-AQU-006 export copied into an own namespace. Native/export provenance is independently pinned under `float_physics/PROVENANCE.json`. The test builds conservative per-source-part convex hulls solely for unoccupied force validation; occupant contact decomposition and mass/draft/gravity/species are separate gates.

`FLOAT_FORCE003.json` passes eleven checks, including settling, physical impulse recovery, dry-water separation and a 103.519 m actual-corridor circuit with no runtime transform/velocity writes after initial fixtures. Maximum frame movement 0.010153 m and lateral offset 0.025886 m. This is unoccupied rigid-float acceptance in local actual-annex context, not avatar swimming, AFK interaction, actual-main occupied operation or fluid simulation. `FLOAT_FORCE002` remains HOLD for the original south rail obstruction. Source revision fixes the real rail; the same circuit criteria/forces remain. No controller/mask/hidden-walk change.

The integration owner must supply the original-player water-mode hook, stable float-slot inventory/admission/mount/dock IDs, actual occupied support, interruption/pause/save recovery and slide mode before avatar acceptance. See `WATER_GAMEPLAY_INTERFACE.json`; no competing controller or review copy is introduced. Existing water-care/changing/cascade/thermal/GrandPool interface holds remain. Read-only main observation is `OBSERVED_SHARED_MAIN_R018.json`; only shared ship.gd differs among protected inputs, and owner reconciles adapter calls there. No Group6 main/checkpoint ref write.

Current photo is Library version 6, WIDE020, with exact caption in `LIBRARY_PHOTO_DELIVERY.json`. Detail020 and source view receipts are immutable. Studio source/geometry review does not accept ordinary lighting or final art. `MILESTONE.md` states implemented/tested/reviewed/unfinished distinctions and retains the premature native check scheduling error honestly.

## r019 optical/source and inactive cascade continuation

The current annex adapter selects r019 and OPTICAL_PROFILE001. It retains all14 original fixtures, adds19 fitted sources (including east-side rinse fittings), and uses real exposed receiver/cone/reach profiles. Two west housings move clear of the preserved structural column. No ambient, global budget, original controller, material source or renderer change. The same once-before-budget receiving call applies. No r018 source/image byte is overwritten.

The optional cascade proposal is inactive by default. After r019 receiving and before the budget, the shared owner can review this exact call:

```gdscript
load("res://scripts/group6_completion/cascade_proposal.gd").build(
    $ShipSpace/Districts/AquaticRiverSlideAnnex_WIP)
```

It pins the required r019 and original AST-AQU-015 runtime, adds only new console/control/task meshes on the existing shoulder/hood and uses the original RMB/E interaction contract. It neither replaces a receiver/spine nor installs proposed onward pipe envelopes. Persistent proposal IDs are stable; capacity, rooms and compiler owners remain. `interfaces/CASCADE_BRANCH_ENVELOPES001.json` describes source-fitted clearance envelopes and the unresolved single-spine/channel/pump/support/tie-in ownership. Group8/shared owner chooses adoption; no shared registry/root is mutated here.

`OPTICAL003` passes386 local checks. `SHARED_ROUTE001` passes10,184 actual-main invariants and31 original-player legs, two supported route fixtures, existing routes/return, 19-fitted optics and both mechanical controls. The seven stationary optical samples are separate from traversal. Main includes shadow consistency checks over existing sources; the count is not a new-mesh count. Source references/curtain and proposed envelopes remain checked at112 and210 samples respectively. Source context is retained baseline plus r019/proposal; integration owner's latest shared root reconciliation is still required. Original-player water hook remains required for occupied swimming/AFK/slide/hoist acceptance.

Local ordinary rendering is under `lighting_local004` and `lighting_local005`; earlier001/002 and full-main capture failures remain. Actual-main graphics failed by memory limit; local captures omit wider ship/sky, use the original environment/retro shader and identify software adapter. No target-hardware/final-art or motion/visibility-popping signoff. SOURCE_CASCADE_PROPOSAL002 and its receipt show actual source with render-only original floor/water context. No new user/Library image delivery: version6 is still r018/WIDE020 and its original caption.
