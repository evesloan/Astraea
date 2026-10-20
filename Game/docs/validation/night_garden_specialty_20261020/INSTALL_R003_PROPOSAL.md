# Night Garden D15 exact installation proposal

Proposal only. No shared startup, ship, bootstrap or Central Homes file has been edited. Parent/startup owner applies only after retained checkpoint and safe startup boundary. Use additive script `scripts/night_garden_specialty_d15_20261020_r003.gd`, not the frozen r002 hook script.

## Single coordinated hook
In `scripts/startup_residency_20261020/central_homes_adoption.gd`, append after the existing `star_atlas_d17_receiving_first` build and its construction step:

```gdscript
load("res://scripts/night_garden_specialty_d15_20261020_r003.gd").build(ship)
await ship._construction_step("central_homes/night_garden_specialty_d15_20261020_r003")
```

Startup owner confirmed this boundary. Do not edit the pinned predecessor `scripts/central_homes_adoption.gd` or original ship. If a different successor becomes canonical, reconcile that owner before applying; do not install both hooks. The candidate guards against duplicate root creation.

## Canonical placement and preserved neighbours
- All 30 model vertices and door/light positions already use ship/world coordinates. New district root and home roots stay identity transforms: no extra `(63,84,0)` translation, no extra mirror or yaw.
- Allocations 404–578 step 6, D15 floor Y=93; X envelopes `[69.05,81.95]` and `[86.05,98.95]`. Exact source allocations and all40 reserved rest slots remain unchanged. Indices are disjoint from the existing80 adopted Night Garden units; their root, script, models, source210 rests, transforms and controls are untouched.
- New streets occupy X81.95–86.05 beyond the offset court; commons approaches use X89–92. No new admitted capacity or room ID is invented.
- The real commons path is `ShipSpace/Districts/D13_D14_StarboardCommons_WIP/D15_D17_StarboardHouseUpper_WIP/StarboardHouseUpperArchitecture`. Original AST-COM-003 wrapper stays at `(63,84,0)`. Frozen r002 script omitted the intermediate D13_D14 root; additive r003 fixes that path.
- Only `HC_ProfileWall_D15_-1_4`, `HC_Wainscot_D15_-1_4`, `HC_ProfileWall_D15_1_4`, `HC_Wainscot_D15_1_4` are removed in memory, together with their per-mesh child contacts. Their immutable GLB is not modified. Ten bounded r003 successor pieces preserve the sides/header around the two X89–92 clear throats; the reading edge at X83 is not touched.
- Exact source floor triangles end at Z±14.0. r002 receiving began at±14.08 and left an8cm gap. Additive r003 extends only the first receiving cell to±14.0; court side-wall start remains±14.08. This is a concrete seam repair, not an expansion of room allocations.

## Mandatory preconditions at application time
1. Retention receipt covers frozen r002 and additive r003 delta. Verify PACKAGE_R003 model/native hashes and original AST-COM-003 hash.
2. Reconcile snapshot hashes in R003_HOOK_PRECONDITIONS.json against current startup work. Original central_homes_adoption and80-room definition must still match preserved pins. Never overwrite startup owner's newer file to make the snapshot match.
3. Ensure vertical_commons has built before the hook and all four exact predecessor meshes are present. Source chain is recorded in the precondition file; r003 focused test uses the actual raw commons model in that source-derived hierarchy.
4. Ensure AST-COM-003 remains outside streamed_models/contact-cell bakes. Present source uses per-mesh child contacts, so freeing each wall removes its contacts. If this ownership changes, regenerate/replace exact contact cells as part of the bounded wall mutation; merely removing visual meshes would leave ghost walls.
5. Refresh Godot imports for r002 room models and r003 receiving before normal `load()` runtime use. Raw-GLB focused tests do not verify editor imports.
6. Do not defeat the startup memory repair by eagerly adding all30 detailed interiors. R003_PRIVATE_PARTITION_PROPOSAL.json supplies exact model hashes and per-node eligible partitions:210 architecture/mixed batches remain resident,1909 entirely imported catalogue-component batches are potential private immutable detail. This conservative proposal has not been baked or enabled. Startup owner should use the existing private-shell workflow and exact parity checks, then route room contact_visual through its private helper; receiving remains always resident. All door/controller/light nodes stay active. If this cannot be completed safely at the current boundary, keep the hook unapplied.

## Small remaining integration gate
The r002 physical checks remain126/126, and r003 adds only intended-node/four source-mesh/two seam checks. Main installation still needs its normal acceptance gate with real controllers and commons contacts; no claim of connected controller/cart traversal, operation, CRT presentation or final art acceptance is made. The isolated approach capture was plain/dim and intentionally shown as unfinished. Do not add a global material pass here.
