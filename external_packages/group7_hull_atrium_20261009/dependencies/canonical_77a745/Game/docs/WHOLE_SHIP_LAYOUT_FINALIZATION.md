# Whole-ship layout finalization

Priority confirmed by the owner on 2026-10-05: finish the complete layout across all decks and sections while retaining the architectural vision. This work coordinates the actual production project; it does not replace it with a demonstration scene.

## Reconciled scope

- All 18 decks and 161 directory programmes are cross-referenced to the numbered historical atlas allocations
- All 1000 guest envelopes and 100 retail addresses belong to exactly one of ten geographic vertical coordination groups
- The 200 historical crew-bank envelopes have now been extracted from the visually reviewed D03 blueprint and added to the plans. They do not yet establish the current bed assignment
- The 400 crew total and 81 luxury replacements remain binding requirements. Berth fit, final luxury footprints and appropriate environmental provisions are still unresolved
- Several construction-status records were stale. Thread & Shell, Orchard, Canopy terrace and the upper starboard commons now point to their actual partial construction owners
- Historical implementation claims, allocation rectangles and geometric floor overlap do not certify current rooms or dictate finished walls

## Vertical neighbourhood coordination

Port/starboard pairs at forward, fore-midship, central, aft-midship and aft catchments group adjacent activities across decks. These are geographic planning references, not new marketing names or recovered room IDs. Each programme, guest allocation and retail address appears once.

- port_forward: 19 directory programmes, 99 guest allocations, 6 retail addresses
- port_fore_midship: 13 directory programmes, 71 guest allocations, 16 retail addresses
- port_central: 19 directory programmes, 164 guest allocations, 8 retail addresses
- port_aft_midship: 13 directory programmes, 75 guest allocations, 16 retail addresses
- port_aft: 18 directory programmes, 94 guest allocations, 4 retail addresses
- starboard_forward: 18 directory programmes, 97 guest allocations, 6 retail addresses
- starboard_fore_midship: 13 directory programmes, 72 guest allocations, 16 retail addresses
- starboard_central: 17 directory programmes, 161 guest allocations, 8 retail addresses
- starboard_aft_midship: 13 directory programmes, 73 guest allocations, 16 retail addresses
- starboard_aft: 18 directory programmes, 94 guest allocations, 4 retail addresses

## Initial coordinated reservations

The four forward/aft house courts now follow the actual room banks rather than stopping at the small commons rectangles. Their tapered plan areas are7,664–8,613m² and their upper residential sections remain22.5m high. The port-forward court is cut back from the protected theater volume. The original20x20m commons focuses remain reserved for shaped lobbies, inhabited terraces and local lift/stair access, so this is not a proposal for four uninterrupted slab holes.

Short outward plan rays identify304 source guest allocations with a potential court-facing edge and no other guest allocation in that ray. This is a view opportunity, not304 fitted windows or final privacy acceptance. Guest access should remain on the inward paired-bank corridor side, avoiding a public passage directly across every bedroom window.

All1000guest allocations are now assigned once to twelve residential house groups: six upper-deck houses containing880units, plus six D04 habitat neighbourhoods of20units each. Their membership is a source crosswalk, not recovered room IDs or finished room placement.

Five public lift/stair cores retain the longitudinal catchments, with the central core moved to Z -100 ahead of the atrium while the Townline catchment remains at -72. Both 4.3 m side bypasses, 4 m end connections and the preserved arrivals crosslink are explicit reservations. A one-metre connector must join the central lobby to the existing apron. These are still unbuilt routes.

Independent review rejected the original mixed public/staff core because it did not reach the existing west arrivals service network. Ten separate port/starboard staff-riser and lobby reservations now avoid source accommodation and programme envelopes. The central starboard lobby was shortened to Z -91.8..-80.2 to avoid both Cinema 3 and the public apron. Staff floor-by-floor connections and access logic remain unfinished.

The D01/D02 port-forward service-link plan follows the hull-side route to the existing X -57 street and X -54 interface without crossing the public spine. Its 3.6 m-wide, flat-ended plan buffer clears intervening allocations and the plan hull. The start was shifted inside its lobby bounds; the existing arrival/service owners retain the terminal floor. This is geometric routing evidence, not constructed floor, wall or door acceptance.

The forward great-pool section is being coordinated with Orchard market above and the protected D07 sport and D10 dining allocations. A proposed wet deck at 46.2 m and basin bottom at 44.8 m retain the 44 m lower arrival and avoid lowering a pool through the sports ceiling. A 26.4 m minimum ramp run at 1:12, landings and a local lift must be fitted; the market can overlook the volume through a controlled wet/dry boundary. The proposed 50 × 18 m water area and 26 × 54 m volume are working dimensions, not approved pool engineering or species-access acceptance.

## What must close before calling the layout final

1. Resolved three-dimensional hull and roof clearances
2. All 161 destination shapes, arrivals and service connections
3. 100 retail addresses assigned to designed courts/streets
4. 1000 unit identity/layout crosswalk including 81 luxury replacements
5. Royalty/Supreme multistorey and all-species provision
6. 400 crew berths and service support
7. Guest and service route connectivity including accessible vertical transport
8. Purpose, floor ownership and protection for every multi-level void
9. Normal-play route, visibility and performance acceptance

## Next construction sequence

Resolve the whole hull/occupied-volume envelope and these cross-deck dependencies first. Fit the guest and screened service network, local residential-house sections, luxury replacements and crew homes against the same crosswalk. Only then promote specific reservations to compiler-owned floors, openings and supports, with tests before repeated furnishing. Existing tested architecture and persistent identities remain protected.

## Review artifacts and verification

The reproducible eighteen individual plans and overview are under docs/whole_ship_plans. Their grey hull guide is not a full slab; darker regions show current structural-plan coverage, and outlined rectangles are source programme envelopes. Coloured reservations remain proposals.

tools/compile_whole_ship_layout.py regenerates data/whole_ship_layout.json from hashed source inputs. Ten planning checks cover complete accounting, unique coordination groups, court protection, core/bypass plan fit, the raised-pool section and non-mutating reservations. The existing five vertical-programme tests and all-current-opening guest conflict audit remain required. These planning checks supplement, rather than replace, the Godot regression suite and normal-height architectural review.

## Verification checkpoint

Ten whole-layout checks and five existing vertical-programme checks pass; the all-current-opening audit finds zero guest-envelope conflicts. The unchanged runtime passed all54 Godot regression groups in207.126seconds fixed60 simulation after the programme-ledger reconciliation. Later crew-footprint extraction and planning images are source evidence only and do not alter runtime geometry.

The D03 source footnote places399 beds in C001–C200 and the player separately. The newer shared player home must reassign an existing crew member within400 total. The working plan retains this as an explicit bed-assignment gate rather than silently assuming200 occupied doubles plus another player room.

The earlier20x20m court-only reservations and first planning image describe the arrival focuses, not the expanded landscaped house courts. The expanded proposal is superseding planning work; no protected guest room has been cut or moved.

## Main lift control preparation
An editable eighteen-stop derivative of AST-CIR-003 now has a three-column, six-row panel. Source/export bounds match, and the focused runtime check selects all eighteen unique, nonoverlapping targets in front of the physical backing. The full55-check runtime suite passes in199.4888seconds fixed60. The derivative is not yet installed in a whole-ship shaft, and loaded18-deck travel, staff access and final visual review are not established. Existing two-, three- and five-stop behavior remains covered by regression.

## Central core promoted to construction
The central atrium-threshold reservation is now authored in the main scene, with physical floors, protected shaft/stair openings, seventeen switchbacks and one eighteen-stop lift. The four other public cores remain unbuilt plans. The earlier panel-only checkpoint above is historical; current test and review evidence is in PRIMARY_ATRIUM_CORE_PROGRESS.md. Whole-ship finalization gates remain open.
