extends RefCounted
# Source-backed east lift landmark and one D09 rest bay. Candidate, not final art.
const CONTRACT := "res://data/architecture/GRAND_POOL_EAST_GALLERY_RUNTIME.json"

static func xyz(p: Array) -> Vector3:
	return Vector3(p[0],p[1],p[2])

static func _source_extras(node: Node) -> Dictionary:
	# Godot's glTF importer nests source extras; direct node metadata is runtime-owned.
	assert(node.has_meta("extras"), "Missing imported source extras: "+str(node.name))
	var extras: Variant = node.get_meta("extras")
	assert(extras is Dictionary)
	return extras

static func _source_nodes(item: Node3D, spec: Dictionary) -> Dictionary:
	assert(item.get_child_count() == 1)
	var visual := item.get_child(0) as Node3D
	assert(visual != null)
	var nodes: Dictionary = {}
	var canonical_names: Dictionary = {}
	for entry in spec.nodes:
		var raw_name: String = str(entry.source_name)
		var canonical: String = raw_name.validate_node_name()
		assert(not canonical_names.has(canonical), "Source name canonicalization collision")
		canonical_names[canonical] = raw_name
		var matches: Array[Node3D] = []
		# The PackedScene root is an importer wrapper, not a declared source node.
		for child in visual.find_children("*", "Node3D", true, false):
			if str(child.name) == canonical:
				matches.append(child)
		assert(matches.size() == 1, "Missing/ambiguous source node: "+raw_name)
		var node: Node3D = matches[0]
		assert(node.get_class() == str(entry.native_class))
		var extras: Dictionary = _source_extras(node)
		assert(str(extras.exported_source_blend_sha256) == str(spec.source_sha256))
		assert(str(extras.parent_design_id) == str(spec.parent_design_id))
		nodes[raw_name] = node
	for entry in spec.nodes:
		var node: Node3D = nodes[str(entry.source_name)]
		var parent_name: String = str(entry.parent_source_name)
		assert(node.get_parent() == (visual if parent_name.is_empty() else nodes[parent_name]))
	return nodes

static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(parent.get_node_or_null(str(data.root_name)) == null)
	assert(ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget") == null)
	for asset in data.models:
		var spec: Dictionary = data.models[asset]
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.file)) == str(spec.sha256))
	var root := Node3D.new()
	root.name = str(data.root_name)
	root.set_meta("persistent_id", "grand_pool_east_gallery_001")
	root.set_meta("scope", "Source-backed lift profile and upper rest bay; native visual finish under review")
	parent.add_child(root)
	var source_nodes: Dictionary = {}
	for entry in data.assemblies:
		var spec: Dictionary = data.models[str(entry.asset)]
		var item: Node3D = ship.model(root, str(spec.file), str(entry.name), Vector3.ZERO)
		assert(item.transform == Transform3D.IDENTITY)
		var nodes: Dictionary = _source_nodes(item, spec)
		source_nodes[str(entry.asset)] = nodes
		for mesh_spec in spec.meshes:
			var mesh: MeshInstance3D = nodes[str(mesh_spec.source_name)]
			assert(mesh.mesh != null and mesh.material_override == null and mesh.material_overlay == null)
			var contact := mesh.get_node_or_null("StaticContact") as StaticBody3D
			assert(contact != null)
			if str(mesh_spec.collision) == "visual_only":
				mesh.remove_child(contact)
				contact.free()
			else:
				assert(str(mesh_spec.collision) == "concave_static_surface")
				assert(contact.get_child_count() == 1)
				var shape := contact.get_child(0) as CollisionShape3D
				assert(shape != null and shape.shape is ConcavePolygonShape3D and not shape.disabled)
			mesh.set_meta("runtime_collision_contract", mesh_spec.collision)
			mesh.set_meta("source_part_name", mesh_spec.source_name)
			if not bool(mesh_spec.cast_shadow):
				mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for entry in data.plants:
		var spec: Dictionary = data.models[str(entry.asset)]
		var item: Node3D = ship.model(root, str(spec.file), str(entry.name), xyz(entry.position_xyz), float(entry.yaw_radians))
		assert(item.scale == Vector3.ONE)
		assert(item.find_children("*", "CollisionObject3D", true, false).is_empty())
		item.set_meta("placement_support", entry.support)
		item.set_meta("collision_contract", "visual_only")
	for entry in data.fixtures:
		var marker: Node3D = source_nodes[str(entry.asset)][str(entry.marker_name)]
		var light := SpotLight3D.new()
		light.name = str(entry.name)
		root.add_child(light)
		light.global_position = marker.global_position
		var direction: Vector3 = (root.global_basis*xyz(entry.direction_xyz)).normalized()
		light.global_basis = Basis.looking_at(direction, root.global_basis.y) # Avoid large-world target subtraction
		ship.apply_light_profile(light, str(entry.profile))
		light.light_energy = float(entry.energy)
		light.spot_range = float(entry.range_m)
		light.spot_angle = float(entry.half_angle_degrees)
		light.set_meta("source_marker", entry.marker_name)
		light.set_meta("physical_housing", entry.physical_housing)
		light.set_meta("physical_lens", entry.physical_lens)
		light.set_meta("physical_receiver_xyz", root.global_transform*xyz(entry.receiver_xyz))
		light.set_meta("illumination_anchor", root.global_transform*xyz(entry.visibility_sample_xyz))
		light.set_meta("fixture_powered", true)
		# The unchanged selector discovers these sources after all builders finish.
	assert(root.find_children("*", "Light3D", true, false).size() == data.fixtures.size())
