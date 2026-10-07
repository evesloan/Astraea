extends RefCounted
# Authenticated medical projection for unchanged historical assertions.
# Every projected byte/owner is checked against the full current postimage first.
const PROOF := "res://docs/MEDICAL_ADDITIVE_SUCCESSOR.json"
const PROOF_SHA := "83702b3cce6e19373e44d4ff14d7489e8b82c5b566d711958ab1f62acd8ed971"
const OWNER := "D05_forward_waiting_support_floor"
const CURRENT_ONLY := ["docs/LAYOUT_COMPILE_CHECKS.json"]
static var checked := false
static var proof: Dictionary = {}
static var old_text: Dictionary = {}
static var current_compiled: Dictionary = {}

static func _relative(path: String) -> String:
	return path.trim_prefix("res://")

static func _ensure() -> void:
	if checked: return
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA,"Medical proof bytes changed")
	proof=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	assert(proof.schema==1 and proof.owner_id==OWNER)
	for path in proof.postimage_sha256:
		assert(FileAccess.get_sha256("res://"+str(path))==str(proof.postimage_sha256[path]),"Unreviewed medical postimage: "+str(path))
	for path in proof.predecessors:
		var spec: Dictionary=proof.predecessors[path]
		var retained_path := "res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained_path)==str(spec.sha256),"Medical predecessor changed: "+str(path))
		old_text[path]=FileAccess.get_file_as_string(retained_path)
	for path in proof.exact_patch_reversals:
		var restored := FileAccess.get_file_as_string("res://"+str(path))
		var reversals: Array=proof.exact_patch_reversals[path]
		for i in range(reversals.size()-1,-1,-1):
			var replacement: Dictionary=reversals[i]
			assert(restored.count(str(replacement.after))==int(replacement.count),"Patch inverse cardinality: "+str(path))
			restored=restored.replace(str(replacement.after),str(replacement.before))
		assert(restored.sha256_text()==str(proof.predecessors[path].sha256),"Every historical assertion/byte must survive: "+str(path))
	var old_layout: Dictionary=JSON.parse_string(old_text["data/spatial_layout.json"])
	var old_compiled: Dictionary=JSON.parse_string(old_text["data/generated/structural_meshes.json"])
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	current_compiled=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	assert(old_layout.regions.size()==285 and old_compiled.regions.size()==271 and old_layout.voids.size()==28)
	assert(layout.regions.size()==286 and current_compiled.regions.size()==272 and layout.voids.size()==28)
	var summary: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/LAYOUT_COMPILE_CHECKS.json"))
	assert(summary==current_compiled.source_checks,"Compile receipt must equal the current actual compiled checks")
	for pair in [[layout,old_layout,proof.new_layout_record],[current_compiled,old_compiled,proof.new_compiled_record]]:
		var retained: Array=[]
		var ids: Dictionary={}
		var found := 0
		for row in pair[0].regions:
			assert(not ids.has(str(row.id)),"Duplicate medical/current owner")
			ids[str(row.id)]=true
			if str(row.id)==OWNER:
				assert(row==pair[2],"Exact authenticated medical record required")
				found+=1
			else: retained.append(row)
		assert(found==1 and retained==pair[1].regions,"All current predecessor records and order must remain exact")
	var globals: Dictionary=layout.duplicate(true)
	var prior_globals: Dictionary=old_layout.duplicate(true)
	globals.erase("regions");prior_globals.erase("regions")
	assert(globals==prior_globals,"All old layout globals and void records must remain exact")
	var record: Dictionary=proof.new_compiled_record
	assert(record.deck=="D05" and absf(float(record.floor_y)-21.0)<.000001 and absf(float(record.thickness)-.24)<.000001)
	assert(absf(float(record.structural_area_m2)-350.72)<.000001)
	var old_core: Dictionary=JSON.parse_string(old_text["data/architecture/FORWARD_PUBLIC_CORE.json"])
	var core: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/FORWARD_PUBLIC_CORE.json"))
	assert(core.enclosure_file==proof.core_derivative_file)
	assert(not old_core.has(str(proof.core_interface_key)) and core.has(str(proof.core_interface_key)))
	core.erase(str(proof.core_interface_key));core.enclosure_file=old_core.enclosure_file
	assert(core==old_core,"Only the core filename and explicit D05 interface may change")
	checked=true

static func retained_text(path: String) -> String:
	_ensure()
	if not checked: return ""
	var relative := _relative(path)
	if old_text.has(relative) and relative not in CURRENT_ONLY: return str(old_text[relative])
	return FileAccess.get_file_as_string(path if path.begins_with("res://") else "res://"+path)

static func retained_sha256(path: String) -> String:
	_ensure()
	if not checked: return ""
	var relative := _relative(path)
	if proof.predecessors.has(relative) and relative not in CURRENT_ONLY: return str(proof.predecessors[relative].sha256)
	return FileAccess.get_sha256(path if path.begins_with("res://") else "res://"+path)

static func retained_compiled(value: Dictionary) -> Dictionary:
	_ensure()
	if not checked: return {}
	var prior: Dictionary=JSON.parse_string(old_text["data/generated/structural_meshes.json"])
	if value!=current_compiled and value!=prior:
		push_error("Caller is neither authenticated full current nor exact retained predecessor")
		return {}
	return prior

static func retained_floor_children(floors: Node) -> Array:
	_ensure()
	if not checked: return []
	if floors==null or floors.get_child_count()!=272:
		push_error("Medical successor requires all272 actual owners")
		return []
	var expected: Dictionary={}
	for record in current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	for owner in floors.get_children():
		var id := str(owner.name)
		if not expected.has(id) or seen.has(id):
			push_error("Unknown or duplicate loaded owner")
			return []
		if owner.get_meta("region_id","")!=id:
			push_error("Actual owner identity mismatch")
			return []
		seen[id]=true
		if id==OWNER:
			var contacts := owner.find_children("*","StaticBody3D",true,false)
			if contacts.size()!=1:
				push_error("Medical slab must have one compiler contact owner")
				return []
		else: retained.append(owner)
	if seen.size()!=272 or retained.size()!=271 or not seen.has(OWNER):
		push_error("Incomplete actual floor owner roster")
		return []
	return retained

static func retained_owner_count(floors: Node) -> int:
	var retained: Array=retained_floor_children(floors)
	if not checked or retained.size()!=271: return -1
	return retained.size()

static func retained_json(path: String) -> Dictionary:
	var content: String=retained_text(path)
	if not checked or content.is_empty(): return {}
	var value: Variant=JSON.parse_string(content)
	if not value is Dictionary:
		push_error("Expected an authenticated dictionary")
		return {}
	return value

static func validate_current(floors: Node = null) -> Dictionary:
	_ensure()
	if not checked: return {}
	if floors==null:
		push_error("Actual loaded floor root required for completed medical validation")
		return {}
	var retained: Array=retained_floor_children(floors)
	if retained.size()!=271: return {}
	var result: Dictionary=proof.duplicate(true)
	result["validation_completed"]=true
	return result
