# Astraea residential production: shared source families and 500-unit rollout

## Current production scope, superseding the initial 26-room pilot below

The full ship schedule is 1,000 guest units. This source production lane covers all 500 source-classified ordinary/family allocations outside D17: 200 standard twins and 300 family triples. The 26-address D13 inset was the first connected reference set, never the overall target.

`RESIDENTIAL_500_PLAN.json` preserves 668 adjacent/opposing-room variation constraints and all 1,300 rest positions: 214 are directly recovered historical coordinates and 1,086 are explicitly proposed where the original coordinates are unknown. Existing D13-13017 and D13-13041 are untouched. `PROTOTYPE_PLAN.json` defines 17 shared geometry/view/handedness combinations from three coordinated architectural profiles. The mass assembly contains 498 new room instances in 18 deck/house sections, with the two existing rooms retained separately.

The final corrected source candidate is `outputs/production_r005`. Revisions r001–r004 and their failure reports are superseded diagnostic evidence. A broad independent surface check found bench/wainscot and bench/bath-return penetrations in r004 that the narrower furniture-only overlap test missed. r005 applies the measured shared-template placement corrections before retention. No bed anchor moves. Fixed shower/door-frame mounting interfaces remain explicit exceptions; closed source geometry is not a door-motion or actual runtime clearance pass.

The receiving Game has not been changed by this source work. Its current builders are eager and have no verified room streaming or disk-persistence service. Runtime adoption must add bounded activation through the existing ship/controller/door/light conventions, receiving support and connected streets across all 18 sections. Source geometry alone is not a finished district.

Every new source instance has explicit prototype-to-unit bed-slot bindings using the full schedule's proposed `:rest:01` identity convention. No second unlinked rest-ID namespace is introduced. Original save IDs remain unknown; proposed IDs are not described as recovered.

The actual shared book meshes are exported separately as `detail_props.glb`, so a later runtime assembly can reproduce the reviewed source rather than silently dropping them. Three room profiles, view variants, two recovered family handed rest layouts and profile palettes are materialized. The extra independently seeded book-count proposal differs from the shared realized prototype in 303 instances and is explicitly deferred in the instance map. It is not claimed as applied per-occupant variation.

The complete 1,000-unit schedule and family matrix are retained under `inputs/`. The 81 luxury replacements and 400 specialty allocations remain distinct production lanes. The candidate six-house D17 assignment is a documented proposal, not an automatically adopted registry. Luxury/royalty/supreme rooms need their own geometry, multilevel access, amenities and actual interior/space outlooks; they are never scaled standard rooms.

Source scripts resolve the retained catalogue from their package location or `ASTRAEA_CATALOGUE_ROOT`; `ASTRAEA_GAME_ROOT` can locate the pinned Game inputs. `build_family.py --plan PROTOTYPE_PLAN.json --revision NEW_REVISION` creates a new source version without overwriting earlier output. `ASTRAEA_PRODUCTION_REVISION` selects that version for detail export and section assembly. Root-relative batch paths and relative Blender library links make the retained source package portable; original absolute paths in historical audit receipts are provenance only.

## Useful result

The recoverable method is three coordinated room-layout families, deliberate asset placement, and a deterministic rule that neighboring doors do not repeat the same layout. The original roughly 600-suite generator has not been recovered. Its October 1–2 reports establish the method; the surviving October 3–4 sources establish the implementation starting point.

The bounded next construction pass is the entire D13 starboard-central neighborhood: 26 addressed existing allocations, comprising 16 standard twins and 10 specialty singles, around the retained D13 commons. Two twins are already installed. All 42 historical bed positions and the 1,000-unit total remain exact. No luxury replacement or species population allocation is silently made.

## What is implemented here

- `source/plan_neighborhood.py` produces `NEIGHBORHOOD_PLAN.json`. It maps every recovered address to its exact existing census envelope, retains the original unknown save-ID status, pins the two existing assemblies, and colors a 34-edge adjacency graph deterministically.
- `source/build_family.py` reuses the two retained authored suite builders in a source-only adapter. It omits their original save/export sections, varies actual shell profiles, sleeping privacy, gathering arrangements, ceilings, woven finishes and placed objects, and emits editable shells, optimized shell GLBs, complete source assemblies and placement contracts into new revision folders.
- Five representative candidates cover the three twin layouts plus two acoustic single-cocoon layouts. `outputs/r002/` contains 13065, 13005, 13077, 13101 and 13125. The initial `r001` is retained as superseded diagnostic output; r002 fixes material-name isolation and export batching.
- `source/verify_source_exports.py` independently decodes actual GLB geometry and transforms. All five r002 shells match evaluated source bounds and triangle totals exactly, retain the correct world-space bed anchors, and use seven to nine static material batches. No room without a supported view candidate contains rear glazing.
- `source/render_samples.py` makes source-review entry views and explicitly labeled plan cutaways. These use neutral Blender review lights. They are not Godot images or evidence of production lighting.

The source generator now includes a small books-to-desk contact correction discovered after r002 was built. A fresh revision is required after the representative visual/contact review, before expansion. Earlier output is not overwritten.

## Direct reusable sources

Catalogue root: `/workspace/shared/astraea-catalogue-continuation-20261002`.

- `assets/residential_suite/source/build_residential_suite.py`: AST-SUI-001, offset wet-room entry, swept living walls, rising ceiling, inward glazing and open twin sleeping zone
- `assets/residential_suite/source/build_twin_retreat_suite.py`: AST-SUI-002, split sleeping alcoves and bifurcated approaches
- `assets/guest_rest`: AST-SLP-001 single rest support; AST-SLP-002 remains a separate unused component and is not substituted for two historical anchors
- `assets/guest_wash`: AST-SAN-001 vanity, AST-SAN-002 toilet, AST-SAN-003 low-threshold shower
- `assets/guest_privacy_door`: AST-DOR-001
- `assets/guest_entry_door`: AST-DOR-002 paired enclosed sliding entry. Its widened derivative is not assumed compatible with the current entry wall.
- `assets/furniture`: AST-FUR-001 bench, AST-FUR-002 reading chair and AST-FUR-003 table
- `assets/residential_arrival`: AST-ARR-001 shared street-ceiling/runner source. A facing room pair must share one corridor segment rather than generate duplicate ceilings, runners and lights.
- Existing shared residential edges AST-RES-001 through 004 remain source candidates for already allocated commons/arrival edges, not extra rooms.

Game integration presently lives in `scripts/residential_suite.gd`. It hard-codes two rooms and a shared source frame; it is not yet an arbitrary-address batch assembler. The existing main ship invokes it once. Future adoption must extend this builder and the existing profile convention, not add a second room registry, controller or world.

## Evidence and preservation

`qa/INPUT_RETENTION.json` records 113 inputs whose SHA-256 hashes matched the independently retained checkpoint. Live GitHub BACKUP_STATUS returned the matching checkpoint-manifest hash, and the publisher heartbeat advanced across three reads. This protects the existing sources, not the newly staged candidate. No source publisher, credentials, permissions or remote branches were changed.

The current census, complete master chapters 4, 5, 6, 8, 21, 25, 27 and 32, current species/luxury overlays, retained suite builders, installed wiring, source manifests and actual saved reference images were inspected. The complete historical source archive and old mass-suite implementation were not found locally. Current retained Git history begins October 2.

Historical method reports supplied by the parent:
- October 1 19:43, `Sentinel_1926444a0e3c8191b709c064ed9d66f0`: three authored layout variants across 600 standard/family suites; neighboring doors avoid repetition
- October 1 23:42, `Sentinel_0ec7475de6dc8191b26563f09792bc29`: coordinated walls, ceilings and floor finishes replacing the generic shell
- October 2 04:25, `Sentinel_88b93f878304819185fc35a3fdb9bfce`: enclosed sliding-door pockets and catalogue furniture/doorway/ceiling components

These reports are historical claims, not current runtime verification.

## Architectural batch scope

Build the rooms and their street as one connected neighborhood. The existing north street occupies X81.95–86.05 and currently ends at Z−53; its commons connection occupies Z−26 to −14. The full north branch extends to Z−90. A supported south branch from the commons at Z+14 through Z+90 is missing. Exact new floor regions need an additive ownership/void review; surviving floor/void polygons must remain unchanged. The deck floor is Y84 and the next datum is Y88.5.

The six inner standard rooms wholly inside the central atrium's longitudinal band may develop actual inward views. Inner rooms reaching beyond Z±64 and all outer rooms receive opaque, composed rear boundaries in this candidate until a meaningful actual view is proven. Do not invent exterior windows through neighboring space or call a 4.1 m access street a grand court.

Standard profiles:
1. Open salon: a shared window-/room-facing bench, writing edge, low privacy threshold and rising ceiling.
2. Twin retreat: two distinct sleeping alcoves, central acoustic spine and bifurcated access, with a shared front salon.
3. Gathering gallery: a facing-chair/table pocket, recessed library/writing edge and folded ceiling threshold separating sleep and gathering.

Specialty singles retain one bed anchor each. The master identifies D13 with quiet-cocoon accommodation and the current canon requires Mantelid quiet cocoons. The two candidates therefore provide hollow acoustic sleeping enclosures and different screened lounge approaches. They do not claim approved Mantelid body dimensions, sleeping poses, functional molting care, environmental simulation or universal-species fit. No Baelin aquatic claim or Mindo charging feature is invented. The exact missing evidence is approved Mantelid body/rest envelopes and specific service/molt-care requirements. Ordinary dry source construction can continue while that fit remains unaccepted.

The 81 luxury units remain replacements within the 1,000-unit ledger: 50 deluxe, 25 premium, five royalty and one supreme, with the multistory and habitat-support requirements intact. The current global luxury IDs/allocation mix are unresolved; this local batch does not allocate or consume them.

## Review, expansion and adoption gate

1. Inspect all five representative entry and plan views. Review three actual layout silhouettes, privacy, usable gathering spaces, meaningful rear boundaries and coordinated finishes. Correct source/contact issues in a fresh revision.
2. Check source/export transforms, exact historical anchors, layer contacts, door pocket/sweep reservations, fixture approaches, route headroom and material roles. Keep two existing rooms byte-for-byte.
3. After representative review, run the same generator for the remaining 24 candidate identities, retaining all graph constraints. Emit explicit per-address profiles, reusable-component transforms and an immutable batch map. Do not make 24 hand-maintained copies.
4. Build both connected streets, shared paired-row ceilings/lighting, commons thresholds, end conditions and restrained neighborhood identifiers as one additive section package. Reuse the existing commons lift, stairs and wayfinding identities. No ceiling or railing is duplicated by facing room instances.
5. Retain the candidate independently before any reviewed Game adoption. The new scratch files are not automatically protected by the existing production watcher.
6. At the single reviewed adoption boundary, extend the current builder/profile system. Read GLB extras from `node.get_meta('extras')` as a Dictionary. Canonicalize imported node names with Godot's `validate_node_name()` rule and use a pinned source batch map; do not assert arbitrary direct metadata or uncanonicalized dotted names.
7. Run focused actual Godot normal-arrival, physical player and loaded-cart routes, all door operations and obstruction sweeps, bed/fixture approaches, source-light exits, compiler ownership, adjacent commons/lift and protected-void regressions. Then run the unchanged full registered validation suite and inspect normal player-height/effects-on and effects-off views of the entire neighborhood. Existing test timing is not device FPS.

Stop expansion if a variant needs another unit's allocation, moves an anchor, creates an unsupported floor or view, needs unapproved capacity/tier reassignment, or depends on an invented species requirement. A catalogue count, source render or focused check does not mean the neighborhood is complete.

## Current limits

No Game or Catalogue edit, import, Godot process, new backup run, engine switch, external share or publication has been performed. The source candidates need representative visual/contact review. Actual corridor construction, locks/privacy behavior, storage operation, NPC use, save state, species-body acceptance, local acoustics and final district art remain unfinished.
