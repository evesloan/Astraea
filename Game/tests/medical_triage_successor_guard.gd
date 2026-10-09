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
# One exact later pool-finish helper; every other triage input stays directly hashed.
const POOL_FINISH_HELPER := "tests/grand_pool_feature_builder_successor.gd"
const POOL_FINISH_GUARD := "res://tests/grand_pool_finish_successor.gd"
const POOL_FINISH_GUARD_SHA := "ca9b3300e47a1c5413ecd43390e9e839a6d07acfab7b847c085f979b3cb0b596"
static func _pool_finish_text(path: String) -> String:
	var relative := _relative(path)
	if relative != POOL_FINISH_HELPER: return _botanical_current_text(relative)
	assert(FileAccess.get_sha256(POOL_FINISH_GUARD)==POOL_FINISH_GUARD_SHA,"Exact pool finish projection source required")
	return load(POOL_FINISH_GUARD).retained_text(relative)
static func _pool_finish_sha256(path: String) -> String:
	var relative := _relative(path)
	if relative == POOL_FINISH_HELPER: return _pool_finish_text(relative).sha256_text()
	_botanical_ensure()
	if relative in botanical_proof.projected_paths: return _botanical_current_text(relative).sha256_text()
	return FileAccess.get_sha256("res://"+relative)
static func _ensure() -> void:
	if checked: return
	_botanical_ensure()
	assert(FileAccess.get_sha256(PROOF)==PROOF_SHA,"Exact triage successor proof required")
	proof=JSON.parse_string(FileAccess.get_file_as_string(PROOF))
	assert(proof.schema==1 and proof.owner_id==OWNER)
	for path in proof.postimage_sha256:
		assert(_pool_finish_sha256(str(path))==str(proof.postimage_sha256[path]),"Unreviewed triage postimage: "+str(path))
	for path in proof.predecessors:
		var spec: Dictionary=proof.predecessors[path]
		var retained := "res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained)==str(spec.sha256),"Triage predecessor changed: "+str(path))
		old_text[path]=FileAccess.get_file_as_string(retained)
	for path in proof.exact_patch_reversals:
		var restored := _botanical_current_text("res://"+str(path))
		var reversals: Array=proof.exact_patch_reversals[path]
		for index in range(reversals.size()-1,-1,-1):
			var item: Dictionary=reversals[index]
			assert(restored.count(str(item.after))==int(item.count),"Exact triage inverse cardinality")
			restored=restored.replace(str(item.after),str(item.before))
		assert(restored==str(old_text[path]),"Complete predecessor source bytes must survive triage: "+str(path))
	var layout: Dictionary=JSON.parse_string(_botanical_current_text("res://data/spatial_layout.json"))
	var old_layout: Dictionary=JSON.parse_string(str(old_text["data/spatial_layout.json"]))
	current_compiled=JSON.parse_string(_botanical_current_text("res://data/generated/structural_meshes.json"))
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
	var summary: Dictionary=JSON.parse_string(_botanical_current_text("res://docs/LAYOUT_COMPILE_CHECKS.json"))
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
	return _pool_finish_text(relative)
static func retained_sha256(path: String) -> String:
	_ensure()
	if not checked: return ""
	var relative := _relative(path)
	if proof.predecessors.has(relative): return str(proof.predecessors[relative].sha256)
	return _pool_finish_sha256(relative)
static func is_current_compiled(value: Dictionary) -> bool:
	value=load("res://tests/d12_pair_successor_guard.gd").project_compiled(value)
	_ensure()
	return checked and (value==current_compiled or value==botanical_current_compiled or value==team_lounge_current_compiled or value==movement_current_compiled or value==moss_current_compiled or value==sports_care_current_compiled or value==night_current_compiled or value==laundry_current_compiled or value==crew_current_compiled)
static func retained_compiled(value: Dictionary) -> Dictionary:
	value=load("res://tests/d12_pair_successor_guard.gd").project_compiled(value)
	_ensure()
	if not checked: return {}
	if value==crew_current_compiled: value=laundry_current_compiled
	if value==laundry_current_compiled: value=night_current_compiled
	if value==night_current_compiled: value=sports_care_current_compiled
	if value==sports_care_current_compiled: value=moss_current_compiled
	if value==moss_current_compiled: value=movement_current_compiled
	if value==movement_current_compiled: value=team_lounge_current_compiled
	if value==team_lounge_current_compiled: value=botanical_current_compiled
	if value==botanical_current_compiled: value=current_compiled
	if value!=current_compiled and value!=old_compiled:
		push_error("Caller is not authenticated current or immediate predecessor compiled data")
		return {}
	return old_compiled
static func retained_floor_children(floors: Node) -> Array:
	_ensure()
	if not checked or floors==null: return []
	var actual_owners: Array=_botanical_floor_children(floors)
	if actual_owners.size()!=current_compiled.regions.size():
		push_error("Complete actual triage-era floor roster required")
		return []
	var expected: Dictionary={}
	for record in current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	for owner in actual_owners:
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
	_crew_validate_runtime(floors.get_parent().get_parent())
	_laundry_validate_runtime(floors.get_parent().get_parent())
	_night_validate_runtime(floors.get_parent().get_parent())
	_upper_hull_validate_runtime(floors.get_parent().get_parent())
	_star_fitted_validate_runtime(floors.get_parent().get_parent())
	var result: Dictionary=proof.duplicate(true)
	result["validation_completed"]=true
	return result
# BOTANICAL_EXACT_SECTION_BEGIN
# One bounded extension of this existing consumer, not a new adapter chain.
const BOTANICAL_PROOF := "res://data/architecture/packages/botanical_court/BOTANICAL_RUNTIME_PROOF.json"
const BOTANICAL_PROOF_SHA := "be4f1f97e4c573ce4f53ec29e1560ceaaea9c6447be6749e59b9cc02c38a8c1d"
static var botanical_checked := false
static var botanical_proof: Dictionary = {}
static var botanical_predecessor_text: Dictionary = {}
static var botanical_current_compiled: Dictionary = {}

static func _botanical_ensure() -> void:
	if botanical_checked: return
	_team_lounge_ensure()
	assert(FileAccess.get_sha256(BOTANICAL_PROOF)==BOTANICAL_PROOF_SHA,"Exact closed botanical proof required")
	botanical_proof=JSON.parse_string(FileAccess.get_file_as_string(BOTANICAL_PROOF))
	assert(botanical_proof.schema==1 and botanical_proof.added_owner_ids.size()==2)
	for path in botanical_proof.current_sha256:
		var observed_sha: String=_team_lounge_current_sha256("res://"+str(path))
		if str(path)=="tests/validate_botanical_receiving_access.gd":
			observed_sha=_moss_current_sha256("res://"+str(path))
		assert(observed_sha==str(botanical_proof.current_sha256[path]),"Unreviewed botanical input: "+str(path))
	for path in botanical_proof.predecessors:
		var spec: Dictionary=botanical_proof.predecessors[path]
		var retained_path: String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained_path)==str(spec.sha256),"Botanical predecessor changed: "+str(path))
		botanical_predecessor_text[path]=FileAccess.get_file_as_string(retained_path)
	var own_source := _team_lounge_current_text("res://tests/medical_triage_successor_guard.gd")
	var begin: String="# BOTANICAL_EXACT_SECTION_"+"BEGIN\n"
	var end: String="# BOTANICAL_EXACT_SECTION_"+"END\n"
	assert(own_source.count(begin)==1 and own_source.count(end)==1)
	var start := own_source.find(begin)
	var finish := own_source.find(end)+end.length()
	var block := own_source.substr(start,finish-start)
	assert(block.count(BOTANICAL_PROOF_SHA)==1)
	assert(block.replace(BOTANICAL_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(botanical_proof.integration_block_normalized_sha256),"Exact integrated proof logic required")
	var recovered := own_source.substr(0,start)+own_source.substr(finish)
	for edit in botanical_proof.consumer_inverse_edits:
		assert(recovered.count(str(edit.after))==int(edit.count),"Exact consumer inverse cardinality")
		recovered=recovered.replace(str(edit.after),str(edit.before))
	assert(recovered==str(botanical_predecessor_text["tests/medical_triage_successor_guard.gd"]),"All previous pool/medical consumer bytes must survive")
	for path in botanical_proof.exact_inverse_edits:
		var restored := _team_lounge_current_text("res://"+str(path))
		for edit in botanical_proof.exact_inverse_edits[path]:
			assert(restored.count(str(edit.after))==int(edit.count),"Exact botanical source inverse cardinality")
			restored=restored.replace(str(edit.after),str(edit.before))
		assert(restored==str(botanical_predecessor_text[path]),"Every preceding compiler/ship byte must survive")
	var layout: Dictionary=JSON.parse_string(_team_lounge_current_text("res://data/spatial_layout.json"))
	var prior_layout: Dictionary=JSON.parse_string(str(botanical_predecessor_text["data/spatial_layout.json"]))
	botanical_current_compiled=JSON.parse_string(_team_lounge_current_text("res://data/generated/structural_meshes.json"))
	var prior_compiled: Dictionary=JSON.parse_string(str(botanical_predecessor_text["data/generated/structural_meshes.json"]))
	for pair in [[layout,prior_layout,botanical_proof.added_layout_records],[botanical_current_compiled,prior_compiled,botanical_proof.added_compiled_records]]:
		var wanted: Array=pair[1].regions.duplicate(true)
		wanted.append_array(pair[2])
		assert(pair[0].regions==wanted,"Exact complete old records/order plus exactly two approved owners required")
		var seen: Dictionary={}
		for record in pair[0].regions:
			assert(not seen.has(str(record.id)),"Duplicate botanical/current owner")
			seen[str(record.id)]=true
	var global_now: Dictionary=layout.duplicate(true)
	var global_old: Dictionary=prior_layout.duplicate(true)
	global_now.erase("regions");global_old.erase("regions")
	assert(global_now==global_old,"All predecessor void/global records must remain exact")
	var summary: Dictionary=JSON.parse_string(_team_lounge_current_text("res://docs/LAYOUT_COMPILE_CHECKS.json"))
	assert(summary==botanical_current_compiled.source_checks and summary==botanical_proof.compile_summary)
	assert(summary.botanical_court_additive_preservation.complete_old_records_preserved)
	for row in botanical_proof.added_compiled_records:
		assert(row.deck=="D06" and float(row.floor_y)==27.0 and float(row.thickness)==.24 and float(row.structural_area_m2)==120.0)
	assert(botanical_current_compiled.regions.size()==275 and prior_compiled.regions.size()==273)
	botanical_checked=true

static func _botanical_current_text(path: String) -> String:
	_botanical_ensure()
	var relative := _relative(path)
	if relative in botanical_proof.projected_paths: return str(botanical_predecessor_text[relative])
	return FileAccess.get_file_as_string("res://"+relative)

static func _botanical_faces(mesh: Mesh) -> PackedVector3Array:
	var result := PackedVector3Array()
	for surface in range(mesh.get_surface_count()):
		var arrays: Array=mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var indices: Variant=arrays[Mesh.ARRAY_INDEX]
		if indices!=null and indices.size()>0:
			for index in indices: result.append(vertices[index])
		else: result.append_array(vertices)
	return result

static func _botanical_triangles(faces: PackedVector3Array, pose: Transform3D=Transform3D.IDENTITY) -> Dictionary:
	assert(faces.size()%3==0)
	var result: Dictionary={}
	for i in range(0,faces.size(),3):
		var vertices: Array[String]=[]
		for j in range(3): vertices.append(var_to_bytes(pose*faces[i+j]).hex_encode())
		vertices.sort()
		var key: String="|".join(PackedStringArray(vertices))
		result[key]=int(result.get(key,0))+1
	return result

static func _botanical_top(triangles: Array, y: float) -> PackedVector3Array:
	var result := PackedVector3Array()
	for triangle in triangles:
		for p in triangle: result.append(Vector3(float(p[0]),y,float(p[1])))
	return result

static func _botanical_validate_slab(owner: Node3D, record: Dictionary) -> void:
	assert(owner.name==str(record.id) and owner.get_meta("region_id","")==str(record.id))
	assert(owner.global_transform==Transform3D.IDENTITY,"Compiled slab transform changed")
	var y: float=float(record.floor_y)
	var depth: float=float(record.thickness)
	var top := _botanical_top(record.triangles,y)
	var edges := PackedVector3Array()
	for p in top: edges.append(p-Vector3.UP*depth)
	for ring in record.rings:
		for i in range(ring.size()):
			var p: Array=ring[i]
			var q: Array=ring[(i+1)%ring.size()]
			var a:=Vector3(float(p[0]),y,float(p[1]))
			var b:=Vector3(float(q[0]),y,float(q[1]))
			var down_a:=a-Vector3.UP*depth
			var down_b:=b-Vector3.UP*depth
			for v in [a,b,down_b,a,down_b,down_a]: edges.append(v)
	var complete: PackedVector3Array=top.duplicate()
	complete.append_array(edges)
	var arrays: Array=[]
	arrays.resize(Mesh.ARRAY_MAX);arrays[Mesh.ARRAY_VERTEX]=complete
	var expected_mesh:=ArrayMesh.new()
	expected_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var expected_contact: ConcavePolygonShape3D=expected_mesh.create_trimesh_shape()
	var bodies: Array=owner.find_children("*","StaticBody3D",true,false)
	var contacts: Array=owner.find_children("*","CollisionShape3D",true,false)
	assert(bodies.size()==1 and contacts.size()==1,"Every compiler owner needs exactly one contact body/shape")
	var contact: CollisionShape3D=contacts[0] as CollisionShape3D
	assert(not contact.disabled and contact.shape is ConcavePolygonShape3D)
	assert(bodies[0].collision_layer==1 and bodies[0].collision_mask==1)
	assert(_botanical_triangles((contact.shape as ConcavePolygonShape3D).get_faces(),contact.global_transform)==_botanical_triangles(expected_contact.get_faces()),"Complete live slab contact differs from authenticated compiler record")
	var visuals: Array=owner.find_children("*","MeshInstance3D",true,false)
	if record.render_chunks.is_empty():
		assert(visuals.size()==1)
		assert(_botanical_triangles(_botanical_faces(visuals[0].mesh),visuals[0].global_transform)==_botanical_triangles(complete),"Full live slab render geometry changed")
	else:
		assert(visuals.size()==record.render_chunks.size()+1)
		for chunk in record.render_chunks:
			var visual: MeshInstance3D=owner.get_node(NodePath(str(chunk.id))) as MeshInstance3D
			assert(_botanical_triangles(_botanical_faces(visual.mesh),visual.global_transform)==_botanical_triangles(_botanical_top(chunk.triangles,y)),"Live slab render chunk changed")
		var underside: MeshInstance3D=owner.get_node("StructuralSidesAndUnderside") as MeshInstance3D
		assert(_botanical_triangles(_botanical_faces(underside.mesh),underside.global_transform)==_botanical_triangles(edges),"Live slab edge/underside changed")

static func _botanical_guard_triangles(faces: PackedVector3Array, pose: Transform3D, spec: Dictionary) -> Dictionary:
	var mapped: Dictionary={}
	var result: Dictionary={}
	assert(faces.size()==spec.triangles.size()*3,"Guard triangle count changed")
	for i in range(0,faces.size(),3):
		var ids: Array[int]=[]
		for j in range(3):
			var p: Vector3=pose*faces[i+j]
			var key: String=var_to_bytes(p).hex_encode()
			if not mapped.has(key):
				var nearest: int=-1
				var distance: float=0.0001
				for k in range(spec.vertices_world.size()):
					var raw: Array=spec.vertices_world[k]
					var gap: float=p.distance_to(Vector3(float(raw[0]),float(raw[1]),float(raw[2])))
					if gap<=distance: nearest=k;distance=gap
				assert(nearest>=0,"Live guard vertex deviates from pinned export")
				mapped[key]=nearest
			ids.append(int(mapped[key]))
		ids.sort()
		var triangle_key: String=str(ids)
		result[triangle_key]=int(result.get(triangle_key,0))+1
	return result

static func _botanical_import_names(expected_objects: Dictionary) -> Dictionary:
	var mapping: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(botanical_proof.import_name_map_path)))
	assert(mapping.schema==1 and mapping.mesh_count==136 and mapping.identity_name_count==130 and mapping.pairs.size()==6)
	assert(str(mapping.source_export_sha256)==str(botanical_proof.current_sha256["assets/models/"+str(botanical_proof.guard_file)]))
	assert(str(mapping.expected_geometry_sha256)==str(botanical_proof.current_sha256[str(botanical_proof.guard_geometry_path)]))
	var source_to_import: Dictionary={}
	var alias_targets: Dictionary={}
	for pair in mapping.pairs:
		var source_name: String=str(pair.source_name)
		var imported_name: String=str(pair.imported_name)
		assert(source_name!=imported_name and expected_objects.has(source_name) and not expected_objects.has(imported_name),"Alias must name one exact source mesh and a distinct imported spelling")
		assert(not source_to_import.has(source_name) and not alias_targets.has(imported_name),"Import alias must be bijective")
		source_to_import[source_name]=imported_name
		alias_targets[imported_name]=true
	var import_to_source: Dictionary={}
	for source_name in expected_objects:
		var imported_name: String=str(source_to_import.get(str(source_name),str(source_name)))
		assert(not import_to_source.has(imported_name),"Alias collides with another expected imported name")
		import_to_source[imported_name]=str(source_name)
	assert(import_to_source.size()==136 and source_to_import.size()==6)
	return import_to_source

static func _botanical_validate_guards(floors: Node) -> void:
	load("res://tests/botanical_pair_court_guard.gd").validate(floors,botanical_proof)

static func _botanical_validate_guards_pre_d06(floors: Node) -> void:
	var wrapper: Node3D=floors.get_parent().get_node(NodePath(str(botanical_proof.guard_root))) as Node3D
	assert(wrapper!=null and wrapper.global_transform==Transform3D.IDENTITY)
	assert(wrapper.get_meta("catalogue_file","")==str(botanical_proof.guard_file))
	assert(wrapper.get_child_count()==1,"Exactly one source guard assembly required")
	var expected: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(botanical_proof.guard_geometry_path)))
	var import_names: Dictionary=_botanical_import_names(expected.objects)
	var visual_root: Node=wrapper.get_child(0)
	var meshes: Array=visual_root.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==expected.objects.size())
	assert(visual_root.find_children("*","StaticBody3D",true,false).size()==expected.objects.size())
	assert(visual_root.find_children("*","CollisionShape3D",true,false).size()==expected.objects.size())
	assert(visual_root.find_children("*","Area3D",true,false).is_empty())
	var seen: Dictionary={}
	for mesh_value in meshes:
		var mesh: MeshInstance3D=mesh_value as MeshInstance3D
		var imported_key:=str(mesh.name)
		assert(import_names.has(imported_key),"Unknown imported guard mesh name")
		var name_key: String=str(import_names[imported_key])
		assert(expected.objects.has(name_key) and not seen.has(name_key),"Unknown/duplicate guard mesh")
		seen[name_key]=true
		assert(mesh.visible==(not _moss_guard_is_open(name_key)) and mesh.material_override==null and mesh.mesh!=null)
		var spec: Dictionary=expected.objects[name_key]
		var reference: Dictionary={}
		for triangle in spec.triangles:
			var ids: Array[int]=[]
			for value in triangle: ids.append(int(value))
			ids.sort()
			var key: String=str(ids)
			reference[key]=int(reference.get(key,0))+1
		assert(_botanical_guard_triangles(_botanical_faces(mesh.mesh),mesh.global_transform,spec)==reference,"Actual closed guard render no longer matches pinned export")
		var contacts: Array=mesh.find_children("*","CollisionShape3D",true,false)
		assert(contacts.size()==1 and contacts[0].disabled==_moss_guard_is_open(name_key) and contacts[0].shape is ConcavePolygonShape3D)
		var native_expected: ConcavePolygonShape3D=mesh.mesh.create_trimesh_shape()
		assert(_botanical_triangles(contacts[0].shape.get_faces(),contacts[0].global_transform)==_botanical_triangles(native_expected.get_faces(),mesh.global_transform),"Actual closed guard contact differs from its source-matching render")
		assert(contacts[0].get_parent() is StaticBody3D and contacts[0].get_parent().collision_layer==1 and contacts[0].get_parent().collision_mask==1)
	# Reject any unexpected hierarchy node, even one without a collision/mesh class.
	var template: Node3D=(load("res://assets/models/"+str(botanical_proof.guard_file)) as PackedScene).instantiate()
	var expected_paths: Dictionary={}
	for node in template.find_children("*","Node",true,false): expected_paths[str(template.get_path_to(node))]=node.get_class()
	for node in visual_root.find_children("*","Node",true,false):
		if node is StaticBody3D or node is CollisionShape3D: continue
		var path_key: String=str(visual_root.get_path_to(node))
		assert(expected_paths.has(path_key) and str(expected_paths[path_key])==node.get_class(),"Unexpected loaded guard hierarchy")
	template.free()

static func _botanical_floor_children(floors: Node) -> Array:
	_botanical_ensure()
	var actual_owners: Array=_team_lounge_floor_children(floors)
	assert(floors!=null and actual_owners.size()==botanical_current_compiled.regions.size(),"Complete 275-owner current floor roster required")
	var expected: Dictionary={}
	for record in botanical_current_compiled.regions: expected[str(record.id)]=record
	var retained: Array=[]
	var seen: Dictionary={}
	for value in actual_owners:
		assert(value is Node3D)
		var owner: Node3D=value as Node3D
		var ident:=str(owner.name)
		assert(expected.has(ident) and not seen.has(ident),"Unknown, missing or duplicate loaded floor owner")
		seen[ident]=true
		_botanical_validate_slab(owner,expected[ident])
		if ident not in botanical_proof.added_owner_ids: retained.append(owner)
	assert(seen.size()==275 and retained.size()==273)
	_botanical_validate_guards(floors)
	return retained
# BOTANICAL_EXACT_SECTION_END
# TEAM_LOUNGE_EXACT_SECTION_BEGIN
# Bounded 275-to-277 successor: authenticate the whole current world before projection.
const TEAM_LOUNGE_PROOF := "res://data/architecture/packages/team_lounge/TEAM_LOUNGE_RUNTIME_PROOF.json"
const TEAM_LOUNGE_PROOF_SHA := "e00dea1ada3a55d1f9827ad486a4f462076718fa04d36f406f47af0b8b9ead84"
static var team_lounge_checked := false
static var team_lounge_proof: Dictionary = {}
static var team_lounge_predecessor_text: Dictionary = {}
static var team_lounge_current_compiled: Dictionary = {}

static func _team_lounge_ensure() -> void:
	if team_lounge_checked: return
	_movement_ensure()
	assert(FileAccess.get_sha256(TEAM_LOUNGE_PROOF)==TEAM_LOUNGE_PROOF_SHA,"Exact whole Team Lounge successor proof required")
	team_lounge_proof=JSON.parse_string(FileAccess.get_file_as_string(TEAM_LOUNGE_PROOF))
	assert(team_lounge_proof.schema==1 and team_lounge_proof.programme_key=="D07_directory_08")
	assert(team_lounge_proof.added_owner_ids==["D07_team_lounge_receiving_floor","D07_team_lounge_axial_connector"])
	for path in team_lounge_proof.current_sha256:
		assert(_movement_current_sha256("res://"+str(path))==str(team_lounge_proof.current_sha256[path]),"Unreviewed lounge postimage: "+str(path))
	for path in team_lounge_proof.predecessors:
		var spec: Dictionary=team_lounge_proof.predecessors[path]
		var retained: String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained)==str(spec.sha256),"Lounge predecessor changed: "+str(path))
		team_lounge_predecessor_text[path]=FileAccess.get_file_as_string(retained)
	var own_source := _movement_current_text("res://tests/medical_triage_successor_guard.gd")
	var begin: String="# TEAM_LOUNGE_EXACT_SECTION_"+"BEGIN\n"
	var end: String="# TEAM_LOUNGE_EXACT_SECTION_"+"END\n"
	assert(own_source.count(begin)==1 and own_source.count(end)==1)
	var start:=own_source.find(begin)
	var finish:=own_source.find(end)+end.length()
	var block:=own_source.substr(start,finish-start)
	assert(block.count(TEAM_LOUNGE_PROOF_SHA)==1)
	assert(block.replace(TEAM_LOUNGE_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(team_lounge_proof.integration_block_normalized_sha256),"Exact lounge consumer implementation required")
	var recovered:=own_source.substr(0,start)+own_source.substr(finish)
	for edit in team_lounge_proof.consumer_inverse_edits:
		assert(recovered.count(str(edit.after))==int(edit.count),"Exact lounge consumer inverse cardinality")
		recovered=recovered.replace(str(edit.after),str(edit.before))
	assert(recovered==str(team_lounge_predecessor_text["tests/medical_triage_successor_guard.gd"]),"Every preceding botanical, medical and pool consumer byte must survive")
	for path in team_lounge_proof.exact_inverse_edits:
		var restored:=_movement_current_text("res://"+str(path))
		for edit in team_lounge_proof.exact_inverse_edits[path]:
			assert(restored.count(str(edit.after))==int(edit.count),"Exact lounge source inverse cardinality")
			restored=restored.replace(str(edit.after),str(edit.before))
		assert(restored==str(team_lounge_predecessor_text[path]),"Every preceding compiler/ship byte must survive: "+str(path))
	var layout: Dictionary=JSON.parse_string(_movement_current_text("res://data/spatial_layout.json"))
	var prior_layout: Dictionary=JSON.parse_string(str(team_lounge_predecessor_text["data/spatial_layout.json"]))
	team_lounge_current_compiled=JSON.parse_string(_movement_current_text("res://data/generated/structural_meshes.json"))
	var prior_compiled: Dictionary=JSON.parse_string(str(team_lounge_predecessor_text["data/generated/structural_meshes.json"]))
	for pair in [[layout,prior_layout,team_lounge_proof.added_layout_records],[team_lounge_current_compiled,prior_compiled,team_lounge_proof.added_compiled_records]]:
		var wanted: Array=pair[1].regions.duplicate(true)
		wanted.append_array(pair[2])
		assert(pair[0].regions==wanted,"Every full preceding record/order plus exactly the two approved lounge records required")
		var seen: Dictionary={}
		for record in pair[0].regions:
			assert(not seen.has(str(record.id)),"Duplicate current floor owner")
			seen[str(record.id)]=true
	var current_globals: Dictionary=layout.duplicate(true)
	var prior_globals: Dictionary=prior_layout.duplicate(true)
	current_globals.erase("regions");prior_globals.erase("regions")
	assert(current_globals==prior_globals,"Every predecessor global/void record must survive")
	var compiled_globals: Dictionary=team_lounge_current_compiled.duplicate(true)
	var prior_compiled_globals: Dictionary=prior_compiled.duplicate(true)
	for key in ["regions","source_checks"]:
		compiled_globals.erase(key);prior_compiled_globals.erase(key)
	assert(compiled_globals==prior_compiled_globals,"Every non-summary compiler global must survive")
	var summary: Dictionary=JSON.parse_string(_movement_current_text("res://docs/LAYOUT_COMPILE_CHECKS.json"))
	assert(summary==team_lounge_current_compiled.source_checks and summary==team_lounge_proof.compile_summary)
	assert(summary.team_lounge_additive_preservation.complete_old_records_preserved)
	assert(team_lounge_current_compiled.regions.size()==277 and prior_compiled.regions.size()==275)
	for row in team_lounge_proof.added_compiled_records:
		assert(row.deck=="D07" and float(row.floor_y)==35.5 and float(row.thickness)==.24)
	assert(float(team_lounge_proof.added_compiled_records[0].structural_area_m2)==2477.7225461174385)
	assert(float(team_lounge_proof.added_compiled_records[1].structural_area_m2)==16.0)
	team_lounge_checked=true

static func _team_lounge_current_text(path: String) -> String:
	_team_lounge_ensure()
	var relative:=_relative(path)
	if relative=="tools/validate.py":return load("res://tests/d12_pair_successor_guard.gd").current_text("res://"+relative)
	if relative in team_lounge_proof.projected_paths: return str(team_lounge_predecessor_text[relative])
	return FileAccess.get_file_as_string("res://"+relative)

static func _team_lounge_current_sha256(path: String) -> String:
	_team_lounge_ensure()
	var relative:=_relative(path)
	if relative=="tools/validate.py":return load("res://tests/d12_pair_successor_guard.gd").current_sha256("res://"+relative)
	if relative in team_lounge_proof.projected_paths: return _team_lounge_current_text(relative).sha256_text()
	return FileAccess.get_sha256("res://"+relative)

static func _team_lounge_floor_children(floors: Node) -> Array:
	_team_lounge_ensure()
	var movement_predecessor_children: Array=_movement_floor_children(floors)
	assert(floors!=null and movement_predecessor_children.size()==277,"Complete actual 277-owner roster required before predecessor projection")
	var expected: Dictionary={}
	for record in team_lounge_current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	var children: Array=movement_predecessor_children
	for index in range(children.size()):
		assert(children[index] is Node3D)
		var owner: Node3D=children[index] as Node3D
		var ident:=str(owner.name)
		assert(expected.has(ident) and not seen.has(ident),"Unknown, duplicate or missing actual lounge-era owner")
		assert(ident==str(team_lounge_current_compiled.regions[index].id),"Complete owner order changed")
		seen[ident]=true
		_botanical_validate_slab(owner,expected[ident])
		if ident not in team_lounge_proof.added_owner_ids: retained.append(owner)
	assert(seen.size()==277 and retained.size()==275)
	_team_lounge_validate_runtime(floors)
	return retained

static func _team_lounge_v(value: Array) -> Vector3:
	return Vector3(float(value[0]),float(value[1]),float(value[2]))

static func _team_lounge_paths(root: Node) -> Dictionary:
	var result: Dictionary={}
	for node in root.find_children("*","Node",true,false):
		var key:=str(root.get_path_to(node))
		assert(not result.has(key))
		result[key]=node.get_class()
	return result

static func _team_lounge_expected_faces(spec: Dictionary) -> PackedVector3Array:
	assert(FileAccess.get_sha256(str(spec.faces_file))==str(spec.sha256))
	var bytes:=FileAccess.get_file_as_bytes(str(spec.faces_file))
	assert(bytes.size()==int(spec.triangles)*36)
	var values:=bytes.to_float32_array()
	var result:=PackedVector3Array()
	result.resize(int(values.size()/3))
	for index in range(result.size()): result[index]=Vector3(values[index*3],values[index*3+1],values[index*3+2])
	return result

static func _team_lounge_validate_runtime(floors: Node) -> void:
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(team_lounge_proof.runtime_manifest)))
	assert(str(data.source_sha256)=="b2afb9a77e892c813123924f9e3b62ebcef230896e95846b6c29cd488a917ae0")
	assert(str(data.derivative_sha256)=="292eeb623ca272882ea051aa37abecd5cdce80802c272234edcdf331ee1e3e6e")
	assert(FileAccess.get_sha256(str(data.source_file))==str(data.source_sha256))
	assert(FileAccess.get_sha256(str(data.derivative_file))==str(data.derivative_sha256))
	var space: Node=floors.get_parent()
	var ship: Node=space.get_parent()
	var roots: Array=space.find_children("D07_TeamLounge_Receiving_WIP","Node3D",true,false)
	assert(roots.size()==1 and roots[0].get_parent()==space,"Exactly one direct whole receiving placement required")
	var root: Node3D=roots[0] as Node3D
	assert(root.global_transform==Transform3D(Basis.IDENTITY,Vector3(31,35.5,216)))
	assert(root.get_meta("program_key","")=="D07_directory_08")
	assert(root.get_meta("source_sha256","")==str(data.source_sha256) and root.get_meta("derivative_sha256","")==str(data.derivative_sha256))
	assert(root.get_meta("admission_capacity_created",true)==false and root.get_script()==null)
	assert(root.get_meta("status","")=="installed_receiving_source_WIP_validation_pending")
	var source: Node3D=root.get_node("RuntimeSource") as Node3D
	var template: Node3D=(load(str(data.derivative_file)) as PackedScene).instantiate() as Node3D
	template.name="RuntimeSource"
	assert(source.transform==template.transform and source.get_script()==template.get_script())
	assert(template.find_children("*","Light3D",true,false).is_empty(),"Pinned derivative has no active imported emitters")
	var actual_nodes: Dictionary={}
	var expected_paths: Dictionary={"RuntimeSource":template.get_class(),"RestContacts":"Node3D"}
	var source_expected:=_team_lounge_paths(template)
	var imported_meshes:=0
	var imported_surfaces:=0
	for path in source_expected:
		var actual: Node=source.get_node(NodePath(str(path)))
		var expected: Node=template.get_node(NodePath(str(path)))
		assert(actual.get_class()==expected.get_class() and actual.get_script()==expected.get_script(),"Imported source hierarchy/class/script changed")
		assert(not actual_nodes.has(str(actual.name)),"Duplicate runtime source identity")
		actual_nodes[str(actual.name)]=actual
		expected_paths["RuntimeSource/"+str(path)]=expected.get_class()
		if actual is Node3D:
			assert((actual as Node3D).transform==(expected as Node3D).transform,"Exact source node transform changed")
		if actual is MeshInstance3D:
			var mesh: MeshInstance3D=actual as MeshInstance3D
			var prior_mesh: MeshInstance3D=expected as MeshInstance3D
			assert(mesh.visible and mesh.material_override==null and mesh.mesh!=null)
			assert(mesh.mesh.get_surface_count()==prior_mesh.mesh.get_surface_count())
			imported_meshes+=1
			for surface in range(mesh.mesh.get_surface_count()):
				assert(mesh.get_surface_override_material(surface)==null,"Source material override is forbidden")
				assert(mesh.mesh.surface_get_arrays(surface)==prior_mesh.mesh.surface_get_arrays(surface),"Exact imported source vertex/UV/index arrays changed")
				assert(mesh.get_active_material(surface)==prior_mesh.get_active_material(surface),"Source material identity changed")
				imported_surfaces+=1
	assert(imported_surfaces==241 and imported_meshes==241)
	assert(data.semantic_nodes.size()==4676)
	var semantic_seen: Dictionary={}
	for spec in data.semantic_nodes:
		var name_key:=str(spec.runtime_name)
		assert(actual_nodes.has(name_key) and not semantic_seen.has(int(spec.source_index)),"Missing/duplicate source semantic identity")
		semantic_seen[int(spec.source_index)]=true
		var node: Node=actual_nodes[name_key]
		assert(node.get_meta("wp15_source_index",-1)==int(spec.source_index))
		assert(node.get_meta("wp15_source_name","")==str(spec.source_name))
		assert(node.get_meta("wp15_semantic_kind","")==str(spec.kind))
	assert(semantic_seen.size()==4676)
	assert(data.collision_groups.size()==101)
	var collision_seen: Dictionary={}
	var static_count:=0
	for spec in data.collision_groups:
		var ident:=str(spec.id)
		assert(not collision_seen.has(ident));collision_seen[ident]=true
		var parent: Node3D=root if spec.runtime_parent_name==null else actual_nodes[str(spec.runtime_parent_name)] as Node3D
		if spec.runtime_parent_name==null: static_count+=1
		var body: StaticBody3D=parent.get_node(NodePath(ident)) as StaticBody3D
		assert(body!=null and body.transform==Transform3D.IDENTITY and body.get_child_count()==1)
		assert(body.collision_layer==1 and body.collision_mask==1 and body.get_script()==null)
		assert(body.get_meta("wp15_collision_policy","")==str(spec.policy) and body.get_meta("wp15_faces_sha256","")==str(spec.sha256))
		var contact: CollisionShape3D=body.get_node("ExactSourceFaces") as CollisionShape3D
		assert(contact!=null and not contact.disabled and contact.transform==Transform3D.IDENTITY and contact.get_child_count()==0)
		assert(contact.shape is ConcavePolygonShape3D and contact.get_script()==null)
		assert((contact.shape as ConcavePolygonShape3D).get_faces()==_team_lounge_expected_faces(spec),"Every exact final collision face and multiplicity must survive")
		var body_path:=str(root.get_path_to(body))
		expected_paths[body_path]="StaticBody3D"
		expected_paths[body_path+"/ExactSourceFaces"]="CollisionShape3D"
	assert(static_count==4)
	assert(data.rest_contacts.size()==96)
	var rests: Node3D=root.get_node("RestContacts") as Node3D
	assert(rests.transform==Transform3D.IDENTITY and rests.get_child_count()==96 and rests.get_script()==null)
	var rest_seen: Dictionary={}
	for spec in data.rest_contacts:
		var ident:=str(spec.id)
		assert(not rest_seen.has(ident));rest_seen[ident]=true
		var marker: Marker3D=rests.get_node(NodePath(ident)) as Marker3D
		assert(marker!=null and marker.get_script()==null and marker.get_child_count()==0)
		assert(marker.position==_team_lounge_v(spec.local_position) and marker.basis==Basis.looking_at(_team_lounge_v(spec.forward),Vector3.UP))
		assert(marker.get_meta("proposed_rest_contact",false)==true and marker.get_meta("admission_capacity_created",true)==false)
		assert(marker.get_meta("furniture_instance","")==str(spec.furniture_instance))
		expected_paths["RestContacts/"+ident]="Marker3D"
	assert(data.lights.size()==90)
	var budget: Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
	var light_seen: Dictionary={}
	for spec in data.lights:
		var name_key:=str(spec.runtime_parent_name)
		assert(actual_nodes.has(name_key) and not light_seen.has(name_key));light_seen[name_key]=true
		var light: SpotLight3D=actual_nodes[name_key].get_node("PhysicalSource") as SpotLight3D
		assert(light!=null and light.transform==Transform3D.IDENTITY and light.get_script()==null and light.get_child_count()==0)
		assert(light.light_color==Color(float(spec.color[0]),float(spec.color[1]),float(spec.color[2])))
		assert(light.light_energy==_team_lounge_f32(spec.light_energy) and light.spot_range==_team_lounge_f32(spec.spot_range))
		assert(light.spot_angle==_team_lounge_f32(spec.spot_angle) and light.spot_attenuation==_team_lounge_f32(spec.spot_attenuation))
		assert(light.spot_angle_attenuation==_team_lounge_f32(spec.spot_angle_attenuation))
		assert(light.get_meta("fixture_powered",false)==true and light.get_meta("wp15_source_index",-1)==int(spec.source_index))
		assert(light.get_meta("wp15_fixture_members",[])==spec.fixture_members)
		assert(light.get_meta("wp15_source_inner_cone_degrees",-1)==float(spec.source_inner_cone_degrees))
		assert(light.get_meta("wp15_calibration","")=="initial_bounded_source_normalization_unaccepted")
		if spec.illumination_anchor==null: assert(not light.has_meta("illumination_anchor"))
		else: assert(light.get_meta("illumination_anchor")==_team_lounge_v(spec.illumination_anchor))
		assert(budget.sources.count(light)==1 and budget.requested_shadow.get(light.get_instance_id(),false)==true,"Every actual physical source must request the sole existing manager")
		assert(light.visible==light.shadow_enabled,"No visible unshadowed fallback is permitted")
		expected_paths[str(root.get_path_to(light))]="SpotLight3D"
	var active:=0
	for light in budget.sources:
		if light.visible and light.shadow_enabled: active+=1
	assert(active<=8,"Existing global shadow cap changed")
	assert(_team_lounge_paths(root)==expected_paths,"Unexpected, missing or duplicate lounge runtime node")
	assert(data.finish_top_chunks.size()==52)
	var owner: Node3D=floors.get_node("D07_team_lounge_receiving_floor") as Node3D
	var finish_seen: Dictionary={}
	for chunk in data.finish_top_chunks:
		assert(not finish_seen.has(str(chunk)));finish_seen[str(chunk)]=true
		var mesh: MeshInstance3D=owner.get_node(NodePath(str(chunk))) as MeshInstance3D
		var material: ShaderMaterial=mesh.get_surface_override_material(0) as ShaderMaterial
		assert(material!=null and material.shader.resource_path=="res://shaders/team_lounge_receiving_finish.gdshader")
		for texture in data.finish_textures:
			var actual: Texture2D=material.get_shader_parameter(str(texture.role)) as Texture2D
			assert(actual!=null and actual.resource_path==str(texture.file))
	_team_lounge_validate_import(source,data,actual_nodes)
	template.free()

static func _team_lounge_f32(value: Variant) -> float:
	return PackedFloat32Array([float(value)])[0]

static func _team_lounge_accessor(document: Dictionary, binary: PackedByteArray, index: int) -> Dictionary:
	var accessor: Dictionary=document.accessors[index]
	assert(not accessor.has("sparse") and not bool(accessor.get("normalized",false)),"Only the selected derivative's exact unnormalized accessors are supported")
	var components: Dictionary={"SCALAR":1,"VEC2":2,"VEC3":3}
	var sizes: Dictionary={5123:2,5125:4,5126:4}
	assert(components.has(str(accessor.type)) and sizes.has(int(accessor.componentType)))
	var count:=int(accessor.count)
	var width: int=int(components[str(accessor.type)])*int(sizes[int(accessor.componentType)])
	var view: Dictionary=document.bufferViews[int(accessor.bufferView)]
	assert(int(view.buffer)==0 and not accessor.has("extensions") and not view.has("extensions"))
	var offset:=int(view.get("byteOffset",0))+int(accessor.get("byteOffset",0))
	var stride:=int(view.get("byteStride",width))
	assert(stride>=width and offset>=0 and offset+(count-1)*stride+width<=binary.size())
	var data:=PackedByteArray()
	data.resize(count*width)
	for row in range(count):
		for column in range(width): data[row*width+column]=binary[offset+row*stride+column]
	return {"bytes":data,"count":count,"type":str(accessor.type),"component_type":int(accessor.componentType)}

static func _team_lounge_source_indices(document: Dictionary, binary: PackedByteArray, primitive: Dictionary, count: int) -> PackedInt32Array:
	var result:=PackedInt32Array()
	if not primitive.has("indices"):
		result.resize(count)
		for index in range(count): result[index]=index
		return result
	var accessor:=_team_lounge_accessor(document,binary,int(primitive.indices))
	assert(accessor.type=="SCALAR" and int(accessor.component_type) in [5123,5125])
	var bytes: PackedByteArray=accessor.bytes
	result.resize(int(accessor.count))
	for index in range(result.size()):
		result[index]=bytes.decode_u16(index*2) if int(accessor.component_type)==5123 else bytes.decode_u32(index*4)
	return result

static func _team_lounge_corner_key(point: Vector3, uv: Vector2) -> String:
	return var_to_bytes(point).hex_encode()+":"+var_to_bytes(uv).hex_encode()

static func _team_lounge_oriented_triangle(corners: Array[String]) -> String:
	assert(corners.size()==3)
	var candidates: Array[String]=[]
	for start in range(3): candidates.append(corners[start]+"|"+corners[(start+1)%3]+"|"+corners[(start+2)%3])
	candidates.sort()
	return candidates[0]

static func _team_lounge_import_surface(mesh: Mesh, surface: int) -> Dictionary:
	var arrays: Array=mesh.surface_get_arrays(surface)
	var positions: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
	var uvs: PackedVector2Array=arrays[Mesh.ARRAY_TEX_UV]
	assert(positions.size()==uvs.size(),"Full source UV corner ownership is required")
	var indices: Variant=arrays[Mesh.ARRAY_INDEX]
	var order:=PackedInt32Array()
	if indices!=null and indices.size()>0: order=indices
	else:
		order.resize(positions.size())
		for index in range(order.size()): order[index]=index
	assert(order.size()%3==0)
	var keys: Array[String]=[]
	keys.resize(positions.size())
	for index in range(keys.size()): keys[index]=_team_lounge_corner_key(positions[index],uvs[index])
	var result: Dictionary={}
	for start in range(0,order.size(),3):
		var corners: Array[String]=[keys[order[start]],keys[order[start+1]],keys[order[start+2]]]
		var key:=_team_lounge_oriented_triangle(corners)
		result[key]=int(result.get(key,0))+1
	return result

static func _team_lounge_validate_import(source: Node3D, data: Dictionary, actual: Dictionary) -> void:
	# Decode the pinned GLB independently; a second imported template alone cannot
	# establish that the importer preserved the source's actual position/UV arrays.
	var blob:=FileAccess.get_file_as_bytes(str(data.derivative_file))
	assert(blob.decode_u32(0)==0x46546c67 and blob.decode_u32(4)==2 and blob.decode_u32(8)==blob.size())
	var json_size:=int(blob.decode_u32(12))
	assert(blob.decode_u32(16)==0x4e4f534a)
	var document: Dictionary=JSON.parse_string(blob.slice(20,20+json_size).get_string_from_utf8())
	var binary_start:=20+json_size
	var binary_size:=int(blob.decode_u32(binary_start))
	assert(blob.decode_u32(binary_start+4)==0x004e4942 and binary_start+8+binary_size==blob.size())
	var binary:=blob.slice(binary_start+8)
	assert(document.nodes.size()==4766 and document.meshes.size()==241)
	var parents: Dictionary={}
	for index in range(document.nodes.size()):
		for child in document.nodes[index].get("children",[]):
			assert(not parents.has(int(child)),"Derivative source must be a unique-parent tree")
			parents[int(child)]=index
	var source_triangles:=0
	var source_meshes:=0
	var material_seen: Dictionary={}
	for index in range(document.nodes.size()):
		var record: Dictionary=document.nodes[index]
		var name_key:=str(record.name)
		assert(actual.has(name_key),"Every original identity and generated batch must survive import")
		var node: Node3D=actual[name_key] as Node3D
		assert(node!=null)
		var parent: Node=source if not parents.has(index) else actual[str(document.nodes[int(parents[index])].name)]
		assert(node.get_parent()==parent,"Exact source parentage must survive import")
		assert(node.position==_team_lounge_v(record.get("translation",[0,0,0])),"Exact source local translation must survive import")
		if not record.has("mesh"): continue
		assert(node is MeshInstance3D)
		var visual: MeshInstance3D=node as MeshInstance3D
		var expected_mesh: Dictionary=document.meshes[int(record.mesh)]
		assert(visual.mesh.get_surface_count()==expected_mesh.primitives.size())
		source_meshes+=1
		for surface in range(expected_mesh.primitives.size()):
			var primitive: Dictionary=expected_mesh.primitives[surface]
			assert(int(primitive.get("mode",4))==4 and primitive.attributes.has("POSITION") and primitive.attributes.has("TEXCOORD_0"))
			var position_accessor:=_team_lounge_accessor(document,binary,int(primitive.attributes.POSITION))
			var uv_accessor:=_team_lounge_accessor(document,binary,int(primitive.attributes.TEXCOORD_0))
			assert(position_accessor.type=="VEC3" and uv_accessor.type=="VEC2" and position_accessor.component_type==5126 and uv_accessor.component_type==5126)
			assert(position_accessor.count==uv_accessor.count)
			var positions: PackedFloat32Array=position_accessor.bytes.to_float32_array()
			var uvs: PackedFloat32Array=uv_accessor.bytes.to_float32_array()
			var indices:=_team_lounge_source_indices(document,binary,primitive,int(position_accessor.count))
			assert(indices.size()%3==0)
			var keys: Array[String]=[]
			keys.resize(int(position_accessor.count))
			for vertex in range(keys.size()): keys[vertex]=_team_lounge_corner_key(Vector3(positions[vertex*3],positions[vertex*3+1],positions[vertex*3+2]),Vector2(uvs[vertex*2],uvs[vertex*2+1]))
			var expected: Dictionary={}
			for start in range(0,indices.size(),3):
				# glTF counter-clockwise winding is reversed by Godot's importer.
				var corners: Array[String]=[keys[indices[start]],keys[indices[start+2]],keys[indices[start+1]]]
				var key:=_team_lounge_oriented_triangle(corners)
				expected[key]=int(expected.get(key,0))+1
			assert(_team_lounge_import_surface(visual.mesh,surface)==expected,"Exact derivative position/UV/winding/multiplicity must survive; no degenerate-face exemption")
			source_triangles+=int(indices.size()/3)
			var material_index:=int(primitive.material)
			var material: Material=visual.get_active_material(surface)
			assert(material!=null and material.resource_name==str(document.materials[material_index].name),"Exact source material assignment required")
			if material_seen.has(material_index): assert(material_seen[material_index]==material)
			else: material_seen[material_index]=material
	assert(source_meshes==241 and source_triangles==494470)
# TEAM_LOUNGE_EXACT_SECTION_END
# MOVEMENT_EXACT_SECTION_BEGIN
# Bounded 277-to-279 successor: authenticate the whole current world before projection.
const MOVEMENT_PROOF := "res://data/architecture/packages/movement_studio/MOVEMENT_RUNTIME_PROOF.json"
const MOVEMENT_PROOF_SHA := "36c0ff269d1ddc2d2a70380bc7e7bd9b396c602671934071824982f4c3fd411b"
static var movement_checked := false
static var movement_proof: Dictionary = {}
static var movement_predecessor_text: Dictionary = {}
static var movement_current_compiled: Dictionary = {}

static func _movement_ensure() -> void:
	if movement_checked: return
	_moss_ensure()
	assert(FileAccess.get_sha256(MOVEMENT_PROOF)==MOVEMENT_PROOF_SHA,"Exact whole Team Lounge successor proof required")
	movement_proof=JSON.parse_string(FileAccess.get_file_as_string(MOVEMENT_PROOF))
	assert(movement_proof.schema==1 and movement_proof.programme_key=="D07_directory_02")
	assert(movement_proof.added_owner_ids==["D07_movement_studio_floor","D07_movement_studio_entry"])
	for path in movement_proof.current_sha256:
		assert(_moss_current_sha256("res://"+str(path))==str(movement_proof.current_sha256[path]),"Unreviewed lounge postimage: "+str(path))
	for path in movement_proof.predecessors:
		var spec: Dictionary=movement_proof.predecessors[path]
		var retained: String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained)==str(spec.sha256),"Lounge predecessor changed: "+str(path))
		movement_predecessor_text[path]=FileAccess.get_file_as_string(retained)
	var own_source := _moss_current_text("res://tests/medical_triage_successor_guard.gd")
	var begin: String="# MOVEMENT_EXACT_SECTION_"+"BEGIN\n"
	var end: String="# MOVEMENT_EXACT_SECTION_"+"END\n"
	assert(own_source.count(begin)==1 and own_source.count(end)==1)
	var start:=own_source.find(begin)
	var finish:=own_source.find(end)+end.length()
	var block:=own_source.substr(start,finish-start)
	assert(block.count(MOVEMENT_PROOF_SHA)==1)
	assert(block.replace(MOVEMENT_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(movement_proof.integration_block_normalized_sha256),"Exact lounge consumer implementation required")
	var recovered:=own_source.substr(0,start)+own_source.substr(finish)
	for edit in movement_proof.consumer_inverse_edits:
		assert(recovered.count(str(edit.after))==int(edit.count),"Exact lounge consumer inverse cardinality")
		recovered=recovered.replace(str(edit.after),str(edit.before))
	assert(recovered==str(movement_predecessor_text["tests/medical_triage_successor_guard.gd"]),"Every preceding botanical, medical and pool consumer byte must survive")
	for path in movement_proof.exact_inverse_edits:
		var restored:=_moss_current_text("res://"+str(path))
		for edit in movement_proof.exact_inverse_edits[path]:
			assert(restored.count(str(edit.after))==int(edit.count),"Exact lounge source inverse cardinality")
			restored=restored.replace(str(edit.after),str(edit.before))
		assert(restored==str(movement_predecessor_text[path]),"Every preceding compiler/ship byte must survive: "+str(path))
	var layout: Dictionary=JSON.parse_string(_moss_current_text("res://data/spatial_layout.json"))
	var prior_layout: Dictionary=JSON.parse_string(str(movement_predecessor_text["data/spatial_layout.json"]))
	movement_current_compiled=JSON.parse_string(_moss_current_text("res://data/generated/structural_meshes.json"))
	var prior_compiled: Dictionary=JSON.parse_string(str(movement_predecessor_text["data/generated/structural_meshes.json"]))
	for pair in [[layout,prior_layout,movement_proof.added_layout_records],[movement_current_compiled,prior_compiled,movement_proof.added_compiled_records]]:
		var wanted: Array=pair[1].regions.duplicate(true)
		wanted.append_array(pair[2])
		assert(pair[0].regions==wanted,"Every full preceding record/order plus exactly the two approved lounge records required")
		var seen: Dictionary={}
		for record in pair[0].regions:
			assert(not seen.has(str(record.id)),"Duplicate current floor owner")
			seen[str(record.id)]=true
	var current_globals: Dictionary=layout.duplicate(true)
	var prior_globals: Dictionary=prior_layout.duplicate(true)
	current_globals.erase("regions");prior_globals.erase("regions")
	assert(current_globals==prior_globals,"Every predecessor global/void record must survive")
	var compiled_globals: Dictionary=movement_current_compiled.duplicate(true)
	var prior_compiled_globals: Dictionary=prior_compiled.duplicate(true)
	for key in ["regions","source_checks"]:
		compiled_globals.erase(key);prior_compiled_globals.erase(key)
	assert(compiled_globals==prior_compiled_globals,"Every non-summary compiler global must survive")
	var summary: Dictionary=JSON.parse_string(_moss_current_text("res://docs/LAYOUT_COMPILE_CHECKS.json"))
	assert(summary==movement_current_compiled.source_checks and summary==movement_proof.compile_summary)
	assert(summary.movement_studio_additive_preservation.complete_old_records_preserved)
	assert(movement_current_compiled.regions.size()==279 and prior_compiled.regions.size()==277)
	for row in movement_proof.added_compiled_records:
		assert(row.deck=="D07" and float(row.floor_y)==35.5 and float(row.thickness)==.24)
	assert(float(movement_proof.added_compiled_records[0].structural_area_m2)==3128.0)
	assert(float(movement_proof.added_compiled_records[1].structural_area_m2)==32.0)
	movement_checked=true

static func _movement_current_text(path: String) -> String:
	_movement_ensure()
	var relative:=_relative(path)
	if relative in movement_proof.projected_paths: return str(movement_predecessor_text[relative])
	return FileAccess.get_file_as_string("res://"+relative)

static func _movement_current_sha256(path: String) -> String:
	_movement_ensure()
	var relative:=_relative(path)
	if relative in movement_proof.projected_paths: return _movement_current_text(relative).sha256_text()
	return FileAccess.get_sha256("res://"+relative)

static func _movement_floor_children(floors: Node) -> Array:
	_movement_ensure()
	var moss_predecessor_children: Array=_moss_floor_children(floors)
	assert(floors!=null and moss_predecessor_children.size()==279,"Complete actual 279-owner roster required before predecessor projection")
	var expected: Dictionary={}
	for record in movement_current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	var children: Array=moss_predecessor_children
	for index in range(children.size()):
		assert(children[index] is Node3D)
		var owner: Node3D=children[index] as Node3D
		var ident:=str(owner.name)
		assert(expected.has(ident) and not seen.has(ident),"Unknown, duplicate or missing actual lounge-era owner")
		assert(ident==str(movement_current_compiled.regions[index].id),"Complete owner order changed")
		seen[ident]=true
		_botanical_validate_slab(owner,expected[ident])
		if ident not in movement_proof.added_owner_ids: retained.append(owner)
	assert(seen.size()==279 and retained.size()==277)
	_movement_validate_runtime(floors)
	return retained

static func _movement_v(a: Array) -> Vector3:
	return Vector3(float(a[0]),float(a[1]),float(a[2]))

static func _movement_model(wrapper: Node3D, filename: String, count: int) -> void:
	var template: Node3D=(load("res://assets/models/"+filename) as PackedScene).instantiate() as Node3D
	var actual: Node3D=wrapper.get_node(NodePath(str(template.name))) as Node3D
	assert(actual!=null and actual.transform==template.transform)
	var meshes:=0
	var nodes: Array=[template]
	nodes.append_array(template.find_children("*","Node",true,false))
	for expected in nodes:
		var node: Node=actual if expected==template else actual.get_node(template.get_path_to(expected))
		assert(node.get_class()==expected.get_class() and node.get_script()==expected.get_script())
		if node is Node3D: assert(node.transform==expected.transform,"Exact imported source pose changed")
		if node is MeshInstance3D:
			meshes+=1
			assert(node.visible and node.material_override==null and node.mesh!=null)
			assert(node.mesh.get_surface_count()==expected.mesh.get_surface_count())
			for surface in range(node.mesh.get_surface_count()):
				assert(node.mesh.surface_get_arrays(surface)==expected.mesh.surface_get_arrays(surface))
				assert(node.get_surface_override_material(surface)==null and node.get_active_material(surface)==expected.get_active_material(surface))
			var body: StaticBody3D=node.get_node("StaticContact") as StaticBody3D
			assert(body!=null and body.transform==Transform3D.IDENTITY and body.get_child_count()==1)
			assert(body.collision_layer==1 and body.collision_mask==1 and body.get_script()==null)
			var contact: CollisionShape3D=body.get_node("SharedShape") as CollisionShape3D
			assert(contact!=null and not contact.disabled and contact.transform==Transform3D.IDENTITY and contact.get_script()==null)
			assert(contact.shape is ConcavePolygonShape3D)
			var wanted: ConcavePolygonShape3D=expected.mesh.create_trimesh_shape()
			assert(contact.shape.get_faces()==wanted.get_faces(),"Complete imported source contact faces changed")
		assert(node.get_child_count()==expected.get_child_count()+(1 if node is MeshInstance3D else 0),"Unexpected source child")
	_movement_validate_import(template,filename,count)
	assert(meshes==count and actual.find_children("*","StaticBody3D",true,false).size()==count)
	assert(actual.find_children("*","Light3D",true,false).is_empty())
	template.free()

static func _movement_validate_runtime(floors: Node) -> void:
	var d: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(movement_proof.runtime_manifest)))
	var ship: Node=floors.get_parent().get_parent()
	var parent: Node=ship.get_node("ShipSpace/Districts")
	var roots: Array=ship.find_children(str(d.root_name),"Node3D",true,false)
	assert(roots.size()==1 and roots[0].get_parent()==parent)
	var root: Node3D=roots[0] as Node3D
	assert(root.transform==Transform3D.IDENTITY and root.get_child_count()==33 and root.get_script()==null)
	assert(root.get_meta("programme_key","")=="D07_directory_02" and root.get_meta("persistent_id","")==str(d.persistent_id))
	assert(root.get_meta("first_pass_quality_accepted",true)==false and root.get_meta("capacity_accepted",true)==false)
	assert(root.get_meta("source_receiving_contract",{})==d)
	var room: Node3D=root.get_node("WholeRetainedMovementStudio") as Node3D
	var guards: Node3D=root.get_node("SourceDerivedReceivingGuards") as Node3D
	assert(room.transform==Transform3D(Basis.IDENTITY,_movement_v(d.placement)) and guards.transform==Transform3D.IDENTITY)
	assert(room.get_child_count()==3 and guards.get_child_count()==1)
	for pair in [[d.model_file,d.model_sha256],[d.guard_file,d.guard_sha256]]:
		var path: String="res://assets/models/"+str(pair[0])
		assert(FileAccess.get_sha256(path)==str(pair[1]))
		var options:=ConfigFile.new()
		assert(options.load(path+".import")==OK)
		assert(bool(options.get_value("params","meshes/force_disable_compression",false)))
		assert(not bool(options.get_value("params","meshes/generate_lods",true)))
		assert(str(options.get_value("params","nodes/root_type",""))=="Node3D")
	_movement_model(room,str(d.model_file),1290)
	_movement_model(guards,str(d.guard_file),20)
	var identities: Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/packages/movement_studio/NODE_BIJECTION.json"))
	assert(identities.size()==1337)
	for spec in identities: assert(room.find_children(str(spec.runtime_name),"Node",true,false).size()==1)
	assert(d.seats.size()==9)
	for spec in d.seats:
		var seat: Node3D=room.find_child(str(spec.runtime_name),true,false) as Node3D
		assert(seat!=null and seat.global_position.distance_to(_movement_v(spec.world))<0.00001)
		assert(seat.get_meta("source_seat_identity","")==str(spec.source_name))
	assert(d.lights.size()==31 and root.find_children("*","Light3D",true,false).size()==31)
	for spec in d.lights:
		var lamp: SpotLight3D=root.get_node(NodePath(str(spec.id))) as SpotLight3D
		assert(lamp!=null and lamp.position==_movement_v(spec.world) and lamp.rotation==Vector3(-PI/2.0,0,0))
		var expected_lamp:=SpotLight3D.new()
		expected_lamp.spot_range=float(spec.spot_range);expected_lamp.spot_angle=float(spec.spot_angle_degrees);expected_lamp.light_energy=float(spec.spot_energy)
		assert(lamp.spot_range==expected_lamp.spot_range and lamp.spot_angle==expected_lamp.spot_angle and lamp.light_energy==expected_lamp.light_energy)
		expected_lamp.free()
		assert(lamp.light_color==Color(float(spec.color[0]),float(spec.color[1]),float(spec.color[2])))
		assert(lamp.get_meta("source_area_id","")==str(spec.source_id) and lamp.get_meta("fixture_node","")==str(spec.fixture_node))
		assert(lamp.get_meta("receiving_calibration_unaccepted",false)==true and lamp.get_script()==null)
		var fixture: MeshInstance3D=room.find_child(str(spec.fixture_node),true,false) as MeshInstance3D
		var bounds: AABB=fixture.global_transform*fixture.get_aabb()
		assert(lamp.global_position.y<bounds.position.y and bounds.position.y-lamp.global_position.y<0.04)
	var info: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/packages/movement_studio/INFORMATION_TARGETS.json"))
	assert(info.candidates.size()==2)
	for spec in info.candidates:
		var target: Node3D=room.get_node(NodePath(str(spec.id))) as Node3D
		assert(target.get_script()==load("res://scripts/movement_studio/amenity_information.gd"))
		assert(target.candidate_id==str(spec.id) and target.prompt==str(spec.label) and target.information==str(spec.information))
		assert(target.global_position.distance_to(_movement_v(spec.focus_world_m))<0.00001 and target.get_child_count()==1)
		var area: Area3D=target.get_node("AuthoredInformationTarget") as Area3D
		assert(area.collision_layer==2 and area.collision_mask==0 and not area.monitoring and not area.monitorable and area.get_child_count()==1)
		var shape: CollisionShape3D=area.get_child(0) as CollisionShape3D
		assert(not shape.disabled and shape.shape is BoxShape3D and shape.shape.size==_movement_v(spec.target_size_m))
	var owner: Node=floors.get_node(NodePath(str(d.floor_owners[0])))
	var chunks:=0
	for node in owner.find_children("cell_*","MeshInstance3D",true,false):
		var material: ShaderMaterial=node.get_surface_override_material(0) as ShaderMaterial
		assert(material!=null and material.shader==load(str(d.floor_shader)))
		assert(material.get_shader_parameter("quiet_stone_texture")==load("res://assets/models/WP11_receiving_warm_stone.png"))
		assert(material.get_shader_parameter("warm_walnut_texture")==load("res://assets/models/WP11_receiving_warm_walnut.png"))
		chunks+=1
	assert(chunks==movement_proof.added_compiled_records[0].render_chunks.size())
	var budgets: Array=ship.find_children("LocalShadowSourceBudget","Node",true,false)
	assert(budgets.size()==1 and budgets[0].shadow_source_budget==8 and budgets[0].MAX_VISIBILITY_CANDIDATES==32)

static func _movement_validate_import(source: Node3D, filename: String, mesh_count: int) -> void:
	var actual: Dictionary={}
	for node in source.find_children("*","Node3D",true,false):
		assert(not actual.has(str(node.name)));actual[str(node.name)]=node
	# Decode the pinned GLB independently; a second imported template alone cannot
	# establish that the importer preserved the source's actual position/UV arrays.
	var blob:=FileAccess.get_file_as_bytes("res://assets/models/"+filename)
	assert(blob.decode_u32(0)==0x46546c67 and blob.decode_u32(4)==2 and blob.decode_u32(8)==blob.size())
	var json_size:=int(blob.decode_u32(12))
	assert(blob.decode_u32(16)==0x4e4f534a)
	var document: Dictionary=JSON.parse_string(blob.slice(20,20+json_size).get_string_from_utf8())
	var binary_start:=20+json_size
	var binary_size:=int(blob.decode_u32(binary_start))
	assert(blob.decode_u32(binary_start+4)==0x004e4942 and binary_start+8+binary_size==blob.size())
	var binary:=blob.slice(binary_start+8)
	assert(document.nodes.size()==actual.size())
	var parents: Dictionary={}
	for index in range(document.nodes.size()):
		for child in document.nodes[index].get("children",[]):
			assert(not parents.has(int(child)),"Derivative source must be a unique-parent tree")
			parents[int(child)]=index
	var source_triangles:=0
	var source_meshes:=0
	var material_seen: Dictionary={}
	for index in range(document.nodes.size()):
		var record: Dictionary=document.nodes[index]
		var name_key:=str(record.name)
		assert(actual.has(name_key),"Every original identity and generated batch must survive import")
		var node: Node3D=actual[name_key] as Node3D
		assert(node!=null)
		var parent: Node=source if not parents.has(index) else actual[str(document.nodes[int(parents[index])].name)]
		assert(node.get_parent()==parent,"Exact source parentage must survive import")
		assert(node.position==_team_lounge_v(record.get("translation",[0,0,0])),"Exact source local translation must survive import")
		if not record.has("mesh"): continue
		assert(node is MeshInstance3D)
		var visual: MeshInstance3D=node as MeshInstance3D
		var expected_mesh: Dictionary=document.meshes[int(record.mesh)]
		assert(visual.mesh.get_surface_count()==expected_mesh.primitives.size())
		source_meshes+=1
		for surface in range(expected_mesh.primitives.size()):
			var primitive: Dictionary=expected_mesh.primitives[surface]
			assert(int(primitive.get("mode",4))==4 and primitive.attributes.has("POSITION") and primitive.attributes.has("TEXCOORD_0"))
			var position_accessor:=_team_lounge_accessor(document,binary,int(primitive.attributes.POSITION))
			var uv_accessor:=_team_lounge_accessor(document,binary,int(primitive.attributes.TEXCOORD_0))
			assert(position_accessor.type=="VEC3" and uv_accessor.type=="VEC2" and position_accessor.component_type==5126 and uv_accessor.component_type==5126)
			assert(position_accessor.count==uv_accessor.count)
			var positions: PackedFloat32Array=position_accessor.bytes.to_float32_array()
			var uvs: PackedFloat32Array=uv_accessor.bytes.to_float32_array()
			var indices:=_team_lounge_source_indices(document,binary,primitive,int(position_accessor.count))
			assert(indices.size()%3==0)
			var keys: Array[String]=[]
			keys.resize(int(position_accessor.count))
			for vertex in range(keys.size()): keys[vertex]=_team_lounge_corner_key(Vector3(positions[vertex*3],positions[vertex*3+1],positions[vertex*3+2]),Vector2(uvs[vertex*2],uvs[vertex*2+1]))
			var expected: Dictionary={}
			for start in range(0,indices.size(),3):
				# glTF counter-clockwise winding is reversed by Godot's importer.
				var corners: Array[String]=[keys[indices[start]],keys[indices[start+2]],keys[indices[start+1]]]
				var key:=_team_lounge_oriented_triangle(corners)
				expected[key]=int(expected.get(key,0))+1
			assert(_team_lounge_import_surface(visual.mesh,surface)==expected,"Exact derivative position/UV/winding/multiplicity must survive; no degenerate-face exemption")
			source_triangles+=int(indices.size()/3)
			var material_index:=int(primitive.material)
			var material: Material=visual.get_active_material(surface)
			assert(material!=null and material.resource_name==str(document.materials[material_index].name),"Exact source material assignment required")
			if material_seen.has(material_index): assert(material_seen[material_index]==material)
			else: material_seen[material_index]=material
	assert(source_meshes==mesh_count)
	if mesh_count==1290: assert(source_triangles==191456)
# MOVEMENT_EXACT_SECTION_END
# MOSS_EXACT_SECTION_BEGIN
# Bounded 279-to-280 successor: authenticate the whole current world before projection.
const MOSS_PROOF := "res://data/architecture/packages/moss_sanctuary/MOSS_RUNTIME_PROOF.json"
const MOSS_PROOF_SHA := "3761cf9c92e86bfd5552e9dd6e5310913b7ba35cc342436d1922905520a1a1e6"
static var moss_checked := false
static var moss_proof: Dictionary = {}
static var moss_predecessor_text: Dictionary = {}
static var moss_current_compiled: Dictionary = {}

static func _moss_ensure() -> void:
	if moss_checked: return
	_sports_care_ensure()
	assert(FileAccess.get_sha256(MOSS_PROOF)==MOSS_PROOF_SHA,"Exact whole Team Lounge successor proof required")
	moss_proof=JSON.parse_string(FileAccess.get_file_as_string(MOSS_PROOF))
	assert(moss_proof.schema==1 and moss_proof.programme_key=="D06_directory_03")
	assert(moss_proof.added_owner_ids==["D06_moss_sanctuary_receiving_floor"])
	for path in moss_proof.current_sha256:
		assert(_sports_care_current_sha256("res://"+str(path))==str(moss_proof.current_sha256[path]),"Unreviewed lounge postimage: "+str(path))
	for path in moss_proof.predecessors:
		var spec: Dictionary=moss_proof.predecessors[path]
		var retained: String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained)==str(spec.sha256),"Lounge predecessor changed: "+str(path))
		moss_predecessor_text[path]=FileAccess.get_file_as_string(retained)
	var own_source := _sports_care_current_text("res://tests/medical_triage_successor_guard.gd")
	var begin: String="# MOSS_EXACT_SECTION_"+"BEGIN\n"
	var end: String="# MOSS_EXACT_SECTION_"+"END\n"
	assert(own_source.count(begin)==1 and own_source.count(end)==1)
	var start:=own_source.find(begin)
	var finish:=own_source.find(end)+end.length()
	var block:=own_source.substr(start,finish-start)
	assert(block.count(MOSS_PROOF_SHA)==1)
	assert(block.replace(MOSS_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(moss_proof.integration_block_normalized_sha256),"Exact lounge consumer implementation required")
	var recovered:=own_source.substr(0,start)+own_source.substr(finish)
	for edit in moss_proof.consumer_inverse_edits:
		assert(recovered.count(str(edit.after))==int(edit.count),"Exact lounge consumer inverse cardinality")
		recovered=recovered.replace(str(edit.after),str(edit.before))
	assert(recovered==str(moss_predecessor_text["tests/medical_triage_successor_guard.gd"]),"Every preceding botanical, medical and pool consumer byte must survive")
	for path in moss_proof.exact_inverse_edits:
		var restored:=_sports_care_current_text("res://"+str(path))
		for edit in moss_proof.exact_inverse_edits[path]:
			assert(restored.count(str(edit.after))==int(edit.count),"Exact lounge source inverse cardinality")
			restored=restored.replace(str(edit.after),str(edit.before))
		assert(restored==str(moss_predecessor_text[path]),"Every preceding compiler/ship byte must survive: "+str(path))
	var layout: Dictionary=JSON.parse_string(_sports_care_current_text("res://data/spatial_layout.json"))
	var prior_layout: Dictionary=JSON.parse_string(str(moss_predecessor_text["data/spatial_layout.json"]))
	moss_current_compiled=JSON.parse_string(_sports_care_current_text("res://data/generated/structural_meshes.json"))
	var prior_compiled: Dictionary=JSON.parse_string(str(moss_predecessor_text["data/generated/structural_meshes.json"]))
	for pair in [[layout,prior_layout,moss_proof.added_layout_records],[moss_current_compiled,prior_compiled,moss_proof.added_compiled_records]]:
		var wanted: Array=pair[1].regions.duplicate(true)
		wanted.append_array(pair[2])
		assert(pair[0].regions==wanted,"Every full preceding record/order plus exactly the two approved lounge records required")
		var seen: Dictionary={}
		for record in pair[0].regions:
			assert(not seen.has(str(record.id)),"Duplicate current floor owner")
			seen[str(record.id)]=true
	var current_globals: Dictionary=layout.duplicate(true)
	var prior_globals: Dictionary=prior_layout.duplicate(true)
	current_globals.erase("regions");prior_globals.erase("regions")
	assert(current_globals==prior_globals,"Every predecessor global/void record must survive")
	var compiled_globals: Dictionary=moss_current_compiled.duplicate(true)
	var prior_compiled_globals: Dictionary=prior_compiled.duplicate(true)
	for key in ["regions","source_checks"]:
		compiled_globals.erase(key);prior_compiled_globals.erase(key)
	assert(compiled_globals==prior_compiled_globals,"Every non-summary compiler global must survive")
	var summary: Dictionary=JSON.parse_string(_sports_care_current_text("res://docs/LAYOUT_COMPILE_CHECKS.json"))
	assert(summary==moss_current_compiled.source_checks and summary==moss_proof.compile_summary)
	assert(summary.moss_sanctuary_additive_preservation.complete_old_records_preserved)
	assert(moss_current_compiled.regions.size()==280 and prior_compiled.regions.size()==279)
	for row in moss_proof.added_compiled_records:
		assert(row.deck=="D06" and float(row.floor_y)==27 and float(row.thickness)==.24)
	assert(float(moss_proof.added_compiled_records[0].structural_area_m2)==3128.0)
	moss_checked=true

static func _moss_current_text(path: String) -> String:
	_moss_ensure()
	var relative:=_relative(path)
	if relative in moss_proof.projected_paths: return str(moss_predecessor_text[relative])
	return FileAccess.get_file_as_string("res://"+relative)

static func _moss_current_sha256(path: String) -> String:
	_moss_ensure()
	var relative:=_relative(path)
	if relative in moss_proof.projected_paths: return _moss_current_text(relative).sha256_text()
	return FileAccess.get_sha256("res://"+relative)

static func _moss_floor_children(floors: Node) -> Array:
	_moss_ensure()
	var sports_care_predecessor_children: Array=_sports_care_floor_children(floors)
	assert(floors!=null and sports_care_predecessor_children.size()==280,"Complete actual 280-owner roster required before predecessor projection")
	var expected: Dictionary={}
	for record in moss_current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	var children: Array=sports_care_predecessor_children
	for index in range(children.size()):
		assert(children[index] is Node3D)
		var owner: Node3D=children[index] as Node3D
		var ident:=str(owner.name)
		assert(expected.has(ident) and not seen.has(ident),"Unknown, duplicate or missing actual lounge-era owner")
		assert(ident==str(moss_current_compiled.regions[index].id),"Complete owner order changed")
		seen[ident]=true
		_botanical_validate_slab(owner,expected[ident])
		if ident not in moss_proof.added_owner_ids: retained.append(owner)
	assert(seen.size()==280 and retained.size()==279)
	_moss_validate_runtime(floors)
	return retained

static func _moss_v(value: Array) -> Vector3:
	return Vector3(float(value[0]),float(value[1]),float(value[2]))

static func _moss_guard_is_open(name_key: String) -> bool:
	return name_key.begins_with("BOTCOURT_port_PORTAL_CLOSURE_")

static func _moss_validate_runtime(floors: Node) -> void:
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(moss_proof.runtime_manifest)))
	var space: Node=floors.get_parent()
	var source: Node3D=space.get_node("D06_MossSanctuary_Receiving_WIP") as Node3D
	assert(source.transform==Transform3D.IDENTITY and source.get_meta("programme_key","")=="D06_directory_03")
	assert(source.get_meta("source_sha256","")==data.source_sha256)
	assert(FileAccess.get_sha256(str(data.derivative_file))==data.derivative_sha256)
	var options:=ConfigFile.new()
	assert(options.load(str(data.derivative_file)+".import")==OK)
	assert(bool(options.get_value("params","meshes/force_disable_compression",false)))
	assert(not bool(options.get_value("params","meshes/generate_lods",true)))
	assert(str(options.get_value("params","nodes/root_type",""))=="Node3D")
	var nodes: Dictionary={}
	for node in source.find_children("WP10_N*","Node3D",true,false):
		assert(not nodes.has(str(node.name)));nodes[str(node.name)]=node
	var template: Node3D=(load(str(data.derivative_file)) as PackedScene).instantiate()
	var meshes:=0
	for original in template.find_children("*","Node3D",true,false):
		assert(nodes.has(str(original.name)))
		var actual: Node3D=nodes[str(original.name)]
		assert(actual.get_class()==original.get_class() and actual.transform==original.transform)
		if not original is MeshInstance3D: continue
		meshes+=1
		var actual_mesh: MeshInstance3D=actual as MeshInstance3D
		assert(actual_mesh.visible and actual_mesh.mesh==original.mesh)
		var contacts: Array=actual.find_children("*","CollisionShape3D",false,false)
		contacts=actual.find_children("ExactMeshLocalFaces","CollisionShape3D",true,false)
		if str(actual.name)==str(data.water_node):
			assert(contacts.is_empty() and actual.find_children("*","StaticBody3D",true,false).is_empty())
			var water: ShaderMaterial=actual_mesh.material_override as ShaderMaterial
			assert(water!=null and water.shader==load("res://shaders/flowing_water.gdshader") and is_equal_approx(float(water.get_shader_parameter("flow_speed")),.12))
		else:
			assert(actual_mesh.material_override==null and contacts.size()==1 and not contacts[0].disabled)
			assert(contacts[0].shape is ConcavePolygonShape3D and contacts[0].get_parent().collision_layer==1 and contacts[0].get_parent().collision_mask==1)
			var expected: ConcavePolygonShape3D=actual_mesh.mesh.create_trimesh_shape()
			assert(contacts[0].shape.get_faces()==expected.get_faces())
	assert(meshes==976 and source.find_children("*","StaticBody3D",true,false).size()==975)
	template.free()
	_moss_validate_import(source,str(data.derivative_file).get_file(),976)
	assert(source.find_children("*","Light3D",true,false).size()==36)
	for record in data.lights:
		var parent: Node3D=nodes[str(record.runtime_name)]
		var lamp: SpotLight3D=parent.get_node("PhysicalSource") as SpotLight3D
		assert(lamp.transform==Transform3D.IDENTITY and lamp.get_meta("fixture_powered",false) and lamp.get_meta("source_fixture","")==record.source_name)
		assert(lamp.get_meta("receiving_calibration_pending",false))
		var wanted:=SpotLight3D.new()
		wanted.light_energy=float(record.energy);wanted.spot_range=float(record.range_m);wanted.spot_angle=float(record.outer_angle_degrees)
		assert(lamp.light_energy==wanted.light_energy and lamp.spot_range==wanted.spot_range and lamp.spot_angle==wanted.spot_angle)
		assert(lamp.light_color==Color(record.color[0],record.color[1],record.color[2]))
		wanted.free()
	var info: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/moss_sanctuary/information_targets.json"))
	for record in info.candidates:
		var target: Node3D=source.get_node(NodePath(str(record.id)))
		assert(target.get_script()==load("res://scripts/moss_sanctuary/amenity_information.gd"))
		assert(target.candidate_id==str(record.id) and target.prompt==str(record.label) and target.information==str(record.information))
		assert(target.global_position.distance_to(_moss_v(record.focus_world_m))<.00001)
		var area: Area3D=target.get_node("AuthoredInformationTarget")
		assert(area.collision_layer==2 and area.collision_mask==0 and not area.monitoring and not area.monitorable)
		var shape: CollisionShape3D=area.get_child(0)
		assert(not shape.disabled and shape.shape is BoxShape3D and shape.shape.size==_moss_v(record.target_size_m))
	var owner: Node=floors.get_node(NodePath(str(data.floor_owner)))
	var finished:=0
	for key in data.finish_top_chunks:
		var visual: MeshInstance3D=owner.get_node(NodePath(str(key)))
		var material: ShaderMaterial=visual.get_surface_override_material(0)
		assert(material!=null and material.shader==load(str(data.floor_shader)))
		for texture in data.finish_textures: assert(material.get_shader_parameter(str(texture.role))==load(str(texture.file)))
		finished+=1
	assert(finished==moss_proof.added_compiled_records[0].render_chunks.size())
	var wrapper: Node=space.get_node("BotanicalCourtReceivingClosedInterim")
	var opened:=0
	var closed:=0
	for visual in wrapper.find_children("*","MeshInstance3D",true,false):
		var contacts: Array=visual.find_children("*","CollisionShape3D",true,false)
		assert(contacts.size()==1)
		if str(visual.name) in data.opened_guard_names:
			assert(not visual.visible and contacts[0].disabled and visual.get_meta("moss_supported_portal_open",false));opened+=1
		else:
			assert(visual.visible and not contacts[0].disabled and not visual.has_meta("moss_supported_portal_open"));closed+=1
	load("res://tests/botanical_pair_court_guard.gd").validate_moss_roster(wrapper,opened,closed,data.opened_guard_names)
	var budgets: Array=space.get_parent().find_children("LocalShadowSourceBudget","Node",true,false)
	assert(budgets.size()==1 and budgets[0].shadow_source_budget==8 and budgets[0].MAX_VISIBILITY_CANDIDATES==32)

static func _moss_validate_import(source: Node3D, filename: String, mesh_count: int) -> void:
	var actual: Dictionary={}
	for node in source.find_children("WP10_N*","Node3D",true,false):
		assert(not actual.has(str(node.name)));actual[str(node.name)]=node
	# Decode the pinned GLB independently; a second imported template alone cannot
	# establish that the importer preserved the source's actual position/UV arrays.
	var blob:=FileAccess.get_file_as_bytes("res://assets/models/"+filename)
	assert(blob.decode_u32(0)==0x46546c67 and blob.decode_u32(4)==2 and blob.decode_u32(8)==blob.size())
	var json_size:=int(blob.decode_u32(12))
	assert(blob.decode_u32(16)==0x4e4f534a)
	var document: Dictionary=JSON.parse_string(blob.slice(20,20+json_size).get_string_from_utf8())
	var binary_start:=20+json_size
	var binary_size:=int(blob.decode_u32(binary_start))
	assert(blob.decode_u32(binary_start+4)==0x004e4942 and binary_start+8+binary_size==blob.size())
	var binary:=blob.slice(binary_start+8)
	assert(document.nodes.size()==actual.size())
	var parents: Dictionary={}
	for index in range(document.nodes.size()):
		for child in document.nodes[index].get("children",[]):
			assert(not parents.has(int(child)),"Derivative source must be a unique-parent tree")
			parents[int(child)]=index
	var source_triangles:=0
	var source_meshes:=0
	var material_seen: Dictionary={}
	for index in range(document.nodes.size()):
		var record: Dictionary=document.nodes[index]
		var name_key:=str(record.name)
		assert(actual.has(name_key),"Every original identity and generated batch must survive import")
		var node: Node3D=actual[name_key] as Node3D
		assert(node!=null)
		var parent: Node=source if not parents.has(index) else actual[str(document.nodes[int(parents[index])].name)]
		assert(node.get_parent()==parent,"Exact source parentage must survive import")
		assert(node.position==_team_lounge_v(record.get("translation",[0,0,0])),"Exact source local translation must survive import")
		if not record.has("mesh"): continue
		assert(node is MeshInstance3D)
		var visual: MeshInstance3D=node as MeshInstance3D
		var expected_mesh: Dictionary=document.meshes[int(record.mesh)]
		assert(visual.mesh.get_surface_count()==expected_mesh.primitives.size())
		source_meshes+=1
		for surface in range(expected_mesh.primitives.size()):
			var primitive: Dictionary=expected_mesh.primitives[surface]
			assert(int(primitive.get("mode",4))==4 and primitive.attributes.has("POSITION") and primitive.attributes.has("TEXCOORD_0"))
			var position_accessor:=_team_lounge_accessor(document,binary,int(primitive.attributes.POSITION))
			var uv_accessor:=_team_lounge_accessor(document,binary,int(primitive.attributes.TEXCOORD_0))
			assert(position_accessor.type=="VEC3" and uv_accessor.type=="VEC2" and position_accessor.component_type==5126 and uv_accessor.component_type==5126)
			assert(position_accessor.count==uv_accessor.count)
			var positions: PackedFloat32Array=position_accessor.bytes.to_float32_array()
			var uvs: PackedFloat32Array=uv_accessor.bytes.to_float32_array()
			var indices:=_team_lounge_source_indices(document,binary,primitive,int(position_accessor.count))
			assert(indices.size()%3==0)
			var keys: Array[String]=[]
			keys.resize(int(position_accessor.count))
			for vertex in range(keys.size()): keys[vertex]=_team_lounge_corner_key(Vector3(positions[vertex*3],positions[vertex*3+1],positions[vertex*3+2]),Vector2(uvs[vertex*2],uvs[vertex*2+1]))
			var expected: Dictionary={}
			for start in range(0,indices.size(),3):
				# glTF counter-clockwise winding is reversed by Godot's importer.
				var corners: Array[String]=[keys[indices[start]],keys[indices[start+2]],keys[indices[start+1]]]
				var key:=_team_lounge_oriented_triangle(corners)
				expected[key]=int(expected.get(key,0))+1
			assert(_team_lounge_import_surface(visual.mesh,surface)==expected,"Exact derivative position/UV/winding/multiplicity must survive; no degenerate-face exemption")
			source_triangles+=int(indices.size()/3)
			var material_index:=int(primitive.material)
			var material: Material=visual.mesh.surface_get_material(surface)
			assert(material!=null and material.resource_name==str(document.materials[material_index].name),"Exact source material assignment required")
			if material_seen.has(material_index): assert(material_seen[material_index]==material)
			else: material_seen[material_index]=material
	assert(source_meshes==mesh_count)
	assert(source_triangles==760942)
# MOSS_EXACT_SECTION_END
# SPORTS_CARE_EXACT_SECTION_BEGIN
# Bounded 280-to-282 successor: authenticate the whole current world before projection.
const SPORTS_CARE_PROOF := "res://data/architecture/packages/sports_care/SPORTS_CARE_RUNTIME_PROOF.json"
const SPORTS_CARE_PROOF_SHA := "ae06c4068c7f379e5fbbdbfeac2e41feda8b8441cec69766a80c5c2c7358fad8"
static var sports_care_checked := false
static var sports_care_proof: Dictionary = {}
static var sports_care_predecessor_text: Dictionary = {}
static var sports_care_current_compiled: Dictionary = {}

static func _sports_care_ensure() -> void:
	if sports_care_checked: return
	_sports_sign_ensure()
	assert(FileAccess.get_sha256(SPORTS_CARE_PROOF)==SPORTS_CARE_PROOF_SHA,"Exact whole Team Lounge successor proof required")
	sports_care_proof=JSON.parse_string(FileAccess.get_file_as_string(SPORTS_CARE_PROOF))
	assert(sports_care_proof.schema==1 and sports_care_proof.programme_key=="D07_directory_10")
	assert(sports_care_proof.added_owner_ids==["D07_sports_care_floor","D07_sports_care_entry"])
	for path in sports_care_proof.current_sha256:
		assert(_sports_sign_current_sha256("res://"+str(path))==str(sports_care_proof.current_sha256[path]),"Unreviewed lounge postimage: "+str(path))
	for path in sports_care_proof.predecessors:
		var spec: Dictionary=sports_care_proof.predecessors[path]
		var retained: String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained)==str(spec.sha256),"Lounge predecessor changed: "+str(path))
		sports_care_predecessor_text[path]=FileAccess.get_file_as_string(retained)
	var own_source := _sports_sign_current_text("res://tests/medical_triage_successor_guard.gd")
	var begin: String="# SPORTS_CARE_EXACT_SECTION_"+"BEGIN\n"
	var end: String="# SPORTS_CARE_EXACT_SECTION_"+"END\n"
	assert(own_source.count(begin)==1 and own_source.count(end)==1)
	var start:=own_source.find(begin)
	var finish:=own_source.find(end)+end.length()
	var block:=own_source.substr(start,finish-start)
	assert(block.count(SPORTS_CARE_PROOF_SHA)==1)
	assert(block.replace(SPORTS_CARE_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(sports_care_proof.integration_block_normalized_sha256),"Exact lounge consumer implementation required")
	var recovered:=own_source.substr(0,start)+own_source.substr(finish)
	for edit in sports_care_proof.consumer_inverse_edits:
		assert(recovered.count(str(edit.after))==int(edit.count),"Exact lounge consumer inverse cardinality")
		recovered=recovered.replace(str(edit.after),str(edit.before))
	assert(recovered==str(sports_care_predecessor_text["tests/medical_triage_successor_guard.gd"]),"Every preceding botanical, medical and pool consumer byte must survive")
	for path in sports_care_proof.exact_inverse_edits:
		var restored:=_star_fitted_current_text("res://"+str(path))
		for edit in sports_care_proof.exact_inverse_edits[path]:
			assert(restored.count(str(edit.after))==int(edit.count),"Exact lounge source inverse cardinality")
			restored=restored.replace(str(edit.after),str(edit.before))
		assert(restored==str(sports_care_predecessor_text[path]),"Every preceding compiler/ship byte must survive: "+str(path))
	var layout: Dictionary=JSON.parse_string(_night_current_text("res://data/spatial_layout.json"))
	var prior_layout: Dictionary=JSON.parse_string(str(sports_care_predecessor_text["data/spatial_layout.json"]))
	sports_care_current_compiled=JSON.parse_string(_night_current_text("res://data/generated/structural_meshes.json"))
	var prior_compiled: Dictionary=JSON.parse_string(str(sports_care_predecessor_text["data/generated/structural_meshes.json"]))
	for pair in [[layout,prior_layout,sports_care_proof.added_layout_records],[sports_care_current_compiled,prior_compiled,sports_care_proof.added_compiled_records]]:
		var wanted: Array=pair[1].regions.duplicate(true)
		wanted.append_array(pair[2])
		assert(pair[0].regions==wanted,"Every full preceding record/order plus exactly the two approved lounge records required")
		var seen: Dictionary={}
		for record in pair[0].regions:
			assert(not seen.has(str(record.id)),"Duplicate current floor owner")
			seen[str(record.id)]=true
	var current_globals: Dictionary=layout.duplicate(true)
	var prior_globals: Dictionary=prior_layout.duplicate(true)
	current_globals.erase("regions");prior_globals.erase("regions")
	assert(current_globals==prior_globals,"Every predecessor global/void record must survive")
	var compiled_globals: Dictionary=sports_care_current_compiled.duplicate(true)
	var prior_compiled_globals: Dictionary=prior_compiled.duplicate(true)
	for key in ["regions","source_checks"]:
		compiled_globals.erase(key);prior_compiled_globals.erase(key)
	assert(compiled_globals==prior_compiled_globals,"Every non-summary compiler global must survive")
	var summary: Dictionary=JSON.parse_string(_night_current_text("res://docs/LAYOUT_COMPILE_CHECKS.json"))
	assert(summary==sports_care_current_compiled.source_checks and summary==sports_care_proof.compile_summary)
	assert(summary.sports_care_additive_preservation.complete_old_records_preserved)
	assert(sports_care_current_compiled.regions.size()==282 and prior_compiled.regions.size()==280)
	for row in sports_care_proof.added_compiled_records:
		assert(row.deck=="D07" and float(row.floor_y)==35.5 and float(row.thickness)==.24)
	assert(float(sports_care_proof.added_compiled_records[0].structural_area_m2)==3128.0)
	assert(float(sports_care_proof.added_compiled_records[1].structural_area_m2)==32.0)
	sports_care_checked=true

static func _sports_care_current_text(path: String) -> String:
	_sports_care_ensure()
	var relative:=_relative(path)
	if relative=="tests/validate_botanical_receiving_access.gd":return load("res://tests/botanical_pair_successor_guard.gd").current_text("res://"+relative)
	if relative in sports_care_proof.projected_paths: return str(sports_care_predecessor_text[relative])
	return FileAccess.get_file_as_string("res://"+relative)

static func _sports_care_current_sha256(path: String) -> String:
	_sports_care_ensure()
	var relative:=_relative(path)
	if relative=="tests/validate_botanical_receiving_access.gd":return load("res://tests/botanical_pair_successor_guard.gd").current_sha256("res://"+relative)
	if relative in sports_care_proof.projected_paths: return _sports_care_current_text(relative).sha256_text()
	return FileAccess.get_sha256("res://"+relative)

static func _sports_care_floor_children(floors: Node) -> Array:
	_sports_care_ensure()
	assert(floors!=null)
	var children: Array=_night_floor_children(floors)
	assert(children.size()==282,"Complete actual 284-owner roster authenticated before predecessor projection")
	var expected: Dictionary={}
	for record in sports_care_current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	for index in range(children.size()):
		assert(children[index] is Node3D)
		var owner: Node3D=children[index] as Node3D
		var ident:=str(owner.name)
		assert(expected.has(ident) and not seen.has(ident),"Unknown, duplicate or missing actual lounge-era owner")
		assert(ident==str(sports_care_current_compiled.regions[index].id),"Complete owner order changed")
		seen[ident]=true
		_botanical_validate_slab(owner,expected[ident])
		if ident not in sports_care_proof.added_owner_ids: retained.append(owner)
	assert(seen.size()==282 and retained.size()==280)
	_sports_care_validate_runtime(floors)
	return retained

static func _sports_care_v(a: Array) -> Vector3:
	return Vector3(float(a[0]),float(a[1]),float(a[2]))

static func _sports_care_model(wrapper: Node3D, filename: String, count: int) -> void:
	var template: Node3D=(load("res://assets/models/"+filename) as PackedScene).instantiate() as Node3D
	var actual: Node3D=wrapper.get_node(NodePath(str(template.name))) as Node3D
	assert(actual!=null and actual.transform==template.transform)
	var meshes:=0
	var nodes: Array=[template]
	nodes.append_array(template.find_children("*","Node",true,false))
	for expected in nodes:
		var node: Node=actual if expected==template else actual.get_node(template.get_path_to(expected))
		assert(node.get_class()==expected.get_class() and node.get_script()==expected.get_script())
		if node is Node3D: assert(node.transform==expected.transform,"Exact imported source pose changed")
		if node is MeshInstance3D:
			meshes+=1
			assert(node.visible and node.material_override==null and node.mesh!=null)
			assert(node.mesh.get_surface_count()==expected.mesh.get_surface_count())
			for surface in range(node.mesh.get_surface_count()):
				assert(node.mesh.surface_get_arrays(surface)==expected.mesh.surface_get_arrays(surface))
				assert(node.get_surface_override_material(surface)==null and node.get_active_material(surface)==expected.get_active_material(surface))
			var body: StaticBody3D=node.get_node("StaticContact") as StaticBody3D
			assert(body!=null and body.transform==Transform3D.IDENTITY and body.get_child_count()==1)
			assert(body.collision_layer==1 and body.collision_mask==1 and body.get_script()==null)
			var contact: CollisionShape3D=body.get_node("SharedShape") as CollisionShape3D
			assert(contact!=null and not contact.disabled and contact.transform==Transform3D.IDENTITY and contact.get_script()==null)
			assert(contact.shape is ConcavePolygonShape3D)
			var wanted: ConcavePolygonShape3D=expected.mesh.create_trimesh_shape()
			assert(contact.shape.get_faces()==wanted.get_faces(),"Complete imported source contact faces changed")
		assert(node.get_child_count()==expected.get_child_count()+(1 if node is MeshInstance3D else 0),"Unexpected source child")
	_sports_care_validate_import(template,filename,count)
	assert(meshes==count and actual.find_children("*","StaticBody3D",true,false).size()==count)
	assert(actual.find_children("*","Light3D",true,false).is_empty())
	template.free()

static func _sports_care_validate_runtime(floors: Node) -> void:
	var d: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(sports_care_proof.runtime_manifest)))
	var ship: Node=floors.get_parent().get_parent()
	var parent: Node=ship.get_node("ShipSpace/Districts")
	var roots: Array=ship.find_children(str(d.root_name),"Node3D",true,false)
	assert(roots.size()==1 and roots[0].get_parent()==parent)
	var root: Node3D=roots[0] as Node3D
	assert(root.transform==Transform3D.IDENTITY and root.get_child_count()==49 and root.get_script()==null)
	assert(root.get_meta("programme_key","")=="D07_directory_10" and root.get_meta("persistent_id","")==str(d.persistent_id))
	assert(root.get_meta("first_pass_quality_accepted",true)==false and root.get_meta("capacity_accepted",true)==false)
	assert(root.get_meta("source_receiving_contract",{})==d)
	var room: Node3D=root.get_node("WholeRetainedSportsCare") as Node3D
	var guards: Node3D=root.get_node("SourceDerivedReceivingGuards") as Node3D
	assert(room.transform==Transform3D(Basis.IDENTITY,_sports_care_v(d.placement)) and guards.transform==Transform3D.IDENTITY)
	assert(room.get_child_count()==3 and guards.get_child_count()==1)
	for pair in [[d.model_file,d.model_sha256],[d.guard_file,d.guard_sha256]]:
		var path: String="res://assets/models/"+str(pair[0])
		assert(FileAccess.get_sha256(path)==str(pair[1]))
		var options:=ConfigFile.new()
		assert(options.load(path+".import")==OK)
		assert(bool(options.get_value("params","meshes/force_disable_compression",false)))
		assert(not bool(options.get_value("params","meshes/generate_lods",true)))
		assert(str(options.get_value("params","nodes/root_type",""))=="Node3D")
	_sports_care_model(room,str(d.model_file),1734)
	_sports_sign_validate_unaffected(room)
	_sports_care_model(guards,str(d.guard_file),20)
	var identities: Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/packages/sports_care/NODE_BIJECTION.json"))
	assert(identities.size()==1908)
	for spec in identities: assert(room.find_children(str(spec.runtime_name),"Node",true,false).size()==1)
	assert(d.source_labels==79)
	var labels: Array=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/packages/sports_care/ORIGINAL_LABELS.json"))
	assert(labels.size()==79)
	var source_names: Dictionary={}
	for spec in identities: source_names[str(spec.source_name)]=str(spec.runtime_name)
	for spec in labels:
		assert(source_names.has(str(spec.name)))
		assert(room.find_child(str(source_names[str(spec.name)]),true,false) is MeshInstance3D)
	assert(d.lights.size()==47 and root.find_children("*","Light3D",true,false).size()==47)
	for spec in d.lights:
		var lamp: SpotLight3D=root.get_node(NodePath(str(spec.id))) as SpotLight3D
		assert(lamp!=null and lamp.position==_sports_care_v(spec.world) and lamp.rotation==Vector3(-PI/2.0,0,0))
		var expected_lamp:=SpotLight3D.new()
		expected_lamp.spot_range=float(spec.spot_range);expected_lamp.spot_angle=float(spec.spot_angle_degrees);expected_lamp.light_energy=float(spec.spot_energy)
		assert(lamp.spot_range==expected_lamp.spot_range and lamp.spot_angle==expected_lamp.spot_angle and lamp.light_energy==expected_lamp.light_energy)
		expected_lamp.free()
		assert(lamp.light_color==Color(float(spec.color[0]),float(spec.color[1]),float(spec.color[2])))
		assert(lamp.get_meta("source_light_id","")==str(spec.source_id) and lamp.get_meta("fixture_node","")==str(spec.fixture_node))
		assert(lamp.get_meta("receiving_calibration_unaccepted",false)==true and lamp.get_script()==null)
		var fixture: MeshInstance3D=room.find_child(str(spec.fixture_node),true,false) as MeshInstance3D
		var bounds: AABB=fixture.global_transform*fixture.get_aabb()
		assert(lamp.global_position.y<bounds.position.y and bounds.position.y-lamp.global_position.y<0.12)
	var info: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/packages/sports_care/INFORMATION_TARGETS.json"))
	assert(info.candidates.size()==2)
	for spec in info.candidates:
		var target: Node3D=room.get_node(NodePath(str(spec.id))) as Node3D
		assert(target.get_script()==load("res://scripts/sports_care/amenity_information.gd"))
		assert(target.candidate_id==str(spec.id) and target.prompt==str(spec.label) and target.information==str(spec.information))
		assert(target.global_position.distance_to(_sports_care_v(spec.focus_world_m))<0.00001 and target.get_child_count()==1)
		var area: Area3D=target.get_node("AuthoredInformationTarget") as Area3D
		assert(area.collision_layer==2 and area.collision_mask==0 and not area.monitoring and not area.monitorable and area.get_child_count()==1)
		var shape: CollisionShape3D=area.get_child(0) as CollisionShape3D
		assert(not shape.disabled and shape.shape is BoxShape3D and shape.shape.size==_sports_care_v(spec.target_size_m))
	var owner: Node=floors.get_node(NodePath(str(d.floor_owners[0])))
	var chunks:=0
	for node in owner.find_children("cell_*","MeshInstance3D",true,false):
		var material: ShaderMaterial=node.get_surface_override_material(0) as ShaderMaterial
		assert(material!=null and material.shader==load(str(d.floor_shader)))
		assert(material.get_shader_parameter("warm_stone_texture")==load("res://assets/models/WP02_receiving_warm_stone.png"))
		assert(material.get_shader_parameter("oatmeal_texture")==load("res://assets/models/WP02_receiving_oatmeal_weave.png"))
		assert(material.get_shader_parameter("enamel_texture")==load("res://assets/models/WP02_receiving_ivory_enamel.png"))
		chunks+=1
	assert(chunks==sports_care_proof.added_compiled_records[0].render_chunks.size())
	var budgets: Array=ship.find_children("LocalShadowSourceBudget","Node",true,false)
	assert(budgets.size()==1 and budgets[0].shadow_source_budget==8 and budgets[0].MAX_VISIBILITY_CANDIDATES==32)

static func _sports_care_validate_import(source: Node3D, filename: String, mesh_count: int) -> void:
	var actual: Dictionary={}
	for node in source.find_children("*","Node3D",true,false):
		assert(not actual.has(str(node.name)));actual[str(node.name)]=node
	# Decode the pinned GLB independently; a second imported template alone cannot
	# establish that the importer preserved the source's actual position/UV arrays.
	var blob:=FileAccess.get_file_as_bytes("res://assets/models/"+filename)
	assert(blob.decode_u32(0)==0x46546c67 and blob.decode_u32(4)==2 and blob.decode_u32(8)==blob.size())
	var json_size:=int(blob.decode_u32(12))
	assert(blob.decode_u32(16)==0x4e4f534a)
	var document: Dictionary=JSON.parse_string(blob.slice(20,20+json_size).get_string_from_utf8())
	var binary_start:=20+json_size
	var binary_size:=int(blob.decode_u32(binary_start))
	assert(blob.decode_u32(binary_start+4)==0x004e4942 and binary_start+8+binary_size==blob.size())
	var binary:=blob.slice(binary_start+8)
	assert(document.nodes.size()==actual.size())
	var parents: Dictionary={}
	for index in range(document.nodes.size()):
		for child in document.nodes[index].get("children",[]):
			assert(not parents.has(int(child)),"Derivative source must be a unique-parent tree")
			parents[int(child)]=index
	var source_triangles:=0
	var source_meshes:=0
	var material_seen: Dictionary={}
	for index in range(document.nodes.size()):
		var record: Dictionary=document.nodes[index]
		var name_key:=str(record.name)
		assert(actual.has(name_key),"Every original identity and generated batch must survive import")
		var node: Node3D=actual[name_key] as Node3D
		assert(node!=null)
		var parent: Node=source if not parents.has(index) else actual[str(document.nodes[int(parents[index])].name)]
		assert(node.get_parent()==parent,"Exact source parentage must survive import")
		assert(node.position==_team_lounge_v(record.get("translation",[0,0,0])),"Exact source local translation must survive import")
		assert(not record.has("matrix"),"Current Sports Care source is TRS-only; a changed transform format needs review")
		var rotation_source: Array=record.get("rotation",[0,0,0,1])
		var expected_basis:=Basis(Quaternion(float(rotation_source[0]),float(rotation_source[1]),float(rotation_source[2]),float(rotation_source[3])))
		expected_basis=expected_basis.scaled(_team_lounge_v(record.get("scale",[1,1,1])))
		for axis in range(3): assert(node.basis[axis].distance_to(expected_basis[axis])<0.000001,"Source TRS basis changed during import")
		if not record.has("mesh"): continue
		assert(node is MeshInstance3D)
		var visual: MeshInstance3D=node as MeshInstance3D
		var expected_mesh: Dictionary=document.meshes[int(record.mesh)]
		assert(visual.mesh.get_surface_count()==expected_mesh.primitives.size())
		source_meshes+=1
		for surface in range(expected_mesh.primitives.size()):
			var primitive: Dictionary=expected_mesh.primitives[surface]
			assert(int(primitive.get("mode",4))==4 and primitive.attributes.has("POSITION") and primitive.attributes.has("TEXCOORD_0"))
			var position_accessor:=_team_lounge_accessor(document,binary,int(primitive.attributes.POSITION))
			var uv_accessor:=_team_lounge_accessor(document,binary,int(primitive.attributes.TEXCOORD_0))
			assert(position_accessor.type=="VEC3" and uv_accessor.type=="VEC2" and position_accessor.component_type==5126 and uv_accessor.component_type==5126)
			assert(position_accessor.count==uv_accessor.count)
			var positions: PackedFloat32Array=position_accessor.bytes.to_float32_array()
			var uvs: PackedFloat32Array=uv_accessor.bytes.to_float32_array()
			var indices:=_team_lounge_source_indices(document,binary,primitive,int(position_accessor.count))
			assert(indices.size()%3==0)
			var keys: Array[String]=[]
			keys.resize(int(position_accessor.count))
			for vertex in range(keys.size()): keys[vertex]=_team_lounge_corner_key(Vector3(positions[vertex*3],positions[vertex*3+1],positions[vertex*3+2]),Vector2(uvs[vertex*2],uvs[vertex*2+1]))
			var expected: Dictionary={}
			for start in range(0,indices.size(),3):
				# glTF counter-clockwise winding is reversed by Godot's importer.
				var corners: Array[String]=[keys[indices[start]],keys[indices[start+2]],keys[indices[start+1]]]
				var key:=_team_lounge_oriented_triangle(corners)
				expected[key]=int(expected.get(key,0))+1
			assert(_team_lounge_import_surface(visual.mesh,surface)==expected,"Exact derivative position/UV/winding/multiplicity must survive; no degenerate-face exemption")
			source_triangles+=int(indices.size()/3)
			var material_index:=int(primitive.material)
			var material: Material=visual.get_active_material(surface)
			assert(material!=null and material.resource_name==str(document.materials[material_index].name),"Exact source material assignment required")
			if material_seen.has(material_index): assert(material_seen[material_index]==material)
			else: material_seen[material_index]=material
	assert(source_meshes==mesh_count)
	assert(source_triangles==_sports_sign_expected_triangles(filename,mesh_count),"Exact filename-pinned triangle multiplicity, including every degenerate face")
# SPORTS_CARE_EXACT_SECTION_END
# SPORTS_SIGN_EXACT_SECTION_BEGIN
# Exactly four stable source nodes, no owner/compiler or unrelated runtime exception.
const SPORTS_SIGN_PROOF := "res://data/architecture/packages/sports_care/sign_insert002/SIGN_RUNTIME_PROOF.json"
const SPORTS_SIGN_PROOF_SHA := "78dfaad2bfbfff34a2e71adf53fd42d8908270be90f65166e5f91c249424a74a"
static var sports_sign_checked := false
static var sports_sign_proof: Dictionary = {}
static var sports_sign_predecessor_text: Dictionary = {}
static var sports_sign_material_pairs: Dictionary = {}

static func _sports_sign_ensure() -> void:
	if sports_sign_checked: return
	_star_fitted_ensure()
	assert(FileAccess.get_sha256(SPORTS_SIGN_PROOF)==SPORTS_SIGN_PROOF_SHA)
	sports_sign_proof=JSON.parse_string(FileAccess.get_file_as_string(SPORTS_SIGN_PROOF))
	assert(sports_sign_proof.schema==1 and sports_sign_proof.allowed_nodes==["WP02N_0051","WP02N_0052","WP02N_0053","WP02N_0054"])
	for path in sports_sign_proof.current_sha256:
		assert(_star_fitted_current_sha256("res://"+str(path))==str(sports_sign_proof.current_sha256[path]),"Unreviewed signage postimage: "+str(path))
	for path in sports_sign_proof.predecessors:
		var spec: Dictionary=sports_sign_proof.predecessors[path]
		assert(FileAccess.get_sha256("res://"+str(spec.retained_path))==str(spec.sha256))
		sports_sign_predecessor_text[path]=FileAccess.get_file_as_string("res://"+str(spec.retained_path))
	var source:=_star_fitted_current_text("res://tests/medical_triage_successor_guard.gd")
	var first: String="# SPORTS_SIGN_EXACT_SECTION_"+"BEGIN\n"
	var last: String="# SPORTS_SIGN_EXACT_SECTION_"+"END\n"
	assert(source.count(first)==1 and source.count(last)==1)
	var start:=source.find(first)
	var end:=source.find(last)+last.length()
	var block:=source.substr(start,end-start)
	assert(block.count(SPORTS_SIGN_PROOF_SHA)==1)
	assert(block.replace(SPORTS_SIGN_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(sports_sign_proof.block_normalized_sha256))
	var recovered:=source.substr(0,start)+source.substr(end)
	for edit in sports_sign_proof.guard_inverse_edits:
		assert(recovered.count(str(edit.after))==int(edit.count))
		recovered=recovered.replace(str(edit.after),str(edit.before))
	assert(recovered==str(sports_sign_predecessor_text["tests/medical_triage_successor_guard.gd"]),"Every prior proof byte must survive the exact bounded successor")
	var old_contract: Dictionary=JSON.parse_string(str(sports_sign_predecessor_text[str(sports_sign_proof.runtime_path)]))
	var wanted_contract: Dictionary=old_contract.duplicate(true)
	wanted_contract.model_file=sports_sign_proof.new_model_file
	wanted_contract.model_sha256=sports_sign_proof.new_model_sha256
	assert(JSON.parse_string(FileAccess.get_file_as_string("res://"+str(sports_sign_proof.runtime_path)))==wanted_contract,"Only model filename/hash may change in room contract")
	var old_info: Dictionary=JSON.parse_string(str(sports_sign_predecessor_text[str(sports_sign_proof.information_path)]))
	var wanted_info: Dictionary=old_info.duplicate(true)
	var patched:=0
	for target in wanted_info.candidates:
		if str(target.id)=="WP02_info_care_01":
			assert(target.visual_node=="WP02N_0052")
			target.focus_world_m=sports_sign_proof.focus_world_m
			target.target_size_m=sports_sign_proof.target_size_m
			patched+=1
	assert(patched==1 and JSON.parse_string(FileAccess.get_file_as_string("res://"+str(sports_sign_proof.information_path)))==wanted_info,"All target identity/prose/access/approach fields remain exact")
	var old_labels: Array=JSON.parse_string(str(sports_sign_predecessor_text[str(sports_sign_proof.labels_path)]))
	var wanted_labels: Array=old_labels.duplicate(true)
	patched=0
	for label in wanted_labels:
		if str(label.name)=="CareInfoCopy": label.text="SunCorp  |  CLOTHS / PADS";patched+=1
	assert(patched==1 and JSON.parse_string(FileAccess.get_file_as_string("res://"+str(sports_sign_proof.labels_path)))==wanted_labels)
	var old_fixture: Dictionary=JSON.parse_string(str(sports_sign_predecessor_text[str(sports_sign_proof.fixture_path)]))
	var wanted_fixture: Dictionary=old_fixture.duplicate(true)
	wanted_fixture.runtime_sha256=sports_sign_proof.current_sha256[str(sports_sign_proof.runtime_path)]
	wanted_fixture.information_manifest_sha256=sports_sign_proof.current_sha256[str(sports_sign_proof.information_path)]
	assert(JSON.parse_string(FileAccess.get_file_as_string("res://"+str(sports_sign_proof.fixture_path)))==wanted_fixture,"All378 privacy rays, paths, interactions and input pins remain unchanged")
	var runner:=FileAccess.get_file_as_string("res://"+str(sports_sign_proof.runner_path))
	var runner_edit: Dictionary=sports_sign_proof.runner_hash_inverse
	assert(runner.count(str(runner_edit.after))==1)
	assert(runner.replace(str(runner_edit.after),str(runner_edit.before))==str(sports_sign_predecessor_text[str(sports_sign_proof.runner_path)]),"No acceptance assertion may change")
	_sports_sign_validate_source_delta()
	sports_sign_checked=true

static func _sports_sign_current_text(path: String) -> String:
	_sports_sign_ensure()
	var relative:=_relative(path)
	if sports_sign_predecessor_text.has(relative): return str(sports_sign_predecessor_text[relative])
	return FileAccess.get_file_as_string("res://"+relative)

static func _sports_sign_current_sha256(path: String) -> String:
	_sports_sign_ensure()
	var relative:=_relative(path)
	if sports_sign_predecessor_text.has(relative): return str(sports_sign_predecessor_text[relative]).sha256_text()
	return _star_fitted_current_sha256("res://"+relative)

static func _sports_sign_glb(filename: String) -> Dictionary:
	var raw:=FileAccess.get_file_as_bytes("res://assets/models/"+filename)
	assert(raw.decode_u32(0)==0x46546c67 and raw.decode_u32(4)==2 and raw.decode_u32(8)==raw.size())
	var length:=int(raw.decode_u32(12))
	assert(raw.decode_u32(16)==0x4e4f534a)
	var at:=20+length
	assert(raw.decode_u32(at+4)==0x004e4942 and at+8+int(raw.decode_u32(at))==raw.size())
	return {"document":JSON.parse_string(raw.slice(20,at).get_string_from_utf8()),"binary":raw.slice(at+8)}

static func _sports_sign_validate_source_delta() -> void:
	var prior:=_sports_sign_glb(str(sports_sign_proof.old_model_file))
	var current:=_sports_sign_glb(str(sports_sign_proof.new_model_file))
	var old: Dictionary=prior.document
	var now: Dictionary=current.document
	var original: PackedByteArray=prior.binary
	var actual: PackedByteArray=current.binary
	assert(actual.slice(0,original.size())==original,"Original binary payload must remain verbatim")
	assert(now.nodes.size()==old.nodes.size() and now.meshes.size()==old.meshes.size())
	assert(now.accessors.slice(0,old.accessors.size())==old.accessors and now.bufferViews.slice(0,old.bufferViews.size())==old.bufferViews)
	var mapping: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(sports_sign_proof.patch_map)))
	assert(mapping.nodes.size()==4 and int(mapping.binary_append_offset)==original.size())
	var repaired: Dictionary=now.duplicate(true)
	var indices: Array=[]
	var mesh_indices: Array=[]
	var named: Array=[]
	for spec in mapping.nodes:
		var index:=int(spec.node_index)
		var mi:=int(spec.mesh_index)
		assert(not index in indices and not mi in mesh_indices)
		indices.append(index);mesh_indices.append(mi);named.append(str(spec.runtime_name))
		assert(old.nodes[index]==spec.old_node and now.nodes[index]==spec.new_node)
		assert(old.meshes[mi]==spec.old_mesh and now.meshes[mi]==spec.new_mesh)
		repaired.nodes[index]=old.nodes[index]
		repaired.meshes[mi]=old.meshes[mi]
		for primitive in now.meshes[mi].primitives:
			assert(primitive.attributes.has("TEXCOORD_0") and int(primitive.indices)>=old.accessors.size())
			assert(int(primitive.material)>=0 and int(primitive.material)<old.materials.size())
			for key in primitive.attributes: assert(int(primitive.attributes[key])>=old.accessors.size())
	assert(named==sports_sign_proof.allowed_nodes)
	for index in range(old.nodes.size()):
		if index not in indices: assert(int(old.nodes[index].get("mesh",-1)) not in mesh_indices,"A changed shared mesh may not affect another node")
	repaired.accessors=repaired.accessors.slice(0,old.accessors.size())
	repaired.bufferViews=repaired.bufferViews.slice(0,old.bufferViews.size())
	repaired.buffers=old.buffers
	assert(repaired==old,"Exact original reconstruction outside four named nodes/meshes required")
	for index in range(old.bufferViews.size(),now.bufferViews.size()):
		var view: Dictionary=now.bufferViews[index]
		assert(int(view.buffer)==0 and int(view.get("byteOffset",0))>=original.size())
		assert(int(view.get("byteOffset",0))+int(view.byteLength)<=actual.size())
	for index in range(old.accessors.size(),now.accessors.size()): assert(int(now.accessors[index].bufferView)>=old.bufferViews.size())

static func _sports_sign_expected_triangles(filename: String,mesh_count: int) -> int:
	_sports_sign_ensure()
	if filename==str(sports_sign_proof.new_model_file):
		assert(mesh_count==1734)
		return int(sports_sign_proof.new_source_triangle_count)
	if filename==str(sports_sign_proof.old_model_file):
		assert(mesh_count==1734)
		return 66346
	assert(filename==str(sports_sign_proof.guard_model_file) and mesh_count==20)
	return 448

static func _sports_sign_material_equal(a: Material,b: Material) -> void:
	assert(a!=null and b!=null and a.get_class()==b.get_class())
	var pair:=str(a.get_instance_id())+":"+str(b.get_instance_id())
	if sports_sign_material_pairs.has(pair): return
	assert(a.get_property_list()==b.get_property_list())
	for spec in a.get_property_list():
		var name_key:=str(spec.name)
		# Imported resource locations/scene serialization IDs differ between new/old GLB containers.
		# All material state and actual texture pixels remain strict.
		if (int(spec.usage) & PROPERTY_USAGE_STORAGE)==0 or name_key in ["resource_path","resource_scene_unique_id"]: continue
		var x=a.get(name_key)
		var y=b.get(name_key)
		if x is Texture2D:
			assert(y is Texture2D and x.get_class()==y.get_class())
			var xi: Image=x.get_image()
			var yi: Image=y.get_image()
			assert(xi.get_size()==yi.get_size() and xi.get_format()==yi.get_format() and xi.has_mipmaps()==yi.has_mipmaps() and xi.get_data()==yi.get_data(),"Unaffected material texture pixels changed")
		else: assert(x==y,"Unaffected imported material property changed: "+name_key)
	sports_sign_material_pairs[pair]=true

static func _sports_sign_validate_unaffected(wrapper: Node3D) -> void:
	_sports_sign_ensure()
	var original: Node3D=(load("res://assets/models/"+str(sports_sign_proof.old_model_file)) as PackedScene).instantiate() as Node3D
	var current: Node3D=(load("res://assets/models/"+str(sports_sign_proof.new_model_file)) as PackedScene).instantiate() as Node3D
	var actual: Node3D=wrapper.get_node(NodePath(str(current.name))) as Node3D
	var originals: Dictionary={}
	var actuals: Dictionary={}
	for node in original.find_children("*","Node3D",true,false):
		assert(not originals.has(str(node.name)));originals[str(node.name)]=node
	for node in current.find_children("*","Node3D",true,false):
		assert(not actuals.has(str(node.name)))
		actuals[str(node.name)]=actual.get_node(current.get_path_to(node))
	assert(originals.size()==1908 and actuals.size()==1908)
	var unchanged_nodes:=0
	var unchanged_meshes:=0
	for identity in originals:
		var old: Node3D=originals[identity]
		var live: Node3D=actuals[identity]
		if identity in sports_sign_proof.allowed_nodes: continue
		unchanged_nodes+=1
		assert(live.get_class()==old.get_class() and live.get_script()==old.get_script() and live.transform==old.transform)
		assert(live.get_meta_list()==old.get_meta_list())
		for key in old.get_meta_list(): assert(live.get_meta(key)==old.get_meta(key))
		assert(live.get_child_count()==old.get_child_count()+(1 if live is MeshInstance3D else 0))
		if live is MeshInstance3D:
			unchanged_meshes+=1
			assert(live.visible and live.material_override==null and live.mesh.get_surface_count()==old.mesh.get_surface_count())
			for surface in range(old.mesh.get_surface_count()):
				assert(live.mesh.surface_get_arrays(surface)==old.mesh.surface_get_arrays(surface),"Any unrelated geometry/UV/normal/index change is forbidden")
				assert(live.get_surface_override_material(surface)==null)
				_sports_sign_material_equal(live.get_active_material(surface),old.get_active_material(surface))
			var contact: CollisionShape3D=live.get_node("StaticContact/SharedShape") as CollisionShape3D
			var original_contact: ConcavePolygonShape3D=old.mesh.create_trimesh_shape()
			assert(contact!=null and contact.shape is ConcavePolygonShape3D and not contact.disabled and contact.shape.get_faces()==original_contact.get_faces(),"All unaffected actual contacts remain exact")
	assert(unchanged_nodes==1904 and unchanged_meshes==1730)
	original.free();current.free()
# SPORTS_SIGN_EXACT_SECTION_END
# STAR_FITTED_EXACT_SECTION_BEGIN
const STAR_FITTED_PROOF := "res://data/architecture/packages/star_atlas_fitted/RUNTIME_PROOF.json"
const STAR_FITTED_PROOF_SHA := "31d5677bee1282c257da564860a3169c50b33d43d4a6834bd82fe8f254930bf0"
static var star_fitted_checked := false
static var star_fitted_proof: Dictionary = {}
static var star_fitted_predecessor_text: Dictionary = {}

static func _star_fitted_ensure() -> void:
	if star_fitted_checked: return
	assert(FileAccess.get_sha256(STAR_FITTED_PROOF)==STAR_FITTED_PROOF_SHA)
	star_fitted_proof=JSON.parse_string(FileAccess.get_file_as_string(STAR_FITTED_PROOF))
	assert(star_fitted_proof.schema==1 and star_fitted_proof.old_floor_owner_count==282)
	assert(star_fitted_proof.allowed_new_subtree=="StarAtlasFittedInteriors_Candidate")
	for path in star_fitted_proof.current_sha256: assert(_upper_hull_current_sha256("res://"+str(path))==str(star_fitted_proof.current_sha256[path]),"Changed fitted successor input: "+str(path))
	for path in star_fitted_proof.predecessors:
		var spec: Dictionary=star_fitted_proof.predecessors[path]
		assert(FileAccess.get_sha256("res://"+str(spec.retained_path))==str(spec.sha256))
		star_fitted_predecessor_text[path]=FileAccess.get_file_as_string("res://"+str(spec.retained_path))
	var ship_source:=_upper_hull_current_text("res://scripts/ship.gd")
	var hook: Dictionary=star_fitted_proof.ship_inverse
	assert(ship_source.count(str(hook.after))==1)
	assert(ship_source.replace(str(hook.after),str(hook.before))==str(star_fitted_predecessor_text["scripts/ship.gd"]),"Only the one immediate post-Star-Atlas ship hook is allowed")
	var source:=_upper_hull_current_text("res://tests/medical_triage_successor_guard.gd")
	var first: String="# STAR_FITTED_EXACT_SECTION_"+"BEGIN\n"
	var last: String="# STAR_FITTED_EXACT_SECTION_"+"END\n"
	assert(source.count(first)==1 and source.count(last)==1)
	var start:=source.find(first)
	var finish:=source.find(last)+last.length()
	var block:=source.substr(start,finish-start)
	assert(block.count(STAR_FITTED_PROOF_SHA)==1)
	assert(block.replace(STAR_FITTED_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(star_fitted_proof.block_normalized_sha256))
	var recovered:=source.substr(0,start)+source.substr(finish)
	for edit in star_fitted_proof.guard_inverse_edits:
		assert(recovered.count(str(edit.after))==int(edit.count))
		recovered=recovered.replace(str(edit.after),str(edit.before))
	assert(recovered==str(star_fitted_predecessor_text["tests/medical_triage_successor_guard.gd"]),"Complete previous nested guard bytes must survive")
	var floors: Dictionary=JSON.parse_string(_night_current_text("res://data/generated/structural_meshes.json"))
	assert(floors.regions.size()==282)
	star_fitted_checked=true

static func _star_fitted_current_text(path: String) -> String:
	_star_fitted_ensure()
	var relative:=_relative(path)
	if star_fitted_predecessor_text.has(relative): return str(star_fitted_predecessor_text[relative])
	return _night_current_text("res://"+relative)

static func _star_fitted_current_sha256(path: String) -> String:
	_star_fitted_ensure()
	var relative:=_relative(path)
	if star_fitted_predecessor_text.has(relative): return str(star_fitted_predecessor_text[relative]).sha256_text()
	return _night_current_sha256("res://"+relative)

static func _star_fitted_validate_runtime(ship: Node) -> void:
	_star_fitted_ensure()
	var district: Node3D=ship.get_node("ShipSpace/Districts/D12_D14_StarAtlas_WIP") as Node3D
	var fitted: Node3D=district.get_node("StarAtlasFittedInteriors_Candidate") as Node3D
	assert(district.get_meta("programme_keys")==["D12_directory_05","D13_directory_04","D14_directory_03"] and district.get_meta("historical_library_id")=="D12_stargazing4")
	var witness: Dictionary=load("res://scripts/star_atlas_fitted_receiving.gd").validate(district)
	assert(witness.passed and witness.old_state_before_sha256==witness.old_state_after_sha256 and witness.preserved_old_nodes>0)
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/star_atlas_fitted_interiors.json"))
	assert(data.models.size()==105 and data.clusters.size()==24 and data.fixtures.size()==15 and data.labels.size()==5 and data.stock_profiles.size()==14)
	assert(data.capacity_change==0 and data.new_floor_owners.is_empty())
	assert(fitted.transform==Transform3D.IDENTITY and fitted.get_meta("authoring_owner")=="D12_D14_star_atlas" and fitted.get_meta("capacity_change")==0)
	var ids: Dictionary={}
	for item in data.models:
		assert(not ids.has(str(item.id)));ids[str(item.id)]=true
		var object: Node3D=fitted.get_node(NodePath(str(item.id))) as Node3D
		assert(object.get_meta("catalogue_file")==item.file and object.get_meta("fitted_role")==item.role)
		var expected:=Node3D.new()
		expected.position=Vector3(float(item.position[0]),float(item.position[1]),float(item.position[2]));expected.rotation.y=float(item.yaw)
		assert(object.transform==expected.transform);expected.free()
		if item.has("support"): assert(object.get_meta("support_id")==item.support)
		var settings:=ConfigFile.new()
		var filename: String="res://assets/models/"+str(item.file)
		assert(settings.load(filename+".import")==OK)
		var remap:=str(settings.get_value("remap","path",""))
		var md5:=ConfigFile.new()
		assert(not remap.is_empty() and md5.load(remap.get_basename()+".md5")==OK and str(md5.get_value("","source_md5",""))==FileAccess.get_md5(filename),"Existing retained-model import must be fresh")
	var budgets: Array=ship.find_children("LocalShadowSourceBudget","Node",true,false)
	assert(budgets.size()==1 and budgets[0].shadow_source_budget==8 and budgets[0].MAX_VISIBILITY_CANDIDATES==32)
	var budget: Node=budgets[0]
	assert(fitted.find_children("*","Light3D",true,false).size()==15)
	var switch_count:=0
	for source in data.fixtures:
		var lamp: SpotLight3D=fitted.get_node(NodePath(str(source.id)+"_OpticalSource")) as SpotLight3D
		assert(lamp!=null and lamp in budget.sources and bool(budget.requested_shadow[lamp.get_instance_id()]))
		assert(lamp.light_color==(Color(.82,.90,1.0) if str(source.id)=="D12_ReturnCare_Fixture" else Color(1,.94,.86)))
		if source.type=="task":
			assert(lamp.spot_range==2 and lamp.spot_angle==75 and is_equal_approx(lamp.light_energy,.35))
			var control: Node3D=fitted.get_node(NodePath(str(source.id)+"_Switch")) as Node3D
			assert(control.get_script()==load("res://scripts/fixture_switch.gd") and control.persistent_id==StringName("star_atlas_fitted_"+str(source.id)) and control.source==lamp)
			switch_count+=1
		else: assert(source.type=="floor" and lamp.spot_range==3 and lamp.spot_angle==65 and is_equal_approx(lamp.light_energy,.65))
	assert(switch_count==10 and fitted.find_children("IntegratedCollectionLabel","Label3D",true,false).size()==5)
	for spec in data.labels:
		var label: Label3D=fitted.get_node(NodePath(str(spec.parent)+"/IntegratedCollectionLabel")) as Label3D
		assert(label!=null and label.text==spec.text and label.font_size==32 and is_equal_approx(label.pixel_size,float(spec.pixel_size)) and not label.no_depth_test and label.outline_size==0)
		assert(label.position==Vector3(float(spec.position[0]),float(spec.position[1]),float(spec.position[2])) and is_equal_approx(label.rotation.x,float(spec.rotation_x)))
	var stock_groups:=0
	for batch in fitted.find_children("FittedCollectionStock_*","MultiMeshInstance3D",false,false): stock_groups+=batch.multimesh.instance_count
	assert(stock_groups==294)
	var active:=0
	for light in budget.sources:
		if light.visible and light.shadow_enabled: active+=1
	assert(active<=8,"New lights must obey the sole unchanged global budget")
# STAR_FITTED_EXACT_SECTION_END
# UPPER_HULL_EXACT_SECTION_BEGIN
const UPPER_HULL_PROOF="res://data/architecture/packages/upper_hull_skin/RUNTIME_PROOF.json"
const UPPER_HULL_PROOF_SHA="382c8325138ee5f73e5866dfec0bacec85167edf898b7251ac5c00885d6b3918"
static var upper_hull_checked:=false
static var upper_hull_old:Dictionary={}
static func _upper_hull_ensure()->void:
	if upper_hull_checked:return
	assert(FileAccess.get_sha256(UPPER_HULL_PROOF)==UPPER_HULL_PROOF_SHA)
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(UPPER_HULL_PROOF))
	for path in p.predecessors:
		var spec:Dictionary=p.predecessors[path]
		assert(FileAccess.get_sha256("res://"+str(spec.retained_path))==str(spec.sha256))
		upper_hull_old[path]=FileAccess.get_file_as_string("res://"+str(spec.retained_path))
	for path in p.current_sha256:assert(_night_current_sha256("res://"+str(path))==str(p.current_sha256[path]))
	for path in p.inverse_edits:
		var current:=_night_current_text("res://"+str(path))
		if str(path)=="tests/medical_triage_successor_guard.gd":
			var a: String="# UPPER_HULL_EXACT_SECTION_"+"BEGIN\n"
			var z: String="# UPPER_HULL_EXACT_SECTION_"+"END\n"
			assert(current.count(a)==1 and current.count(z)==1)
			var i:=current.find(a);var j:=current.find(z)+z.length()
			assert(current.substr(i,j-i).replace(UPPER_HULL_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(p.block_normalized_sha256))
			current=current.substr(0,i)+current.substr(j)
		for edit in p.inverse_edits[path]:
			if edit.has("section_only"):
				var i:=current.find("# STAR_FITTED_EXACT_SECTION_"+"BEGIN")
				var tail:=current.substr(i);assert(tail.count(str(edit.after))==1)
				current=current.substr(0,i)+tail.replace(str(edit.after),str(edit.before))
			else:
				assert(current.count(str(edit.after))==int(edit.count));current=current.replace(str(edit.after),str(edit.before))
		assert(current==str(upper_hull_old[path]),"Complete predecessor bytes must survive")
	upper_hull_checked=true
static func _upper_hull_current_text(path:String)->String:
	_upper_hull_ensure()
	var key:=path.trim_prefix("res://")
	return str(upper_hull_old[key]) if upper_hull_old.has(key) else _night_current_text(path)
static func _upper_hull_current_sha256(path:String)->String:
	_upper_hull_ensure()
	var key:=path.trim_prefix("res://")
	return str(upper_hull_old[key]).sha256_text() if upper_hull_old.has(key) else _night_current_sha256(path)
static func _upper_hull_validate_runtime(ship:Node)->void:
	_upper_hull_ensure()
	var root:Node3D=ship.get_node("ShipSpace/Districts/TheaterWestUpperHull_Skin_WIP")
	assert(root.transform==Transform3D.IDENTITY and root.get_meta("persistent_id")=="theater_west_upper_hull_skin_002")
	var original:Node3D=(load("res://assets/models/AST-HUL-002.glb")as PackedScene).instantiate()
	assert(root.get_child_count()==1)
	var visual:Node3D=root.get_child(0)
	assert(visual.name==original.name and visual.transform==original.transform)
	var count:=0
	for mesh in original.find_children("*","MeshInstance3D",true,false):
		var actual:MeshInstance3D=visual.get_node(original.get_path_to(mesh))
		assert(actual.transform==mesh.transform and actual.mesh==mesh.mesh and actual.material_override==null)
		var collision:CollisionShape3D=actual.get_node("StaticContact/SharedShape")
		assert(collision.shape.get_faces()==mesh.mesh.create_trimesh_shape().get_faces())
		count+=1
	assert(count==74)
	original.free()
# UPPER_HULL_EXACT_SECTION_END
# NIGHT_TABLE_EXACT_SECTION_BEGIN
const NIGHT_PROOF="res://data/architecture/packages/night_table/RUNTIME_PROOF.json"
const NIGHT_PROOF_SHA="b6a034fc705342adaec8448ca6493f943764a1737efd62e51393b06c32eeef67"
static var night_checked:=false
static var night_old:Dictionary={}
static var night_current_compiled:Dictionary={}
static var night_proof:Dictionary={}
static func _night_ensure()->void:
	if night_checked:return
	assert(FileAccess.get_sha256(NIGHT_PROOF)==NIGHT_PROOF_SHA)
	night_proof=JSON.parse_string(FileAccess.get_file_as_string(NIGHT_PROOF))
	for path in night_proof.predecessors:
		var spec:Dictionary=night_proof.predecessors[path]
		var file:String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(file)==str(spec.sha256))
		night_old[path]=FileAccess.get_file_as_string(file)
	for path in night_proof.current_sha256:
		assert(_laundry_current_sha256("res://"+str(path))==str(night_proof.current_sha256[path]))
	for path in night_proof.inverse_edits:
		var current:=_laundry_current_text("res://"+str(path))
		if str(path)=="tests/medical_triage_successor_guard.gd":
			var a:String="# NIGHT_TABLE_EXACT_SECTION_"+"BEGIN\n"
			var z:String="# NIGHT_TABLE_EXACT_SECTION_"+"END\n"
			assert(current.count(a)==1 and current.count(z)==1)
			var i:=current.find(a);var j:=current.find(z)+z.length()
			assert(current.substr(i,j-i).replace(NIGHT_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(night_proof.block_normalized_sha256))
			current=current.substr(0,i)+current.substr(j)
		for edit in night_proof.inverse_edits[path]:
			assert(current.count(str(edit.after))==int(edit.count))
			current=current.replace(str(edit.after),str(edit.before))
		assert(current==str(night_old[path]),"Night Table must preserve every predecessor byte")
	var layout:Dictionary=JSON.parse_string(_laundry_current_text("res://data/spatial_layout.json"))
	var old_layout:Dictionary=JSON.parse_string(str(night_old["data/spatial_layout.json"]))
	night_current_compiled=JSON.parse_string(_laundry_current_text("res://data/generated/structural_meshes.json"))
	var old_compiled_n:Dictionary=JSON.parse_string(str(night_old["data/generated/structural_meshes.json"]))
	for pair in [[layout,old_layout,night_proof.added_layout],[night_current_compiled,old_compiled_n,night_proof.added_compiled]]:
		var wanted:Array=pair[1].regions.duplicate(true);wanted.append_array(pair[2])
		assert(pair[0].regions==wanted)
		var ids:Dictionary={}
		for row in pair[0].regions:assert(not ids.has(row.id));ids[row.id]=true
	var a:Dictionary=layout.duplicate(true);var b:Dictionary=old_layout.duplicate(true)
	a.erase("regions");b.erase("regions");assert(a==b)
	a=night_current_compiled.duplicate(true);b=old_compiled_n.duplicate(true)
	for key in ["regions","source_checks"]:a.erase(key);b.erase(key)
	assert(a==b)
	assert(night_current_compiled.source_checks==JSON.parse_string(_laundry_current_text("res://docs/LAYOUT_COMPILE_CHECKS.json")))
	assert(night_current_compiled.regions.size()==284 and old_compiled_n.regions.size()==282)
	night_checked=true
static func _night_current_text(path:String)->String:
	_night_ensure()
	var key:=path.trim_prefix("res://")
	return str(night_old[key]) if night_old.has(key) else _laundry_current_text(path)
static func _night_current_sha256(path:String)->String:
	_night_ensure()
	return _night_current_text(path).sha256_text() if night_old.has(path.trim_prefix("res://")) else _laundry_current_sha256(path)
static func _night_floor_children(floors:Node)->Array:
	_night_ensure()
	assert(floors!=null)
	var children:=_laundry_floor_children(floors);assert(children.size()==284);var retained:Array=[]
	for i in range(children.size()):
		var row:Dictionary=night_current_compiled.regions[i]
		assert(str(children[i].name)==str(row.id))
		_botanical_validate_slab(children[i],row)
		if i<282:retained.append(children[i])
	return retained
static func _night_validate_runtime(ship:Node)->void:
	_night_ensure()
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_table/runtime_manifest.json"))
	var root:Node3D=ship.get_node("ShipSpace/"+str(data.root_name))
	assert(root.transform==Transform3D.IDENTITY and root.get_child_count()==1)
	assert(root.get_meta("source_dining_places")==240 and root.get_meta("operational_acceptance")==false)
	var wrapper:Node3D=root.get_node("NightTableSource")
	assert(wrapper.position==Vector3(-31,61,216) and wrapper.basis==Basis.IDENTITY)
	var original:Node3D=(load("res://assets/models/"+str(data.model_file))as PackedScene).instantiate()
	assert(wrapper.get_child_count()==1)
	var visual:Node3D=wrapper.get_child(0);assert(visual.transform==original.transform)
	var count:=0
	for mesh in original.find_children("*","MeshInstance3D",true,false):
		var actual:MeshInstance3D=visual.get_node(original.get_path_to(mesh))
		assert(actual.transform==mesh.transform and actual.mesh==mesh.mesh and actual.material_override==null)
		var collision:CollisionShape3D=actual.get_node("StaticContact/SharedShape")
		assert(collision.shape.get_faces()==mesh.mesh.create_trimesh_shape().get_faces())
		count+=1
	assert(count>0)
	for spec in data.lights:
		var light:Light3D=visual.find_child(str(spec.runtime_name),true,false)
		assert(light!=null and is_equal_approx(light.light_energy,float(spec.energy)))
		assert(light.light_color.is_equal_approx(Color(spec.color[0],spec.color[1],spec.color[2])))
		assert(light.get_meta("source_light_name")==str(spec.source_name))
	original.free()
# NIGHT_TABLE_EXACT_SECTION_END
# LAUNDRY_EXACT_SECTION_BEGIN
const LAUNDRY_PROOF="res://data/architecture/packages/laundry/RUNTIME_PROOF.json"
const LAUNDRY_PROOF_SHA="e3ed362925a429ad2080b0fc7c42722b8992d8a6d3a0fa110d8edf2b03c8e2a0"
static var laundry_checked:=false
static var laundry_old:Dictionary={}
static var laundry_current_compiled:Dictionary={}
static var laundry_proof:Dictionary={}
static func _laundry_ensure()->void:
	if laundry_checked:return
	assert(FileAccess.get_sha256(LAUNDRY_PROOF)==LAUNDRY_PROOF_SHA)
	laundry_proof=JSON.parse_string(FileAccess.get_file_as_string(LAUNDRY_PROOF))
	for path in laundry_proof.predecessors:
		var spec:Dictionary=laundry_proof.predecessors[path]
		var file:String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(file)==str(spec.sha256))
		laundry_old[path]=FileAccess.get_file_as_string(file)
	for path in laundry_proof.current_sha256:
		assert(_crew_current_sha256("res://"+str(path))==str(laundry_proof.current_sha256[path]))
	for path in laundry_proof.inverse_edits:
		var current:=_crew_current_text("res://"+str(path))
		if str(path)=="tests/medical_triage_successor_guard.gd":
			var a:String="# LAUNDRY_EXACT_SECTION_"+"BEGIN\n"
			var z:String="# LAUNDRY_EXACT_SECTION_"+"END\n"
			assert(current.count(a)==1 and current.count(z)==1)
			var i:=current.find(a);var j:=current.find(z)+z.length()
			assert(current.substr(i,j-i).replace(LAUNDRY_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(laundry_proof.block_normalized_sha256))
			current=current.substr(0,i)+current.substr(j)
		for edit in laundry_proof.inverse_edits[path]:
			assert(current.count(str(edit.after))==int(edit.count))
			current=current.replace(str(edit.after),str(edit.before))
		assert(current==str(laundry_old[path]),"Laundry must preserve every predecessor byte")
	var layout:Dictionary=JSON.parse_string(_crew_current_text("res://data/spatial_layout.json"))
	var old_layout:Dictionary=JSON.parse_string(str(laundry_old["data/spatial_layout.json"]))
	laundry_current_compiled=JSON.parse_string(_crew_current_text("res://data/generated/structural_meshes.json"))
	var old_compiled_n:Dictionary=JSON.parse_string(str(laundry_old["data/generated/structural_meshes.json"]))
	for pair in [[layout,old_layout,laundry_proof.added_layout],[laundry_current_compiled,old_compiled_n,laundry_proof.added_compiled]]:
		var wanted:Array=pair[1].regions.duplicate(true);wanted.append_array(pair[2])
		assert(pair[0].regions==wanted)
		var ids:Dictionary={}
		for row in pair[0].regions:assert(not ids.has(row.id));ids[row.id]=true
	var a:Dictionary=layout.duplicate(true);var b:Dictionary=old_layout.duplicate(true)
	a.erase("regions");b.erase("regions");assert(a==b)
	a=laundry_current_compiled.duplicate(true);b=old_compiled_n.duplicate(true)
	for key in ["regions","source_checks"]:a.erase(key);b.erase(key)
	assert(a==b)
	assert(laundry_current_compiled.source_checks==JSON.parse_string(_crew_current_text("res://docs/LAYOUT_COMPILE_CHECKS.json")))
	assert(laundry_current_compiled.regions.size()==286 and old_compiled_n.regions.size()==284)
	laundry_checked=true
static func _laundry_current_text(path:String)->String:
	_laundry_ensure()
	var key:=path.trim_prefix("res://")
	return str(laundry_old[key]) if laundry_old.has(key) else _crew_current_text(path)
static func _laundry_current_sha256(path:String)->String:
	_laundry_ensure()
	return _laundry_current_text(path).sha256_text() if laundry_old.has(path.trim_prefix("res://")) else _crew_current_sha256(path)
static func _laundry_floor_children(floors:Node)->Array:
	_laundry_ensure()
	assert(floors!=null and load("res://tests/d12_pair_successor_guard.gd").floor_children(floors).size()==296)
	var children:=_crew_floor_children(floors);var retained:Array=[]
	for i in range(children.size()):
		var row:Dictionary=laundry_current_compiled.regions[i]
		assert(str(children[i].name)==str(row.id))
		_botanical_validate_slab(children[i],row)
		if i<284:retained.append(children[i])
	return retained
static func _laundry_validate_runtime(ship:Node)->void:
	_laundry_ensure()
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/laundry/runtime_manifest.json"))
	var root:Node3D=ship.get_node("ShipSpace/"+str(data.root_name))
	assert(root.transform==Transform3D.IDENTITY and root.get_child_count()==1)
	assert(root.get_meta("operational_acceptance")==false)
	var wrapper:Node3D=root.get_node("LaundrySource")
	assert(wrapper.position==Vector3.ZERO and wrapper.basis==Basis.IDENTITY)
	var original:Node3D=(load("res://assets/models/"+str(data.model_file))as PackedScene).instantiate()
	assert(wrapper.get_child_count()==1)
	var visual:Node3D=wrapper.get_child(0);assert(visual.transform==original.transform)
	var count:=0
	for mesh in original.find_children("*","MeshInstance3D",true,false):
		var actual:MeshInstance3D=visual.get_node(original.get_path_to(mesh))
		assert(actual.transform==mesh.transform and actual.mesh==mesh.mesh and actual.material_override==null)
		var collision:CollisionShape3D=actual.get_node("StaticContact/SharedShape")
		assert(collision.shape.get_faces()==mesh.mesh.create_trimesh_shape().get_faces())
		count+=1
	assert(count>0)
	for spec in data.lights:
		var light:Light3D=visual.find_child(str(spec.runtime_name),true,false)
		assert(light!=null and is_equal_approx(light.light_energy,float(spec.energy)))
		assert(light.light_color.is_equal_approx(Color(spec.color[0],spec.color[1],spec.color[2])))
		assert(light.get_meta("source_light_name")==str(spec.source_name))
	original.free()
# LAUNDRY_EXACT_SECTION_END
# CREW_EXACT_SECTION_BEGIN
const CREW_PROOF="res://data/architecture/packages/crew_batch/RUNTIME_PROOF.json"
const CREW_PROOF_SHA="d86c341e89135752ec2b3ad12fc7eedf03b8f50ea53c080da1c323ec0d318395"
static var crew_checked:=false
static var crew_old:Dictionary={}
static var crew_current_compiled:Dictionary={}
static var crew_proof:Dictionary={}
static func _crew_ensure()->void:
	if crew_checked:return
	assert(load("res://tests/d12_pair_successor_guard.gd").current_sha256(CREW_PROOF)==CREW_PROOF_SHA)
	crew_proof=JSON.parse_string(load("res://tests/d12_pair_successor_guard.gd").current_text(CREW_PROOF))
	for path in crew_proof.predecessors:
		var spec:Dictionary=crew_proof.predecessors[path]
		var file:String="res://"+str(spec.retained_path)
		assert(load("res://tests/d12_pair_successor_guard.gd").current_sha256(file)==str(spec.sha256))
		crew_old[path]=load("res://tests/d12_pair_successor_guard.gd").current_text(file)
	for path in crew_proof.current_sha256:
		assert(load("res://tests/d12_pair_successor_guard.gd").current_sha256("res://"+str(path))==str(crew_proof.current_sha256[path]))
	for path in crew_proof.inverse_edits:
		var current:String=load("res://tests/d12_pair_successor_guard.gd").current_text("res://"+str(path))
		if str(path)=="tests/medical_triage_successor_guard.gd":
			var a:String="# CREW_EXACT_SECTION_"+"BEGIN\n"
			var z:String="# CREW_EXACT_SECTION_"+"END\n"
			assert(current.count(a)==1 and current.count(z)==1)
			var i:=current.find(a);var j:=current.find(z)+z.length()
			assert(current.substr(i,j-i).replace(CREW_PROOF_SHA,"<PROOF_SHA>").sha256_text()==str(crew_proof.block_normalized_sha256))
			current=current.substr(0,i)+current.substr(j)
		for edit in crew_proof.inverse_edits[path]:
			assert(current.count(str(edit.after))==int(edit.count))
			current=current.replace(str(edit.after),str(edit.before))
		assert(current==str(crew_old[path]),"Laundry must preserve every predecessor byte")
	var layout:Dictionary=JSON.parse_string(load("res://tests/d12_pair_successor_guard.gd").current_text("res://data/spatial_layout.json"))
	var old_layout:Dictionary=JSON.parse_string(str(crew_old["data/spatial_layout.json"]))
	crew_current_compiled=JSON.parse_string(load("res://tests/d12_pair_successor_guard.gd").current_text("res://data/generated/structural_meshes.json"))
	var old_compiled_n:Dictionary=JSON.parse_string(str(crew_old["data/generated/structural_meshes.json"]))
	for pair in [[layout,old_layout,crew_proof.added_layout],[crew_current_compiled,old_compiled_n,crew_proof.added_compiled]]:
		var wanted:Array=pair[1].regions.duplicate(true);wanted.append_array(pair[2])
		assert(pair[0].regions==wanted)
		var ids:Dictionary={}
		for row in pair[0].regions:assert(not ids.has(row.id));ids[row.id]=true
	var a:Dictionary=layout.duplicate(true);var b:Dictionary=old_layout.duplicate(true)
	a.erase("regions");b.erase("regions");assert(a==b)
	a=crew_current_compiled.duplicate(true);b=old_compiled_n.duplicate(true)
	for key in ["regions","source_checks"]:a.erase(key);b.erase(key)
	assert(a==b)
	assert(crew_current_compiled.source_checks==JSON.parse_string(load("res://tests/d12_pair_successor_guard.gd").current_text("res://docs/LAYOUT_COMPILE_CHECKS.json")))
	assert(crew_current_compiled.regions.size()==296 and old_compiled_n.regions.size()==286)
	crew_checked=true
static func _crew_current_text(path:String)->String:
	_crew_ensure()
	var key:=path.trim_prefix("res://")
	return str(crew_old[key]) if crew_old.has(key) else load("res://tests/d12_pair_successor_guard.gd").current_text(path)
static func _crew_current_sha256(path:String)->String:
	_crew_ensure()
	return _crew_current_text(path).sha256_text() if crew_old.has(path.trim_prefix("res://")) else load("res://tests/d12_pair_successor_guard.gd").current_sha256(path)
static func _crew_floor_children(floors:Node)->Array:
	_crew_ensure()
	assert(floors!=null)
	var children:Array=load("res://tests/d12_pair_successor_guard.gd").floor_children(floors);assert(children.size()==296)
	var retained:Array=[]
	for i in range(children.size()):
		var row:Dictionary=crew_current_compiled.regions[i]
		assert(str(children[i].name)==str(row.id))
		_botanical_validate_slab(children[i],row)
		if i<286:retained.append(children[i])
	return retained
static func _crew_validate_model(wrapper:Node3D,file:String,expected_meshes:int)->void:
	var original:Node3D=(load("res://assets/models/"+file)as PackedScene).instantiate()
	assert(wrapper.get_child_count()==1)
	var visual:Node3D=wrapper.get_child(0);assert(visual.transform==original.transform)
	var count:=0
	for mesh in original.find_children("*","MeshInstance3D",true,false):
		var actual:MeshInstance3D=visual.get_node(original.get_path_to(mesh))
		assert(actual.transform==mesh.transform and actual.mesh==mesh.mesh and actual.material_override==null)
		var collision:CollisionShape3D=actual.get_node("StaticContact/SharedShape")
		assert(collision.shape.get_faces()==mesh.mesh.create_trimesh_shape().get_faces());count+=1
	assert(count==expected_meshes);original.free()
static func _crew_validate_runtime(ship:Node)->void:
	_crew_ensure()
	var data:Dictionary=JSON.parse_string(load("res://tests/d12_pair_successor_guard.gd").current_text("res://data/architecture/crew_batch/runtime_manifest.json"))
	var root:Node3D=ship.get_node("ShipSpace/"+str(data.root_name))
	assert(root.transform==Transform3D.IDENTITY and root.get_child_count()==5 and root.get_meta("operational_acceptance")==false)
	var counts:Dictionary={"D03_directory_05":555,"D03_directory_06":576,"D03_directory_07":403,"D03_directory_08":346,"D03_directory_10":817}
	for section in data.sections:
		var room:Node3D=root.get_node(str(section.root_name));assert(room.transform==Transform3D.IDENTITY and room.get_meta("programme_key")==str(section.programme))
		var wrapper:Node3D=room.get_node("Source");assert(wrapper.transform==Transform3D.IDENTITY)
		_crew_validate_model(wrapper,str(section.model_file),int(counts[section.programme]))
		assert(room.get_child_count()==1+section.mounted_receiving_lights.size())
		var index:=0
		for spec in section.mounted_receiving_lights:
			var light:OmniLight3D=room.get_node("MountedSourceFixture_%02d"%index);index+=1
			assert(light.position.is_equal_approx(Vector3(spec.position[0],spec.position[1],spec.position[2])))
			assert(is_equal_approx(light.light_energy,float(spec.energy))and is_equal_approx(light.omni_range,float(spec.range_m)))
			assert(light.light_color.is_equal_approx(Color(spec.color[0],spec.color[1],spec.color[2])))
			assert(light.get_meta("source_fixture")==str(spec.fixture_source_name))
			var fixture:MeshInstance3D=wrapper.find_child(str(spec.fixture_runtime_name),true,false)as MeshInstance3D;assert(fixture!=null)
			var center:Vector3=ship.get_node("ShipSpace").to_local(fixture.to_global(fixture.mesh.get_aabb().get_center()))
			assert(center.is_equal_approx(Vector3(spec.fixture_center[0],spec.fixture_center[1],spec.fixture_center[2])))
	var aft:Node3D=ship.get_node("ShipSpace/Districts/AftPublicCore_WIP/PrimaryCoreEnclosure")
	_crew_validate_model(aft,"AST-CIR-005_aft_uniforms_d03.glb",9)
# CREW_EXACT_SECTION_END
