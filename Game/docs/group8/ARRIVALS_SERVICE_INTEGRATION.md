# D01 baggage holding and handoff construction

An additive physical suite within existing `D01_directory_01`, in the retained D01/D02 arrivals/fusion shell. Seventeen activity assemblies provide four racks with 36 inactive suitcase silhouettes, packing, dispatch and records surfaces, a staffed handoff hatch, two exact original reading chairs, seven visible fixtures and one operating standard staff door. This does not create inventory, passenger ownership, check-in or custody gameplay. Original arrivals architecture/reception, sealed machinery, visitor lift, ceremonial stair, protected D02 service screens and opaque D03 cover remain intact.

## Adoption

1. Adopt the Group8 arrivals additions from the handoff checkpoint, preserving originals and earlier attempts. Final editable source: `BlenderCatalogue/assets/group8_arrivals_service_20261011/ArrivalsService_r002.blend` (SHA256 `99e88a36250bfe415e824270a1eed5481ce1f4ee362a66be074bd299b6720e1c`). Final runtime: `Game/assets/models/G8_ARRIVALS_SERVICE_r003.glb` (SHA256 `86e12886a114b8c744b8829bd83dee66f41e7419e470cd0f2414a358a59f3cbd`). Historical native sources are preserved, not recreated or substituted.
2. Apply the supplied scoped ship patch, or add exactly one `load("res://scripts/group8/arrivals_service.gd").build(self)` call after original arrivals construction and before the existing lighting-budget construction. Keep the Crown four-interior and Orchard calls independent; Upper Horizon stays held. Shared root/registry adoption belongs to Group1.
3. The loader creates one new instance of the unchanged `service_door.gd` using original `AST-STF-008`. Its authored persistent ID is `D01_arrivals_g8_baggage_service_001`; it rejects duplicate installation/identity and requires the original programme, reception and lift. Metadata `new_controllers:0` means zero new controller implementations, not zero controller instances. There is no permissions change.
4. Import and run `godot --headless --path Game --fixed-fps 60 --script res://tests/group8/validate_arrivals_service.gd`. The supplied test appends a candidate to the unmodified main scene. After default adoption, replace only its `.build(g8_ship)` call with lookup of `ShipSpace/Districts/Group8ArrivalsService_WIP`, retaining all assertions. Run shared regression and ordinary Game/CRT review separately; keep the Botanical gate enforced.

## Physical interfaces

The suite occupies the existing northwest shell approximately X−53.85..−40, Z−465.85..−448, with a chamfer toward X−40/Z−450, on the original D01 floor Y0. It reuses the existing west/north walls and reception canopy; new roof pieces cover only missing areas at Y3.8..3.98, with precise supports to the retained D02 underside Y5.76. There is no new slab, programme or capacity. The independent audit records only named, measured structural joints, including one 25mm front-wall/north-wainscot junction; no general overlap exemption is granted.

Door datum: (−40,0,−452), yaw +PI/2, opening inward toward−X. Its wall aperture is 2.75m; this is not a 2.4m cart-street or broad-species guarantee. Preserve the original door motion/interaction range. Public handoff lip is Y0.75 and the private work surface Y0.94. Group3 owns any external staff/service connection and controlled transfer; the existing opaque west wall has no new opening. All wider arrivals reception/concourse/check-in/embarkation operations remain open.

## Evidence and criteria

Source PASS: 482 native meshes, 109 runtime batches, 17,756 oriented triangles, exact UVs/embedded textures and 376,924 independent boundary/route/retained-context checks. Position error is at most 0.0153mm; two original chairs retain all 60 meshes, topology, UVs, modifiers, packed materials and rigid poses. Fresh final-native export reproduces the exact runtime SHA256.

Focused candidate PASS on independently materialized current main `bc731d6d6d54bb2595331ee2f4368558d4d24fda`: 12,389 checks, 26 continuous walking legs, 3,144 walk frames and 162.45m; one initial setup placement and zero subsequent teleports. All 2,223 original arrivals node poses, 39 original service-door identities and the visitor lift identity/stops survive. Twenty-nine floor supports, seven named retained contacts, seven mounted source lights with receivers, actual leaf collision, precise RMB/E from both sides, 400 moving-door frames and occupied-sweep refusal pass. Eleven protected current-main files remain byte-identical. Exact test/log/process receipts are retained; neither cart travel nor pressure/species/fire/engineering acceptance is inferred.

The contextual court view is saved in Library as `libfile_d5b54babd6548191a64b3d8693ab8497`; the interior and handoff views remain alongside it in the source package.

Visual source review: wide 1600×900 textured native views show the actual retained court, gallery, reception and new suite. WIDE002 views use explicitly recorded broad documentation fill because source fixture-only WIDE001 views were too dark. This fill is not an architectural fixture-performance claim. No native/export was modified for rendering; ordinary Godot/CRT lighting, shadows/popping and final-art acceptance remain unfinished.

Failed attempts remain immutable: the first roof layout conflicted with an existing canopy; a later check exposed an undeclared north joint; the importer alias and distant moving control focus produced two failed tests; Cycles denoising was unavailable and its slower fallback was stopped. The final source and focused test correct those specific issues without changing originals or relaxing controls/criteria.

Unfinished: default-scene/shared-suite adoption, live check-in/custody/inventory/save and permissions behavior, loaded carts/broad species, controlled staff transfer, powered engineering/pressure/fire and ordinary textured Game/CRT/final-art review. This checkpoint does not accept the whole arrivals destination or Group8.
