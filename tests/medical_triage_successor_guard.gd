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
	_ensure()
	return checked and (value==current_compiled or value==botanical_current_compiled or value==team_lounge_current_compiled or value==movement_current_compiled or value==moss_current_compiled)
static func retained_compiled(value: Dictionary) -> Dictionary:
	_ensure()
	if not checked: return {}
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
	if relative in team_lounge_proof.projected_paths: return str(team_lounge_predecessor_text[relative])
	return FileAccess.get_file_as_string("res://"+relative)

static func _team_lounge_current_sha256(path: String) -> String:
	_team_lounge_ensure()
	var relative:=_relative(path)
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
	assert(FileAccess.get_sha256(MOSS_PROOF)==MOSS_PROOF_SHA,"Exact whole Team Lounge successor proof required")
	moss_proof=JSON.parse_string(FileAccess.get_file_as_string(MOSS_PROOF))
	assert(moss_proof.schema==1 and moss_proof.programme_key=="D06_directory_03")
	assert(moss_proof.added_owner_ids==["D06_moss_sanctuary_receiving_floor"])
	for path in moss_proof.current_sha256:
		assert(FileAccess.get_sha256("res://"+str(path))==str(moss_proof.current_sha256[path]),"Unreviewed lounge postimage: "+str(path))
	for path in moss_proof.predecessors:
		var spec: Dictionary=moss_proof.predecessors[path]
		var retained: String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained)==str(spec.sha256),"Lounge predecessor changed: "+str(path))
		moss_predecessor_text[path]=FileAccess.get_file_as_string(retained)
	var own_source := FileAccess.get_file_as_string("res://tests/medical_triage_successor_guard.gd")
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
		var restored:=FileAccess.get_file_as_string("res://"+str(path))
		for edit in moss_proof.exact_inverse_edits[path]:
			assert(restored.count(str(edit.after))==int(edit.count),"Exact lounge source inverse cardinality")
			restored=restored.replace(str(edit.after),str(edit.before))
		assert(restored==str(moss_predecessor_text[path]),"Every preceding compiler/ship byte must survive: "+str(path))
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	var prior_layout: Dictionary=JSON.parse_string(str(moss_predecessor_text["data/spatial_layout.json"]))
	moss_current_compiled=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
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
	var summary: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/LAYOUT_COMPILE_CHECKS.json"))
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
	assert(floors!=null and floors.get_child_count()==280,"Complete actual 280-owner roster required before predecessor projection")
	var expected: Dictionary={}
	for record in moss_current_compiled.regions: expected[str(record.id)]=record
	var seen: Dictionary={}
	var retained: Array=[]
	var children: Array=floors.get_children()
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
	assert(opened==14 and closed==122)
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
