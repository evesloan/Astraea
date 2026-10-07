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
	return checked and (value==current_compiled or value==botanical_current_compiled)
static func retained_compiled(value: Dictionary) -> Dictionary:
	_ensure()
	if not checked: return {}
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
	assert(FileAccess.get_sha256(BOTANICAL_PROOF)==BOTANICAL_PROOF_SHA,"Exact closed botanical proof required")
	botanical_proof=JSON.parse_string(FileAccess.get_file_as_string(BOTANICAL_PROOF))
	assert(botanical_proof.schema==1 and botanical_proof.added_owner_ids.size()==2)
	for path in botanical_proof.current_sha256:
		assert(FileAccess.get_sha256("res://"+str(path))==str(botanical_proof.current_sha256[path]),"Unreviewed botanical input: "+str(path))
	for path in botanical_proof.predecessors:
		var spec: Dictionary=botanical_proof.predecessors[path]
		var retained_path: String="res://"+str(spec.retained_path)
		assert(FileAccess.get_sha256(retained_path)==str(spec.sha256),"Botanical predecessor changed: "+str(path))
		botanical_predecessor_text[path]=FileAccess.get_file_as_string(retained_path)
	var own_source := FileAccess.get_file_as_string("res://tests/medical_triage_successor_guard.gd")
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
		var restored := FileAccess.get_file_as_string("res://"+str(path))
		for edit in botanical_proof.exact_inverse_edits[path]:
			assert(restored.count(str(edit.after))==int(edit.count),"Exact botanical source inverse cardinality")
			restored=restored.replace(str(edit.after),str(edit.before))
		assert(restored==str(botanical_predecessor_text[path]),"Every preceding compiler/ship byte must survive")
	var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/spatial_layout.json"))
	var prior_layout: Dictionary=JSON.parse_string(str(botanical_predecessor_text["data/spatial_layout.json"]))
	botanical_current_compiled=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
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
	var summary: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/LAYOUT_COMPILE_CHECKS.json"))
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
		assert(mesh.visible and mesh.material_override==null and mesh.mesh!=null)
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
		assert(contacts.size()==1 and not contacts[0].disabled and contacts[0].shape is ConcavePolygonShape3D)
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
	assert(floors!=null and floors.get_child_count()==botanical_current_compiled.regions.size(),"Complete 275-owner current floor roster required")
	var expected: Dictionary={}
	for record in botanical_current_compiled.regions: expected[str(record.id)]=record
	var retained: Array=[]
	var seen: Dictionary={}
	for value in floors.get_children():
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
