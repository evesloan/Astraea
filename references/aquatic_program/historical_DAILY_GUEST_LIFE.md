# Daily hospitality, households and finite facility use

Species canon update, 1 October 2026: **Koblins, Mantelids, Humans, Baelins, Munkos and Mindos** replace the former roster. See [SPECIES_CANON.md](SPECIES_CANON.md) for exact traits and implementation boundaries. Runtime behavior below still describes legacy rig/profile indices until the six-species migration is verified.

This is an additive extension of `scripts/guest_life.gd`, the production model already owned by the main scene. It does not add a second population, controller, renderer or story system. The 2,000 passenger IDs, 1,000 accommodation IDs, 2,000 passenger bed keys, 400 crew berths and player record remain unchanged.

## Meals and needs

The legacy model has one hospitality timetable across its eight rig/profile indices: passenger breakfast, lunch and dinner, and crew before-shift, mid-shift and after-shift service. It has no distinct biological meal cadence per canonical species. This is current implementation, not biological canon: Munko extreme appetite has no approved numeric cadence or quantity, and Mindo diet, charging, ports and rest are unspecified. Different measured completion times arise from home, work, body-compatible seats, travel and shift offsets.

An intent is captured when its scheduled window starts, including while someone is travelling, eating or waiting for a facility. That intent survives the window and is completed only after the owner reaches an individually reserved physical seat and receives eighteen minutes of service. Each record retains its current due time, maximum completion delay, twelve recent completed-service records and outstanding named periods. A full venue sends the requester to their permanent home rather than creating several overlapping doorway queues.

The previous need model grew hunger by 1.728 units per day but three eighteen-minute services could remove only about 1.026. Normal service therefore could not sustain normal needs. Hunger now grows by 0.00085 per minute and seated service removes 0.055 per minute, with the existing gentle lower bound. There are no penalties, death states or new chores imposed on the player.

If a venue is unavailable for whole days, equivalent obsolete requests are coalesced into the oldest unresolved request of that named period. `meal_coalesced_count`, `missed_windows` and `last_due_key` retain that fact rather than pretending the missed service happened. The queue is at most three named periods; serving today's actual need does not require a punishing backlog of fictional meals. The production audit checks that this fallback is unnecessary during the tested normal run.

A meal completed just after the 72-hour measurement boundary is reported as carryover. Calendar-day completion counts are not presented as proof of exactly three completed meals per person per calendar day. After service, the next already-due meal or the current sleep/rest routine takes priority; finishing a late dinner no longer starts an unrelated leisure trip.

## Canonical accommodation and household requirements

Baelins require aquatic accommodation, including any Baelin crew homes. Mantelids need quiet cocoons. Koblins have large families but no extraordinary needs; adjoining existing three-berth units are a proposed larger-household solution. Preserve each real berth and the unchanged 1,000-unit/2,000-passenger/400-crew ledger. No demographics, ages or species-to-role mapping are prescribed.

## Supported travel parties

By default, the 300 three-berth family accommodations have one guide companion, one companion and one supported traveler. These are configurable fictional travel-party roles, not ages, medical classifications or claims of incapacity. All other accommodation parties remain independent companions. The global `family_support_roles` setting can disable the default. `configure_household_roles(party_id, guide_id, supported_id)` can select different members of the same family accommodation; `(-1, -1)` restores an independent companion party. Explicit configurations persist across import.

The guide's existing schedule offset supplies shared activity windows. A supported party chooses a common destination, gathers at the actual room doorway and follows individual finite routes. Each member has a small departure gap. Lift and tram stages wait for the party, and arrived members wait for the others. The shared corridor portion is followed by each person's own route into their real chair, berth or admitted amenity place. No companion position is copied or teleported, and no meal, swimming, conversation or sleep credit is copied between records.

Meals reserve three free places at one actual four-place dining table. Each person receives their own eighteen-minute service; seats remain held until all three finish. Pending food can interrupt leisure. Home rest and sleep use each person's permanent bed. Social visits get a minimum arrived visit and priority rotates by individual social need rather than always pairing the same first two IDs.

A venue with only two authored visitor places cannot fit a supported trio. Such a party chooses a nearby shared lounge; temporary saturation sends the party home and retains a later retry. Original favorite data remains available. Independent companion parties can visit these smaller shops separately.

Old saves retain their positions, needs, histories and identities. Previously separated members finish an occupied meal or an existing journey and reunite at home before beginning supported outings. This is a transitional migration of an existing independent-party save; it does not claim that already-started historical travel was accompanied. Reconfiguration and reunion state are also saved. Current complete family journeys, group meal waits and reunion state round-trip unchanged.

## Facilities

The host supplies conservative, physically authored concurrent-use slots under `room.facility_slots`. Each slot has a stable ID, position and applicable activities, with optional family compatibility, authored approach, facing, duration and water loop. The model reserves one physical slot key across staff and guests. A browse/work position with combined activities therefore still admits only one owner.

Admission uses retained request order among currently eligible compatible waiters. Sleeping or eating people do not block an otherwise ready visitor. Reservations persist during travel and are rebuilt from the saved owners. Release, reuse, an interrupted visit and current save/import keep ownership unique. No capacity is inferred from room area.

The integrated registry includes sixteen dry changing cubicles, real shop/browse positions, separate water exercise cells and crew station/inspection places. Shopping remains at the reserved display instead of walking into another shopper's place. Swimmers use the reserved cell's loop and dry staging. A legacy swimmer without a slot leaves by the saved dry route before taking a new admitted visit.

Changing and shopping visits use their authored durations. Water visitors finish the actual water exit before releasing. Work defaults to a maximum 120-minute arrived station visit, training to eighteen minutes, and other authored facilities to forty-five minutes unless the host supplies a duration. Food and sleep take priority; overflow and turn-taking use quiet home rest and later retry.

Public amenity/social uses without a matching authored slot category retain their previous behavior. A room's work-only inspection places do not invent or restrict its public visitor capacity. Those remaining public activities are not yet bounded by this admission system. Crew work/training remains arrived time at an authored place, and breaks do not yet run the passenger paired-conversation system; specialist operations and crew conversation are separate future work.

## Evidence and limits

See `reviews/daily-lifecycle-followthrough.md` for the exact final measurements and commands. The new `tests/lifecycle_72h_regression.gd` audits every person for a continuous midnight-to-midnight 72 hours, including each expected named meal, carryover completion, hunger saturation, daily sleep, species totals and missing routes. `tests/household_facility_regression.gd` uses the production registry, routes and GuestLife class for supported travel, own-chair/bed credit, delayed group admission, save/import, independent configuration, actual changing saturation, FIFO reuse and separate water-cell visits.

These model guarantees are separate from visible crowd behavior. At most forty nearby actors are projected. The host's actual-main physical slot sweep checks authored paths and water cells with a 0.65 m static body screen. It does not establish dynamic NPC avoidance, loaded-room crowd throughput, all silhouettes in motion, detailed station animation, swimming physics, clinical practice or certified building occupancy. Existing event/claim ownership, background completion and the cozy player workload remain the same systems.

## Species residue migration

The current source-attributed incident system remains protected. Baelin gooey oily trails require special cleaners; Mantelids are ordinarily low-mess but their molt is extremely gruesome. These traits override a harmless-only species-residue rule. Exact incident timing, treatment, depiction and save migration are pending; no simple old-profile rename establishes them.
