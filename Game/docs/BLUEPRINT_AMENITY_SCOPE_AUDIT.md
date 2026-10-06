# Blueprint amenity scope audit

The ship scope includes every explicit amenity child space and system, not only the 161 directory headings. Current pool/market construction is an installed candidate with passing walking access; it is not a completed waterpark. D17 Royalty lower construction is partial and does not establish VIP pools, lounge or dining. The 31 partial named programmes / 130 without verified owner snapshot cannot measure total remaining ship work.

## Material omissions and unresolved mappings

- VIP secondary pools are explicitly required by the latest user clarification. Their count, deck, membership access and parent house/programme are unresolved. No inspected blueprint label establishes a reliable count.
- The public aquatic sheet explicitly calls for six thermal pools and gravity-adaptive pools. The register retains broad thermal-bath/spring headings, not a pool-level inventory.
- The theater reference explicitly labels royal boxes, orchestra, lower/upper balcony and foyer access, and captions a balcony lounge. These are child requirements or mapping decisions, not extra theater programmes or automatic additional seats.
- Historical theater documentation specifies foyers, stairs, a three-stop gallery lift, ramps, viewing/transfer bays and cinema projector booths. scripts/ship.gd currently does not load an auditorium builder and scripts/auditoriums.gd is absent. The retained historical 3,400-chair and lift proofs do not establish this production build.
- VIP lounge/bar, VIP private dining, family childcare/play and distributed residential alcoves lack a resolved current child-level crosswalk. Some may belong inside existing commons; this audit does not invent duplicate rooms.

## Precedence and conflicts

Authoritative v0.3 governs the corrected 18-deck role map and baseline venue counts. MASTER_CURRENT_APPLICATION.json records later luxury/admission and full-waterpark/slides/floatable-AFK-river decisions. Blueprint functions must be reconciled rather than erased when old deck numbers conflict. Public sports/aquatic/retail/dining/culture/observation become D07/D08/D09/D10/D11/D12. The guest-sheet D12 VIP row cannot be copied into canonical public D12; later D17 luxury decisions do not by themselves assign its shared amenities.

The theater remains 2,200 places (740/740/720) with six 200-place cinemas, not a new seat count inferred from royal boxes. Orchestra is an explicit image label, but an orchestra pit is not established. Dining remains 2,200 total; conflicting printed 2,400 grand-hall/1,200 specialty subtotals are not additive. The botanical atrium is D02–D17, not the image’s narrower 28 m D09–D11 inset.

## Evidence and row inventory

This finite audit records 206 rows: 112 existing directory headings and 94 child/system rows. These layers must not be summed into a claimed ship room count. No additional programme count is asserted. Exact source paths, hashes and unresolved mappings are in data/architecture/AMENITY_SCOPE_AUDIT.json.

- master: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx; chapter 4 table 2; chapters 5, 9, 19, 30 and 33; paragraph indices are zero-based python-docx paragraph positions
- public_sheet: /workspace/shared/astraea-catalogue-continuation-20261002/references/aquatic_program/public_blueprint.png; ASW-GV-03 sheet 3 of 6: deck plans, aquatic inset and capacities
- guest_sheet: /workspace/shared/astraea-recovery-20261005/DesignArchive/References/Uploaded_46/03/3.png; ASW-GV-02 sheet 2 of 6: VIP/premier and family rows
- overview: /workspace/shared/astraea-recovery-20261005/DesignArchive/References/Uploaded_46/02/image(1).png; ASW-GV-01 sheet 1 of 6: deck index, top view, cutaway
- performance: /workspace/shared/astraea-catalogue-continuation-20261002/references/auditorium/theater_reference.png; Theater plan labels 1–6 and captioned foyer / balcony lounge images
- legacy_auditoriums: /workspace/shared/astraea-recovery-20261005/DesignArchive/Historical_Design/Editable_Source/project_docs/AUDITORIUMS.md; Capacity and geometry; Entry care and circulation; Original performance and film program
- current_overlay: docs/master_source/MASTER_CURRENT_APPLICATION.json; latest_decision_overrides: Recreation and sound; chapter_application chapter 19
- user_clarification: User clarification relayed by parent 2026-10-06: secondary pools for VIP members, theater and all sections in blueprint photos; User clarification relayed by parent 2026-10-06: secondary pools for VIP members, theater and all sections in blueprint photos
- current_register: data/programme_ledger.json; destinations
- current_build: scripts/ship.gd; _ready build calls; no auditoriums module loaded
- pool: scripts/grand_pool_section.gd; build; GrandPoolProgramme; Shallow trial water scope
- aquatic: scripts/aquatic_section.gd; build; GentleWatersArrival; ShallowWaterVisual_NoSwimmingYet

## Per item evidence

### AME-001 The living grove
- Type: parent_programme; deck/span: D06; parent: D06_directory_01
- Source: current_register:D06_directory_01; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-002 The waterside grove
- Type: parent_programme; deck/span: D06; parent: D06_directory_09
- Source: current_register:D06_directory_09; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_09; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-003 Cloud conservatory
- Type: parent_programme; deck/span: D06; parent: D06_directory_02
- Source: current_register:D06_directory_02; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-004 Sunset garden cafe
- Type: parent_programme; deck/span: D06; parent: D06_directory_10
- Source: current_register:D06_directory_10; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_10; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-005 Moss sanctuary
- Type: parent_programme; deck/span: D06; parent: D06_directory_03
- Source: current_register:D06_directory_03; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-006 Botanical nursery
- Type: parent_programme; deck/span: D06; parent: D06_directory_04
- Source: current_register:D06_directory_04; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_04; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-007 Canopy terrace
- Type: parent_programme; deck/span: D06; parent: D06_directory_05
- Source: current_register:D06_directory_05; data/reference/directory_allocations.json: atlas page 8
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D06_directory_05; Partial authored architecture with route tests and visual review; full programme and final art unfinished; scripts/canopy_terrace.gd; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-008 Sheltered walk
- Type: parent_programme; deck/span: D06; parent: D06_directory_06
- Source: current_register:D06_directory_06; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-009 Orchard gardens
- Type: parent_programme; deck/span: D06; parent: D06_directory_07
- Source: current_register:D06_directory_07; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_07; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-010 Fern cathedral
- Type: parent_programme; deck/span: D06; parent: D06_directory_08
- Source: current_register:D06_directory_08; data/reference/directory_allocations.json: atlas page 8
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D06_directory_08; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-011 Orbit full court
- Type: parent_programme; deck/span: D07; parent: D07_directory_01
- Source: current_register:D07_directory_01; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-012 Activity terrace
- Type: parent_programme; deck/span: D07; parent: D07_directory_09
- Source: current_register:D07_directory_09; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_09; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-013 Movement studio
- Type: parent_programme; deck/span: D07; parent: D07_directory_02
- Source: current_register:D07_directory_02; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-014 Sports care & changing
- Type: parent_programme; deck/span: D07; parent: D07_directory_10
- Source: current_register:D07_directory_10; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_10; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-015 Adaptive arena
- Type: parent_programme; deck/span: D07; parent: D07_directory_03
- Source: current_register:D07_directory_03; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-016 Sports viewing
- Type: parent_programme; deck/span: D07; parent: D07_directory_04
- Source: current_register:D07_directory_04; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_04; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-017 Training commons
- Type: parent_programme; deck/span: D07; parent: D07_directory_05
- Source: current_register:D07_directory_05; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-018 Simulation suites
- Type: parent_programme; deck/span: D07; parent: D07_directory_06
- Source: current_register:D07_directory_06; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-019 Gravity practice
- Type: parent_programme; deck/span: D07; parent: D07_directory_07
- Source: current_register:D07_directory_07; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_07; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-020 Team lounge
- Type: parent_programme; deck/span: D07; parent: D07_directory_08
- Source: current_register:D07_directory_08; data/reference/directory_allocations.json: atlas page 9
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D07_directory_08; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-021 The grand aquatic pool
- Type: parent_programme; deck/span: D08; parent: D08_directory_01
- Source: current_register:D08_directory_01; data/reference/directory_allocations.json: atlas page 10
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D08_directory_01; required programme; architecture pending; scripts/ship.gd:_ready loads grand_pool_section.gd; docs/GRAND_POOL_ACCESS_VALIDATION.json and docs/GRAND_POOL_ADOPTION.json: candidate capsule access passes; no completed waterpark
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room. Owner register predates installed pool/market candidate.

### AME-022 Panoramic repose
- Type: parent_programme; deck/span: D08; parent: D08_directory_09
- Source: current_register:D08_directory_09; data/reference/directory_allocations.json: atlas page 10
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D08_directory_09; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-023 Tidal thermal baths
- Type: parent_programme; deck/span: D08; parent: D08_directory_02
- Source: current_register:D08_directory_02; data/reference/directory_allocations.json: atlas page 10
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D08_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-024 Towels & care
- Type: parent_programme; deck/span: D08; parent: D08_directory_10
- Source: current_register:D08_directory_10; data/reference/directory_allocations.json: atlas page 10
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D08_directory_10; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-025 Mineral springs
- Type: parent_programme; deck/span: D08; parent: D08_directory_03
- Source: current_register:D08_directory_03; data/reference/directory_allocations.json: atlas page 10
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D08_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-026 Hushed grotto
- Type: parent_programme; deck/span: D08; parent: D08_directory_04
- Source: current_register:D08_directory_04; data/reference/directory_allocations.json: atlas page 10
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D08_directory_04; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-027 Wellness studio
- Type: parent_programme; deck/span: D08; parent: D08_directory_05
- Source: current_register:D08_directory_05; data/reference/directory_allocations.json: atlas page 10
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D08_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-028 Relaxation gallery
- Type: parent_programme; deck/span: D08; parent: D08_directory_06
- Source: current_register:D08_directory_06; data/reference/directory_allocations.json: atlas page 10
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D08_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-029 Universal changing
- Type: parent_programme; deck/span: D08; parent: D08_directory_07
- Source: current_register:D08_directory_07; data/reference/directory_allocations.json: atlas page 10
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D08_directory_07; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-030 Gentle waters
- Type: parent_programme; deck/span: D08; parent: D08_directory_08
- Source: current_register:D08_directory_08; data/reference/directory_allocations.json: atlas page 10
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D08_directory_08; partial authored construction; capacity, activity and final architectural acceptance remain pending; scripts/aquatic_section.gd / partial Gentle Waters architecture and access; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-031 Orchard market
- Type: parent_programme; deck/span: D09; parent: D09_directory_01
- Source: current_register:D09_directory_01; data/reference/directory_allocations.json: atlas page 11
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D09_directory_01; required programme; architecture pending; scripts/ship.gd:_ready loads orchard_exchange.gd and grand_pool_section.gd; partial installed market shell
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room. Owner register predates installed pool/market candidate.

### AME-032 Starlight bakery
- Type: parent_programme; deck/span: D09; parent: D09_directory_09
- Source: current_register:D09_directory_09; data/reference/directory_allocations.json: atlas page 11
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D09_directory_09; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-033 The copper kettle
- Type: parent_programme; deck/span: D09; parent: D09_directory_02
- Source: current_register:D09_directory_02; data/reference/directory_allocations.json: atlas page 11
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D09_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-034 Companion games
- Type: parent_programme; deck/span: D09; parent: D09_directory_10
- Source: current_register:D09_directory_10; data/reference/directory_allocations.json: atlas page 11
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D09_directory_10; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-035 Paper moon books
- Type: parent_programme; deck/span: D09; parent: D09_directory_03
- Source: current_register:D09_directory_03; data/reference/directory_allocations.json: atlas page 11
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D09_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-036 Thread & shell
- Type: parent_programme; deck/span: D09; parent: D09_directory_04
- Source: current_register:D09_directory_04; data/reference/directory_allocations.json: atlas page 11
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D09_directory_04; Partial authored architecture with route tests and visual review; full programme and final art unfinished; scripts/thread_shell.gd; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-037 Little makers gallery
- Type: parent_programme; deck/span: D09; parent: D09_directory_05
- Source: current_register:D09_directory_05; data/reference/directory_allocations.json: atlas page 11
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D09_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-038 Conversation salon
- Type: parent_programme; deck/span: D09; parent: D09_directory_06
- Source: current_register:D09_directory_06; data/reference/directory_allocations.json: atlas page 11
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D09_directory_06; partial architecture; D09_salon5_initial_terrace; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-039 Post & parcels
- Type: parent_programme; deck/span: D09; parent: D09_directory_07
- Source: current_register:D09_directory_07; data/reference/directory_allocations.json: atlas page 11
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D09_directory_07; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-040 Living gifts
- Type: parent_programme; deck/span: D09; parent: D09_directory_08
- Source: current_register:D09_directory_08; data/reference/directory_allocations.json: atlas page 11
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D09_directory_08; partial authored construction; capacity, activity and final architectural acceptance remain pending; scripts/living_gifts.gd + scripts/aquatic_section.gd / partial florist and shared access; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-041 The shared table / 240
- Type: parent_programme; deck/span: D10; parent: D10_directory_01
- Source: current_register:D10_directory_01; data/reference/directory_allocations.json: atlas page 12
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D10_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-042 Moonfruit parlor / 160
- Type: parent_programme; deck/span: D10; parent: D10_directory_09
- Source: current_register:D10_directory_09; data/reference/directory_allocations.json: atlas page 12
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D10_directory_09; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-043 Sunward dining / 240
- Type: parent_programme; deck/span: D10; parent: D10_directory_02
- Source: current_register:D10_directory_02; data/reference/directory_allocations.json: atlas page 12
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D10_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-044 Observation cafe / 120
- Type: parent_programme; deck/span: D10; parent: D10_directory_10
- Source: current_register:D10_directory_10; data/reference/directory_allocations.json: atlas page 12
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D10_directory_10; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-045 Lantern restaurant / 240
- Type: parent_programme; deck/span: D10; parent: D10_directory_03
- Source: current_register:D10_directory_03; data/reference/directory_allocations.json: atlas page 12
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D10_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-046 Orchard food hall / 240
- Type: parent_programme; deck/span: D10; parent: D10_directory_04
- Source: current_register:D10_directory_04; data/reference/directory_allocations.json: atlas page 12
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D10_directory_04; Partial authored architecture with route tests and visual review; full programme and final art unfinished; scripts/orchard_foodhall.gd; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-047 Tide kitchen / 240
- Type: parent_programme; deck/span: D10; parent: D10_directory_05
- Source: current_register:D10_directory_05; data/reference/directory_allocations.json: atlas page 12
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D10_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-048 Mineral broth hall / 240
- Type: parent_programme; deck/span: D10; parent: D10_directory_06
- Source: current_register:D10_directory_06; data/reference/directory_allocations.json: atlas page 12
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D10_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-049 The night table / 240
- Type: parent_programme; deck/span: D10; parent: D10_directory_07
- Source: current_register:D10_directory_07; data/reference/directory_allocations.json: atlas page 12
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D10_directory_07; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-050 Vesper dining / 240
- Type: parent_programme; deck/span: D10; parent: D10_directory_08
- Source: current_register:D10_directory_08; data/reference/directory_allocations.json: atlas page 12
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D10_directory_08; partial authored construction; capacity, activity and final architectural acceptance remain pending; scripts/vesper_dining.gd + scripts/vesper_service.gd + scripts/vesper_watercourse.gd / partial54-seat dining, finishing and visual water feature; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-051 Grand Lantern Theater / 2,200 seats
- Type: parent_programme; deck/span: D11; parent: D11_directory_01
- Source: current_register:D11_directory_01; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-052 Performers' commons
- Type: parent_programme; deck/span: D11; parent: D11_directory_09
- Source: current_register:D11_directory_09; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_09; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-053 Cinema 1 / 200 seats
- Type: parent_programme; deck/span: D11; parent: D11_directory_02
- Source: current_register:D11_directory_02; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-054 Games & companionship
- Type: parent_programme; deck/span: D11; parent: D11_directory_10
- Source: current_register:D11_directory_10; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_10; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-055 Cinema 2 / 200 seats
- Type: parent_programme; deck/span: D11; parent: D11_directory_03
- Source: current_register:D11_directory_03; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-056 Cultural gallery
- Type: parent_programme; deck/span: D11; parent: D11_directory_11
- Source: current_register:D11_directory_11; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_11; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-057 Cinema 3 / 200 seats
- Type: parent_programme; deck/span: D11; parent: D11_directory_04
- Source: current_register:D11_directory_04; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_04; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-058 Immersive sound
- Type: parent_programme; deck/span: D11; parent: D11_directory_12
- Source: current_register:D11_directory_12; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_12; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-059 Cinema 4 / 200 seats
- Type: parent_programme; deck/span: D11; parent: D11_directory_05
- Source: current_register:D11_directory_05; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-060 Backstage workshop
- Type: parent_programme; deck/span: D11; parent: D11_directory_13
- Source: current_register:D11_directory_13; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_13; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-061 Cinema 5 / 200 seats
- Type: parent_programme; deck/span: D11; parent: D11_directory_06
- Source: current_register:D11_directory_06; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-062 Cinema 6 / 200 seats
- Type: parent_programme; deck/span: D11; parent: D11_directory_07
- Source: current_register:D11_directory_07; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_07; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-063 The music room
- Type: parent_programme; deck/span: D11; parent: D11_directory_08
- Source: current_register:D11_directory_08; data/reference/directory_allocations.json: atlas page 13
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D11_directory_08; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-064 Horizon room
- Type: parent_programme; deck/span: D12; parent: D12_directory_01
- Source: current_register:D12_directory_01; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-065 Vesper panorama
- Type: parent_programme; deck/span: D12; parent: D12_directory_09
- Source: current_register:D12_directory_09; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_09; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-066 The long library
- Type: parent_programme; deck/span: D12; parent: D12_directory_02
- Source: current_register:D12_directory_02; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-067 Celestial lounge
- Type: parent_programme; deck/span: D12; parent: D12_directory_10
- Source: current_register:D12_directory_10; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_10; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-068 Listening salon
- Type: parent_programme; deck/span: D12; parent: D12_directory_03
- Source: current_register:D12_directory_03; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-069 Grand theater / First gallery
- Type: parent_programme; deck/span: D12; parent: D12_directory_11
- Source: current_register:D12_directory_11; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_11; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-070 The stillroom
- Type: parent_programme; deck/span: D12; parent: D12_directory_04
- Source: current_register:D12_directory_04; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_04; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-071 Star atlas
- Type: parent_programme; deck/span: D12; parent: D12_directory_05
- Source: current_register:D12_directory_05; data/reference/directory_allocations.json: atlas page 14
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D12_directory_05; partial authored construction; capacity, activity and final architectural acceptance remain pending; scripts/star_atlas.gd + scripts/star_atlas_arrival.gd / partial library and connected court; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-072 Night garden
- Type: parent_programme; deck/span: D12; parent: D12_directory_06
- Source: current_register:D12_directory_06; data/reference/directory_allocations.json: atlas page 14
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D12_directory_06; Partial fitted architecture, vegetation and local lighting; final art and guest use incomplete; scripts/night_garden.gd / AST-GAR-006; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-073 Many worlds gallery
- Type: parent_programme; deck/span: D12; parent: D12_directory_07
- Source: current_register:D12_directory_07; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_07; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-074 Reading nooks
- Type: parent_programme; deck/span: D12; parent: D12_directory_08
- Source: current_register:D12_directory_08; data/reference/directory_allocations.json: atlas page 14
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D12_directory_08; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-075 Grand theater / Crown gallery
- Type: parent_programme; deck/span: D13; parent: D13_directory_01
- Source: current_register:D13_directory_01; data/reference/directory_allocations.json: atlas page 15
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D13_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-076 Port forward commons
- Type: parent_programme; deck/span: D13; parent: D13_directory_02
- Source: current_register:D13_directory_02; data/reference/directory_allocations.json: atlas page 15
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D13_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-077 Starboard forward commons
- Type: parent_programme; deck/span: D13; parent: D13_directory_03
- Source: current_register:D13_directory_03; data/reference/directory_allocations.json: atlas page 15
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D13_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-078 Port atrium commons
- Type: parent_programme; deck/span: D13; parent: D13_directory_04
- Source: current_register:D13_directory_04; data/reference/directory_allocations.json: atlas page 15
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D13_directory_04; partial authored construction; capacity, activity and final architectural acceptance remain pending; scripts/star_atlas.gd / partial shared study and connected court; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-079 Starboard atrium commons
- Type: parent_programme; deck/span: D13; parent: D13_directory_05
- Source: current_register:D13_directory_05; data/reference/directory_allocations.json: atlas page 15
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D13_directory_05; Partial connected two-level architecture with walkable stair and tested physical lift; final art, guest use and full access review incomplete; scripts/vertical_commons.gd + scripts/commons_lift.gd / AST-COM-001, AST-CIR-003, AST-DOR-003; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-080 Port aft commons
- Type: parent_programme; deck/span: D13; parent: D13_directory_06
- Source: current_register:D13_directory_06; data/reference/directory_allocations.json: atlas page 15
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D13_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-081 Starboard aft commons
- Type: parent_programme; deck/span: D13; parent: D13_directory_07
- Source: current_register:D13_directory_07; data/reference/directory_allocations.json: atlas page 15
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D13_directory_07; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-082 Port forward commons
- Type: parent_programme; deck/span: D14; parent: D14_directory_01
- Source: current_register:D14_directory_01; data/reference/directory_allocations.json: atlas page 16
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D14_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-083 Starboard forward commons
- Type: parent_programme; deck/span: D14; parent: D14_directory_02
- Source: current_register:D14_directory_02; data/reference/directory_allocations.json: atlas page 16
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D14_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-084 Port atrium commons
- Type: parent_programme; deck/span: D14; parent: D14_directory_03
- Source: current_register:D14_directory_03; data/reference/directory_allocations.json: atlas page 16
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D14_directory_03; partial authored construction; capacity, activity and final architectural acceptance remain pending; scripts/star_atlas.gd / partial conversation gallery and connected court; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-085 Starboard atrium commons
- Type: parent_programme; deck/span: D14; parent: D14_directory_04
- Source: current_register:D14_directory_04; data/reference/directory_allocations.json: atlas page 16
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D14_directory_04; Partial connected two-level architecture with walkable stair and tested physical lift; final art, guest use and full access review incomplete; scripts/vertical_commons.gd + scripts/commons_lift.gd / AST-COM-001, AST-CIR-003, AST-DOR-003; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-086 Port aft commons
- Type: parent_programme; deck/span: D14; parent: D14_directory_05
- Source: current_register:D14_directory_05; data/reference/directory_allocations.json: atlas page 16
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D14_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-087 Starboard aft commons
- Type: parent_programme; deck/span: D14; parent: D14_directory_06
- Source: current_register:D14_directory_06; data/reference/directory_allocations.json: atlas page 16
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D14_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-088 Port forward commons
- Type: parent_programme; deck/span: D15; parent: D15_directory_01
- Source: current_register:D15_directory_01; data/reference/directory_allocations.json: atlas page 17
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D15_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-089 Starboard forward commons
- Type: parent_programme; deck/span: D15; parent: D15_directory_02
- Source: current_register:D15_directory_02; data/reference/directory_allocations.json: atlas page 17
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D15_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-090 Port atrium commons
- Type: parent_programme; deck/span: D15; parent: D15_directory_03
- Source: current_register:D15_directory_03; data/reference/directory_allocations.json: atlas page 17
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D15_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-091 Starboard atrium commons
- Type: parent_programme; deck/span: D15; parent: D15_directory_04
- Source: current_register:D15_directory_04; data/reference/directory_allocations.json: atlas page 17
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D15_directory_04; Partial connected D13-D17 house with local stairs, physical lift and authored resting edges; full neighbourhood and final art unfinished; scripts/vertical_commons.gd; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-092 Port aft commons
- Type: parent_programme; deck/span: D15; parent: D15_directory_05
- Source: current_register:D15_directory_05; data/reference/directory_allocations.json: atlas page 17
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D15_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-093 Starboard aft commons
- Type: parent_programme; deck/span: D15; parent: D15_directory_06
- Source: current_register:D15_directory_06; data/reference/directory_allocations.json: atlas page 17
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D15_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-094 Port forward commons
- Type: parent_programme; deck/span: D16; parent: D16_directory_01
- Source: current_register:D16_directory_01; data/reference/directory_allocations.json: atlas page 18
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D16_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-095 Starboard forward commons
- Type: parent_programme; deck/span: D16; parent: D16_directory_02
- Source: current_register:D16_directory_02; data/reference/directory_allocations.json: atlas page 18
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D16_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-096 Port atrium commons
- Type: parent_programme; deck/span: D16; parent: D16_directory_03
- Source: current_register:D16_directory_03; data/reference/directory_allocations.json: atlas page 18
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D16_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-097 Starboard atrium commons
- Type: parent_programme; deck/span: D16; parent: D16_directory_04
- Source: current_register:D16_directory_04; data/reference/directory_allocations.json: atlas page 18
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D16_directory_04; Partial connected D13-D17 house with local stairs, physical lift and authored resting edges; full neighbourhood and final art unfinished; scripts/vertical_commons.gd; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-098 Port aft commons
- Type: parent_programme; deck/span: D16; parent: D16_directory_05
- Source: current_register:D16_directory_05; data/reference/directory_allocations.json: atlas page 18
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D16_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-099 Starboard aft commons
- Type: parent_programme; deck/span: D16; parent: D16_directory_06
- Source: current_register:D16_directory_06; data/reference/directory_allocations.json: atlas page 18
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D16_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-100 Port forward commons
- Type: parent_programme; deck/span: D17; parent: D17_directory_01
- Source: current_register:D17_directory_01; data/reference/directory_allocations.json: atlas page 19
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D17_directory_01; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-101 Starboard forward commons
- Type: parent_programme; deck/span: D17; parent: D17_directory_02
- Source: current_register:D17_directory_02; data/reference/directory_allocations.json: atlas page 19
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D17_directory_02; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-102 Port atrium commons
- Type: parent_programme; deck/span: D17; parent: D17_directory_03
- Source: current_register:D17_directory_03; data/reference/directory_allocations.json: atlas page 19
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D17_directory_03; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-103 Starboard atrium commons
- Type: parent_programme; deck/span: D17; parent: D17_directory_04
- Source: current_register:D17_directory_04; data/reference/directory_allocations.json: atlas page 19
- Status: partial_current_construction
- Current evidence: data/programme_ledger.json:D17_directory_04; Partial connected D13-D17 house with local stairs, physical lift and authored resting edges; full neighbourhood and final art unfinished; scripts/vertical_commons.gd; loaded parent ship build calls checked, scope partial only
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-104 Port aft commons
- Type: parent_programme; deck/span: D17; parent: D17_directory_05
- Source: current_register:D17_directory_05; data/reference/directory_allocations.json: atlas page 19
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D17_directory_05; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-105 Starboard aft commons
- Type: parent_programme; deck/span: D17; parent: D17_directory_06
- Source: current_register:D17_directory_06; data/reference/directory_allocations.json: atlas page 19
- Status: no_verified_current_programme_builder
- Current evidence: data/programme_ledger.json:D17_directory_06; required programme; architecture pending
- Mapping/boundary: Historical envelope is an allocation; does not establish finished room.

### AME-106 50 m unobstructed main swimming lane
- Type: subspace; deck/span: D08; parent: D08_directory_01
- Source: master:T2R8; public_sheet:aquatic inset
- Status: partial_current_construction
- Current evidence: scripts/grand_pool_section.gd; data/architecture/GRAND_POOL_SECTION_PLAN.json: retained lane and trial wet datum
- Explicit source count: 1
- Mapping/boundary: Installed candidate shell and access, not swimming acceptance

### AME-107 Thermal pool set
- Type: subspace; deck/span: D08; parent: D08_directory_02
- Source: public_sheet:aquatic inset THERMAL POOLS 6
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Explicit source count: 6
- Mapping/boundary: Six pools are explicit image programme. Split between thermal baths/mineral springs/gentle waters needs resolution; do not create six extra directory programmes

### AME-108 Gravity-adaptive pools
- Type: system; deck/span: D08; parent: D08_directory_01, D08_directory_02
- Source: public_sheet:aquatic inset GRAVITY-ADAPTIVE POOLS
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Functional requirement; exact pool subset/count unresolved

### AME-109 Full waterpark
- Type: system; deck/span: D08; parent: D08_directory_01, D08_directory_08
- Source: current_overlay:Recreation and sound; chapter 19
- Status: not_verified_built
- Current evidence: docs/GRAND_POOL_CONNECTED_SECTION.md: waterpark explicitly remains open
- Mapping/boundary: Whole aquatic activity programme, not an extra unnamed room

### AME-110 Water slides
- Type: system; deck/span: D08; parent: D08_directory_01, D08_directory_08
- Source: current_overlay:Recreation and sound; docs/AQUATIC_VERTICAL_COORDINATION.md: slides and queues
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Count/trajectories/launch levels unresolved; no penetrations through D11 reservation

### AME-111 Floatable AFK lazy river
- Type: system; deck/span: D08; parent: D08_directory_01, D08_directory_08
- Source: current_overlay:Recreation and sound
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Loop boarding recovery and tube behaviour required; actual layout unresolved

### AME-112 Lazy river tubes
- Type: interactive_equipment; deck/span: D08; parent: D08_directory_01, D08_directory_08
- Source: current_overlay:chapter 19 tube requests
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Equipment requirement, not a room; count unspecified

### AME-113 Wet dry entry and exit
- Type: subspace; deck/span: D08; parent: D08_directory_01, D08_directory_08
- Source: master:P195; docs/AQUATIC_VERTICAL_COORDINATION.md
- Status: partial_architectural_only
- Current evidence: scripts/aquatic_section.gd: arrival canopy/waiting perch; scripts/grand_pool_section.gd: ramp
- Mapping/boundary: Water-entry assistance and guest water poses not implemented in candidate

### AME-114 Sheltered wet retreat and resting seating
- Type: subspace; deck/span: D08; parent: D08_directory_08
- Source: docs/AQUATIC_VERTICAL_COORDINATION.md:Gentle Waters; scripts/aquatic_section.gd
- Status: partial_current_construction
- Current evidence: AST-AQU-011 ShelteredWetRetreat; AST-AQU-014 arrival
- Mapping/boundary: Existing seating/threshold is partial child scope

### AME-115 Vesper restaurant watercourse and waterfall
- Type: system; deck/span: D10; parent: D10_directory_08
- Source: current_overlay:Recreation and sound
- Status: partial_architectural_only
- Current evidence: scripts/vesper_watercourse.gd: AST-AQU-015 animated appearance; no fluid simulation; docs/VESPER_WATERCOURSE.md
- Mapping/boundary: Do not count this visual restaurant feature as lazy river or aquatic swimming

### AME-116 Vesper dining mezzanine
- Type: subspace; deck/span: D10; parent: D10_directory_08
- Source: docs/VESPER_MEZZANINE_INTEGRATION.md
- Status: partial_current_construction
- Current evidence: scripts/vesper_mezzanine.gd
- Mapping/boundary: Dining programme remains 240 total places, not 240 plus mezzanine

### AME-117 Secondary pools for VIP members
- Type: subspace; deck/span: None; parent: unresolved
- Source: user_clarification
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Required explicitly by latest user. Inspected guest sheet labels lounge/bar/private dining but gives no VIP-pool count or deck. D17 luxury proposal does not resolve pools; retain mapping open rather than assign generic D17 commons.

### AME-118 VIP lounge and bar
- Type: subspace; deck/span: None; parent: unresolved
- Source: guest_sheet:VIP row center-left
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Image calls this D12 but authoritative master D12 is public observation; VIP accommodation moves into canonical residential decks and later D17 luxury decisions. Shared amenity destination/house mapping remains unresolved.

### AME-119 VIP private dining
- Type: subspace; deck/span: None; parent: unresolved
- Source: guest_sheet:VIP row center-right
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Image calls this D12 but authoritative master D12 is public observation; VIP accommodation moves into canonical residential decks and later D17 luxury decisions. Shared amenity destination/house mapping remains unresolved.

### AME-120 VIP aft observation lounge
- Type: subspace; deck/span: None; parent: unresolved
- Source: guest_sheet:VIP row aft
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Image calls this D12 but authoritative master D12 is public observation; VIP accommodation moves into canonical residential decks and later D17 luxury decisions. Shared amenity destination/house mapping remains unresolved.

### AME-121 VIP forward observation lounge
- Type: subspace; deck/span: None; parent: unresolved
- Source: guest_sheet:VIP row forward
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Image calls this D12 but authoritative master D12 is public observation; VIP accommodation moves into canonical residential decks and later D17 luxury decisions. Shared amenity destination/house mapping remains unresolved.

### AME-122 Lantern Stalls / orchestra seating
- Type: subspace; deck/span: D11; parent: D11_directory_01
- Source: legacy_auditoriums:740 stalls; performance:plan label 2 ORCHESTRA
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Orchestra label can mean stalls rather than separate orchestra pit. No pit requirement inferred

### AME-123 First Gallery / lower balcony
- Type: subspace; deck/span: D12; parent: D11_directory_01
- Source: legacy_auditoriums:740 first-gallery places; performance:plan label 3
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Alias D12_directory_11, not additional seats

### AME-124 Crown Gallery / upper balcony
- Type: subspace; deck/span: D13; parent: D11_directory_01
- Source: legacy_auditoriums:720 crown-gallery places; performance:plan label 4
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Canonical crown-gallery elevation overrides illustrative balcony-level count

### AME-125 Royal boxes
- Type: subspace; deck/span: D11–D13 unresolved; parent: D11_directory_01
- Source: performance:plan label 5 ROYAL BOXES
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Not independently named in register. Reconcile within existing 2,200 places, no extra tier/capacity

### AME-126 Stage and proscenium
- Type: subspace; deck/span: D11–D13; parent: D11_directory_01
- Source: public_sheet:stage width 36 m / height 16 m; performance:plan label 1; legacy_auditoriums:stage
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Real off-axis 22 m chamber required

### AME-127 Theater foyer and three public entry thresholds
- Type: subspace; deck/span: D11–D13; parent: D11_directory_01
- Source: performance:plan label 6 FOYER ACCESS; FOYER APPROACH caption; legacy_auditoriums:Entry care and circulation
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Current programme boundaries reserve theater; no installed foyer builder

### AME-128 Balcony lounge
- Type: subspace; deck/span: D11–D13 unresolved; parent: D11_directory_01
- Source: performance:BALCONY LOUNGE caption
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Explicit caption; which gallery and whether shared lounge remains unresolved

### AME-129 Theater gallery lift with three landings and gates
- Type: system; deck/span: D11–D13; parent: D11_directory_01
- Source: legacy_auditoriums:Entry care and circulation; master:P134
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Historical physical platform proof is dated; current public core lifts do not substitute for theater lift

### AME-130 Theater switchback stair
- Type: system; deck/span: D11–D13; parent: D11_directory_01
- Source: legacy_auditoriums:3.2 m clear flights
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Separate from gallery lift; current builder absent

### AME-131 Theater raked gangways side aisles and upper side galleries
- Type: subspace; deck/span: D11–D13; parent: D11_directory_01
- Source: legacy_auditoriums:Entry care and circulation
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Circulation children, not separate venue programmes

### AME-132 Accessible stage ramp
- Type: system; deck/span: D11; parent: D11_directory_01
- Source: legacy_auditoriums:genuine 1:12 stage ramp
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: No new room

### AME-133 Viewing and transfer bays
- Type: subspace; deck/span: D11–D13; parent: D11_directory_01
- Source: legacy_auditoriums:front landing bays
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: Substitute for existing numbered places; no extra capacity

### AME-134 Original theater light performance
- Type: system; deck/span: D11; parent: D11_directory_01
- Source: master:P328; legacy_auditoriums:Original performance
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready contains no auditoriums builder; scripts/auditoriums.gd absent; Historical AUDITORIUMS.md and catalogue auditorium components are retained evidence only
- Mapping/boundary: A Thousand Small Worlds; equipment is not extra rooms. Exact later storyline detail deferred

### AME-135 Cinema 1 rear foyer and entry
- Type: subspace; deck/span: D11; parent: D11_directory_02
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-136 Cinema 1 projector booth
- Type: subspace; deck/span: D11; parent: D11_directory_02
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-137 Cinema 1 raked aisles and rear return ramps
- Type: subspace; deck/span: D11; parent: D11_directory_02
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-138 Cinema 1 screen original abstract-short program and speakers
- Type: system; deck/span: D11; parent: D11_directory_02
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-139 Cinema 1 viewing transfer bay
- Type: subspace; deck/span: D11; parent: D11_directory_02
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-140 Cinema 2 rear foyer and entry
- Type: subspace; deck/span: D11; parent: D11_directory_03
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-141 Cinema 2 projector booth
- Type: subspace; deck/span: D11; parent: D11_directory_03
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-142 Cinema 2 raked aisles and rear return ramps
- Type: subspace; deck/span: D11; parent: D11_directory_03
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-143 Cinema 2 screen original abstract-short program and speakers
- Type: system; deck/span: D11; parent: D11_directory_03
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-144 Cinema 2 viewing transfer bay
- Type: subspace; deck/span: D11; parent: D11_directory_03
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-145 Cinema 3 rear foyer and entry
- Type: subspace; deck/span: D11; parent: D11_directory_04
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-146 Cinema 3 projector booth
- Type: subspace; deck/span: D11; parent: D11_directory_04
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-147 Cinema 3 raked aisles and rear return ramps
- Type: subspace; deck/span: D11; parent: D11_directory_04
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-148 Cinema 3 screen original abstract-short program and speakers
- Type: system; deck/span: D11; parent: D11_directory_04
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-149 Cinema 3 viewing transfer bay
- Type: subspace; deck/span: D11; parent: D11_directory_04
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-150 Cinema 4 rear foyer and entry
- Type: subspace; deck/span: D11; parent: D11_directory_05
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-151 Cinema 4 projector booth
- Type: subspace; deck/span: D11; parent: D11_directory_05
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-152 Cinema 4 raked aisles and rear return ramps
- Type: subspace; deck/span: D11; parent: D11_directory_05
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-153 Cinema 4 screen original abstract-short program and speakers
- Type: system; deck/span: D11; parent: D11_directory_05
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-154 Cinema 4 viewing transfer bay
- Type: subspace; deck/span: D11; parent: D11_directory_05
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-155 Cinema 5 rear foyer and entry
- Type: subspace; deck/span: D11; parent: D11_directory_06
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-156 Cinema 5 projector booth
- Type: subspace; deck/span: D11; parent: D11_directory_06
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-157 Cinema 5 raked aisles and rear return ramps
- Type: subspace; deck/span: D11; parent: D11_directory_06
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-158 Cinema 5 screen original abstract-short program and speakers
- Type: system; deck/span: D11; parent: D11_directory_06
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-159 Cinema 5 viewing transfer bay
- Type: subspace; deck/span: D11; parent: D11_directory_06
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-160 Cinema 6 rear foyer and entry
- Type: subspace; deck/span: D11; parent: D11_directory_07
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-161 Cinema 6 projector booth
- Type: subspace; deck/span: D11; parent: D11_directory_07
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-162 Cinema 6 raked aisles and rear return ramps
- Type: subspace; deck/span: D11; parent: D11_directory_07
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-163 Cinema 6 screen original abstract-short program and speakers
- Type: system; deck/span: D11; parent: D11_directory_07
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-164 Cinema 6 viewing transfer bay
- Type: subspace; deck/span: D11; parent: D11_directory_07
- Source: legacy_auditoriums:Entry care and circulation; Original performance; master:P328
- Status: no_verified_current_programme_builder
- Current evidence: scripts/ship.gd:_ready: no auditorium builder; scripts/auditoriums.gd absent
- Mapping/boundary: Part of existing 200-place cinema; equipment/ramps do not add programme or seats

### AME-165 Fitness center
- Type: subspace; deck/span: D07/D08 unresolved; parent: D07_directory_05, D08_directory_05
- Source: public_sheet:D09 Fitness Center; canonical aquatic shift to D08; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Ambiguous relationship to Training commons and Wellness studio; do not duplicate both

### AME-166 Panoramic relaxation deck
- Type: subspace; deck/span: D08; parent: D08_directory_09
- Source: public_sheet:D09 wellness row; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Panoramic repose is plausible parent; allocation does not establish view-ready geometry

### AME-167 Recreation lounge
- Type: subspace; deck/span: D08; parent: unresolved
- Source: public_sheet:D09 wellness row; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Potential Relaxation gallery overlap unresolved

### AME-168 Gaming lounges
- Type: subspace; deck/span: D11; parent: D11_directory_10
- Source: public_sheet:D11 Gaming Lounges; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Games & companionship parent; no invented number of lounges

### AME-169 Immersive experience zone
- Type: subspace; deck/span: D11; parent: D11_directory_12
- Source: public_sheet:D11 label; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Immersive sound is plausible current parent; exact visual/experience system remains open

### AME-170 Astraea sky lounge
- Type: subspace; deck/span: D12; parent: D12_directory_10
- Source: public_sheet:D12 label; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Celestial lounge naming crosswalk unresolved

### AME-171 Panoramic observation gallery
- Type: subspace; deck/span: D12; parent: unresolved
- Source: public_sheet:D12 label; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Likely distributed observation programme; do not count again as every named panorama

### AME-172 Art gallery
- Type: subspace; deck/span: D11/D12; parent: D11_directory_11, D12_directory_07
- Source: public_sheet:D11 and D12 art-gallery labels; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Two deck functions; resolve distinct rooms versus multi-level gallery

### AME-173 Nursery and childrens center
- Type: subspace; deck/span: D16 or family decks unresolved; parent: unresolved
- Source: guest_sheet:D11 family row; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Canonical family/residential remap; day activity does not add overnight occupants

### AME-174 Play and learning zone
- Type: subspace; deck/span: D16 or family decks unresolved; parent: unresolved
- Source: guest_sheet:D11 family row; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: May be contained in family commons; no explicit programme key yet

### AME-175 Family dining
- Type: subspace; deck/span: D16 or D10 unresolved; parent: unresolved
- Source: guest_sheet:D11 family row; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Canonical total dining remains 2,200; cannot add printed image diner subtotal

### AME-176 Hydroponic garden lounge
- Type: subspace; deck/span: D16 or family decks unresolved; parent: unresolved
- Source: guest_sheet:D11 family row; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Family garden/commons mapping needs explicit decision

### AME-177 Hydration and feeding alcoves
- Type: subspace; deck/span: residential decks unresolved; parent: unresolved
- Source: guest_sheet:D10 standard row; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Distributed accommodation support; no separate hotel-unit capacity

### AME-178 Multifaith meditation
- Type: subspace; deck/span: residential decks unresolved; parent: unresolved
- Source: guest_sheet:D09 label; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Possible quiet commons mapping unresolved

### AME-179 Observation nooks
- Type: subspace; deck/span: residential decks unresolved; parent: unresolved
- Source: guest_sheet:D09 label; master:P494/P497 canonical crosswalk
- Status: not_verified_built
- Current evidence: scripts/ship.gd: no dedicated loaded builder identified for this item; allocation/floor overlap alone is insufficient
- Mapping/boundary: Embedded shared-space children rather than extra accommodations

## Limits and next acceptance

Only read-only source inspection was performed. No imports, engine runs, builds, runtime edits, existing ledger edits or commits occurred. Allocation/floor overlap never proves finished architecture, routes, species support or activity. Catalogue presence never proves installation. Resolve explicit child mappings, then construct and verify each destination/child system against the current revision. Optional operational ideas such as an orchestra pit, ticket office, pool lifeguard room or extra dressing rooms remain suggestions unless sourced.

## Additional detailed aquatic and habitat crosswalk

### AME-180 Spa pods
- Type: subspace; deck/span: D08 or coordinated upper aquatic levels; parent: D08_directory_02, D08_directory_03
- Source: aquatic_detailed:floor plan labels 1–9; detail captions and section
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Number and distinction from six thermal pools unresolved

### AME-181 Aquatic lounge terraces and river lounge
- Type: subspace; deck/span: D08 or coordinated upper aquatic levels; parent: D08_directory_06, D08_directory_08
- Source: aquatic_detailed:floor plan labels 1–9; detail captions and section
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Captioned/plan-labelled terraces; exact allocation and all occupied upper levels unresolved

### AME-182 Aquatic bridges
- Type: system; deck/span: D08 or coordinated upper aquatic levels; parent: D08_directory_08
- Source: aquatic_detailed:floor plan labels 1–9; detail captions and section
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Plan label 5; required crossing composition must fit real basin/loop without blocking 50 m lane; number not inferred

### AME-183 Aquatic bar and refreshments
- Type: subspace; deck/span: D08 or coordinated upper aquatic levels; parent: D08_directory_08
- Source: aquatic_detailed:floor plan labels 1–9; detail captions and section
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Plan label 6 explicitly calls for bar/refreshments; no existing directory child crosswalk; coordinate with dining capacity

### AME-184 Aquatic local stairs and elevators
- Type: system; deck/span: D08 or coordinated upper aquatic levels; parent: D08_directory_08
- Source: aquatic_detailed:floor plan labels 1–9; detail captions and section
- Status: partial_architectural_only
- Evidence: scripts/aquatic_section.gd and docs/AQUATIC_VERTICAL_COORDINATION.md: partial three-stop access
- Mapping/boundary: Plan label 7; current 3-stop aquatic lift and switchbacks are partial infrastructure, not all reference levels

### AME-185 Aquatic changing rooms
- Type: subspace; deck/span: D08 or coordinated upper aquatic levels; parent: D08_directory_07
- Source: aquatic_detailed:floor plan labels 1–9; detail captions and section
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Plan label 8; existing Universal changing broad heading needs privacy/sub-room resolution

### AME-186 Aquatic planted islands and green zones
- Type: architectural_zone; deck/span: D08 or coordinated upper aquatic levels; parent: D08_directory_08
- Source: aquatic_detailed:floor plan labels 1–9; detail captions and section
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Plan label 9; architectural composition, not discrete mandatory room or exact island count

### AME-187 Aquatic waterfall focal sequence
- Type: system; deck/span: D08 or coordinated upper aquatic levels; parent: D08_directory_08
- Source: aquatic_detailed:floor plan labels 1–9; detail captions and section
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Actual swimming reference section depicts upper water feature; coexistence with restaurant watercourse and atrium feature needs coordinated interpretation, not duplicated spectacle

### AME-188 Aquatic habitat pods and water corridors
- Type: habitat_support; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D07 aquatic/arboreal row; canonical residential decks D04/D13–D17. Water rest accommodations/support must be reconciled against1000 units; not ordinary swimming-pool programme

### AME-189 Arboreal perch habitats
- Type: habitat_support; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D07 row. Rest support type is historical, not an extra species; map valid morphology/canonical six species before generation

### AME-190 Thermal rest chambers
- Type: habitat_support; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D08 row. Accommodation/rest family, not automatically a public thermal pool

### AME-191 Low gravity suites and gravity modulation
- Type: habitat_support; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D08 row and legend. Environmental support is part of existing units; no new population or speculative gravity simulator

### AME-192 Species adapted suites
- Type: habitat_support; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D08 row. Six current species supersede old imagery species/count assumptions

### AME-193 Refuge rooms
- Type: subspace; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D08 row; fixed units/day-support mapping unresolved. Printed20 cannot create extra hotel units or beds

### AME-194 Pressure transition vestibules
- Type: subspace; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D08 row. Habitat thresholds need mapping and actual environmental/support semantics

### AME-195 Species specific bio sanitation nodes
- Type: system; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D08 row; canonical current needs differ by species. Privacy/service interfaces belong with existing habitats, not invented unit increments

### AME-196 Hydration feeding kiosks and biosanitation nodes
- Type: system; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet legend/standard/habitat rows. Distributed child support, no new accommodation count

### AME-197 Multi environment garden lounges
- Type: subspace; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest sheet D07 Bionic lounge/life/terrarium garden labels; map residential shared spaces and botanical destinations without double counting

### AME-198 Variable atmosphere and humidity temperature acoustic lighting support
- Type: system; deck/span: D04/D13–D17 mapping unresolved; parent: unresolved
- Source: guest_sheet:habitat rows/legend; master:chapter6 and chapter8; P497
- Status: not_verified_built
- Evidence: scripts/ship.gd: no dedicated loaded builder identified; allocation is not construction
- Mapping/boundary: Guest-sheet environmental zoning/legend. Values are historical illustrative ranges; preserve confirmed qualitative needs, decide numeric specs separately

### AME-199 Private sleeping social dining and view zones inside guest units
- Type: architectural_zone; deck/span: residential decks; parent: unresolved
- Source: residential_current_reference:Uploaded46/44/45/46 actual pixels; master:chapter6; latest curated windows overlay
- Status: partial_current_construction
- Evidence: scripts/residential_suite.gd; scripts/d17_connected_house.gd; docs/D17_CONNECTED_ADOPTION.json; unit790 lower only
- Mapping/boundary: Images show supported sleeping, intimate seating/dining, framed internal court or external space view and profile/material hierarchy. These are room-family composition obligations inside the fixed1000units, not three extra rooms per unit. Partial D13 suites and D17 Royalty lower construction do not cover all instances.

## Reference scope screening inventory

All56 entries in this bounded amenity-related source inventory were visually checked: primary labelled sheets, detailed pool/theater/shopping images and selected residential sources at full image scale; remaining composition references and historical sheet variants at overview/contact-sheet scale. No known relevant source entry remains unread at scope-screening level. Full-size district design review remains required before authoring and this is not all72-reference or whole-ship acceptance.

- REF-aa10009828: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Additional_Historical_References/image(20261002-002522).png
- REF-f685af904b: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/1(1).png
- REF-e66ade3d9f: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/2(1).png
- REF-45bcf5b4f3: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/250d8f2d-6ef1-44c5-9009-67d50e20542f.png
- REF-858525bb42: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/3(1).png
- REF-546a6287cb: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/981c332a-deb3-49bf-af73-86469b55f869.png
- REF-be035845a6: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/Futuristic Luxury Space Atrium Garden.png
- REF-15abcd5aa3: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/Futuristic Suite Overlooking a Garden Atrium.png
- REF-82a66b7ffa: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/Luxury Space Cruise Suite with Planetary View.png
- REF-b4f7c83f24: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/Retro-Futurist Suite Overlooking Atrium.png
- REF-10dc8358ad: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-1(1).png
- REF-3f5de9e10f: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-1(2).png
- REF-419e1ed876: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-1(3).png
- REF-344c7d2696: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-1.png
- REF-2122ff0b9a: full_pixels_checked; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-2(1).png
- REF-c0d2dc2025: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-2(2).png
- REF-1a21aaa8f3: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-2(3).png
- REF-6fdf9f5234: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-2.png
- REF-6c3a18ea3f: full_pixels_checked; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-3(1).png
- REF-396d790bef: full_pixels_checked; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-3(2).png
- REF-48fd2aa4fe: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-3.png
- REF-e3e8d05223: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-4(1).png
- REF-1284874dbe: overview_contact_sheet_checked_only; DesignArchive/References/Historical_Concepts_And_Blueprints/image-gen-4.png
- REF-f34e721fb6: full_pixels_checked; DesignArchive/References/Uploaded_46/01/image.png
- REF-3813a0ecc3: full_pixels_checked; DesignArchive/References/Uploaded_46/02/image(1).png
- REF-90ba2f6d31: full_pixels_checked; DesignArchive/References/Uploaded_46/03/3.png
- REF-1d51d4a06e: full_pixels_checked; DesignArchive/References/Uploaded_46/04/2.png
- REF-6729d6150c: full_pixels_checked; DesignArchive/References/Uploaded_46/05/1.png
- REF-f84205f20a: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/07/image(3).png
- REF-72c49c565c: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/11/image(6).png
- REF-3c524e22a5: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/12/image(7).png
- REF-762f06b7c7: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/13/image(8).png
- REF-f80a4f58ec: full_pixels_checked; DesignArchive/References/Uploaded_46/14/image(20261001-035516).png
- REF-58874dc6da: full_pixels_checked; DesignArchive/References/Uploaded_46/15/image(20261001-035517).png
- REF-4f1d548bc8: full_pixels_checked; DesignArchive/References/Uploaded_46/16/image(20261001-035518).png
- REF-240d196d5a: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/20/image(20261001-071306).png
- REF-bec8e6ecaa: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/21/image(20261001-071604).png
- REF-20281d3bb3: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/22/image(20261001-071704).png
- REF-0478dfabb9: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/23/image(20261001-072858).png
- REF-a72a10a7d5: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/27/image(20261001-190511).png
- REF-72e9a4a1d0: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/28/image(20261001-190512).png
- REF-b74349b557: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/30/image(20261001-191914).png
- REF-bacc0c55bb: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/31/image(20261001-191915).png
- REF-980fe8b7e6: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/32/image(20261001-191916).png
- REF-4e1375543a: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/33/image(20261001-191917).png
- REF-b5f0c64e29: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/34/image(20261001-200233).png
- REF-dbea2b3b3d: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/35/image(20261001-200235).png
- REF-ab439aa6fa: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/40/image(20261001-213117).png
- REF-7ca7281301: composition_pixels_checked_at_contact_sheet_scale; DesignArchive/References/Uploaded_46/41/image(20261001-213118).png
- REF-0328f70e49: full_pixels_checked; DesignArchive/References/Uploaded_46/44/image(20261002-000722).png
- REF-9c453f4498: full_pixels_checked; DesignArchive/References/Uploaded_46/45/image(20261002-001051).png
- REF-0a92cd5adc: full_pixels_checked; DesignArchive/References/Uploaded_46/46/image(20261002-001347).png
- REF-32858f7ec1: composition_pixels_checked_at_contact_sheet_scale; BlenderCatalogue/references/hospitality/vibe_dining_edge.jpg
- REF-d0f54a5bb3: composition_pixels_checked_at_contact_sheet_scale; BlenderCatalogue/references/salon/vibe_observation_lounge.jpg
- REF-48cca6e8b3: composition_pixels_checked_at_contact_sheet_scale; BlenderCatalogue/references/salon/vibe_vertical_atrium.jpg
- REF-a2b1a7bd5c: composition_pixels_checked_at_contact_sheet_scale; BlenderCatalogue/references/residential_20261004/Luxury_single_space_view_8079.jpg

## Final composition findings

- Remaining residential references repeat sleeping/social/dining/view composition or show modular wall/window/ceiling/furniture kits. They do not explicitly add private swimming pools or extra unit counts.
- Library references show intimate reading alcoves, integrated shelving, overlook/stair/escalator relationships and viewing/study spaces; existing library/reading programmes must express these functions without copying a specific branded library.
- Atrium references show grounded botanical/water focal sequence, active terraces, purposeful crossings/lifts and linked destinations. Exact illustrated number of trees/islands/terraces is not mandatory and cannot override16-level opening.
- Shopping reference names Nexus/Terra&Tide/StellarFinds illustrate storefront identities; master architecture clause5 explicitly prohibits adding businesses or moving all100shops to ring. Preserve addressed100shop inventory separately from10directory retail headings.
- No remaining composition image established VIP secondary-pool count/deck; latest user-required scope remains explicitly unresolved.

## Canonical parent coverage closure

The amenity and engineering/service audit programme associations together cover all161canonical keys with zero missing or outside keys. Seven parent rows were added to close the earlier154-key union: all six D04habitat-neighbourhood commons and D18Upper Horizon. This is inventory closure, not architectural or functional acceptance. Parent and child overlap remains non-additive.

### AME-200 Port forward commons
- Programme: D04_directory_01; deck: D04
- Source: current_register:D04_directory_01; master:chapter4 D04 residential support / D18 command observation; data/reference/directory_allocations.json: atlas page 6
- Status: no_verified_current_programme_builder
- Evidence: data/programme_ledger.json:D04_directory_01; source directory identity only; data/reference/directory_allocations.json: atlas page 6; scripts/ship.gd:_ready: no dedicated loaded builder identified for this D04 commons; residential unit allocation does not prove commons construction
- Boundary: Existing habitat-neighbourhood commons heading inside the161programme total. Shared support must serve existing1000unit inventory; no additional homes/berths or mandatory subroom count inferred.

### AME-201 Starboard forward commons
- Programme: D04_directory_02; deck: D04
- Source: current_register:D04_directory_02; master:chapter4 D04 residential support / D18 command observation; data/reference/directory_allocations.json: atlas page 6
- Status: no_verified_current_programme_builder
- Evidence: data/programme_ledger.json:D04_directory_02; source directory identity only; data/reference/directory_allocations.json: atlas page 6; scripts/ship.gd:_ready: no dedicated loaded builder identified for this D04 commons; residential unit allocation does not prove commons construction
- Boundary: Existing habitat-neighbourhood commons heading inside the161programme total. Shared support must serve existing1000unit inventory; no additional homes/berths or mandatory subroom count inferred.

### AME-202 Port atrium commons
- Programme: D04_directory_03; deck: D04
- Source: current_register:D04_directory_03; master:chapter4 D04 residential support / D18 command observation; data/reference/directory_allocations.json: atlas page 6
- Status: no_verified_current_programme_builder
- Evidence: data/programme_ledger.json:D04_directory_03; source directory identity only; data/reference/directory_allocations.json: atlas page 6; scripts/ship.gd:_ready: no dedicated loaded builder identified for this D04 commons; residential unit allocation does not prove commons construction
- Boundary: Existing habitat-neighbourhood commons heading inside the161programme total. Shared support must serve existing1000unit inventory; no additional homes/berths or mandatory subroom count inferred.

### AME-203 Starboard atrium commons
- Programme: D04_directory_04; deck: D04
- Source: current_register:D04_directory_04; master:chapter4 D04 residential support / D18 command observation; data/reference/directory_allocations.json: atlas page 6
- Status: no_verified_current_programme_builder
- Evidence: data/programme_ledger.json:D04_directory_04; source directory identity only; data/reference/directory_allocations.json: atlas page 6; scripts/ship.gd:_ready: no dedicated loaded builder identified for this D04 commons; residential unit allocation does not prove commons construction
- Boundary: Existing habitat-neighbourhood commons heading inside the161programme total. Shared support must serve existing1000unit inventory; no additional homes/berths or mandatory subroom count inferred.

### AME-204 Port aft commons
- Programme: D04_directory_05; deck: D04
- Source: current_register:D04_directory_05; master:chapter4 D04 residential support / D18 command observation; data/reference/directory_allocations.json: atlas page 6
- Status: no_verified_current_programme_builder
- Evidence: data/programme_ledger.json:D04_directory_05; source directory identity only; data/reference/directory_allocations.json: atlas page 6; scripts/ship.gd:_ready: no dedicated loaded builder identified for this D04 commons; residential unit allocation does not prove commons construction
- Boundary: Existing habitat-neighbourhood commons heading inside the161programme total. Shared support must serve existing1000unit inventory; no additional homes/berths or mandatory subroom count inferred.

### AME-205 Starboard aft commons
- Programme: D04_directory_06; deck: D04
- Source: current_register:D04_directory_06; master:chapter4 D04 residential support / D18 command observation; data/reference/directory_allocations.json: atlas page 6
- Status: no_verified_current_programme_builder
- Evidence: data/programme_ledger.json:D04_directory_06; source directory identity only; data/reference/directory_allocations.json: atlas page 6; scripts/ship.gd:_ready: no dedicated loaded builder identified for this D04 commons; residential unit allocation does not prove commons construction
- Boundary: Existing habitat-neighbourhood commons heading inside the161programme total. Shared support must serve existing1000unit inventory; no additional homes/berths or mandatory subroom count inferred.

### AME-206 Upper horizon
- Programme: D18_directory_09; deck: D18
- Source: current_register:D18_directory_09; master:chapter4 D04 residential support / D18 command observation; data/reference/directory_allocations.json: atlas page 20
- Status: partial_current_construction
- Evidence: data/programme_ledger.json:D18_directory_09; source directory identity only; data/reference/directory_allocations.json: atlas page 20; scripts/ship.gd:_ready loads aft_crown_platform.gd and upper_horizon_enclosure.gd; data/architecture/AFT_CROWN_PLATFORM_RUNTIME.json and UPPER_HORIZON_ENCLOSURE_RUNTIME.json; docs/UPPER_HORIZON_ENCLOSURE_FOCUSED_VALIDATION.json and docs/AFT_CROWN_PLATFORM_VALIDATION.json: partial installed foyer/observation geometry, not complete furnishing/occupation
- Boundary: Installed partial Upper Horizon overrides stale ledger nullowner/pending status. Historical envelope is not a required finished footprint; onward closure furnishing lighting and guest use remain open.

Grand Pool and Orchard Market parent rows explicitly record the installed walking-tested partial candidate rather than the stale pending register status. Upper Horizon is also installed partial via the aft-crown platform and enclosure runtime contracts, despite the stale owner field.
