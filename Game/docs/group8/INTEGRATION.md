# Additive D18 destination fittings

Use the Group 8 handoff branch derived from `affc5c807087ff87da29f3642c2d6e418241b896`. This branch adds group-owned files only. It does not integrate itself into the default ship.

## Adoption

1. Review `BlenderCatalogue/assets/group8_destinations_20261011/PLAN.json`, native/export/route receipts, failed attempts and photographs. The candidate asset ID `AST-G8-CROWN-001` is unused in the exact baseline catalogue and remains locally reserved; shared catalogue registration belongs to the integration owner.
2. Cherry-pick the Group 8 checkpoint. Do not merge stale baseline changes onto current main or replace an original export. Retain the final native `CrownInteriors_r004.blend`, final runtime `G8_CROWN_INTERIORS_r006.glb`, source scripts and immutable earlier attempts. Only r006 is a runtime input.
3. Check all prerequisite shells: `BridgeEnclosure_WIP`, `CentralCommandCrown_WIP`, `AftCommandCrown_WIP`, `UpperHorizonEnclosure_WIP`. Current common crown replacement and the five received interiors remain intact. Existing Group 1 aft sitting bays and their lanterns are excluded from these fittings.
4. Apply `ship_integration.patch` after inspecting current ship.gd. It adds one loader call immediately after aft sitting lighting and before the existing lighting budget is created. If that context has moved, add the same call once at that boundary. The loader requires original shells and pins its own runtime export. It never creates another door, lift, cart or light-budget controller.
5. Refresh Godot imports, then run `godot --headless --path Game --fixed-fps 60 --script res://tests/group8/validate_crown_interiors.gd`. The provided test appends its candidate after main starts; once integrated, remove that extra test invocation or use the idempotent integration test adaptation described below. Run current-main integration regression through `Game/tools/validate.py` as the integration owner, and visually inspect the original-player route with CRT on/off.

The test intentionally refuses a duplicate installation. For an already integrated scene, change its one candidate call to `ship.get_node("ShipSpace/Districts/Group8CrownInteriors_WIP")` in the owner's test adaptation. All remaining assertions and route criteria stay the same. This avoids a duplicate construction process and tests the actual main installation.

## Physical contract

The new fittings occupy only five existing D18 programme boundaries at floor Y106.5. There are no new slabs, programme addresses, passenger/crew allocations or door identities. Twelve physical task-light fixtures use the existing shared light budget; each light is attached to its actual native exported lens marker. Existing door leaves/controllers and 83 received section keys retain their original identities.

Fifty-nine activity fittings include 29 rigid original chair copies, console banks, status walls, screened voice desks, records/rescue stores and the Upper Horizon reading/orientation edge. The console readouts and rescue stores are passive architectural fittings. They do not claim navigation, permissions, pressure simulation, inventory, evacuation or rescue gameplay.

## Acceptance remains separated

Implemented: editable native construction, optimized runtime export, scoped loader and one-line integration patch.

Tested: consult exact source/native/runtime receipts for each verified criterion. Original source and shared files are unchanged; no count/capacity acceptance is inferred from furniture.

Shared suite blocker: `SHARED_PREFLIGHT_BLOCKERS.json` records five stale Botanical Pair proof pins in the unchanged retained baseline. The shared integration owner must reconcile the actual current files and proof chain before tools/validate.py can validate. Group8 leaves that guard and its files untouched.

Visually reviewed: wide actual native source photographs in retained bridge context. Workbench studio material colours and exact compiler floor triangles are used for clarity. These pictures omit original texture appearance, ordinary Godot lighting, CRT, exterior vista and the rest of the ship. Large unused bridge areas still need further composition/use review.

Unfinished: default-scene integration/current-main full regression; all purpose-specific operational/permission/pressure systems; occupied species/body/pose and loaded-cart use; primary structural engineering; textured lighting/CRT/hardware/final-art acceptance. The remaining arrivals, dining, theater, libraries, service interfaces and safety/escape construction in REQUIREMENTS_AND_OWNERSHIP.md are not completed by this crown package. The lifeboat/embarkation quantity gate and missing historical native sources remain held without invented replacements.
