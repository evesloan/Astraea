# Grand Pool architecture runtime draft: independent read-only review

Reviewed 2026-10-06, starting 10:36 UTC. This review concerns the initial scratch candidate, not an installed Game change. Parent has begun correcting the draft in response; those later edits are not certified by this report.

## Result

No concrete GDScript compilation/API defect or currently broken source support witness was found by inspection. There are focused-validator false-positive/claim-scope gaps listed below. The builder's use of `ship.model`, automatic `StaticContact`, visual-only AST-BOT handling, player arrival, compiler-floor node ownership, and lighting-budget APIs agrees with the current Game implementations.

No Godot, Blender, importer, renderer, or Git mutation was run. Compilation, actual imported resources, physics/controller behavior, lighting visibility and visual acceptance remain unverified.

Initial reviewed SHA-256 values:

- `grand_pool_architecture.gd`: a764584c22010fc5aaf6ef36cf257fb70be73b659e2d6ff189ec84ca8e4be2b4
- `validate_grand_pool_architecture.gd`: 6aee56d27adfe31445d2a9f6646b98a96d97f523fd5c708834dc482361c0c6b1
- `GRAND_POOL_ARCHITECTURE_RUNTIME.json`: 59301613210d3ec372eaf9362a8afc48729422207be08e2466355645f8164da0

Line references below refer to those initial versions unless a Game implementation is named.

## Required correction or narrower test claim

### 1. Standing budget sample was labelled as seated

`validate_grand_pool_architecture.gd:136–148,158–161` checks a seated sightline but refreshes the budget with the actor still at the standing approach endpoint. For Fore, the actor is approximately (-50.95, 46.2, -442.2); the authored seated eye is (-51.65, 47.44, -442.2).

`Game/scripts/lighting_budget.gd:33,61–62` derives both ranking and visibility samples from `actor.global_position`, so the original `POOL ARCHITECTURE SEAT LIGHT SAMPLE` output did not establish seated budget behavior.

Correction: label this as standing approach coverage, or explicitly supply a separately scoped seated observer. Parent selected the first correction; the changed label was observed during review. Seat-surface selected-light cone/ray reach is additional evidence, not photometric or visual acceptance.

### 2. Support tests did not bind the expected live root or precise support surface

`validate_grand_pool_architecture.gd:96–104` accepts any descendant collider of the old architecture wrapper for the 48 roof-rib witnesses. `probe.owner` identifies a specific rib, but that identity is not tested.

`validate_grand_pool_architecture.gd:105–112` does not use each plant probe's `item` or `support`, or each seat probe's `part`, in its assertions. The only live owner requirement is membership under the entire `GrandPoolWetLoggias` wrapper. A valid ray to the right height on the wrong material/batch passes. More importantly, plant support checks query a stored world point but never establish that the actual imported plant root occupies that point. Plant wrapper transform assertions at lines 85–89 do not check transforms/geometry inside the imported scene.

Correction: map named retained rib, soil and pad source parts to their exact checked export mesh/batch; assert that owner. Bind all 639 probes to vertices of their named live imported plant. Assert the intended probe and seat-approach counts, so empty/truncated arrays cannot silently satisfy the loops and their success report. Parent reports these changes are being made.

Verified exact current hit batches:

- Roof rib -451: `GPM_CELL_-2_-23_7_ASTRAEA_ivory_enamel_concave_static_surface` (16 probes)
- Roof rib -433: `GPM_CELL_-2_-22_7_ASTRAEA_ivory_enamel_concave_static_surface` (16 probes)
- Roof rib -416: `GPM_CELL_-2_-21_7_ASTRAEA_ivory_enamel_concave_static_surface` (16 probes)
- Plant soil: `GPA_loggia_BATCH_004_botanical_soil` (207 probes), `_009_botanical_soil` (216), `_014_botanical_soil` (216)
- Seat pads: `GPA_loggia_BATCH_002_aquatic_clay_sling`, `_007_aquatic_clay_sling`, `_012_aquatic_clay_sling` (one probe each)

This is a validation gap, not evidence of current floating roots or wrong soil contacts. Every present witness checked against actual export triangles succeeds.

### 3. Physical sightline does not test visual-only botanical occlusion

`validate_grand_pool_architecture.gd:137` uses a physics ray. The new botanical instances deliberately have no CollisionObject3D (`grand_pool_architecture.gd:29–34`; `Game/scripts/ship.gd:175–176`). Their rendered leaves/branches therefore cannot block that ray even if they block the view.

Correction: label this specifically as a physical sightline check, keep the independently checked actual-triangle botanical/view evidence in the gate chain, and retain native image acceptance as pending. If claiming a complete imported visual sightline test, intersect the imported render triangles of visual-only geometry as well. The existing source `check_new_seat_approaches003b.py:22–38` already includes all twelve botanical derivatives in its offline view test. No present botanical obstruction was demonstrated by this audit.

## Preservation scope requiring an explicit decision

`prepare_runtime_supports003.py:49` preserves only `D08_grand_pool_wet` and `D10_shared_table_reserved_cap`; initial contract lines 8946–8948 and 10893, and validator lines 44–51, implement that two-record scope. Both records currently match Game exactly, and they cover all 66 direct floor-support witnesses.

That does not by itself establish unchanged records for the whole eight-region pool/market programme. Recommended additive-safe guard: retain the eight existing `GRAND_POOL_SECTION_RUNTIME.json.floor_regions` IDs and compare those eight compiled records individually. Do not pin the entire evolving compiler file or a global owner count; engineering/theater additions are independent. If retaining only two, document that this is rooted-support scope and rely on the required affected access/full-suite gates for the wider preservation claim.

The eight scoped IDs are:

- D08_grand_pool_base
- D08_grand_pool_wet
- D08_grand_pool_core_tongue
- D09_orchard_market_gallery
- D09_orchard_market_core_tongue
- D08_grand_pool_upper_staff
- D09_orchard_market_upper_staff
- D10_shared_table_reserved_cap

## Optional strengthening, not a demonstrated current break

- Lines 65–82 check mesh names, triangle counts, AABBs, texture presence and collision-face counts. They do not compare the actual collision faces with render faces or verify each expected material identity/PBR channel. Current `static_contact_cache.gd:6–24` creates the contact directly from the render mesh, and checked source GLB hashes already protect inputs. Exact imported face/material checks would make stronger importer-regression claims; do not describe count/AABB checks as a full imported source-equivalence proof.
- Existing-model hash checks are covered by required affected validators. The focused architecture contract itself pins the three new architecture GLBs and twelve reused plant GLBs, plus eight retained script/JSON files; it does not independently pin every original programme asset.

## Independently verified without native execution

Actual retained/export bytes and a separate GLB geometry reader were used. No checked source or candidate file was rewritten.

- All 15 model SHA-256 pins match their currently retained inputs.
- All eight preserved script/JSON SHA-256 pins match current Game.
- All 65 architecture mesh names, triangle counts and actual bounds match the candidate contract: 7,776 triangles total.
- All 48 roof-rib short rays hit the actual old GLB at the exact expected position.
- All 62 wet-floor probes fall on the current compiled floor triangles at y=46.2.
- All four cap probes fall on the current compiled cap underside at y=60.76.
- All 639 botanical soil rays hit the new actual GLB soil batches. Maximum target deviation: 0.000001220703119 m.
- Smallest botanical probe distance from its authored soil boundary: 0.219465512 m.
- All three seat-pad rays hit the new actual GLB pads at the exact expected position.
- Both retained floor records equal the current compiled records.

These checks are source/input and geometric-witness evidence. They are not a native import, physics, full-suite, performance or visual pass.
