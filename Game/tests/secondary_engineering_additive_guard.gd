extends RefCounted
# Exact additive roster gate shared by retained section regressions.
const PROOF := "res://docs/SECONDARY_ENGINEERING_ADDITIVE_PRESERVATION.json"
const PROOF_SHA := "ee806149c47846c5d2a2374269615f2c13c681b949cea8f2ceb05ad81856e6cc"
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_RUNTIME.json"
const CONTRACT_SHA := "bef8d64a2238d96a11907083c1ad68aa3db484f71e504299d0c0613ccd9606da"
static func validate(compiled: Dictionary) -> Dictionary:
	assert(FileAccess.get_sha256(PROOF) == PROOF_SHA)
	assert(FileAccess.get_sha256(CONTRACT) == CONTRACT_SHA)
	var proof: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	var original: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json") == proof.new_compiled_sha256)
	assert(FileAccess.get_sha256("res://data/spatial_layout.json") == proof.new_layout_sha256)
	assert(compiled.regions.size() == 261 and original.old_region_records.size() == 258 and proof.new_records.size() == 3)
	var current: Dictionary = {}
	for row in compiled.regions:
		assert(not current.has(str(row.id)))
		current[str(row.id)] = row
	for row in original.old_region_records:
		assert(current.has(str(row.id)) and current[str(row.id)] == row, "Retained whole compiled record changed: " + str(row.id))
	for id in proof.new_records:
		assert(current.has(id) and current[id] == proof.new_records[id], "Unapproved engineering compiled owner: " + str(id))
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	var owned: Array = layout.regions.filter(func(row: Dictionary) -> bool: return str(row.get("authoring_owner", "")) == "secondary_engineering_section")
	assert(owned == proof.new_layout_records, "Exactly the reviewed three engineering layout owners required")
	return proof.new_records
