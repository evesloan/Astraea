# Blueprint engineering and service scope audit

The full service ship exceeds the currently connected lower staff backbone and upper wet/market interfaces. This is an evidence inventory, not a new registry, geometry plan or finished-ship claim. All eighteen decks and the 1,082 × up-to-240 × 118 m ship envelope remain intact. No runtime, existing ledger, source document or capacity has been changed.

## Authority and evidence

- Master: `docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx`, v0.3. Paragraph locators are zero-based OOXML paragraph positions, not invented rendered page numbers. Tables use zero-based extraction indexes (Table 2 deck matrix; Table 3 service systems).
- Inspected image pixels: `/workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png`, printed Sheet 4 of 6, V1.0.3, 25.07.04. Diagram labels, overview tables and lower legend/emergency panels were inspected directly.
- Current overrides: `docs/master_source/MASTER_CURRENT_APPLICATION.json`, particularly shared staff home, dated rebuild status and screened primary fusion exhibit.
- Current geometry evidence is source-builder inspection, not a fresh runtime or functional acceptance test. Master historical implementation/verification must not be promoted into current rebuild evidence.

## Essential reconciliation

The printed technical-sheet deck labels are not the current ship plan: logistics D03 becomes D01, engineering D04 becomes D02, crew D06 becomes D03, while medical D05 remains D05 (master P491). The medical sheet also depicts atmosphere, water and life-support control. The master places engineering plant/oversight on D02; retain that contradiction until distributed plant/control placement is resolved. Do not silently delete either reference or duplicate plant totals.

Current `programme_ledger.json` contains 161 destination programmes across the ship. `whole_ship_layout.json` calls itself programme/accounting crosswalk and initial vertical reservations, expressly not final construction or a room registry. Ten D01 and ten D02 directory destinations aggregate multiple plant modules, holds, docks, stores, workshops and subspaces. They omit distinct identities for engineering control rooms, technical/general stores, security stations, service-vehicle bay, lifeboat embarkation and several clinical subspaces. A programme may contain multiple subspaces; a system may run across programmes. Neither omission nor aggregation authorizes overlapping extra room counts.

The 200 D03 crew-bank envelopes in `data/reference/D03_crew_envelopes.json` are unlabelled allocations, not mandatory cabin walls or finished housing. Printed 320 standard quarters, 40 officer cabins and diagram 200 crew-quarter label must not be summed. Retain 400 crew including player and apply the current shared-home override.

The lower network source explicitly excludes finished rooms, beds and assignments. D03 home and depot are bounded unfurnished thresholds, the depot has no stock. Current `lower_staff_network.gd` also references the grand-pool extension and preserved lower lift plus D08 wet/D09 market stops. This does not establish a completed shipwide technical/logistics network, housing, actual staff life, cargo operation, laundry throughput or operating reactor. Two AST-ENG-007 contained exhibits in the primary gallery do not prove the secondary gallery or two operating reactors. One synthesis service bay containing pump/filter/water-console props is not four synthesis hubs or D02 water recovery.

## Evidence inventory

Source quantities below are retained as reference claims, not additive room totals. “Unknown” means distinct geometry/function was not established from the bounded inspected sources. The JSON companion retains per-item classification, programme keys, provenance, actual geometry evidence and unresolved mapping.

### ENGS-001 Primary fusion core / gallery
- Classification: room and contained system; canonical deck: 2; source quantity: 1
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D02_directory_01
- Current evidence: Integrated arrivals/fusion architecture and lift checked; partial hospitality fit-out. Final art, full programme equipment and NPC use pending [scripts/arrivals_fusion.gd]; scripts/arrivals_fusion.gd installs two ContainedFusionExhibit AST-ENG-007 displays inside primary gallery programme. Their loop count is not proof that secondary gallery/second operational reactor is built. Curated sealed machinery and screened service catwalks are explicit.
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-002 Secondary fusion core / gallery
- Classification: room and contained system; canonical deck: 2; source quantity: 1
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D02_directory_02
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-003 Engineering control rooms
- Classification: room; canonical deck: 2; source quantity: 2
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-004 Aft engineering
- Classification: department / subspace; canonical deck: 2; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-005 Life support plant
- Classification: system / plant modules; canonical deck: 2; source quantity: 4 modules
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D02_directory_08
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-006 Atmosphere processors
- Classification: system / plant modules; canonical deck: 2; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D02_directory_03
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-007 Water recycling plant
- Classification: system / plant modules; canonical deck: 2; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D02_directory_04
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-008 Waste recycling / matter reclamation
- Classification: system / plant modules; canonical deck: 1; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D01_directory_07
- Current evidence: required programme; architecture pending [None]
- Open: Printed engineering D04 becomes D02 (Master P491). Waste overlaps D01 reclamation programme; exact plant split unresolved.

### ENGS-009 Power distribution nodes
- Classification: system nodes; canonical deck: 2; source quantity: 6
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D02_directory_07
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-010 Maintenance workshops
- Classification: rooms / workshop facilities; canonical deck: 2; source quantity: 6
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D02_directory_05
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-011 Technical stores
- Classification: storage rooms / facilities; canonical deck: 2; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-012 Environmental systems
- Classification: system / department; canonical deck: 2; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-013 Reserve emergency power
- Classification: system; canonical deck: 2; source quantity: 100% (30 days)
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Engineering & Reactor diagram / Engineering systems table
- Programme association: D02_directory_06
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-014 Shuttle docks
- Classification: docking facilities; canonical deck: 1; source quantity: 4 (2 port / 2 starboard)
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_01
- Current evidence: Integrated arrivals/fusion architecture and lift checked; partial hospitality fit-out. Final art, full programme equipment and NPC use pending [scripts/arrivals_fusion.gd]
- Open: Printed logistics D03 becomes D01. Shuttle arrivals/concourse do not account for four dock facilities. Cargo exchange/dispatch aggregate logistics, not additional holds.

### ENGS-015 Shuttle concourse
- Classification: room / circulation; canonical deck: 1; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_09
- Current evidence: required programme; architecture pending [None]
- Open: Printed logistics D03 becomes D01. Shuttle arrivals/concourse do not account for four dock facilities. Cargo exchange/dispatch aggregate logistics, not additional holds.

### ENGS-016 Cargo holds A–C
- Classification: storage volumes; canonical deck: 1; source quantity: 6,000 tonnes capacity; three labeled hold groups
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_04
- Current evidence: required programme; architecture pending [None]
- Open: Printed logistics D03 becomes D01. Shuttle arrivals/concourse do not account for four dock facilities. Cargo exchange/dispatch aggregate logistics, not additional holds.

### ENGS-017 Cargo dispatch
- Classification: programme; canonical deck: 1; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_08
- Current evidence: required programme; architecture pending [None]
- Open: Printed logistics D03 becomes D01. Shuttle arrivals/concourse do not account for four dock facilities. Cargo exchange/dispatch aggregate logistics, not additional holds.

### ENGS-018 Cold refrigerated storage
- Classification: storage volume; canonical deck: 1; source quantity: 12,000 m³
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_02
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-019 Food synthesis hubs
- Classification: system / facilities; canonical deck: 1; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_05
- Current evidence: Partial synthesis service bay, machinery and tested service door fitted with a supported approach to the D01 port service spine; full plant, production and restocking workflows remain unfinished [scripts/staff_section.gd]; scripts/staff_section.gd explicitly one service bay only, with TransferPump AST-ENG-001, FilterVessel AST-ENG-002 and WaterRecoveryConsole AST-ENG-003. Water-themed props at D01 do not complete D02 water plant.
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-020 Housekeeping / laundry
- Classification: processing facilities; canonical deck: 1; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_03
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-021 General stores and supplies
- Classification: storage facilities; canonical deck: 1; source quantity: 6
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-022 Waste processing
- Classification: processing facilities; canonical deck: 1; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_07
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-023 Repair workshops
- Classification: workshop facilities; canonical deck: 1; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: D01_directory_06
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-024 Maintenance bay
- Classification: bay; canonical deck: 1; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-025 Service vehicle bay
- Classification: bay; canonical deck: 1; source quantity: Yes
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-026 Lifeboat embarkation points
- Classification: emergency embarkation facilities; canonical deck: 1; source quantity: 8 (per side)
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Logistics & Services diagram / Logistics & Support table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-027 Crew accommodation banks
- Classification: accommodation allocation; canonical deck: 3; source quantity: 320 standard quarters in overview; diagram label Crew quarters (200)
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Printed crew D06 becomes D03. 400 crew including player is binding, not an additive sum of printed quarter labels. 200 unlabelled current D03 allocation envelopes are not finished rooms. Current override changes player private cabin to shared home; story deferred.

### ENGS-028 Officer cabins
- Classification: accommodation; canonical deck: 3; source quantity: 40
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Printed crew D06 becomes D03. 400 crew including player is binding, not an additive sum of printed quarter labels. 200 unlabelled current D03 allocation envelopes are not finished rooms. Current override changes player private cabin to shared home; story deferred.

### ENGS-029 Player shared staff home
- Classification: accommodation; canonical deck: 3; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_01
- Current evidence: required programme; architecture pending [None]
- Open: Printed crew D06 becomes D03. 400 crew including player is binding, not an additive sum of printed quarter labels. 200 unlabelled current D03 allocation envelopes are not finished rooms. Current override changes player private cabin to shared home; story deferred.

### ENGS-030 Custodian breakroom
- Classification: room; canonical deck: 3; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_02
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-031 Equipment depot
- Classification: room / stores; canonical deck: 3; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_03
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-032 Crew dining
- Classification: room / activity capacity; canonical deck: 3; source quantity: 300 seats
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_04
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-033 Staff recreation
- Classification: rooms / facilities; canonical deck: 3; source quantity: 3
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_07
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-034 Training rooms
- Classification: rooms; canonical deck: 3; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_05
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-035 Briefing rooms
- Classification: rooms; canonical deck: 3; source quantity: 2
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_08
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-036 Staff administration
- Classification: suite; canonical deck: 3; source quantity: 1
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_06
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-037 Security stations
- Classification: stations / rooms; canonical deck: 3; source quantity: 6
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-038 Uniforms and locker rooms
- Classification: support rooms; canonical deck: 3; source quantity: 6 M/F/universal locker rooms
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_10
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-039 Crew medical dedicated
- Classification: care support; canonical deck: 3; source quantity: Yes
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: D03_directory_09
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-040 Bridge access
- Classification: circulation interface; canonical deck: 3; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Crew Quarters & Operations diagram / Crew Facilities Overview
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-041 General medical bay
- Classification: room / clinical capacity; canonical deck: 5; source quantity: 20 beds
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_02
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-042 Surgical suites
- Classification: rooms; canonical deck: 5; source quantity: 4
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-043 Quarantine rooms
- Classification: rooms; canonical deck: 5; source quantity: 12
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-044 Species triage pods
- Classification: subspaces; canonical deck: 5; source quantity: 8
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_01
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-045 Medical laboratories / research
- Classification: rooms; canonical deck: 5; source quantity: 6
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_03
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-046 Pharmacy and xenomed storage
- Classification: storage / support; canonical deck: 5; source quantity: 2
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_04
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-047 Isolation airborne / contact
- Classification: support system / rooms unresolved; canonical deck: 5; source quantity: Yes
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-048 Multi-species care capability
- Classification: service capability; canonical deck: 5; source quantity: Yes
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-049 Telemedicine / remote specialists
- Classification: service / communications; canonical deck: 5; source quantity: Yes
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-050 Recovery care
- Classification: room; canonical deck: 5; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_05
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-051 Hydration support
- Classification: support programme; canonical deck: 5; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_09
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-052 Consultation pods
- Classification: subspaces; canonical deck: 5; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_07
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-053 Quiet care
- Classification: room; canonical deck: 5; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_08
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-054 Atmosphere research
- Classification: research room; canonical deck: 5; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_06
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-055 Family waiting
- Classification: room; canonical deck: 5; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D05_directory_10
- Current evidence: required programme; architecture pending [None]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-056 Life support control on medical diagram
- Classification: control / disputed location; canonical deck: 5; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Medical & Life Support diagram / Medical Facilities table
- Programme association: D02_directory_08
- Current evidence: required programme; architecture pending [None]
- Open: Reference shows atmosphere processors, water recycling and life-support control on medical D05 as well as engineering D04. Master Table 2 assigns engineering atmosphere/water/power oversight D02; D05 research/care remains. Do not duplicate full plants without resolving distributed control/plant relationship.

### ENGS-057 Dual-fusion redundancy
- Classification: system relationship; canonical deck: distributed or unresolved; source quantity: Full power from either core; 100% redundancy
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-058 Independent life support
- Classification: system relationship; canonical deck: distributed or unresolved; source quantity: 4 isolated plants; 72-hour island mode
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-059 Multiple escape systems
- Classification: emergency system; canonical deck: distributed or unresolved; source quantity: Distributed lifeboats; 8 embarkation points
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-060 Emergency egress routes
- Classification: circulation system; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-061 Medical surge capacity
- Classification: capability; canonical deck: distributed or unresolved; source quantity: Expandable wards; epidemic containment ready
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-062 Airlock / pressure doors
- Classification: threshold system; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-063 Primary bulkheads
- Classification: structural system; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-064 Restricted service access
- Classification: circulation / access separation; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-065 Separated guest and service corridors
- Classification: circulation network; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: data/architecture/LOWER_STAFF_NETWORK.json: one screened D01/D02/D03 enclosure and corridors, no general floors, cabins/gates, beds, job/species assignments or finished rooms. D03 home threshold unfurnished/no beds/no identity; depot threshold unfurnished/no stock. scripts/lower_staff_network.gd connects preserved lift plus sourced upper wet/market stops. Full network unresolved.
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-066 Restricted vertical service lifts
- Classification: circulation system; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-067 Guest vertical lifts
- Classification: circulation interface; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-068 Gravity zones
- Classification: environmental system; canonical deck: distributed or unresolved; source quantity: 0.3g–1.5g adjustable
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Blueprint system claim does not require deep engineering simulation. Old Aquan naming is noncanonical under master six-species roster; no gas/pressure/harmful biology or quantitative gravity simulation is approved.

### ENGS-069 Atmosphere mixes
- Classification: environmental reference claim; canonical deck: distributed or unresolved; source quantity: Human, Baelin, Aquan, custom
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Blueprint system claim does not require deep engineering simulation. Old Aquan naming is noncanonical under master six-species roster; no gas/pressure/harmful biology or quantitative gravity simulation is approved.

### ENGS-070 Nutrition systems
- Classification: food service capability; canonical deck: distributed or unresolved; source quantity: Omnivore / herbivore / specialized
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-071 Universal medical protocols
- Classification: care capability; canonical deck: distributed or unresolved; source quantity: AI-assisted nanomedicine
- Source: /workspace/shared/astraea-catalogue-continuation-20261002/references/engineering/technical_reference.png — printed Sheet 4 of 6; Legend, transverse/longitudinal sections, Service Circulation Flow, Emergency & Redundancy Systems and Multi-species Support panels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Blueprint system claim does not require deep engineering simulation. Old Aquan naming is noncanonical under master six-species roster; no gas/pressure/harmful biology or quantitative gravity simulation is approved.

### ENGS-072 D10 finishing galleys
- Classification: back-of-house facilities; canonical deck: 10; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 3 Food and provisions; P169
- Programme association: D10_directory_08, D10_directory_04
- Current evidence: scripts/vesper_service.gd builds one local AST-DIN-003 finishing/return space, two counters AST-HSP-001, plate/tray stock AST-HSP-005, dirty return AST-HSP-004 and persistent service door at D10 y61. Explicitly no full kitchen throughput claim; orchard is partial architecture
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-073 Food delivery and dirty returns
- Classification: workflow / service routes; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master P169
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-074 Distributed care alcoves and stock cupboards
- Classification: distributed subspaces / restocking network; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master P165–169 and Table 3 Laundry and sanitation
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-075 Local bins and service waste-transfer points
- Classification: distributed fixtures / transfer nodes; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 3 Waste and recycling
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-076 Aquatic wet service and towel returns
- Classification: service interfaces / routes; canonical deck: 8; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 3 Water and recovery
- Programme association: unmapped distinct identity
- Current evidence: scripts/lower_staff_network.gd uses GRAND_POOL_SECTION_RUNTIME staff data, preserved lower lift identity and adds D08 wet service / D09 market service stops; still WIP, not water-plant or shipwide logistics completion
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-077 Local habitat environmental support
- Classification: distributed systems; canonical deck: distributed or unresolved; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master P148–156 and Table 3 Atmosphere and habitats
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-078 Command bridge
- Classification: room / operational control; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 D18 and Table 3 Communications and command
- Programme association: D18_directory_01
- Current evidence: Unfurnished bridge shell under integration; operational systems and acceptance unfinished [scripts/bridge_enclosure.gd]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-079 Navigation
- Classification: room / operational control; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 D18
- Programme association: D18_directory_02
- Current evidence: Unfurnished central crown programme shell under integration; operational equipment, runtime and visual acceptance pending [scripts/central_command_crown.gd]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-080 Communications
- Classification: room / operational system; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 D18
- Programme association: D18_directory_03
- Current evidence: Unfurnished central crown programme shell under integration; operational equipment, runtime and visual acceptance pending [scripts/central_command_crown.gd]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-081 Emergency control
- Classification: room / operational control; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 D18; current programme ledger
- Programme association: D18_directory_10
- Current evidence: Unfurnished aft command shell; operational systems and acceptance pending [scripts/aft_command_crown.gd]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-082 Ship status control
- Classification: room / operational control; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 3 operational nodes; current programme ledger
- Programme association: D18_directory_08
- Current evidence: Unfurnished aft command shell; operational systems and acceptance pending [scripts/aft_command_crown.gd]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-083 Bridge briefing
- Classification: room; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 D18; current programme ledger
- Programme association: D18_directory_06
- Current evidence: Unfurnished central crown programme shell under integration; operational equipment, runtime and visual acceptance pending [scripts/central_command_crown.gd]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-084 Officer respite
- Classification: room / crew support; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 D18; current programme ledger
- Programme association: D18_directory_05
- Current evidence: Unfurnished central crown programme shell under integration; operational equipment, runtime and visual acceptance pending [scripts/central_command_crown.gd]
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-085 Backstage service interface
- Classification: service subspaces / routes; canonical deck: 11; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 D11 backstage
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-086 Retail repairs and parcel support
- Classification: service programmes; canonical deck: 9; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 D09 repairs and parcels
- Programme association: unmapped distinct identity
- Current evidence: No distinct programme mapping or installed geometry/function established in inspected current sources
- Open: Allocation/directory identity does not establish subspace count, full equipment, usable geometry or activity acceptance

### ENGS-087 Custodial depot
- Classification: directory programme; canonical deck: 1; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 principal identity; data/programme_ledger.json D01_directory_10
- Programme association: D01_directory_10
- Current evidence: required programme; architecture pending [None]
- Open: Directory programme is explicit retained allocation but not a separate technical-blueprint system count

### ENGS-088 Solar project archive
- Classification: directory programme; canonical deck: 2; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 principal identity; data/programme_ledger.json D02_directory_09
- Programme association: D02_directory_09
- Current evidence: required programme; architecture pending [None]
- Open: Directory programme is explicit retained allocation but not a separate technical-blueprint system count

### ENGS-089 Inspection dock
- Classification: directory programme; canonical deck: 2; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 principal identity; data/programme_ledger.json D02_directory_10
- Programme association: D02_directory_10
- Current evidence: required programme; architecture pending [None]
- Open: Directory programme is explicit retained allocation but not a separate technical-blueprint system count

### ENGS-090 Solar enclosure chart
- Classification: directory programme; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 principal identity; data/programme_ledger.json D18_directory_04
- Programme association: D18_directory_04
- Current evidence: Unfurnished central crown programme shell under integration; operational equipment, runtime and visual acceptance pending [scripts/central_command_crown.gd]
- Open: Directory programme is explicit retained allocation but not a separate technical-blueprint system count

### ENGS-091 Astrometric station
- Classification: directory programme; canonical deck: 18; source quantity: unspecified
- Source: docs/master_source/Astraea_Master_Game_Design_v0_3_authoritative.docx — Master Table 2 principal identity; data/programme_ledger.json D18_directory_07
- Programme association: D18_directory_07
- Current evidence: Unfurnished central crown programme shell under integration; operational equipment, runtime and visual acceptance pending [scripts/central_command_crown.gd]
- Open: Directory programme is explicit retained allocation but not a separate technical-blueprint system count

## Finite next design questions

1. Resolve plant/control distribution between canonical D02 and medical D05 without replacing the eighteen-deck map
2. Decompose the existing D01/D02 programmes into evidenced facility families and clean/dirty/cargo service paths; preserve source counts as constraints pending reconciliation, not extra directory entries
3. Establish the intended relationship between six engineering workshops and four logistics repair workshops, and the ambiguous eight-per-side lifeboat wording
4. Reconcile crew housing allocations and shared player home before housing/400-crew life claims
5. Extend service circulation according to actual department support, keeping guest and service interfaces separated; current wet/market extension is only one interface
6. Verify ordinary loaded-cart access, usable equipment and visible staff work for each completed programme. Architecture alone cannot certify throughput, staff routines or full simulation

## Practical inferred subrooms

Pump galleries, switch rooms, clean/dirty textile staging, pantry/dishwash zones, service shafts and vestibules can be useful design decompositions. None becomes a compulsory additional room solely from generic ship knowledge. Place each within the existing programme, justify its function, and keep inferred design separate from explicit source requirements. The master explicitly does not require a propulsion simulator, full fluid network, harmful gas simulation, hazardous-material loop, diagnosis gameplay or piloting system.

## Audit boundary

This pass inspects the authoritative master, its current-application overrides, the retained technical blueprint pixels, current programme/layout/allocation data, lower staff and arrivals/fusion/synthesis/Vesper builders. Guest/VIP pools and theater are owned by the separate amenity audit; only source-explicit backstage, wet-service, towel and finishing interfaces are identified here. No archive-wide variant sweep, build/import, engine change, existing file edits, backup recovery or commits were performed.

## Source coverage and completion gate

- Checked: authoritative v0.3 master relevant complete sections, tables and reference crosswalk
- Checked: current-application overrides
- Checked: technical_reference.png full sheet and enlarged emergency/service panel
- Checked: shared_staff_room.png actual pixels
- Checked: clinical and shared-crew programme handoffs
- Checked: current programme ledger, whole-ship layout, D03 allocation metadata
- Checked: arrivals/fusion, synthesis, lower staff network and Vesper finishing builders

- Relevant not examined here: historical_atlas.pdf full medical and crew plan pixels (allocation metadata/handoffs only checked)
- Relevant not examined here: public blueprint/public_reference.png and habitat blueprint pixels: separate amenity audit must reconcile any additional service labels
- Relevant not examined here: staff_and_service style images REF-523733d277, REF-9e43a46063, REF-35f53a078f and staff_lift_reference_20261003.jpg: not inspected here; district-specific architectural comparison still required
- Relevant not examined here: full remaining reference-index imagery beyond bounded technical and shared-crew sources

Complete bounded technical-sheet/master inventory, not confirmed exhaustive inventory of every retained image. Do not start a shipwide exhaustive-inventory claim until the listed relevant source gaps are closed or scoped by the parent.

## Actual crew living subspaces

The inspected shared-room photograph visibly contains two-level rest supports, berth curtains, access ladder, individual lighting, shelves, wardrobe and drawers. Its layout is functional reference, not an approved stack height or ship-species dimension recipe. The shared-crew handoff confirms approved modest rest frame, curtain/track, accessible personal storage and individual task-light/shelf components, while explicitly leaving host room, roommate ID, berth-key migration and fit unresolved. Current master application additionally requires bathing/changing privacy. These are support subspaces/fixtures inside crew homes, not five extra rooms or five added berths. The JSON records each distinctly. Historical 199 doubles plus C036 single gave399 places, with separate employee berth giving400; shared-home integration must reconcile this stale private-player arithmetic without adding a401st person or duplicate berth.
