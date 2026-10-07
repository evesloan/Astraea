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
			vertices.append(var_to_bytes(point).hex_encode())
		vertices.sort()
		var key: String="|".join(PackedStringArray(vertices))
		result[key]=int(result.get(key,0))+1
	return result

func record_top_faces(triangles: Array, y: float) -> PackedVector3Array:
	var result: PackedVector3Array=[]
	for triangle in triangles:
		for point in triangle: result.append(Vector3(float(point[0]),y,float(point[1])))
	return result

func render_input_faces(mesh: Mesh) -> PackedVector3Array:
	var result: PackedVector3Array=[]
	for surface in range(mesh.get_surface_count()):
		var arrays: Array=mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var indices: Variant=arrays[Mesh.ARRAY_INDEX]
		if indices!=null and indices.size()>0:
			for index in indices: result.append(vertices[index])
		else: result.append_array(vertices)
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
	# Production creates its contact through ArrayMesh/TriangleMesh. This exact
	# native path has a float32 codec step; raw render inputs are checked separately.
	var expected_arrays: Array=[];expected_arrays.resize(Mesh.ARRAY_MAX)
	expected_arrays[Mesh.ARRAY_VERTEX]=complete
	var expected_mesh: ArrayMesh=ArrayMesh.new()
	expected_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,expected_arrays)
	var expected_contact: ConcavePolygonShape3D=expected_mesh.create_trimesh_shape()
	var native_expected: PackedVector3Array=expected_contact.get_faces()
	if not require(triangle_multiset(actual,contact.global_transform)==triangle_multiset(native_expected),"Actual medical collision triangles differ from the complete compiled slab"): return false
	var visuals: Array=owner.find_children("*","MeshInstance3D",true,false)
	if not require(visuals.size()==record.render_chunks.size()+1,"Exact bounded render chunks and edge mesh required"): return false
	for chunk in record.render_chunks:
		var visual: MeshInstance3D=owner.get_node(str(chunk.id)) as MeshInstance3D
		if not require(triangle_multiset(render_input_faces(visual.mesh),visual.global_transform)==triangle_multiset(record_top_faces(chunk.triangles,y)),"Actual render chunk differs from compiled triangles: "+str(chunk.id)): return false
	var side: MeshInstance3D=owner.get_node("StructuralSidesAndUnderside") as MeshInstance3D
	if not require(triangle_multiset(render_input_faces(side.mesh),side.global_transform)==triangle_multiset(edges),"Actual underside/closure geometry differs from compiled slab"): return false
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
	if not verify_connected_triage(): return false
	return true


func source_bounds(record: Dictionary) -> bool:
	var node: MeshInstance3D=exact_node(built,str(record.name)) as MeshInstance3D
	if not require(node!=null and node.visible and node.mesh!=null,"Source room mesh missing: "+str(record.name)): return false
	var actual: AABB=node.global_transform*node.get_aabb()
	var lower: Vector3=xyz(record.bounds_world_xyz[0]);var upper: Vector3=xyz(record.bounds_world_xyz[1])
	if not require(actual.position.distance_to(lower)<.003 and actual.end.distance_to(upper)<.003,"Actual source bounds changed: "+str(record.name)): return false
	return true

func source_static_leaf(name: String) -> bool:
	var node: MeshInstance3D=exact_node(built,name) as MeshInstance3D
	if not require(node!=null and node.get_script()==null,"Static source-open leaf required: "+name): return false
	if not require(str(node.get_meta("proposed_state",""))=="source_open_inward" and not bool(node.get_meta("operational_acceptance",true)),"Leaf operation scope changed: "+name): return false
	var contacts: Array=node.find_children("*","CollisionShape3D",true,false)
	if not require(contacts.size()==1,"Static leaf must retain one faithful contact: "+name): return false
	var contact: CollisionShape3D=contacts[0] as CollisionShape3D
	if not require(not contact.disabled and contact.get_parent() is StaticBody3D and contact.shape is ConcavePolygonShape3D,"Leaf contact replaced or disabled: "+name): return false
	var body: StaticBody3D=contact.get_parent() as StaticBody3D
	if not require((body.collision_layer & 1)!=0,"Static leaf must remain in the real world collision layer"): return false
	var expected: ConcavePolygonShape3D=node.mesh.create_trimesh_shape()
	if not require(triangle_multiset((contact.shape as ConcavePolygonShape3D).get_faces(),contact.global_transform)==triangle_multiset(expected.get_faces(),node.global_transform),"Static leaf contact differs from its exact native triangles: "+name): return false
	return true

func architecture_hit(a: Vector3,b: Vector3,label: String) -> bool:
	var hit: Dictionary=ray(a,b,exclusions())
	return require(not hit.is_empty() and built.is_ancestor_of(hit.collider),"Missing actual medical closure/receiver: "+label)

func verify_connected_triage() -> bool:
	if not require(str(data.architecture_file)==str(triage_evidence.architecture_file) and FileAccess.get_sha256("res://assets/models/"+str(data.architecture_file))==str(triage_evidence.architecture_sha256),"Source010 architecture reference/hash changed"): return false
	if not require(str(data.new_floor_owner)=="D05_connected_triage_wing_floor" and float(data.new_floor_area_m2)==544.0,"Additive triage floor identity/area changed"): return false
	if not require(str(data.floor_owner)=="D05_forward_waiting_support_floor" and float(data.floor_area_m2)==350.72,"Retained welcome floor identity/area changed"): return false
	var baseline: Dictionary=load("res://tests/medical_successor_guard.gd").validate_current(floors)
	if not require(baseline.new_compiled_record==triage_evidence.old_compiled_record,"Every old welcome slab record field must remain exact"): return false
	var added: Dictionary=triage_proof.new_compiled_record
	if not require(str(added.id)==str(data.new_floor_owner) and float(added.structural_area_m2)==544.0 and float(added.floor_y)==21.0 and float(added.thickness)==.24,"Authenticated added slab differs from source010 proposal"): return false
	var old_contact_count: Variant=metrics.exact_actual_contact_triangles
	var old_chunk_count: Variant=metrics.exact_actual_render_chunks
	if not verify_actual_slab(added): return false
	metrics["triage_exact_actual_contact_triangles"]=metrics.exact_actual_contact_triangles
	metrics["triage_exact_actual_render_chunks"]=metrics.exact_actual_render_chunks
	metrics["exact_actual_contact_triangles"]=old_contact_count
	metrics["exact_actual_render_chunks"]=old_chunk_count
	if not require(str(data.root_name)=="D05MedicalWelcome_WIP" and str(data.persistent_id)=="d05_forward_medical_welcome_001" and str(built.get_meta("persistent_id",""))==str(data.persistent_id),"Original persistent medical root identity changed"): return false
	if not require(data.children.size()==10 and data.children.slice(0,2)==triage_evidence.baseline_children,"Keep both old child identities before the exact eight added rooms"): return false
	for child in triage_evidence.baseline_children:
		if not require(data.children.has(child),"Original medical child removed"): return false
	for record in triage_evidence.baseline_instances:
		var expected: Dictionary=record
		for successor in triage_evidence.waiting_pose_successors:
			if str(successor.name)==str(record.name):
				if not require(successor.before==record,"Explicit source-pose predecessor changed"): return false
				expected=successor.after
		if not require(data.instances.has(expected),"Original component identity/record or explicitly source-pinned waiting pose changed"): return false
	for record in triage_evidence.baseline_fixtures:
		if not require(data.fixtures.has(record),"Original housed source record changed"): return false
	for key in triage_evidence.baseline_routes:
		if not require(data.physical_test_routes[key]==triage_evidence.baseline_routes[key],"Original passing route changed: "+str(key)): return false
	if not require(data.instances.size()==74 and data.fixtures.size()==34 and data.rooms.size()==8 and data.door_sources.size()==8,"Exact source010 room/assembly/source roster required"): return false
	for record in triage_evidence.admission_mesh_bounds:
		if not source_bounds(record): return false
	var clear: int=0
	for x in [-12.75,-11.0,-9.25]:
		for y in [21.05,22.2,23.95]:
			if not require(ray(Vector3(x,y,-449.60),Vector3(x,y,-450.20),exclusions()).is_empty(),"Former admission end wall still obstructs the real3.6x3.0 opening"): return false
			clear+=1
	for point in [Vector3(-13.4,22,-449.88),Vector3(-8.6,22,-449.88),Vector3(-11,24.6,-449.88)]:
		if not architecture_hit(point+Vector3.BACK*.35,point-Vector3.BACK*.35,"admission shoulders/lintel"): return false
	for x in [-12.65,-11.0,-9.35]:
		for i in range(51):
			var z: float=-449.5-float(i)*.02
			var owner: String="" if absf(z+450.0)<.00001 else (str(data.floor_owner) if z> -450.0 else str(data.new_floor_owner))
			if not support_at(Vector3(x,21,z),owner): return false
	var checked_ids: Dictionary={}
	var mesh_count: int=0
	for value in triage_evidence.rooms:
		var room: Dictionary=value;var id: String=str(room.programme_child)
		if not require(not checked_ids.has(id) and data.children.has(id) and data.rooms.has(room.source_room) and data.door_sources.has(room.door_source),"Exact source room/door identity changed: "+id): return false
		checked_ids[id]=true
		for record in room.mesh_bounds:
			if not source_bounds(record): return false
			mesh_count+=1
		for leaf in room.door_meshes:
			if not source_static_leaf(str(leaf)): return false
		var portal: Vector3=xyz(room.portal_xyz)
		for dx in [-1.74,0.0,1.74]:
			for height in [.06,1.2,2.59]:
				var p: Vector3=portal+Vector3(dx,height,0)
				if not require(ray(p+Vector3.BACK*.35,p-Vector3.BACK*.35,exclusions()).is_empty(),"Source-open room portal obstructed: "+id): return false
				clear+=1
		if not architecture_hit(portal+Vector3(0,3.0,.35),portal+Vector3(0,3.0,-.35),id+" portal header"): return false
		var inside: Vector3=xyz(room.inside_xyz)
		if not support_at(inside,str(data.new_floor_owner)): return false
		if not architecture_hit(inside+Vector3.UP*3.9,inside+Vector3.UP*4.76,id+" vault bearing"): return false
		# The upper surface must stay below the actual D06 datum; roof geometry
		# must neither replace a compiler slab nor open a false inter-deck route.
		for record in room.mesh_bounds:
			if not require(float(record.bounds_world_xyz[1][1])<=25.731,"Medical source exceeds its reviewed roof envelope"): return false
	for source in triage_evidence.new_fixture_sources:
		var matches: Array=[]
		for fixture in data.fixtures:
			if str(fixture.name)==str(source.name): matches.append(fixture)
		if not require(matches.size()==1,"New fixture identity must resolve exactly once: "+str(source.name)): return false
		var fixture: Dictionary=matches[0]
		if not require(xyz(fixture.position_xyz).distance_to(xyz(source.position_xyz))<.001 and xyz(fixture.aim_xyz).distance_to(xyz(source.aim_xyz))<.001,"New source exit/aim diverged from the fitted source: "+str(source.name)): return false
		var owner: Node=built.get_node(str(fixture.source_owner))
		var receiver: MeshInstance3D=exact_node(owner,str(fixture.source_node)) as MeshInstance3D
		if not require(receiver!=null and receiver.visible and receiver.mesh!=null,"Visible modeled fixture receiver missing"): return false
		var receiver_box: AABB=receiver.global_transform*receiver.get_aabb()
		if not require(receiver_box.grow(.35).has_point(xyz(fixture.position_xyz)),"Light floats away from its actual fixture housing"): return false
		var light: SpotLight3D=built.find_child(("MedicalSource_"+str(fixture.name)).validate_node_name(),true,false) as SpotLight3D
		if not require(light!=null and str(light.get_meta("source_node",""))==str(receiver.get_path()),"Runtime light has the wrong real receiver"): return false
	# Staff closure stays capped. Never turn a sign into an operational route.
	if not architecture_hit(Vector3(-42.3,22,-458),Vector3(-41.6,22,-458),"west unconnected staff cap"): return false
	metrics["triage_room_ids"]=checked_ids.keys();metrics["source_room_mesh_bounds"]=mesh_count
	metrics["static_source_open_privacy_leaves"]=16;metrics["triage_clear_aperture_rays"]=clear
	metrics["triage_housed_sources"]=23;metrics["door_operation_accepted"]=false
	return true
