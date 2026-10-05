# Whole-ship layout finalization

Priority confirmed by the owner on2026-10-05: finish the complete layout across all decks and sections while retaining the architectural vision. This work coordinates the actual production project; it does not replace it with a demonstration scene.

## Reconciled scope

- All18decks and161directory programmes are cross-referenced to the numbered historical atlas allocations
- All1000guest envelopes and100retail addresses belong to exactly one of ten geographic vertical coordination groups
- The400crew total and81luxury replacements remain binding requirements. Berth fit, final luxury footprints and appropriate environmental provisions are still unresolved
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

Four20x20m residential courts fit within the forward/aft port/starboard commons on D13–D17 without crossing a retained guest allocation. Their22.5m high local sections are intended to contain distinct arrivals, inhabited terraces, stairs and equivalent lift access. Final house footprints, room views and service routes must shape them; these are not cuts through current floors.

Five longitudinal vertical-core reservations align with the established transport catchments nearZ−432,−216,−72,216and432m. Their shaft envelopes avoid the retained programme, guest and retail rectangles in plan. Four-metre side bypass reservations fit the plan hull and programme boundaries. These still require resolved cars, screened guest/service landings, stair provision, pit/headroom and physical route checks. Their presence on a drawing is not a playable travel system.

The forward great-pool section is being coordinated with Orchard market above and the protected D07sport and D10dining allocations. A proposed wet deck at46.2m and basin bottom at44.8m retain the44m lower arrival and avoid lowering a pool through the sports ceiling. A26.4m minimum ramp run at1:12, landings and a local lift must be fitted; the market can overlook the volume through a controlled wet/dry boundary. The proposed50x18m water area and26x54m volume are working dimensions, not approved pool engineering or species-access acceptance.

## What must close before calling the layout final

1. Resolved three-dimensional hull and roof clearances
2. All161 destination shapes, arrivals and service connections
3. 100retail addresses assigned to designed courts/streets
4. 1000unit identity/layout crosswalk including81luxury replacements
5. Royalty/Supreme multistorey and all-species provision
6. 400crew berths and service support
7. Guest and service route connectivity including accessible vertical transport
8. Purpose, floor ownership and protection for every multi-level void
9. Normal-play route, visibility and performance acceptance

## Next construction sequence

Resolve the whole hull/occupied-volume envelope and these cross-deck dependencies first. Fit the guest and screened service network, local residential-house sections, luxury replacements and crew homes against the same crosswalk. Only then promote specific reservations to compiler-owned floors, openings and supports, with tests before repeated furnishing. Existing tested architecture and persistent identities remain protected.

## Review artifacts and verification

The reproducible eighteen individual plans and overview are under docs/whole_ship_plans. Their grey hull guide is not a full slab; darker regions show current structural-plan coverage, and outlined rectangles are source programme envelopes. Coloured reservations remain proposals.

tools/compile_whole_ship_layout.py regenerates data/whole_ship_layout.json from hashed source inputs. Seven planning checks cover complete accounting, unique coordination groups, court protection, core/bypass plan fit, the raised-pool section and non-mutating reservations. The existing five vertical-programme tests and all-current-opening guest conflict audit remain required. These planning checks supplement, rather than replace, the Godot regression suite and normal-height architectural review.
