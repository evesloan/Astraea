extends RefCounted
# Exact additive roster gate shared by retained section regressions.
const PROOF := "res://docs/SECONDARY_ENGINEERING_ADDITIVE_PRESERVATION.json"
const PROOF_SHA := "ee806149c47846c5d2a2374269615f2c13c681b949cea8f2ceb05ad81856e6cc"
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_RUNTIME.json"
const CONTRACT_SHA := "bef8d64a2238d96a11907083c1ad68aa3db484f71e504299d0c0613ccd9606da"
const SECTION_PROOF := "res://docs/SECONDARY_ENGINEERING_CELL_PRESERVATION.json"
const SECTION_PROOF_SHA := "e4315c57b22eb3c2a7629d7c32444632e488e5cbc9a108cd8dc318e97a2e8051"
# Narrow theater successor: unchanged engineering proofs remain authoritative.
const THEATER_PROPOSAL := "res://docs/THEATER_ADDITIVE_SUCCESSOR_PROPOSAL.json"
const THEATER_PROPOSAL_SHA := "1fa5809a6dfa77f77986a53a3e56f4fbfafdb7f5ab2d9ba1c40080bd6fe0d183"
const THEATER_SUCCESSOR := "res://docs/SECONDARY_ENGINEERING_THEATER_SUCCESSOR.json"
const THEATER_SUCCESSOR_SHA := "bf3dfe3e9b7eb4fe1f916269a6e7fde3a636f226a4f6cd02a66c13e3e0dac6af"
const PREVIOUS_GUARD_SHA := "71fbbeed165ed72f1949673142447109e800db075e472192f7099d961818113f"
const RETAINED_LAYOUT := "data/architecture/packages/theater/retained/spatial_layout.json"
const RETAINED_COMPILED := "data/architecture/packages/theater/retained/structural_meshes.json"
const ALLOWED_THEATER_LAYOUT_IDS := ["D12_theater_gallery_seating", "D12_theater_rear_public_returns", "D12_theater_foyer_landings", "D12_theater_stair_upper_landing", "D13_theater_gallery_seating", "D13_theater_rear_public_returns", "D13_theater_foyer_landings", "D13_theater_stair_upper_landing", "D11_theater_flat_00", "D11_theater_foundation_00", "D11_theater_foundation_01", "D11_theater_foundation_02", "D11_theater_foundation_03", "D11_theater_foundation_04", "D11_theater_foundation_05", "D11_theater_foundation_06", "D11_theater_receiving_bridge"]
const ALLOWED_THEATER_COMPILED_IDS := ["D11_theater_flat_00", "D11_theater_foundation_00", "D11_theater_foundation_01", "D11_theater_foundation_02", "D11_theater_foundation_03", "D11_theater_foundation_04", "D11_theater_foundation_05", "D11_theater_foundation_06", "D11_theater_receiving_bridge"]
const THEATER_INPUT_PATHS := ["data/spatial_layout.json", "data/generated/structural_meshes.json", "scripts/ship.gd"]

static func section_proof() -> Dictionary:
	assert(FileAccess.get_sha256(SECTION_PROOF)==SECTION_PROOF_SHA)
	return JSON.parse_string(FileAccess.get_file_as_string(SECTION_PROOF))

static func validate_pinned_input(path: String, historical_sha: String) -> void:
	var actual := FileAccess.get_sha256("res://"+path)
	var chain := section_proof()
	if not chain.explicit_runtime_pin_successors.has(path):
		assert(actual==historical_sha,"No reviewed byte successor: "+path)
		return
	var previous: Dictionary = chain.explicit_runtime_pin_successors[path]
	assert(historical_sha==str(previous.historical_sha256),"Unexpected historical input hash: "+path)
	if actual==historical_sha: return
	if actual==str(previous.section_sha256):
		if previous.has("capture_audit_file"):
			assert(FileAccess.get_sha256("res://"+str(previous.capture_audit_file))==str(previous.capture_audit_sha256))
		return
	if path=="scripts/presentation.gd" and actual=="a63a5c72f76af86cb81d2bb7dcc2bf9330d0a0583862c2fea5e7f487f5628b1c":
		assert(load("res://tests/engineering_controls_listener_successor.gd").validate_successor(path,historical_sha,actual,previous))
		return
	if path=="scripts/presentation.gd":
		assert(load("res://tests/engineering_signage_capture_successor.gd").validate_successor(path,historical_sha,actual,previous))
		return
	var successor := theater_successor()
	assert(successor.explicit_runtime_pin_successors.has(path),"No exact theater input successor: "+path)
	var input: Dictionary = successor.explicit_runtime_pin_successors[path]
	assert(historical_sha==str(input.historical_sha256) and previous.section_sha256==input.section_sha256,"Exact historical/section chain required: "+path)
	if actual==str(input.theater_sha256): return
	assert(preload("res://tests/secondary_engineering_pool_ship_successor.gd").validate_successor(path,historical_sha,actual,previous,input),"No exact reviewed pool ship successor: "+path)

static func validate_owner_count(actual: int, historical: int) -> void:
	assert(historical==261 and actual==271)
	var preserved := validate(JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json")))
	assert(preserved.size()==4,"Complete chained engineering preservation required")

static func validate(compiled: Dictionary) -> Dictionary:
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA)
	assert(FileAccess.get_sha256(CONTRACT)==CONTRACT_SHA)
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	var original: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	var chain := section_proof()
	assert(chain.previous_proof_sha256==PROOF_SHA and chain.previous_contract_sha256==CONTRACT_SHA)
	assert(chain.previous_compiled_sha256==proof.new_compiled_sha256 and chain.previous_layout_sha256==proof.new_layout_sha256)
	var successor := theater_successor()
	for path in THEATER_INPUT_PATHS:
		var actual := FileAccess.get_sha256("res://"+path)
		var input: Dictionary = successor.explicit_runtime_pin_successors[path]
		if actual==str(input.theater_sha256): continue
		var previous: Dictionary = chain.explicit_runtime_pin_successors[path]
		assert(preload("res://tests/secondary_engineering_pool_ship_successor.gd").validate_successor(path,str(previous.historical_sha256),actual,previous,input),"Mixed or unreviewed theater/pool adoption bytes: "+path)
	assert(compiled==JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json")),"Caller compiled records must match pinned bytes")
	assert(compiled.regions.size()==271 and original.old_region_records.size()==258 and proof.new_records.size()==3)
	assert(chain.unchanged_prior_record_count==260 and chain.current_engineering_records.size()==4)
	var current: Dictionary = {}
	for row in compiled.regions:
		assert(not current.has(str(row.id)))
		current[str(row.id)] = row
	for row in original.old_region_records:
		assert(current.has(str(row.id)) and current[str(row.id)]==row,"Retained whole compiled record changed: "+str(row.id))
	for id in proof.new_records:
		if str(id)==str(chain.changed_owner_id):
			assert(proof.new_records[id]==chain.original_host_record and current[id]==chain.changed_host_record)
		else: assert(current.has(id) and current[id]==proof.new_records[id],"Retained engineering owner changed: "+str(id))
	assert(current[str(chain.new_lower_owner_id)]==chain.new_lower_record)
	for id in chain.current_engineering_records:
		assert(current.has(id) and current[id]==chain.current_engineering_records[id])
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	var owned: Array = layout.regions.filter(func(row: Dictionary) -> bool: return str(row.get("authoring_owner",""))=="secondary_engineering_section")
	assert(owned==chain.current_engineering_layout_records,"Exactly four reviewed engineering layout owners required")
	var proposal: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(THEATER_PROPOSAL))
	assert(_validate_theater_records(compiled,layout,proposal),"Exact retained/additive theater roster required")
	return chain.current_engineering_records

static func _exact_keys(value: Dictionary, expected: Array) -> bool:
	var keys := value.keys()
	var wanted := expected.duplicate()
	keys.sort()
	wanted.sort()
	return keys == wanted

static func theater_successor() -> Dictionary:
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA)
	assert(FileAccess.get_sha256(CONTRACT)==CONTRACT_SHA)
	assert(FileAccess.get_sha256(THEATER_PROPOSAL)==THEATER_PROPOSAL_SHA)
	assert(FileAccess.get_sha256(THEATER_SUCCESSOR)==THEATER_SUCCESSOR_SHA)
	var section := section_proof()
	var proposal: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(THEATER_PROPOSAL))
	var successor: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(THEATER_SUCCESSOR))
	assert(successor.schema==1 and not successor.ship_successor_pending)
	assert(successor.previous_engineering_proof_sha256==PROOF_SHA and successor.previous_engineering_contract_sha256==CONTRACT_SHA)
	assert(section.previous_proof_sha256==PROOF_SHA and section.previous_contract_sha256==CONTRACT_SHA)
	assert(successor.previous_engineering_chain_sha256==SECTION_PROOF_SHA and proposal.previous_engineering_chain_sha256==SECTION_PROOF_SHA)
	assert(successor.previous_engineering_guard_sha256==PREVIOUS_GUARD_SHA and proposal.previous_engineering_guard_sha256==PREVIOUS_GUARD_SHA)
	assert(successor.theater_proposal_path==THEATER_PROPOSAL.trim_prefix("res://") and successor.theater_proposal_sha256==THEATER_PROPOSAL_SHA)
	assert(successor.previous_layout_sha256==section.new_layout_sha256 and successor.previous_layout_sha256==proposal.previous_layout_sha256)
	assert(successor.previous_compiled_sha256==section.new_compiled_sha256 and successor.previous_compiled_sha256==proposal.previous_compiled_sha256)
	assert(successor.new_layout_sha256==proposal.new_layout_sha256 and successor.new_compiled_sha256==proposal.new_compiled_sha256)
	assert(successor.previous_layout_count==268 and successor.previous_compiled_count==262)
	assert(successor.new_layout_count==285 and successor.new_compiled_count==271)
	assert(successor.original_compiled_count==258 and successor.current_engineering_owner_count==4)
	assert(proposal.unchanged_prior_layout_record_count==268 and proposal.unchanged_prior_compiled_record_count==262)
	assert(proposal.new_layout_record_count==285 and proposal.new_compiled_record_count==271)
	assert(proposal.exact_prior_layout_records_preserved and proposal.exact_prior_compiled_records_preserved)
	assert(successor.allowed_new_layout_ids==ALLOWED_THEATER_LAYOUT_IDS and successor.allowed_new_compiled_ids==ALLOWED_THEATER_COMPILED_IDS)
	assert(_exact_keys(proposal.new_layout_records,ALLOWED_THEATER_LAYOUT_IDS) and _exact_keys(proposal.new_compiled_records,ALLOWED_THEATER_COMPILED_IDS))
	assert(successor.retained_layout_path==RETAINED_LAYOUT and successor.retained_compiled_path==RETAINED_COMPILED)
	assert(FileAccess.get_sha256("res://"+RETAINED_LAYOUT)==section.new_layout_sha256)
	assert(FileAccess.get_sha256("res://"+RETAINED_COMPILED)==section.new_compiled_sha256)
	assert(proposal.input_package_sha256[RETAINED_LAYOUT]==section.new_layout_sha256 and proposal.input_package_sha256[RETAINED_COMPILED]==section.new_compiled_sha256)
	assert(_exact_keys(successor.explicit_runtime_pin_successors,THEATER_INPUT_PATHS))
	for path in THEATER_INPUT_PATHS:
		var previous: Dictionary = section.explicit_runtime_pin_successors[path]
		var current: Dictionary = successor.explicit_runtime_pin_successors[path]
		assert(current.historical_sha256==previous.historical_sha256 and current.section_sha256==previous.section_sha256,"Historical input chain changed: "+path)
		assert(str(current.theater_sha256).length()==64 and current.theater_sha256!=current.section_sha256)
	assert(successor.explicit_runtime_pin_successors["data/spatial_layout.json"].theater_sha256==successor.new_layout_sha256)
	assert(successor.explicit_runtime_pin_successors["data/generated/structural_meshes.json"].theater_sha256==successor.new_compiled_sha256)
	return successor

# Pure record checks are separate from byte pins so negative tests can exercise
# preserved records and exact allowlists even if mutated input hashes are repinned.
static func _validate_theater_records(compiled: Dictionary, layout: Dictionary, proposal: Dictionary) -> bool:
	var old_compiled: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://"+RETAINED_COMPILED))
	var old_layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://"+RETAINED_LAYOUT))
	assert(old_compiled.regions.size()==262 and old_layout.regions.size()==268)
	assert(compiled.regions.size()==271 and layout.regions.size()==285)
	for spec in [[compiled,old_compiled,proposal.new_compiled_records,ALLOWED_THEATER_COMPILED_IDS],[layout,old_layout,proposal.new_layout_records,ALLOWED_THEATER_LAYOUT_IDS]]:
		var current: Dictionary = {}
		var retained: Dictionary = {}
		for row in spec[0].regions:
			assert(not current.has(str(row.id)),"Duplicate current owner: "+str(row.id))
			current[str(row.id)] = row
		for row in spec[1].regions:
			assert(not retained.has(str(row.id)),"Duplicate retained owner: "+str(row.id))
			retained[str(row.id)] = row
			assert(current.has(str(row.id)) and current[str(row.id)]==row,"Retained whole record changed: "+str(row.id))
		var additions: Array = spec[3]
		assert(_exact_keys(current,retained.keys()+additions),"Unexpected or missing theater owner")
		for id in additions:
			assert(not retained.has(id) and current[id]==spec[2][id],"Theater addition identity changed: "+str(id))
		var retained_order: Array = []
		for row in spec[0].regions:
			if retained.has(str(row.id)): retained_order.append(row)
		assert(retained_order==spec[1].regions,"Retained record order changed")
	var current_globals := layout.duplicate(true)
	var old_globals := old_layout.duplicate(true)
	current_globals.erase("regions")
	old_globals.erase("regions")
	assert(current_globals==old_globals,"Prior layout/void contract changed")
	for id in ALLOWED_THEATER_LAYOUT_IDS:
		if not ALLOWED_THEATER_COMPILED_IDS.has(id):
			assert(proposal.new_layout_records[id].get("provided_by_asset",false)==true,"Upper source-owned theater surface must remain asset-only")
	return true
