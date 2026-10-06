extends RefCounted
# Source-backed static venue stage. Door/lift operation is deliberately absent.
const CONTRACT := "res://data/architecture/THEATER_RUNTIME_STAGE001.json"
static func vector(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))
static func transform(a: Array) -> Transform3D:
	return Transform3D(Basis(Vector3(a[0][0],a[1][0],a[2][0]),Vector3(a[0][1],a[1][1],a[2][1]),Vector3(a[0][2],a[1][2],a[2][2])),Vector3(a[0][3],a[1][3],a[2][3]))
static func attach_contact(mesh: MeshInstance3D) -> void:
	var shape := mesh.mesh.create_trimesh_shape()
	shape.margin = .001
	var body := StaticBody3D.new()
	body.name = "SourceStaticContact"
	var collider := CollisionShape3D.new()
	collider.name = "ExactSourceTriangles"
	collider.shape = shape
	body.add_child(collider)
	mesh.add_child(body)
static func visual(parent: Node3D, file: String, name: String) -> Node3D:
	var root := (load("res://assets/models/"+file) as PackedScene).instantiate() as Node3D
	root.name = name
	root.set_meta("catalogue_file",file)
	parent.add_child(root)
	return root
static func build(parent: Node3D, _ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.chair_instances == 2200 and data.prototype_instances == 2494)
	var root := Node3D.new()
	root.name = "GrandLanternTheater_ConnectedStaticStage_WIP"
	root.set_meta("persistent_id","grand_lantern_theater_001")
	root.set_meta("programme_keys",["D11_directory_01","D12_directory_11","D13_directory_01"])
	root.set_meta("stage_status","Source-backed venue, D11 receiving portico, held-open main entrance; other external interfaces closed; door/lift operation unfinished")
	parent.add_child(root)
	var glass := ShaderMaterial.new()
	glass.shader = load("res://shaders/hospitality_glass.gdshader")
	var shell := visual(root,str(data.static_file),"TheaterSourceArchitecture")
	var bridge := visual(root,str(data.bridge_file),"TheaterReceivingPortico")
	var static_count := 0
	for collection in [shell,bridge]:
		for node in collection.find_children("*","MeshInstance3D",true,false):
			var mesh := node as MeshInstance3D
			if str(mesh.name) in data.glass_batch_nodes: mesh.material_override = glass
			attach_contact(mesh)
			static_count += 1
	assert(static_count == data.static_batch_nodes.size()+83)
	_build_instances(root,data,glass)
	_build_locked_motion(root,data,glass)
	_build_lights(root,data)
	root.set_meta("static_mesh_batches",static_count)
static func mesh_transform(mesh: Node3D, definition: Node3D) -> Transform3D:
	var result := mesh.transform
	var cursor := mesh.get_parent()
	while cursor != definition:
		assert(cursor != null and cursor is Node3D)
		result = (cursor as Node3D).transform * result
		cursor = cursor.get_parent()
	return result
static func _build_instances(root: Node3D, data: Dictionary, glass: Material) -> void:
	var assembly := Node3D.new()
	assembly.name = "RetainedAuthoredInstances"
	assembly.set_meta("catalogue_file",str(data.prototype_file))
	assembly.set_meta("source_instance_count",2494)
	root.add_child(assembly)
	var template := (load("res://assets/models/"+str(data.prototype_file)) as PackedScene).instantiate() as Node3D
	var definitions: Dictionary = {}
	var shapes: Dictionary = {}
	for identity in data.prototypes:
		var spec: Dictionary = data.prototypes[identity]
		var definition := template.find_child(str(spec.root_node),true,false) as Node3D
		assert(definition != null)
		var meshes: Array = []
		var faces := PackedVector3Array()
		for name in spec.batches:
			var mesh := definition.find_child(str(name),true,false) as MeshInstance3D
			assert(mesh != null)
			var local := mesh_transform(mesh,definition)
			meshes.append({"mesh":mesh.mesh,"transform":local,"name":str(name),"glass":str(name) in data.glass_batch_nodes})
			if spec.collides:
				for point in mesh.mesh.get_faces(): faces.append(local * point)
		definitions[identity] = meshes
		if spec.collides:
			var shape := ConcavePolygonShape3D.new()
			shape.set_faces(faces)
			shape.margin = .001
			shapes[identity] = shape
	var groups: Dictionary = {}
	var chairs := 0
	var instance_index := 0
	for record in data.instances:
		var placement := transform(record.native_matrix)
		var key := str(record.definition)+"|%d|%d|%d" % [floori(placement.origin.x/16.0),floori(placement.origin.y/6.0),floori(placement.origin.z/16.0)]
		if not groups.has(key): groups[key] = []
		groups[key].append({"id":record.id,"definition":record.definition,"transform":placement})
		if record.audience_chair: chairs += 1
		if shapes.has(record.definition):
			var body := StaticBody3D.new()
			body.name = "RetainedContact_%04d" % instance_index
			body.transform = placement
			body.set_meta("source_instance_id",str(record.id))
			body.set_meta("source_definition",str(record.definition))
			var collider := CollisionShape3D.new()
			collider.shape = shapes[record.definition]
			body.add_child(collider)
			assembly.add_child(body)
		instance_index += 1
	var batch_index := 0
	for key in groups:
		var entries: Array = groups[key]
		for part in definitions[entries[0].definition]:
			var mm := MultiMesh.new()
			mm.transform_format = MultiMesh.TRANSFORM_3D
			mm.mesh = part.mesh
			mm.instance_count = entries.size()
			var identities: Array = []
			for i in range(entries.size()):
				mm.set_instance_transform(i,entries[i].transform * part.transform)
				identities.append(str(entries[i].id))
			var view := MultiMeshInstance3D.new()
			view.name = "RetainedVisual_%04d" % batch_index
			view.multimesh = mm
			view.set_meta("source_instance_ids",identities)
			view.set_meta("source_prototype_batch",part.name)
			view.set_meta("source_prototype_file",str(data.prototype_file))
			if part.glass: view.material_override = glass
			assembly.add_child(view)
			batch_index += 1
	assert(chairs == 2200 and instance_index == 2494)
	root.set_meta("source_chair_instances",chairs)
	root.set_meta("source_prototype_instances",instance_index)
	root.set_meta("source_spatial_multimesh_batches",batch_index)
	template.free()
static func _build_locked_motion(root: Node3D, data: Dictionary, glass: Material) -> void:
	var moving := visual(root,str(data.moving_file),"TheaterUnpoweredDoorLiftAssemblies")
	for identity in data.motion_groups:
		var spec: Dictionary = data.motion_groups[identity]
		var node := moving.find_child(str(data.motion_node_names[identity]),true,false) as Node3D
		assert(node != null)
		node.set_meta("source_motion_group",str(identity))
		node.set_meta("operation_enabled",false)
		if identity in data.held_open_groups:
			assert(spec.kind == "paired_sliding_leaf")
			node.position += vector(spec.axis_world) * float(spec.travel_m)
			node.set_meta("locked_pose_fraction",1.0)
		else:
			node.set_meta("locked_pose_fraction",0.0)
		for part in node.find_children("*","MeshInstance3D",true,false):
			var mesh := part as MeshInstance3D
			if str(mesh.name) in data.glass_batch_nodes: mesh.material_override = glass
			if identity not in data.visual_only_motion_groups:
				attach_contact(mesh)
		# The visual cabin and its own gates have no static floor/collider here.
		# Closed landing leaves are separate physical barriers around the shaft.
	moving.set_meta("cabin_static_floor_credit",false)
	moving.set_meta("held_open_main_door_requires_pose_clearance_gate",true)
static func _build_lights(root: Node3D, data: Dictionary) -> void:
	for record in data.fixtures:
		if not record.enabled: continue
		var light: Light3D
		if record.type == "SPOT":
			var spot := SpotLight3D.new()
			spot.spot_range = float(record.range_m)
			spot.spot_angle = float(record.full_cone_degrees)*.5
			light = spot
		else:
			var omni := OmniLight3D.new()
			omni.omni_range = float(record.range_m)
			light = omni
		light.name = str(record.id)
		root.add_child(light)
		light.position = vector(record.position_world)
		if record.type == "SPOT":
			var direction := vector(record.aim_world).normalized()
			light.basis = Basis.looking_at(direction,Vector3.FORWARD if absf(direction.y)>.98 else Vector3.UP)
		light.light_color = Color(record.color[0],record.color[1],record.color[2])
		light.light_energy = float(record.initial_native_energy)
		light.shadow_enabled = true
		light.set_meta("fixture_powered",true)
		light.set_meta("source_fixture_semantic_id",str(record.physical_fixture))
		light.set_meta("source_blend_sha256",str(data.source_bridge_sha256) if record.group == "receiving_bridge" else str(data.source_sha256))
		if record.has("illumination_anchor") and record.illumination_anchor != null:
			light.set_meta("illumination_anchor",vector(record.illumination_anchor))
		# Existing ship-wide LocalShadowSourceBudget selects at most eight.
		# No hidden fill, unshadowed fallback or local budget override is created.
