extends RefCounted
# Authenticate the whole connected triage addition before projecting its predecessor.
const PROOF := "res://docs/MEDICAL_TRIAGE_ADDITIVE_SUCCESSOR.json"
const PROOF_SHA := "392ca67df45c8cd750e8ab308ac8d61d6aac02b31c45acb10efe65dbd824853e"
const OWNER := "D05_connected_triage_wing_floor"
static var checked := false
static var proof: Dictionary = {}
static var old_text: Dictionary = {}
static var current_compiled: Dictionary = {}
static var old_compiled: Dictionary = {}
static func _relative(path: String) -> String:
	return path.trim_prefix("res://")
static func _ensure() -> void:
	if checked: return
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA,"Exact triage successor proof required")
	proof=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	assert(proof.schema==1 and proof.owner_id==OWNER)
	for path in proof.postimage_sha256:
		assert(FileAccess.get_sha256("res://"+str(path))==str(proof.postimage_sha256[path]),"Unreviewed triage postimage: "+str(path))
	for path in proof.predecessors:
		var spec: Dictionary=proof.predecessors[path]
		var retained := "res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained)==str(spec.sha256),"Triage predecessor changed: "+str(path))
		old_text[path]=FileAccess.get_file_as_string(retained)
	for path in proof.exact_patch_reversals:
		var restored := FileAccess.get_file_as_string("res://"+str(path))
		var reversals: Array=proof.exact_patch_reversals[path]
		for index in range(reversals.size()-1,-1,-1):
			var item: Dictionary=reversals[index]
			assert(restored.count(str(item.after))==int(item.count),"Exact triage inverse cardinality")
			restored=restored.replace(str(item.after),str(item.before))
		assert(restored==str(old_text[path]),"Complete predecessor source bytes must survive triage: "+str(path))
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	var old_layout: Dictionary=JSON.parse_string(str(old_text["data/spatial_layout.json"]))
	current_compiled=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
	old_compiled=JSON.parse_string(str(old_text["data/generated/structural_meshes.json"]))
	for pair in [[layout,old_layout,proof.new_layout_record],[current_compiled,old_compiled,proof.new_compiled_record]]:
		var retained: Array=[]
		var ids: Dictionary={}
		var additions := 0
		for record in pair[0].regions:
			assert(not ids.has(str(record.id)),"Duplicate current owner")
			ids[str(record.id)]=true
			if str(record.id)==OWNER:
				assert(record==pair[2],"Exact new triage geometry required")
				additions+=1
			else: retained.append(record)
		assert(additions==1 and retained==pair[1].regions,"Every complete prior record/order must survive")
		assert(pair[0].regions.size()==pair[1].regions.size()+1)
	var globals: Dictionary=layout.duplicate(true)
	var prior_globals: Dictionary=old_layout.duplicate(true)
	globals.erase("regions");prior_globals.erase("regions")
	assert(globals==prior_globals,"All current void/global records must remain exact")
	var summary: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/LAYOUT_COMPILE_CHECKS.json"))
	assert(summary==current_compiled.source_checks)
	assert(summary.medical_triage_additive_preservation.complete_old_records_preserved)
	var added: Dictionary=proof.new_compiled_record
	assert(added.deck=="D05" and float(added.floor_y)==21.0 and float(added.thickness)==.24 and float(added.structural_area_m2)==544.0)
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D05_MEDICAL_WELCOME_RUNTIME.json"))
	var prior: Dictionary=JSON.parse_string(str(old_text["data/architecture/D05_MEDICAL_WELCOME_RUNTIME.json"]))
	for key in ["root_name","persistent_id","origin_xyz","core_file","core_root_name","core_identity","floor_owner","floor_y_m","floor_thickness_m","floor_area_m2","source_clinical_fit_targets","unchanged_global_systems"]:
		assert(data[key]==prior[key],"Retained medical identity/system changed: "+str(key))
	assert(data.fixtures.slice(0,prior.fixtures.size())==prior.fixtures)
	assert(data.floor_owners==[prior.floor_owner,OWNER] and data.new_floor_owner==OWNER and data.new_floor_area_m2==544)
	assert(data.instances.size()==74 and data.fixtures.size()==34 and data.rooms.size()==8 and data.door_sources.size()==8)
	assert(not data.medical_or_repair_gameplay and not data.first_pass_quality_accepted)
	var plan: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/packages/medical/D05_MEDICAL_SECTION_PLAN.json"))
	var old_plan: Dictionary=JSON.parse_string(str(old_text["data/architecture/packages/medical/D05_MEDICAL_SECTION_PLAN.json"]))
	var restored_plan: Dictionary=plan.duplicate(true)
	var programmes: Array=restored_plan.programmes
	for programme in programmes:
		if programme.programme_key!="D05_directory_01": continue
		assert(programme.connected_triage_source010==proof.new_programme_metadata)
		programme.erase("connected_triage_source010")
		for child in programme.children:
			if proof.plan_revisions.has(str(child.id)):
				var revision: Dictionary=proof.plan_revisions[str(child.id)]
				assert(child==revision.after)
				child.clear();child.merge(revision.before,true)
	assert(restored_plan==old_plan,"Only four unbuilt pod rectangles and explicit source metadata may change")
	checked=true
static func retained_text(path: String) -> String:
	_ensure()
	if not checked: return ""
	var relative := _relative(path)
	if old_text.has(relative): return str(old_text[relative])
	return FileAccess.get_file_as_string("res://"+relative)
static func retained_sha256(path: String) -> String:
	_ensure()
	if not checked: return ""
	var relative := _relative(path)
	if proof.predecessors.has(relative): return str(proof.predecessors[relative].sha256)
	return FileAccess.get_sha256("res://"+relative)
static func is_current_compiled(value: Dictionary) -> bool:
	_ensure()
	return checked and value==current_compiled
static func retained_compiled(value: Dictionary) -> Dictionary:
	_ensure()
	if not checked: return {}
	if value!=current_compiled and value!=old_compiled:
		push_error("Caller is not authenticated current or immediate predecessor compiled data")
		return {}
	return old_compiled
static func retained_floor_children(floors: Node) -> Array:
	_ensure()
	if not checked or floors==null: return []
	if floors.get_child_count()!=current_compiled.regions.size():
		push_error("Complete actual triage-era floor roster required")
		return []
	var expected: Dictionary={}
	for record in current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	for owner in floors.get_children():
		var ident := str(owner.name)
		if not expected.has(ident) or seen.has(ident) or owner.get_meta("region_id","")!=ident:
			push_error("Unknown, duplicate or mislabeled actual floor owner")
			return []
		seen[ident]=true
		if ident==OWNER:
			if owner.find_children("*","StaticBody3D",true,false).size()!=1:
				push_error("New triage slab requires its one actual compiler contact owner")
				return []
		else: retained.append(owner)
	if seen.size()!=current_compiled.regions.size() or retained.size()!=old_compiled.regions.size() or not seen.has(OWNER):
		push_error("Incomplete actual triage floor owners")
		return []
	return retained
static func validate_current(floors: Node) -> Dictionary:
	var retained: Array=retained_floor_children(floors)
	if not checked or retained.size()!=old_compiled.regions.size(): return {}
	var result: Dictionary=proof.duplicate(true)
	result["validation_completed"]=true
	return result
