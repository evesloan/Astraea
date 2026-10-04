# Whole-ship architectural and autonomous-life coverage

Current species authority: [SPECIES_CANON.md](../SPECIES_CANON.md). Koblins, Mantelids, Humans, Baelins, Munkos and Mindos replace the prior roster. Existing eight habitat profiles are physical room/rest types and legacy implementation identifiers, not eight species. Baelin aquatic homes and Mantelid quiet cocoons must be represented; new demographic and numeric biological parameters remain open.

**Astraea remains a whole 18-deck project. The user approved Composition04’s fitted booth/tea construction language for deeper whole-ship refinement. This is direction approval, not a claim that every room or the whole salon is finished.**

The immediate priority is the massive ship and its mostly autonomous staff and guest lives: homes, daily needs, work, leisure, capacity, social behavior and meaningful facilities. Preserve the SunCorp/player setting and working cleaning, economy and persistence. **New quests, campaign/story progression and detailed gameplay balancing are deferred.**

## Scope and evidence

The companion [whole_ship_coverage.json](whole_ship_coverage.json) contains every one of the **1,462 exact stable IDs**, membership in **33 architectural work packages**, all 18 deck lists, actual production-kind lists, five independent status dimensions, bounded test evidence and the rollout gates. These work packages organize refinement; they do not replace production kinds or create a second room registry.

A single data-only extraction at **1 October 2026, 02:46 UTC** called the existing `register_rooms()` and `register_meal_seats()`. Its data exactly matched the latest retained revision03 registry. Source hashes were stable during extraction. No main scene, geometry, rendering, physics, lifecycle run or benchmark was launched for this ledger. The four latest reference images were visually inspected; their useful relationships are translated below.

Later source edits do not automatically invalidate unchanged geometry. The implementation owner confirms subsequent profile-save recovery and upper-floor incident-height changes leave the reviewed D09 physical modules unchanged. Eight [actual-main profile/incident checks](../../artifacts/profile-restore-mainship-results.json) pass for those affected behaviors. Keep the original review scope and add checks for the changed module and its dependencies. New art/geometry integration needs a focused visual and physical review; it does not justify repeating every unrelated doorway test.

Facility-reservation work was observed entering `guest_life.gd` after the extraction. Until its verified handoff is incorporated, the life/capacity entries below describe the verified baseline and pending acceptance, rather than certifying or dismissing that work in progress.

## The exact ship to finish

| Deck | Existing program | Registered IDs | Guest units / berths | Crew berths |
|---|---|---:|---:|---:|
| D01 | Logistics & shuttle docks | 10 | 0 / 0 | 0 |
| D02 | Engineering & life support | 10 | 0 / 0 | 0 |
| D03 | Crew quarters & operations | 210 | 0 / 0 | 400 |
| D04 | Aquatic & arboreal habitats | 126 | 120 / 150 | 0 |
| D05 | Medical & species care | 10 | 0 / 0 | 0 |
| D06 | The grand botanical atrium | 11 | 0 / 0 | 0 |
| D07 | Sports & active living | 10 | 0 / 0 | 0 |
| D08 | Aquatic recreation & wellness | 10 | 0 / 0 | 0 |
| D09 | Retail promenade | 110 | 0 / 0 | 0 |
| D10 | Grand dining & restaurants | 10 | 0 / 0 | 0 |
| D11 | Theater & culture | 13 | 0 / 0 | 0 |
| D12 | Panoramic gallery & library | 11 | 0 / 0 | 0 |
| D13 | Quiet cocoon residences | 167 | 160 / 260 | 0 |
| D14 | Thermal-reef residences | 246 | 240 / 550 | 0 |
| D15 | Adaptive habitat residences | 186 | 180 / 240 | 0 |
| D16 | Family gardens & skyline | 206 | 200 / 600 | 0 |
| D17 | Premier suites & horizon | 106 | 100 / 200 | 0 |
| D18 | Bridge & navigation | 10 | 0 / 0 | 0 |
| **Total** | **All 18 decks** | **1,462** | **1,000 / 2,000** | **400** |

Guest accommodation remains **300 standard doubles, 300 family triples, 300 specialty singles and 100 specialty doubles**. D03 contains 200 crew-cabin records: 199 doubles and single-berth `C036`, giving 399 autonomous crew places, plus the separate player home `D03_employee_cabin0` for **400 crew berths including the player**. Treatment beds, audience chairs, decorative niches and gallery aliases add no residential berths.

The current registry also records **2,200 guest dining seats, 300 crew dining seats, 3,400 entertainment seats, 40 shared crew break places and 16 dry changing places**. These counts describe different kinds of places, not interchangeable capacity. **239 records have none of those six tracked numeric fields** (including residential berths); missing capacity is unknown, not zero. Even a counted seat does not establish the whole room's simultaneous usable occupancy.

Circulation is tracked separately: sixteen atrium levels D02–D17, four principal terraces, twelve smaller galleries, all eighteen guest/service street systems, five Townline stops per deck, express approaches, cupboards, theater dependencies and panoramic lift structures. They are not invented extra registered rooms. Floor elevations and actual headroom, not nominal registry height, govern every profile.

## Five independent completion questions

| Dimension | Verified or present now | What still earns acceptance |
|---|---|---|
| Architecture in plan and section | Shared public/residential shells, purpose-specific auditorium/atrium work and a shaped D09 checkpoint exist | An identifiable arrival, activity, privacy/view choice and ceiling/threshold decision for each approved profile; actual whole-room player-height evidence |
| Original asset craft | Original beds, tidal rest fixtures, furniture, vegetation, portals and materials exist; selected rest-asset readability has limited visual approval | Fitted, purposeful assemblies with original silhouettes, coherent joins, transitions and credible contact; an isolated attractive asset is insufficient |
| Materials and fixture lighting | The existing low-resolution material, local-light and CRT systems work; room-specific strengths are documented | Coordinated room-specific pattern scales, material roles and visible sources illuminating useful surfaces; no generic green band, unrelated pucks or dark furniture hidden by effects |
| NPC and facility function | Persistent homes, individual needs, meals, work/rest, bounded social/shopping/swimming/show behavior and recent crew/audience repairs | Plausible complete daily lives, family/group coordination, purposeful facility actions and demand/admission/overflow appropriate to each place |
| Physical access and persistence | All-ID historical query evidence, newer D09/crew focused checks and selected real cart/save tests | Relevant current-module routes, contact/poses, loads, interruptions and migrations; no blanket pass from a registry or center-route screen |

No finished-work percentage is calculated from registered room counts. A recorded narrow pass stays narrow; a planned target stays planned.

## Shared construction language and family differences

Use the references for **relationships**, not photographic imitation: the fitted crew berth/storage/task-light assembly; the yacht lounge's grouped seats, coved ceiling and large patterned textile; the art-deco booth's continuous seat/rib/ceiling/fixture rhythm; the grand lobby's legible vertical destinations and principal focus. Preserve original, low-poly, tactile Creature Kitchen-inspired character at the current 640 × 360 world target and existing CRT stack.

Use pale enclosure to make form readable, selected warm wood for fitted pieces, blue-green for recesses/textiles, muted brass for joints and a restrained local accent. Give broad textile/floor patterns, medium wall/ceiling rhythm and small object labels different scales. Lights must belong to shaped visible fixtures and light the table, task, face or route nearby. Review effects off as well as on; neither stronger pixelation nor higher ambient is a remedy for weak composition.

Every profile needs a meaningful plan decision and a meaningful section/threshold decision. Join walls, built-ins, floor contours, ribs/coves and fixtures with real returns, reveals, supports and transition pieces. Protect actual doors, original IDs and bed/seat keys, broad turning areas, cart routes, headroom, structure and all existing voids. Keep components reusable and placements deterministic; variation follows use, body, privacy, view or hull position.

| Family coverage | Authored direction and deliberate difference |
|---|---|
| 300 standard doubles | Offset entry shields both beds; fitted storage/rest edge opens toward a seated recess. Ceiling and bedside fixtures support privacy and use |
| 300 family triples | Three sleeping alcoves around a shared commons; preserve every berth, shared turning room and the privacy of each rest zone. This is not a standard room with an extra bed |
| 300 specialty singles + 100 doubles | Six canonical species guide accommodation requirements; eight legacy habitat/rest types may remain physical variants. Baelin aquatic homes and Mantelid quiet cocoons are binding. No one-to-one legacy mapping is approved. Doubles require paired privacy and simultaneous use; color or copied habitat tags are insufficient |
| 200 crew cabins + one player home | Compact bed/storage/work/overhead assemblies and practical task lights. Preserve the player's existing home/upgrade functions and adapt crew accommodation to actual bodies |
| 18 residential + six family commons + 12 habitat support rooms | Ordinary neighborhoods need sociable and quiet choices; family commons need shared garden clusters; habitat support needs useful adapted interfaces. Do not repeat the same coffee island in all 36 |
| Ten guest dining venues + one crew dining room | Guest rooms gather around a coherent service island/booth/ceiling composition with distinct mineral, damp, banquet and quiet profiles. Crew service is compact and practical. Existing seats and real approaches remain protected |
| 100 small stores + seven large shopping destinations | Keep every real allocation and address. Recessed entrances, angled browsing/display bays and fitted service edges vary by trade; do not move all stores to the atrium or create identical vending-door fronts |
| Grand atrium + 13 botanical rooms/terraces/walks | One botanical/water focal sequence, meaningful sheltered edges and useful open volume. Plants have canopy/shrub/groundcover hierarchy; the nursery is botanical |
| Six social/tea/stillroom destinations + two library/reading rooms | Integrated tea/social gathering differs from screened withdrawal and quiet reading. A continuous booth/rib/cove/light system must organize use and reveal, with distinct privacy choices |
| Five aquatic rooms + one changing room + six sports/movement rooms | Dry/wet transitions and sheltered rest differ from clear play envelopes and spectator bays. Changing stays dry. Functional rectangular court surfaces are compatible with shaped surrounding architecture |
| Seven auditoriums + two gallery access records | Preserve the actual fan/rake/bowl and reserved multilevel volume; compose useful foyer/aisle/stage sections. Gallery aliases share theater seats and do not increase capacity |
| Nine other culture/recreation + three observation + two waiting rooms | Music, games, exhibits, performers' preparation, outlook and care waiting require different activity arrangements, acoustic/privacy sections and fixtures. Use real outlooks or intentional displays |
| Three crew social rooms | Practical fitted commons support forty owned shared break places and home overflow, with real seating/task/clock access |
| Six clinics + three laboratories + nine engineering rooms | Treatment/privacy, research work bays and service spines need distinct fitted architecture and credible staff/visitor actions. Equipment props alone do not establish facility operation |
| Three command + four training/admin + three staff view/archive + 19 service/logistics rooms | Command hierarchy, instruction/work groups, chart tasks, sorting/storage and clean/dirty/service flows determine form. Back-of-house must have a purpose rather than absorb leftover voids |

The JSON retains exact IDs, deck counts, current functional scope and the specific plan, section, asset, lighting and remaining-function decision for all 33 work packages.

## Rollout and approval gates

1. **Protect the whole ship.** Keep the exact inventory and explicit protected interfaces. Record affected modules, IDs and dependencies for each change. This inventory step is complete for the stated snapshot; architectural and life acceptance is not.
2. **Resolve one connected D09 composition.** Finish the salon and its existing 28 m terrace as one integrated arrival, social/tea destination, quieter withdrawal and garden relationship. The fitted Composition04 kit has user direction approval. Expand its joined architecture/material/fixture method into distinct room families, retain focused visual, spatial/physics and behavior/persistence gates, and continue refining the salon’s remaining service-end/privacy/value details.
3. **Compose the whole atrium with four distinct principal terraces.** D06 is botanical cafe/grove; D09 is social retail/transit arrival; D12 is quiet gallery/library with real theater access; D16 is family garden commons with calm residences. Resolve the D02 basin and quieter galleries as part of the same section. Compare D06, D09, D12 looking down and D16 from ordinary player height. Preserve the sixteen levels, nonuniform elevations, existing limited crossings and clear central volume.
4. **Prove different representative rooms and lives.** Cover a standard double, family triple, specialty single and double, dining room, small store, aquatic/changing destination, theater/gallery, crew cabin/social room and technical workplace inside existing allocations. Include different body and hull/inner conditions. Each gets independent architecture/art, physical and autonomous-life/persistence review before its family expands.
5. **Expand in controlled family/deck batches through all 18 decks.** Residential work covers D04 and D13–D17; public destinations cover D05–D12; staff/logistics/engineering cover D01–D03 and D18. Circulation and service access accompany every batch. Manifest exact changed IDs and variants; screen every affected route/support/interface, inspect typical and unusual profiles and preserve old saves. A failed profile pauses that family's expansion, not unrelated accepted work.
6. **Verify the living whole ship, then return to new story work.** Establish essential daily needs, meaningful work/leisure, family/social behavior and sensible admission/overflow across the integrated ship. Combine current-source population evidence, normal first-person tours, representative real loaded-cart/vertical trips, interruptions/reload and the still-missing platform measurements. Record residual limits explicitly instead of calling sampled evidence universal.

Proposed existing proof addresses are `13001` (standard), `16001` (family), `04001` / `04091` (specialty single/double), `D10_dining0`, `R001`, `D08_pool0` / `D08_bath6`, `D11_grand_theater` / `D12_theater_gallery`, `C001` / `D03_crew1` and `D02_engineering0`. These are candidates, not approval; the JSON also lists specialty examples across all eight legacy physical habitat profiles, not canonical species.

Use at least three independent review perspectives at each consequential checkpoint: **architecture/art**, **physical access/space**, and **autonomous life/capacity/persistence**. Reviewers judge integrated main-build evidence. New isolated demos, generated concept art and empty-scene benchmarks cannot substitute for the existing ship.

## Autonomous-life acceptance alongside architecture

| Area | Verified baseline | Remaining acceptance |
|---|---|---|
| Passenger needs | All 2,000 ate, slept and completed dinner in the retained day test; individual needs and homes persist | Intended breakfast/lunch/dinner windows, complete daily routines under load, recovery from delays and varied meaningful leisure |
| Crew needs/work | All 399 autonomous crew ate and slept over 48 hours; 2,298 seated meals; twelve roles across 59 assigned work rooms; arrived training and bounded traces | Three requests per cycle do not prove three completed meals/day. Demonstrate useful work, station access, adequate rest, peer/leisure behavior and realistic service journeys |
| Families and dependents | Permanent party IDs and 300 three-bed units | Shared departures, meals, activities and regrouping; dependent care requires explicit identities/guardians/accompaniment/support data. No ages or childcare service are inferred |
| Habitat support | Eight legacy room/rest profiles and metadata compatibility; six-species migration pending | Independently meaningful eligibility/needs, useful habitat support and adapted crew homes; full bodies, appendages and animated contact still need evidence |
| Capacity | Real meal/break/show reservations and release/reuse exist | Changing place/workstation ownership, pool/sport/shop/clinic/lounge limits, overflow and full arrival/exit behavior; later facility work is pending its own validated handoff |
| Social use | Bounded paired encounters, partner memory and shared-budget cross-level projections | People visibly use the fitted spaces and coordinate groups; a render cap cannot conceal logical crowding |
| Named facilities | Shopping, swimming, watching and bounded generic visits work | Tea/library/music/game/sports/clinic/lab/command/logistics purposes need credible actions, appropriate occupancy and useful service tasks beyond dwell timers |

## Evidence to retain, gaps to close

- **D09 spatial pass:** [revision03 independent review](../../../astraea-panel-review/d09-revision03/review.md) records 110 ordinary/broad room routes, 120 portal/turn screens, 7,990 support samples, eight salon activity approaches, two reachable care stances, two terrace pockets and the protected tram reserve. One real spring-guided loaded-cart main-axis trip retained all three bottles. It does not certify parking inside every bay, all poses, a complete cleanup episode or art quality
- **Crew/changing focused pass:** [356 approach screens and seven selected theater links](../../reviews/crew-route-collision-review.md) pass ordinary/broad clearance and 26,866 support samples. Final movement into occupied furniture, every theater stair/seat route, full audience waves and dynamic cart use remain outside that check
- **Life and persistence:** [crew/audience remediation](../../reviews/guest-lifecycle-remediation.md), [profile import](../../reviews/profile-import-review.md) and the [eight actual-main profile/upper-floor checks](../../artifacts/profile-restore-mainship-results.json) supersede older reports that crew meals, audience ownership or dry changing did not exist. Preserve each test's scope; model seat routes do not prove all physical seats usable
- **Unclosed route evidence:** the earlier [whole-ship spatial snapshot](../../../astraea-panel-review/spatial.json) had 25 broad-route failures. Newer D09 and crew screens resolve particular scopes; reconcile remaining IDs rather than reuse the old failed total or infer a fresh all-ship pass. The JSON keeps the exact historical per-ID results beside newer evidence
- **D09 reserve:** the 825.8 m² guest enclosure sits within the unchanged 3,128 m² allocation. About 2,302.2 m² still needs an actual structural/service/acoustic purpose and access account. Calling it reserve does not finish it; no extra accommodation or speculative business is authorized by that label
- **Whole-ship residual area:** streets, service galleries, buffers, planted edges, structure and voids occupy real space outside room rectangles. Audit their purpose in source and normal views. Do not treat footprint ratios as empty-space percentages, permission to fill valuable openings or a reason to redesign the hull
- **Residential service reach:** current source adds four midship care cupboards per residence deck at X ±59, Z ±20, separately from the older skipped z=0 district loop. The historical long-trip finding no longer proves a missing cupboard. Actual approach, loaded-cart parking/turning, restocking and service reach remain to be verified
- **Theater and vertical life:** 3,400 seat assignments and actual-seat watching are now modeled, but full audience dynamics/show scheduling and all physical connections remain unverified. Panoramic atrium lift towers are still architectural models; timed NPC transfers are not continuously visible all-deck travel
- **Unverified targets:** no new target-platform performance/memory/frame-time evidence, full-room rendered census, complete crowd-load test or universal body/animation certification was obtained here. Existing ordinary movement, query screens and working renderer settings must not be promoted into those claims

Keep these two coverage files synchronized when an approved profile, repaired behavior or bounded review lands. Update the affected IDs and evidence scope, preserve unrelated passes and open limits, and retain the whole 18-deck objective throughout.

## Live rollout checkpoint — 1 October 2026, 04:04 UTC

Three separate helper families now integrate into the existing builder, replacing the prior relevant shell/furnishing chains: accommodation (standard, family, eight legacy physical habitat profiles, crew and additive employee-cabin fittings); guest hospitality (39 rooms covering dining, reading/social, sport and wellness); service/retail (shops, supplies/logistics, engineering, clinical and research). Their original Blender modules and low-resolution materials are source assets. Parse/component screens have passed; current integrated room captures and final affected-route checks are still in progress. Existing registry IDs, accommodations, seat records, nonuniform decks and protected voids remain binding.

The actual main-scene wayfinding check passes 90 physical kiosk consultation positions (five per deck), including 0.65 m body clearance, floor support and screen sightlines. Its native UI produces an actual walking/lift/walking itinerary from current registry routes and avoids the atrium void. Guest consultation is pending lifecycle integration. This is not universal body/habitat route certification.

Newly authorized aquatic work extends the existing pools into a resort waterpark: a scenic assisted-flow inner-tube loop with player free look/AFK riding and clear exits, slides and shared alien-friendly attractions. The D08 allocation/headroom, adjacent decks, dry access and existing pool places are protected. The reference’s multi-storey imagery guides composition; it does not authorize new structural holes. This feature is planned, not already functional.

The production facility model now has 818 authored concurrent-use places with 818 scoped route/loop checks passing. All 24 added residential midship restock positions passed actual-main local access, cupboard-facing detection and refill-with-prop-identity checks. Daily-life follow-through has persistent meal obligations, family coordination and fair finite reservations; full overnight rest after delayed arrivals remains under active correction.

## Six species migration checkpoint

The six-species roster supersedes prior species language throughout the coverage plan. Preserve all room/bed/person/party/incident IDs, counts and current helper progress. Verify Baelin aquatic assignment for passengers and crew, quiet Mantelid cocoons, extremely gruesome molting, special cleaner support, Munko four-arm contact and extreme appetite, and Mindo recognized sentience without invented charging or diet. Koblin large households across adjoining existing units are proposed, not new beds. No demographic split is defined. Legacy rig/profile evidence is not six-species acceptance.
