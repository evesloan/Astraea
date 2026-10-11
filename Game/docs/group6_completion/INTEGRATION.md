# Group 6 aquatic construction successor

This is an **inactive, scoped construction handoff** from retained baseline
`affc5c807087ff87da29f3642c2d6e418241b896`. It must be reviewed and adopted by
the shared integration owner, construction thread `01a11d7f-8ef6-70bc-858d-bdf8deb7000b`.
It does not modify `ship.gd`, floor registries, programme/capacity ledgers,
catalogue registries, master sources, main, or checkpoint references.

The selected source is `BlenderCatalogue/assets/group6_completion_20261011/AquaticCompletion_r010.blend`.
Its runtime export is `Game/assets/models/AquaticCompletion_r010.glb`.
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
   door identities and thirteen new mounted sources. The existing `service_door.gd`
   state machine and player RMB/E interface own motion and input.
5. Refresh imports with the pinned Godot 4.6.3 and run the candidate test. That test
   adds the adapter to the actual main scene and registers its new lights late only
   for testing. After production adoption, remove the test-only adapter call and
   late light registration from the integration verification variant, and verify
   that one instance is present. Do not alter the production light budget.

## Explicit runtime substitutions

Two original continuous slide-runout north wall members are excluded from the
successor exchange and replaced by side jambs around west-offset recovery stair flights. Eight original
exit tread members are retained in the native but excluded from exchange. Twelve
new step blocks create six 0.18 m risers per flight, clear of the original recovery
seats and their mounts; the parked seats and hoists remain unchanged. They remain untouched in the original native and retained in the
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
