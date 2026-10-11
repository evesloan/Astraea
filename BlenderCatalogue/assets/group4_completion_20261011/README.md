# Group 4 construction handoff, 11 October 2026

Inactive Group 4 construction package on `handoff/group4-completion-20261011`, based on independently verified main `affc5c807087ff87da29f3642c2d6e418241b896`. No shared ship-root, registry, original asset, capacity, room ID or main/checkpoint ref is changed. Group 4 remains unfinished.

The complete selected continuous port guideway, its receiving module, four retained successor stations, northern fore-midship candidate and its receiving/access-protection modules now form one pinned candidate assembly. The old fore-midship station at −216 remains immutable and held against Paper Moon. Master catchments remain −432, −216, −72, +216 and +432. Proposed physical north docking at −241 requires explicit shared-owner adoption.

New editable source r002 adds **142.12 m² of missing-only floor** across forward, aft and aft-midship annexes, **21 lap receivers and threshold tongues**, and **six opal lenses** fitted to retained end/central station backplates. The retained northern annex adds a separate 356.38 m² source proposal. The source floors and receivers are geometric construction; original-slab capacity, cantilever/steel sizing, primary hull load transfer and vibration remain engineering holds. No new berth, room or passenger allocation is introduced.

The inactive runtime package carries 13 exact source models, 14 source-positioned fixture lights, five distinct bindings to the original `commons_lift.gd` and `AST-CIR-003`, and five adapters for the retained physical bridge component. Bridges start stowed and refuse deployment without shared docking authority. The adapter exposes no new input controller. Vehicle source is preserved and pictured only in a stationary review pose; **no operating tram travel, boarding barrier, powered vehicle door, bogie/clamp behavior, cart restraint or guest transport is supplied or accepted**.

`DESTINATION_CONNECTION_CONTRACT.json` preserves all 161 programme keys and original historical IDs, including null identities. It specifies five supported lower-station/core-mouth approaches through the existing axial openings. It does not invent recovered room IDs or certify terminal destination branches. Group 1 homes/courts, Group 3 staff lanes, Group 7 hull/gallery reservations and Group 8 theater/cinema external links remain distinct shared interfaces.

## Evidence

- Baseline: all **43,483** Game/Blender checkpoint files and **173** listed files across seven frozen Group 4 batches hash-verified. Git transport and the independent GitHub connector agree on retained commit/tree. The older restored checkout at `/workspace/Astraea` remains untouched.
- Source: **4,705** checks, including actual exported floor/pit separation, floor-depth receiving, fixed-sill contact and **4,444 unchanged baseline native/export files**.
- Native: **122** checks; 37 editable meshes, five original packed texture images, closed manifold source and byte-identical fresh native re-export.
- Candidate operation: **109** engine checks with no engine/script errors. Five original lifts complete ten unloaded capsule rides; pause and absent-cabin gate refusal pass. Five bridge deployment/stow, docking-refusal and occupancy cycles pass. These are isolated receiving fixtures, with the proposed pit cuts already applied to fixture floors.
- Core transfer: **86** checks and **38** actual capsule legs, **8,940** floor-contact samples, five independent initial fixtures and zero within-route teleports. Actual current core enclosures plus Paper Moon, Thread & Shell and Orchard source contacts are present. The 0.36 m radius / 1.8 m probe uses a test movement script; it is not the original player or a species/cart acceptance test.
- Visually reviewed: [wide north context](SOURCE_GROUP4_NORTH_CONTEXT_WIDE003.png) and [wide forward receiving context](SOURCE_GROUP4_FORWARD_RECEIVING_WIDE001.png), both 1920×1080 real source assemblies. Neutral Workbench shading uses packed-material average colors. Textures, ordinary game lighting, CRT, exterior whole-ship composition and hardware/final art remain unaccepted. Review assembly changes were never saved into native/exports.

Failed source, engine and visual attempts remain retained. r001 had reversed lower-sill tongue direction; r002 corrects only owned receiving source. Initial runtime collision-policy lookup did not account for Godot node-name sanitization; its nominal test PASS was rejected. Initial transfer fixture winding disagreed with the retained production floor builder; corrected tests pass. The first render lacked available denoiser support and the next port view was obscured by Paper Moon. Neither was silently accepted.

## Integration

The shared owner is construction thread `01a11d7f-8ef6-70bc-858d-bdf8deb7000b`. Use `INTEGRATION_OWNER_CONTRACT.json` and verify its exact shared preimages against the current integration branch before applying anything. Cherry-picking this checkpoint adds only owned files and keeps production inactive.

1. Decide whether to adopt physical north docking −241 while retaining `FORE_MIDSHIP` / master catchment −216 and all original variants.
2. Compile four bounded lift recesses in their named existing floor owners: 2.4 m² each for forward/aft/aft-midship and 17.6 m² central, **24.8 m² total**. Do not cut the four-metre pedestrian axis or a public core sidewall. New annex source meshes own their floors; do not create duplicate generic slabs over them.
3. Recheck actual-main contacts, headroom, protected source snapshots and receiving. Update exact dependency pins only as justified by the real compiler change. Activate the owned candidate manifest after those gates.
4. Insert `load("res://scripts/group4_completion.gd").build($ShipSpace/Districts, false, true)` before `lighting_budget.configure(self,player)`. No original public/staff/aquatic/house lift stop or control timing changes are needed.
5. Bind the shared single moving tram, powered cabin/boarding barriers and root docking authority. Keep the original physical cart, products, control stack and world state. Test ordinary E/RMB boarding, actual-player/cart/stock carry, all doors/interlocks, full guideway travel, pause and persistence before calling it an operating line.
6. Finish terminal destination/theater/neighbourhood/service branches, guest finite-time transit, engineering/species and ordinary in-game/CRT/hardware acceptance. Preserve the complete 16-item checklist; this package does not accept the whole group.

Reproduction uses the existing environment:

```sh
source /workspace/astraea-env/activate.sh
python BlenderCatalogue/assets/group4_completion_20261011/audit_receivers.py
blender -b --threads 1 --python BlenderCatalogue/assets/group4_completion_20261011/audit_native.py
godot --headless --path Game --fixed-fps 60 --script res://tests/validate_group4_completion_candidate.gd
godot --headless --path Game --fixed-fps 60 --script res://tests/validate_group4_core_transfers.gd
```

Refresh imports first in a clean worktree. `ENGINE_TEST_EVIDENCE.json` binds accepted logs/receipts; a printed PASS never overrides an engine error. These scoped checks are not the full `tools/validate.py` suite or actual-main acceptance. No watcher, competing publisher, new credentials, permission change, paid asset, engine switch or additional worker was introduced.
