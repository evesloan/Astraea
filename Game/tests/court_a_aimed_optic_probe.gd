extends RefCounted
# Independent assertions only. Never call an optic builder or repair scene geometry.
const CONTRACT := "res://data/architecture/COURT_A_AIMED_OPTIC008.json"
const CONTRACT_SHA := "50a904a7a492dd2ed6e0d97480ce42b7caf8d5ed166f42d6f89df83e8ee7f404"
const BUILDER_SHA := "d4fd5a9250302081e664ba86400f34d33a57d5a4b66fd0457afef537517bfa34"
const SOURCE_SHA := "c252539361fa2454e919b85cb5e357eb75a329b8724f2c311101a936206996b8"
const GLB_SHA := "9e62faa88311b58c644c77b2008c0728b25ab6c370c8cdb5f9159692e2940bca"
const OLD_ASSET := "res://assets/models/AST-CUL-005_static_003.glb"
const OLD_ASSET_SHA := "fa056d66c1064cb6ee917f0fcae7d6ffccbd9426118a95c8a09f1e8b23457947"
const BATCH := "C005_S_0326"
const FIXTURE := "FP2_D11_BANK_0"
const ORIGIN := Vector3(-69.5,73.75,-138.3)
const AIM := Vector3(0.0,-0.6427876096865393,-0.766044443118978)
const LOW := Vector3(-70.9000015258789,73.75499725341797,-138.57000732421875)
const HIGH := Vector3(-68.0999984741211,73.76699829101562,-138.02999877929688)

static func xyz(values: Array) -> Vector3:
	return Vector3(float(values[0]),float(values[1]),float(values[2]))

static func authenticated_contract() -> Dictionary:
	assert(FileAccess.get_sha256(CONTRACT)==CONTRACT_SHA,"Unknown optic source contract")
	assert(FileAccess.get_sha256("res://scripts/court_a_aimed_optic008.gd")==BUILDER_SHA,"Unknown optic builder")
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.schema=="astraea.court_a.aimed_optic008" and data.source.sha256==SOURCE_SHA and data.asset.sha256==GLB_SHA)
	assert(data.mesh_count==7 and data.triangles==116 and data.contacts==7 and data.lights_added==0)
	assert(data.replacement.batch==BATCH and data.replacement.original_triangles==112 and data.replacement.removed_triangles==28 and data.replacement.retained_triangles==84)
	assert(xyz(data.replacement.bounds_min_native)==LOW and xyz(data.replacement.bounds_max_native)==HIGH and float(data.replacement.selection_epsilon_m)==.00006)
	assert(data.fixture.id==FIXTURE and xyz(data.origin_native)==ORIGIN and xyz(data.fixture.aim_native)==AIM)
	for path in data.retained_originals.runtime_sha256:
		assert(FileAccess.get_sha256("res://"+str(path))==str(data.retained_originals.runtime_sha256[path]),"Old optic dependency changed: "+str(path))
	return data

static func fresh_asset(data: Dictionary) -> Node3D:
	var path := "res://assets/models/"+str(data.asset.filename)
	assert(FileAccess.get_sha256(path)==GLB_SHA)
	var policy := ConfigFile.new()
	assert(policy.load(path+".import")==OK)
	# Importer-generated UID/remap names may change; exact policy and source freshness may not.
	assert(policy.get_value("params","meshes/force_disable_compression",false))
	assert(not policy.get_value("params","meshes/generate_lods",true))
	assert(not policy.get_value("params","meshes/create_shadow_meshes",true))
	assert(int(policy.get_value("params","gltf/embedded_image_handling",-1))==3)
	var cache := str(policy.get_value("remap","path",""))
	assert(not cache.is_empty() and FileAccess.file_exists(cache))
	var digest := ConfigFile.new()
	assert(digest.load(cache.get_basename()+".md5")==OK)
	assert(digest.get_value("","source_md5","")==FileAccess.get_md5(path),"Fresh optic import required")
	return (load(path) as PackedScene).instantiate() as Node3D

static func relative(node: Node3D, ancestor: Node3D) -> Transform3D:
	var result := node.transform
	var cursor := node.get_parent()
	while cursor!=ancestor:
		assert(cursor!=null and cursor is Node3D)
		result=(cursor as Node3D).transform*result
		cursor=cursor.get_parent()
	return result

static func same_transform(actual: Transform3D, expected: Transform3D) -> void:
	assert(actual.origin.distance_to(expected.origin)<.000001)
	for axis in range(3): assert(actual.basis[axis].distance_to(expected.basis[axis])<.000001)

static func raw_faces(mesh: Mesh) -> PackedVector3Array:
	var faces := PackedVector3Array()
	for surface in range(mesh.get_surface_count()):
		assert(mesh is ArrayMesh and (mesh as ArrayMesh).surface_get_primitive_type(surface)==Mesh.PRIMITIVE_TRIANGLES)
		var arrays: Array=mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
		var indices: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
		if indices.is_empty(): faces.append_array(vertices)
		else:
			for index in indices: faces.append(vertices[index])
	assert(faces.size()>0 and faces.size()%3==0)
	return faces

static func contact(mesh: MeshInstance3D, expected: PackedVector3Array) -> void:
	assert(mesh.find_children("*","StaticBody3D",true,false).size()==1)
	assert(mesh.find_children("*","CollisionShape3D",true,false).size()==1)
	var body := mesh.get_node("SourceStaticContact") as StaticBody3D
	assert(body.collision_layer==1 and body.collision_mask==1)
	same_transform(body.transform,Transform3D.IDENTITY)
	var shape := body.get_node("ExactSourceTriangles") as CollisionShape3D
	assert(not shape.disabled and shape.shape is ConcavePolygonShape3D)
	same_transform(shape.transform,Transform3D.IDENTITY)
	assert(absf(shape.shape.margin-.001)<.000001)
	assert(shape.shape.get_faces().to_byte_array()==expected.to_byte_array(),"Exact retained/source contact order and coordinates required")

static func inside_old_lens(point: Vector3) -> bool:
	for axis in range(3):
		if point[axis]<LOW[axis]-.00006 or point[axis]>HIGH[axis]+.00006: return false
	return true

static func check_replacement(actual: MeshInstance3D, original: MeshInstance3D) -> void:
	assert(str(actual.name)==BATCH and str(original.name)==BATCH)
	assert(actual.mesh is ArrayMesh and actual.mesh!=original.mesh)
	assert(actual.mesh.get_surface_count()==1 and original.mesh.get_surface_count()==1)
	assert((actual.mesh as ArrayMesh).surface_get_primitive_type(0)==Mesh.PRIMITIVE_TRIANGLES)
	assert((actual.mesh as ArrayMesh).surface_get_name(0)==(original.mesh as ArrayMesh).surface_get_name(0))
	assert(actual.mesh.get_blend_shape_count()==0 and original.mesh.get_blend_shape_count()==0)
	assert(actual.mesh.surface_get_material(0)==original.mesh.surface_get_material(0))
	assert(actual.material_override==original.material_override and actual.material_overlay==original.material_overlay)
	assert(actual.get_surface_override_material(0)==original.get_surface_override_material(0))
	assert(actual.visible==original.visible and actual.cast_shadow==original.cast_shadow and actual.layers==original.layers)
	var before: Array=original.mesh.surface_get_arrays(0)
	var after: Array=actual.mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array=before[Mesh.ARRAY_VERTEX]
	var indices: PackedInt32Array=before[Mesh.ARRAY_INDEX]
	assert(indices.size()==112*3 and original.mesh.get_faces().size()==112*3,"Original static import must remain 112 triangles")
	var kept := PackedInt32Array()
	var removed := 0
	for triangle in range(112):
		var selected := true
		for corner in range(3): selected=selected and inside_old_lens(actual.global_transform*vertices[indices[triangle*3+corner]])
		if selected: removed+=1
		else:
			for corner in range(3): kept.append(indices[triangle*3+corner])
	assert(removed==28 and kept.size()==84*3)
	assert(after[Mesh.ARRAY_INDEX].to_byte_array()==kept.to_byte_array(),"Only the named old lens indices may be removed")
	for slot in range(Mesh.ARRAY_MAX):
		if slot==Mesh.ARRAY_INDEX: continue
		assert(typeof(after[slot])==typeof(before[slot]))
		if before[slot]!=null: assert(after[slot].to_byte_array()==before[slot].to_byte_array(),"Old vertex/UV/normal/tangent/other attribute changed")
	assert(raw_faces(actual.mesh).size()==84*3)
	# The historical builder used create_trimesh_shape(): independently filter its
	# original get_faces order, never substitute the derivative's render order.
	var old_faces: PackedVector3Array=original.mesh.get_faces()
	var kept_faces := PackedVector3Array()
	var removed_contacts := 0
	for triangle in range(112):
		var selected := true
		for corner in range(3): selected=selected and inside_old_lens(actual.global_transform*old_faces[triangle*3+corner])
		if selected: removed_contacts+=1
		else:
			for corner in range(3): kept_faces.append(old_faces[triangle*3+corner])
	assert(removed_contacts==28 and kept_faces.size()==84*3)
	contact(actual,kept_faces)
	assert(actual.has_meta("court_a_optic_replacement"))

static func expected_aim(light: Light3D, previous: Dictionary) -> Vector3:
	if str(light.name)!=FIXTURE: return xyz(previous.aim_world).normalized()
	var data := authenticated_contract()
	assert(str(previous.id)==FIXTURE and previous.type=="SPOT" and light is SpotLight3D)
	assert(xyz(previous.aim_world).distance_to(xyz(data.fixture.before_aim_native))<.000001)
	assert(str(previous.physical_fixture)==str(data.fixture.original_semantic))
	assert(light.global_position.distance_to(ORIGIN)<.0001)
	assert(absf(light.spot_range-7.9)<.00001 and absf(light.light_energy-.8)<.00001 and absf(light.spot_angle-37.5)<.00001)
	assert(light.get_meta("source_fixture_semantic_id")=="CA8_aimed_opal_lens" and light.get_meta("source_blend_sha256")==SOURCE_SHA)
	assert(light.get_meta("court_a_optic_contract")==CONTRACT)
	return AIM.normalized()

static func check_installation(ship: Node3D) -> void:
	var data := authenticated_contract()
	var parent := ship.get_node("ShipSpace/Districts") as Node3D
	var installed := parent.get_node(str(data.root_name)) as Node3D
	assert(installed.get_parent()==parent and installed.visible)
	same_transform(installed.global_transform,Transform3D(Basis.IDENTITY,ORIGIN))
	assert(installed.get_meta("source_sha256")==SOURCE_SHA and installed.get_meta("glb_sha256")==GLB_SHA)
	assert(installed.get_meta("source_contract")==CONTRACT and installed.get_meta("source_contract_sha256")==CONTRACT_SHA)
	assert(installed.get_meta("authored_meshes")==7 and installed.get_meta("authored_triangles")==116 and installed.get_meta("authored_contacts")==7 and installed.get_meta("lights_added")==0)
	assert(installed.get_meta("fixture_id")==FIXTURE)
	assert(installed.find_children("*","MeshInstance3D",true,false).size()==7)
	assert(installed.find_children("*","CollisionObject3D",true,false).size()==7)
	assert(installed.find_children("*","CollisionShape3D",true,false).size()==7)
	assert(installed.find_children("*","Light3D",true,false).is_empty())
	var template := fresh_asset(data)
	assert(template!=null and template.find_children("*","MeshInstance3D",true,false).size()==7)
	assert(template.find_children("*","Light3D",true,false).is_empty())
	var seen: Dictionary={}
	var triangles := 0
	for part in data.parts:
		assert(not seen.has(str(part.node)))
		seen[str(part.node)]=true
		var original := template.find_child(str(part.node),true,false) as MeshInstance3D
		var actual := installed.find_child(str(part.node),true,false) as MeshInstance3D
		assert(original!=null and actual!=null and original.mesh==actual.mesh and actual.visible)
		same_transform(relative(actual,installed),relative(original,template))
		same_transform(relative(actual,installed),Transform3D.IDENTITY)
		assert(actual.material_override==original.material_override and actual.material_overlay==original.material_overlay and actual.cast_shadow==original.cast_shadow and actual.layers==original.layers)
		assert(actual.mesh.get_surface_count()==1 and actual.get_surface_override_material(0)==original.get_surface_override_material(0))
		assert(str(actual.mesh.surface_get_material(0).resource_name)==str(part.material))
		assert(actual.get_meta("source_semantic_id")==str(part.semantic) and actual.get_meta("source_blend_sha256")==SOURCE_SHA)
		var faces := raw_faces(original.mesh)
		assert(faces.size()==int(part.triangles)*3)
		triangles+=int(faces.size()/3)
		var low := Vector3(INF,INF,INF)
		var high := Vector3(-INF,-INF,-INF)
		for vertex in faces:
			var world := actual.global_transform*vertex
			low=low.min(world);high=high.max(world)
		assert(low.distance_to(xyz(part.bounds_native[0]))<.00006 and high.distance_to(xyz(part.bounds_native[1]))<.00006)
		contact(actual,faces)
	assert(seen.size()==7 and triangles==116)
	var marker := installed.find_child(str(data.marker.node),true,false) as Node3D
	assert(marker!=null and marker.global_position.distance_to(ORIGIN)<.000001)
	assert(marker.has_meta("extras") and marker.get_meta("extras") is Dictionary)
	var marker_extras: Dictionary=marker.get_meta("extras")
	assert(marker_extras.has("source_id") and marker_extras.has("optical_axis_native"))
	assert(str(marker_extras.source_id)==FIXTURE and xyz(marker_extras.optical_axis_native).distance_to(AIM)<.000001)
	template.free()
	assert(FileAccess.get_sha256(OLD_ASSET)==OLD_ASSET_SHA)
	var old_template := (load(OLD_ASSET) as PackedScene).instantiate() as Node3D
	var old_original := old_template.find_child(BATCH,true,false) as MeshInstance3D
	var venue := parent.get_node("GrandLanternTheater_ConnectedStaticStage_WIP") as Node3D
	var old_actual := venue.get_node("TheaterSourceArchitecture").find_child(BATCH,true,false) as MeshInstance3D
	assert(old_actual!=null and old_original!=null)
	same_transform(old_actual.global_transform,relative(old_original,old_template))
	check_replacement(old_actual,old_original)
	old_template.free()
	var lights := venue.find_children("*","Light3D",true,false)
	assert(lights.size()==139,"Optic may not add or remove theater lights")
	var previous: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/THEATER_RUNTIME_STAGE001.json"))
	var changed := 0
	var mapped_names: Dictionary={}
	for record in previous.fixtures:
		if not record.enabled: continue
		var native_name: String=str(record.id).validate_node_name()
		assert(not mapped_names.has(native_name),"Source fixtures require a unique canonical native name")
		mapped_names[native_name]=true
		var light := venue.get_node_or_null(NodePath(native_name)) as Light3D
		assert(light!=null)
		if str(record.id)==FIXTURE:
			assert((-light.global_basis.z).distance_to(expected_aim(light,record))<.00001)
			changed+=1
	assert(changed==1 and mapped_names.size()==139 and mapped_names.size()==lights.size())
	for light in lights: assert(mapped_names.has(str(light.name)))
	var budget := ship.get_node("ShipSystems/LocalShadowSourceBudget")
	assert(budget.shadow_source_budget==8 and load("res://scripts/lighting_budget.gd").MAX_VISIBILITY_CANDIDATES==32)
