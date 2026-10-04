# Astraea Grand Voyager — canonical main-build design

Species canon update, 1 October 2026: **Koblins, Mantelids, Humans, Baelins, Munkos and Mindos** replace the former roster. See [SPECIES_CANON.md](SPECIES_CANON.md) for exact traits and implementation boundaries. Runtime behavior below still describes legacy rig/profile indices until the six-species migration is verified.

Baseline 30 September 2026; species canon revised 1 October 2026. Supersedes the earlier fifteen-deck Meridian expansion plan. That earlier implementation is preserved as a development checkpoint, not presented as the current ship.

## Design authority and interpretation

The user's Astraea overview and three design-bible sheets establish the long tapered liner, large central botanical void, repeated habitat modules, paired circulation, separated service network and variety of public destinations. Their deck labels and several printed totals conflict. The approved reconciliation retains those functions in one D01–D18 matrix. The user's explicit written berth counts are authoritative.

SunCorp owns the ship. Astralis Shipworks is the depicted manufacturer. The hospitality facade contrasts warm public comfort with cold, practical staff spaces and the corporation's solar-enclosure program. The player works to pay bills and send money home, while deciding how much comfort and practical equipment they can keep for themselves.

## Binding accommodation ledger

| Class | Units | Berths | Total |
|---|---:|---:|---:|
| Standard | 300 | 2 | 600 |
| Family | 300 | 3 | 900 |
| Specialty single | 300 | 1 | 300 |
| Specialty double | 100 | 2 | 200 |
| Passenger total | 1,000 | | 2,000 |
| Crew, separately | | | 400 |

The crew count includes the player. There are 399 autonomous colleague records and one player roster entry; the private employee berth replaces one ordinary crew berth rather than adding an uncounted 401st bed. Finish tiers and accessibility/environmental tags overlap the categories above and never add phantom rooms or passengers.

## Canonical deck matrix

| Deck | Role | Passenger units / berths |
|---|---|---:|
| 01 | Logistics, cargo, shuttles, provisions, food synthesis, laundry and repair | 0 / 0 |
| 02 | Engineering, two fusion galleries, atmosphere, water recovery, power and oversight | 0 / 0 |
| 03 | Crew quarters, employee cabin, shared breakroom, depot, administration, training and dining | 0 / 0; 400 crew berths |
| 04 | Aquatic and arboreal habitats, terrarium/support commons | 120 / 150 |
| 05 | Medical/species care, recovery, triage, research and pharmacy support | 0 / 0 |
| 06 | Main botanical atrium, gardens, conservatories and nature promenades | 0 / 0 |
| 07 | Full court, adaptive sports, movement, viewing and simulation spaces | 0 / 0 |
| 08 | Aquatic recreation, 50 m pool, thermal baths, wellness and changing support | 0 / 0 |
| 09 | Retail promenade, 100 addressed storefronts, markets, cafes, repair and parcel services | 0 / 0 |
| 10 | Grand dining and specialty venues, 2,200 reserved dining places | 0 / 0 |
| 11 | Three-tier 2,200-seat theater, six 200-seat cinemas, music, galleries and backstage | 0 / 0 |
| 12 | Panoramic observation, library, salons, art and first theater gallery | 0 / 0 |
| 13 | Standard/quiet-cocoon neighborhoods and crown theater gallery | 160 / 260 |
| 14 | Standard, family and thermal/habitat neighborhoods | 240 / 550 |
| 15 | Variable-environment and specialty habitats | 180 / 240 |
| 16 | Family neighborhoods, garden commons and skyline | 200 / 600 |
| 17 | Premier standard suites and inclusive horizon commons | 100 / 200 |
| 18 | Bridge, navigation, communications and upper observation | 0 / 0 |

Exact distribution: D04 has 90 specialty singles and 30 doubles; D13 has 100 standard doubles and 60 specialty singles; D14 has 100 standard doubles, 100 family triples, 30 specialty singles and 10 specialty doubles; D15 has 120 specialty singles and 60 doubles; D16 has 200 family triples; D17 has 100 standard doubles.

## Scale, elevations and circulation

The stationary interior uses metres close to world origin inside a tapered 1,082 m × up-to-240 m envelope. One elevation table gives floors at 0, 6, 12, 16.5, 21, 27, 35.5, 44, 52.5, 61, 69.5, 78, 84, 88.5, 93, 97.5, 102 and 106.5 m. Clear-height allowances, roof/hull depth and local multi-deck voids fit the 118 m reference envelope.

A central street and five Townline catchments reduce long mandatory walks. Main public sidewalks are separate from the service-tram lane. Residential neighborhoods branch from the main spine into local lanes and numbered accommodation. Public destinations have an identifiable entry, activity area, resting edge and care access. Cart turning landings and clear service cupboards are part of the plan.

The botanical atrium spans sixteen visible balcony levels, with actual central floor openings, structural ribs, garden trees, rings, bridges, guards and lift spines. The large theater is a dedicated off-axis volume through the intermediate decks; its slabs are removed from those decks rather than hidden behind a picture. Gallery landings are guarded and connect through explicit continuation points. Residential routes detour around the theater void instead of crossing unsupported floor.

The service tram visibly carries the player's cart with magnetic load restraints. Passenger transit uses timed logical boarding/wait/ride/alighting behind screened embarkation vestibules. Express-deck travel prepares collision geometry before returning control. This is a deliberate game transportation interface, not an assertion that every elevator cabin continuously simulates all eighteen floors.

## Room and material language

Shared structure is consistent: restrained brass hardware, recessed or layered panels, patterned wood/textiles, clear addresses and readable lighting hierarchy. Public rooms are warm; technical and staff rooms are cooler and more institutional. Contrasts are deliberate rather than horror dressing.

Room families carry recognizable functions: curved lounge islands and panoramic glazing; shop counters and parcel displays; books and reading alcoves; garden paths and botanical forms; court markings and physical balls; hollow water basins and a long swimming pool; refectory seating and specialty food halls; raked auditoriums, actual stage/projection geometry and original visual programs; care bays and scientific workstations; reactor and environmental-system landmarks. Standard, family and specialty sleeping spaces use different rest affordances and environmental fittings.

The canonical population comprises six species, including Humans. Koblins are small, troublesome, cheap and often first-time cruisers in large families; Mantelids are reserved insectoids using quiet cocoons, with exceptionally gruesome molting; Baelins require aquatic homes and special cleaners for gooey oily trails; Munkos have four arms and an extreme but respectful appetite; Mindos are synthetic sentient people with recently recognized rights. Exact traits and open design are in SPECIES_CANON.md. The eight existing habitat/rig profiles are legacy physical and implementation categories, not species canon. No species population split is assigned.

Art approval remains a separate gate from functional counts. Current WIP images were shared for user feedback; visual reviewers identified room-warmth, environmental identity, foliage and auditorium-view issues. Do not treat these numeric capacities as proof that the art target has passed.

## Guest and crew life

All 2,000 passengers have persistent unique identities and real assigned bed anchors. Legacy accommodation parties inherit room climates and rest types. New assignment must enforce Baelin aquatic compatibility and Mantelid quiet cocoons. Larger Koblin households may link adjoining existing units as a proposal, without increasing their fixed berths. Mindo diet, power and rest needs are not specified. Needs and a monotonic clock drive travel, reserved meals, rest, amenities and paired conversations. Long trips use finite tram/lift phases. Nearby bodies are a bounded projection of the records, not anonymous rerolled crowd members.

Dining has distinct reservation ownership and credits hunger only after actual arrival and meal progress. Shopping uses browsing, inspection, a small purchase/parcel state and bounded colleague restock work without touching the player's money. Aquatic visits use water anchors and a dry entry/exit; cleaning work appears at the dry exit. Entertainment watching is a light activity model; 3,400 physical theater/cinema chairs do not mean 3,400 fully simulated spectator agents are running simultaneously.

The 400 crew records are separate. Colleagues have home berths, roles and staggered work, break and rest routines. The player is excluded from autonomous movement/rendering. Background care resolves unattended work while preserving claimed partial player jobs.

## Custodial and wage loop

The inherited cart remains a rigid body with a damped handle spring, low center of mass, collisions and real steering lag. Three bottles remain independent physical objects. Loading consumes a full bottle that is actually on the tray; hand-held bottles do not count as available inventory. The legacy cleaning action drains cloth charge and shrinks a guest-attributed incident. New Baelin special-cleaner compatibility and extremely gruesome Mantelid molting are canonical requirements awaiting design and implementation; the old harmless-only residue limit no longer governs these traits. Scattered supplies replenish the parked cart locally. Neither travel nor recovery creates extra product or refunds used cleaner.

A shift pays a predictable base wage and bounded optional care bonus, once per shift ID. Wallet, bank and sent-home totals are separate and conserved. Deposits can be withdrawn. Cabin, breakroom and gear upgrades have visible or mechanical effects. Starting the next shift advances persistent life through a visible yielded overnight transition; input cannot accidentally resume the simulation during that transition. No surprise debt spiral, guest-species penalty or harsh time limit is introduced.

## Rendering, state ownership and loading

Godot Compatibility is retained. A real 640 × 360 world SubViewport provides pixel presentation; the fixed ordered dither and optional CRT pass run before native-resolution HUD/menus. Effects, nearby actor budget and nearby shadow-light budget are adjustable. Local real-time lamps illuminate moving characters, the cart and loose props.

One actual deck and required visible atrium/theater dependencies are built at a time. Static structural collisions remain resident to preserve route safety. Detailed MultiMesh render cells activate with a per-frame budget and unload beyond the working radius; the shared geometry recipes are retained. Main-thread procedural construction is not threaded resource loading. Camera/test activation cannot replace normal arrival validation.

Player, care cart, bottles and balls live outside the streamed deck geometry. Stable IDs, transforms, velocities and consumed supplies are saved. Guest/crew records, room assignments, relationships, incidents, claims and completed-shift ledger persist separately. Saves are atomic, checked, and tied to a layout signature; incompatible development layouts are not silently guessed.

## Verification and honest remaining scope

Independent source, runtime spatial, lifecycle and rendered-image reviews are documented separately. The actual main-scene checks cover door/cart clearances, broad-body dining routes, floor support, guest-made mess targeting, partial cleanup and loose-prop reload, exactly-once wage/completion, and overnight continuity. Focused reruns follow changed geometry.

Current evidence is from a Linux cloud machine using Mesa llvmpipe software rendering. It does not certify native Windows behavior, user GPU frame rate or real-speaker audio quality. The game is not a pressure-vessel certification, detailed gas/medical simulation, full commercial retail economy, full swimming-physics simulation, multiplayer title or completed professional asset-production pipeline. User art approval, the final normal-play walkthrough, moving gallery-lift/cart behavior and final packaging are explicit completion gates.


## Living-atrium revision (1 October 2026)

The original concentric galleries and cross-bridges have been replaced with a true 96 × 128 m slab opening on D02–17. Four wider sculpted leisure terraces and twelve recessed connecting galleries share an eight-node perimeter circulation loop. A branching Blender-authored heliotree, garden island, water basin, shaped planting, glass rails and selected offset walkways form the visible interior. The canonical deck elevations are unchanged. Central residential banks were moved 40 m outboard, preserving room IDs, category counts and berths; their approaches go around the commons footprint. The service tram follows the starboard perimeter instead of crossing the tree. Central express arrival is now at (5.5,0,-72); the five stops are -432,-216,-72,216,432 m.

The main-world directional interior wash is disabled, with low ambient 0.08. Visible bulbs, sconces and plant-light emitters supply real bounded lights. Architectural atrium fixtures remain active across the open volume while near-camera shadow casters retain a separate bounded budget. The visible panoramic lift towers currently provide architectural continuity; express deck travel remains the usable interface, while the theater's gallery platform is a separately verified physical lift.

The old artwork failed independent visual review. New GLB furnishings and the rebuilt atrium remain under actual in-engine review; geometry counts or isolated model renders are not visual acceptance.


### Verified lighting correction

Godot 4.6 Compatibility defaults to 32 positional lights for the entire frame, separately from eight lights per object. The old 65-light atrium set silently displaced nearby task lights. The main build now selects at most 28 view-relevant lights, prioritizing near fixtures and the active deck with stable selection. No broad directional interior wash was restored. Deck-specific light masks, preserved emissive non-shadow-casting meshes and rebased local MultiMesh bounds keep the actual bulbs associated with their geometry. An actual main-game care-alcove frame at 01:02 UTC on 1 October confirms warm local illumination of the stocked cabinet, shaped props, cart and curved surroundings. The wider atrium still awaits its updated visual verdict.

Source: Godot 4.6 ProjectSettings, rendering/limits/opengl/max_renderable_lights and max_lights_per_object: https://docs.godotengine.org/en/4.6/classes/class_projectsettings.html
