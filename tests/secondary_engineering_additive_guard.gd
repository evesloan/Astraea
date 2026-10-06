extends RefCounted
# Exact additive roster gate shared by retained section regressions.
const PROOF := "res://docs/SECONDARY_ENGINEERING_ADDITIVE_PRESERVATION.json"
const PROOF_SHA := "ee806149c47846c5d2a2374269615f2c13c681b949cea8f2ceb05ad81856e6cc"
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_RUNTIME.json"
const CONTRACT_SHA := "bef8d64a2238d96a11907083c1ad68aa3db484f71e504299d0c0613ccd9606da"
const SECTION_PROOF := "res://docs/SECONDARY_ENGINEERING_CELL_PRESERVATION.json"
const SECTION_PROOF_SHA := "e4315c57b22eb3c2a7629d7c32444632e488e5cbc9a108cd8dc318e97a2e8051"
static func section_proof() -> Dictionary:
	assert(FileAccess.get_sha256(SECTION_PROOF)==SECTION_PROOF_SHA)
	return JSON.parse_string(FileAccess.get_file_as_string(SECTION_PROOF))

static func validate_pinned_input(path: String, historical_sha: String) -> void:
	var actual := FileAccess.get_sha256("res://"+path)
	if actual==historical_sha: return
	var chain := section_proof()
	assert(chain.explicit_runtime_pin_successors.has(path),"No reviewed byte successor: "+path)
	var successor: Dictionary = chain.explicit_runtime_pin_successors[path]
	assert(historical_sha==str(successor.historical_sha256) and actual==str(successor.section_sha256),"Exact historical/current byte chain required: "+path)
	if successor.has("capture_audit_file"):
		assert(FileAccess.get_sha256("res://"+str(successor.capture_audit_file))==str(successor.capture_audit_sha256))

static func validate_owner_count(actual: int, historical: int) -> void:
	assert(historical==261 and actual==262)
	validate(JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json")))

static func validate(compiled: Dictionary) -> Dictionary:
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA)
	assert(FileAccess.get_sha256(CONTRACT)==CONTRACT_SHA)
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	var original: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	var chain := section_proof()
	assert(chain.previous_proof_sha256==PROOF_SHA and chain.previous_contract_sha256==CONTRACT_SHA)
	assert(chain.previous_compiled_sha256==proof.new_compiled_sha256 and chain.previous_layout_sha256==proof.new_layout_sha256)
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==chain.new_compiled_sha256)
	assert(FileAccess.get_sha256("res://data/spatial_layout.json")==chain.new_layout_sha256)
	assert(compiled.regions.size()==262 and original.old_region_records.size()==258 and proof.new_records.size()==3)
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
	return chain.current_engineering_records
