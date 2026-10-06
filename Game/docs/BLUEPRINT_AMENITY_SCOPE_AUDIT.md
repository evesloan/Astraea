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

This finite audit records 179 rows: 105 existing directory headings and 74 child/system rows. These layers must not be summed into a claimed ship room count. No additional programme count is asserted. Exact source paths, hashes and unresolved mappings are in data/architecture/AMENITY_SCOPE_AUDIT.json.

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
