extends "res://tests/medical_test_scene.gd"

func _initialize() -> void:
	test_name="medical_structure";call_deferred("run")

func mesh_map(parent: Node) -> Dictionary:
	var found: Dictionary={}
	for value in parent.find_children("*","MeshInstance3D",true,false):
		var node: MeshInstance3D=value as MeshInstance3D
		if not require(not found.has(str(node.name)),"Duplicate native core mesh name"): return {}
		found[str(node.name)]=node
	return found

func mesh_digest(mesh: Mesh) -> String:
	var values: Array=[]
	for index in range(mesh.get_surface_count()): values.append(mesh.surface_get_arrays(index))
	return var_to_bytes(values).hex_encode().sha256_text()

func triangle_multiset(faces: PackedVector3Array, pose: Transform3D=Transform3D.IDENTITY) -> Dictionary:
	var result: Dictionary={}
	if not require(faces.size()%3==0,"Complete triangle triples required"): return {}
	for i in range(0,faces.size(),3):
		var vertices: Array[String]=[]
		for j in range(3):
			var point: Vector3=pose*faces[i+j]
			vertices.append("%.5f,%.5f,%.5f"%[point.x,point.y,point.z])
		vertices.sort()
		var key: String="|".join(PackedStringArray(vertices))
		result[key]=int(result.get(key,0))+1
	return result

func record_top_faces(triangles: Array, y: float) -> PackedVector3Array:
	var result: PackedVector3Array=[]
	for triangle in triangles:
		for point in triangle: result.append(Vector3(float(point[0]),y,float(point[1])))
	return result

func verify_actual_slab(record: Dictionary) -> bool:
	var owner: Node3D=floors.get_node(str(record.id)) as Node3D
	var y: float=float(record.floor_y);var depth: float=float(record.thickness)
	var top: PackedVector3Array=record_top_faces(record.triangles,y)
	var edges: PackedVector3Array=[]
	for point in top: edges.append(point-Vector3.UP*depth)
	for ring in record.rings:
		for i in range(ring.size()):
			var p: Array=ring[i];var q: Array=ring[(i+1)%ring.size()]
			var a: Vector3=Vector3(float(p[0]),y,float(p[1]));var b: Vector3=Vector3(float(q[0]),y,float(q[1]))
			var bottom_a: Vector3=a-Vector3.UP*depth;var bottom_b: Vector3=b-Vector3.UP*depth
			for vertex in [a,b,bottom_b,a,bottom_b,bottom_a]: edges.append(vertex)
	var complete: PackedVector3Array=top.duplicate();complete.append_array(edges)
	var contacts: Array=owner.find_children("*","CollisionShape3D",true,false)
	if not require(contacts.size()==1,"One exact compiled medical collision shape required"): return false
	var contact: CollisionShape3D=contacts[0] as CollisionShape3D
	if not require(contact.shape is ConcavePolygonShape3D,"Medical floor must keep its faithful concave slab contact"): return false
	var actual: PackedVector3Array=(contact.shape as ConcavePolygonShape3D).get_faces()
	if not require(triangle_multiset(actual,contact.global_transform)==triangle_multiset(complete),"Actual medical collision triangles differ from the complete compiled slab"): return false
	var visuals: Array=owner.find_children("*","MeshInstance3D",true,false)
	if not require(visuals.size()==record.render_chunks.size()+1,"Exact bounded render chunks and edge mesh required"): return false
	for chunk in record.render_chunks:
		var visual: MeshInstance3D=owner.get_node(str(chunk.id)) as MeshInstance3D
		if not require(triangle_multiset(visual.mesh.get_faces(),visual.global_transform)==triangle_multiset(record_top_faces(chunk.triangles,y)),"Actual render chunk differs from compiled triangles: "+str(chunk.id)): return false
	var side: MeshInstance3D=owner.get_node("StructuralSidesAndUnderside") as MeshInstance3D
	if not require(triangle_multiset(side.mesh.get_faces(),side.global_transform)==triangle_multiset(edges),"Actual underside/closure geometry differs from compiled slab"): return false
	metrics["exact_actual_contact_triangles"]=actual.size()/3
	metrics["exact_actual_render_chunks"]=record.render_chunks.size()
	return true

func exercise() -> bool:
	var proof: Dictionary=load("res://tests/medical_successor_guard.gd").validate_current(floors)
	var record: Dictionary=proof.new_compiled_record
	if not require(absf(float(record.structural_area_m2)-350.72)<.000001 and float(record.floor_y)==21.0 and float(record.thickness)==.24,"Medical compiler area/datum changed"): return false
	if not verify_actual_slab(record): return false
	var core: Node3D=ship.find_child(str(data.core_root_name),true,false) as Node3D
	var installed: Node3D=core.get_node("PrimaryCoreEnclosure") as Node3D
	if not require(str(installed.get_meta("catalogue_file"))==str(data.core_file),"Wrong actual loaded core derivative"): return false
	var old: Node3D=(load("res://assets/models/AST-CIR-005_forward_pool_market_engineering_access.glb") as PackedScene).instantiate() as Node3D
	var prior: Dictionary=mesh_map(old);var current: Dictionary=mesh_map(installed)
	var removed: Array[String]=["CORE_OuterWall_04_-1","CORE_WallDado_04_-1"]
	var unchanged: int=0
	for name in prior:
		if str(name) in removed or str(name) in [removed[0].validate_node_name(),removed[1].validate_node_name()]: continue
		if not require(current.has(name),"Retained core mesh missing: "+str(name)): return false
		var a: MeshInstance3D=prior[name] as MeshInstance3D;var b: MeshInstance3D=current[name] as MeshInstance3D
		if not require(mesh_digest(a.mesh)==mesh_digest(b.mesh),"Imported retained core mesh changed: "+str(name)): return false
		if not require(a.transform.is_equal_approx(b.transform),"Retained core mesh transform changed: "+str(name)): return false
		unchanged+=1
	old.free()
	metrics["unchanged_imported_core_meshes"]=unchanged
	var positive: int=0;var clear: int=0
	for y in [21.05,21.4,22.2,23.35]:
		for z in [-433.75,-432.0,-430.25]:
			if not require(ray(Vector3(-8.12,y,z),Vector3(-7.55,y,z),exclusions()).is_empty(),"Actual core aperture still blocked"): return false
			clear+=1
	for p in [Vector3(-7.9,22,-434),Vector3(-7.9,22,-430),Vector3(-7.9,24,-432)]:
		var hit: Dictionary=ray(p+Vector3.RIGHT*.4,p-Vector3.RIGHT*.4,exclusions())
		if not require(not hit.is_empty() and core.is_ancestor_of(hit.collider),"Real shoulder/lintel closure missing"): return false
		positive+=1
	for z in [-433.6,-432.0,-430.4]:
		for index in range(41):
			var x: float=-8.3+float(index)*.02
			var owner: String="" if absf(x+7.8)<.00001 else (str(data.floor_owner) if x< -7.8 else "D05_forward_public_core_floor")
			if not support_at(Vector3(x,21,z),owner): return false
	metrics["actual_clear_aperture_rays"]=clear;metrics["actual_closure_rays"]=positive
	if not require(not bool(built.get_meta("first_pass_quality_accepted")) and not bool(built.get_meta("clinical_operation_accepted")),"Construction scope must remain truthful"): return false
	var budget: Node=ship.find_child("LocalShadowSourceBudget",true,false)
	if not require(budget!=null and int(budget.get("shadow_source_budget"))==8,"Shared eight-source cap changed"): return false
	var lights: Array=built.find_children("MedicalSource_*","SpotLight3D",true,false)
	if not require(lights.size()==data.fixtures.size(),"Actual housed medical source count mismatch"): return false
	for value in data.fixtures:
		var item: Dictionary=value
		var light: SpotLight3D=built.find_child(("MedicalSource_"+str(item.name)).validate_node_name(),true,false) as SpotLight3D
		if not require(light!=null and light.global_position.distance_to(xyz(item.position_xyz))<.001,"Fixture exit transform mismatch"): return false
		if not require(budget.get("sources").has(light),"Existing light budget must own the medical source"): return false
		var direction: Vector3=(xyz(item.aim_xyz)-light.global_position).normalized()
		if not require(ray(light.global_position,light.global_position+direction*.04,exclusions()).is_empty(),"Modeled medical light exit is blocked"): return false
	metrics["housed_sources"]=lights.size()
	return true
