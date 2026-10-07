extends RefCounted
# Whole WP15 receiving installation. No capacity, interaction or new light manager.
const DATA := "res://data/architecture/team_lounge/runtime_manifest.json"

static func build(ship: Node3D) -> Node3D:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	var space: Node3D = ship.get_node("ShipSpace")
	assert(not space.has_node("D07_TeamLounge_Receiving_WIP"), "Duplicate Team Lounge")
	assert(FileAccess.get_sha256(data.derivative_file) == data.derivative_sha256)
	var packed := load(data.derivative_file) as PackedScene
	assert(packed != null)
	var source := packed.instantiate() as Node3D
	# The selected derivative has inert emitter witnesses, no imported Light3D.
	# Quarantine any unexpected importer-created source before entering the tree.
	for imported in source.find_children("*", "Light3D", true, false):
		imported.visible = false
		imported.shadow_enabled = false
	assert(source.find_children("*", "Light3D", true, false).is_empty())
	source.name = "RuntimeSource"
	var root := Node3D.new()
	root.name = "D07_TeamLounge_Receiving_WIP"
	root.position = _v(data.placement)
	root.set_meta("program_key", "D07_directory_08")
	root.set_meta("source_sha256", data.source_sha256)
	root.set_meta("derivative_sha256", data.derivative_sha256)
	root.set_meta("admission_capacity_created", false)
	root.set_meta("status", "installed_receiving_source_WIP_validation_pending")
	root.add_child(source)
	var nodes: Dictionary = {}
	_index(source, nodes)
	for record in data.semantic_nodes:
		assert(nodes.has(record.runtime_name), "Missing WP15 semantic identity")
		var witness: Node = nodes[record.runtime_name]
		witness.set_meta("wp15_source_index", int(record.source_index))
		witness.set_meta("wp15_source_name", record.source_name)
		witness.set_meta("wp15_semantic_kind", record.kind)
	for record in data.collision_groups:
		var parent: Node3D = root if record.runtime_parent_name == null else nodes[record.runtime_parent_name]
		assert(not parent.has_node(NodePath(record.id)))
		assert(FileAccess.get_sha256(record.faces_file) == record.sha256)
		var bytes := FileAccess.get_file_as_bytes(record.faces_file)
		assert(bytes.size() == int(record.triangles) * 36)
		var scalars := bytes.to_float32_array()
		var faces := PackedVector3Array()
		faces.resize(scalars.size() / 3)
		for i in range(faces.size()):
			faces[i] = Vector3(scalars[i * 3], scalars[i * 3 + 1], scalars[i * 3 + 2])
		var shape := ConcavePolygonShape3D.new()
		shape.set_faces(faces)
		var contact := CollisionShape3D.new()
		contact.name = "ExactSourceFaces"
		contact.shape = shape
		var body := StaticBody3D.new()
		body.name = record.id
		body.set_meta("wp15_collision_policy", record.policy)
		body.set_meta("wp15_faces_sha256", record.sha256)
		body.add_child(contact)
		parent.add_child(body)
	var rests := Node3D.new()
	rests.name = "RestContacts"
	root.add_child(rests)
	for record in data.rest_contacts:
		var marker := Marker3D.new()
		marker.name = record.id
		marker.position = _v(record.local_position)
		marker.basis = Basis.looking_at(_v(record.forward), Vector3.UP)
		marker.set_meta("proposed_rest_contact", true)
		marker.set_meta("admission_capacity_created", false)
		marker.set_meta("furniture_instance", record.furniture_instance)
		rests.add_child(marker)
	for record in data.lights:
		var parent: Node3D = nodes[record.runtime_parent_name]
		var light := SpotLight3D.new()
		light.name = "PhysicalSource"
		light.visible = false
		light.shadow_enabled = false
		light.light_color = Color(record.color[0], record.color[1], record.color[2])
		light.light_energy = float(record.light_energy)
		light.spot_range = float(record.spot_range)
		light.spot_angle = float(record.spot_angle)
		light.spot_attenuation = float(record.spot_attenuation)
		light.spot_angle_attenuation = float(record.spot_angle_attenuation)
		light.set_meta("fixture_powered", true)
		light.set_meta("wp15_source_index", int(record.source_index))
		light.set_meta("wp15_fixture_members", record.fixture_members)
		light.set_meta("wp15_source_inner_cone_degrees", record.source_inner_cone_degrees)
		light.set_meta("wp15_calibration", "initial_bounded_source_normalization_unaccepted")
		if record.illumination_anchor != null:
			light.set_meta("illumination_anchor", _v(record.illumination_anchor))
		# Sole existing manager scans these requests synchronously after build().
		light.shadow_enabled = true
		parent.add_child(light)
	space.add_child(root)
	_finish_floor(space, data)
	return root

static func _index(node: Node, into: Dictionary) -> void:
	assert(not into.has(str(node.name)), "Duplicate imported WP15 node name")
	into[str(node.name)] = node
	for child in node.get_children():
		_index(child, into)

static func _v(value: Array) -> Vector3:
	return Vector3(value[0], value[1], value[2])

static func _finish_floor(space: Node3D, data: Dictionary) -> void:
	var floor: Node3D = space.get_node("CompiledStructuralFloors_NotFinishedRooms/D07_team_lounge_receiving_floor")
	var material := ShaderMaterial.new()
	material.shader = load("res://shaders/team_lounge_receiving_finish.gdshader")
	for texture in data.finish_textures:
		assert(FileAccess.get_sha256(texture.file) == texture.sha256)
		material.set_shader_parameter(texture.role, load(texture.file))
	var applied := 0
	for chunk_name in data.finish_top_chunks:
		var visual := floor.get_node(NodePath(chunk_name)) as MeshInstance3D
		assert(visual != null and visual.mesh.get_surface_count() == 1)
		visual.set_surface_override_material(0, material)
		applied += 1
	assert(applied == 52)
