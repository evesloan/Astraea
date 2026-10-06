extends RefCounted
# Additive source-backed crowns and feature lights. Incremental WIP, not final finish.
const CONTRACT := "res://data/architecture/GRAND_POOL_FEATURE_LAYERS_RUNTIME.json"

static func xyz(p: Array) -> Vector3:
	return Vector3(p[0],p[1],p[2])

static func _exact_node(visual: Node3D, name: String) -> Node3D:
	var matches: Array[Node3D] = []
	# These pinned GLBs omit GODOT_single_root: visual is always an importer
	# wrapper, never a declared source node, regardless of its generated name.
	for child in visual.find_children("*","Node3D",true,false):
		if str(child.name) == name:
			matches.append(child)
	assert(matches.size() == 1,"Missing or ambiguous checked feature node: "+name)
	return matches[0]

static func _source_nodes(item: Node3D, spec: Dictionary) -> Dictionary:
	assert(item.get_child_count() == 1)
	var visual := item.get_child(0) as Node3D
	assert(visual != null and visual.transform == Transform3D.IDENTITY)
	var nodes: Dictionary = {}
	for entry in spec.nodes:
		var node: Node3D = _exact_node(visual,str(entry.name))
		assert(node.get_class() == str(entry.native_class))
		assert(node.position == xyz(entry.translation_xyz) and node.basis == Basis.IDENTITY)
		nodes[str(entry.name)] = node
	var declared_roots: int = 0
	for entry in spec.nodes:
		var node: Node3D = nodes[str(entry.name)]
		if str(entry.parent_name).is_empty():
			assert(node.get_parent() == visual)
			declared_roots += 1
		else:
			assert(node.get_parent() == nodes[str(entry.parent_name)])
	assert(visual.get_child_count() == declared_roots)
	return nodes

static func _check_meshes(item: Node3D, spec: Dictionary, nodes: Dictionary) -> void:
	assert(item.find_children("*","MeshInstance3D",true,false).size() == int(spec.mesh_batches))
	for entry in spec.meshes:
		var mesh := nodes[str(entry.name)] as MeshInstance3D
		assert(mesh != null and mesh.mesh != null)
		assert(mesh.material_override == null and mesh.material_overlay == null)
		assert(mesh.mesh.get_surface_count() == entry.surfaces.size())
		for index in range(entry.surfaces.size()):
			var expected: Dictionary = entry.surfaces[index]
			assert(mesh.get_surface_override_material(index) == null)
			var material: Material = mesh.get_active_material(index)
			assert(material != null and str(material.resource_name) == str(expected.material_name))
			assert((mesh.mesh.surface_get_format(index) & Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES) == 0)
			var arrays: Array = mesh.mesh.surface_get_arrays(index)
			assert(arrays[Mesh.ARRAY_VERTEX].size() == int(expected.vertices))
			assert(arrays[Mesh.ARRAY_INDEX] != null and arrays[Mesh.ARRAY_INDEX].size() == int(expected.indices))
		mesh.set_meta("runtime_collision_contract",entry.collision)
		mesh.set_meta("source_part_names",entry.source_part_names)
		if not bool(entry.cast_shadow):
			mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		else:
			assert(mesh.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_ON)
	item.set_meta("checked_source_sha256",spec.source_sha256)
	item.set_meta("checked_export_sha256",spec.sha256)

static func build(parent: Node3D, ship: Node3D, architecture: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(architecture.get_parent() == parent and architecture.transform == Transform3D.IDENTITY)
	assert(str(architecture.name) == str(data.preservation.architecture_root))
	assert(architecture.get_child_count() == int(data.preservation.architecture_child_count))
	assert(parent.get_node_or_null(NodePath(str(data.root_name))) == null)
	assert(architecture.find_children("*","Light3D",true,false).is_empty())
	# The unchanged shared selector discovers all sources after every builder.
	assert(ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget") == null)
	for key in data.models:
		var spec: Dictionary = data.models[key]
		assert(FileAccess.get_sha256("res://assets/models/"+str(spec.file)) == str(spec.sha256))
	var old_children: Array[Node] = architecture.get_children()
	var preserved: Array = []
	for entry in data.preservation.plants:
		var old := architecture.get_node(NodePath(str(entry.name))) as Node3D
		assert(old != null and old.visible and old.position == xyz(entry.position_xyz))
		assert(absf(old.rotation.y-float(entry.yaw_radians)) < 0.000001 and old.scale.is_equal_approx(Vector3.ONE))
		assert(str(old.get_meta("catalogue_file")) == str(entry.model_file))
		assert(old.find_children("*","CollisionObject3D",true,false).is_empty())
		preserved.append({"node":old,"transform":old.transform,"global_transform":old.global_transform,"visible":old.visible,"basal":bool(entry.basal)})
	var root := Node3D.new()
	root.name = str(data.root_name)
	root.set_meta("persistent_id","grand_pool_feature_layers_001")
	root.set_meta("scope",data.scope)
	parent.add_child(root)
	assert(root.transform == architecture.transform and root.global_transform == architecture.global_transform)
	var hidden: Array[Node3D] = []
	var soil_markers: int = 0
	for entry in data.plants:
		var old := architecture.get_node(NodePath(str(entry.replaces_instance))) as Node3D
		var spec: Dictionary = data.models[str(entry.asset)]
		var item: Node3D = ship.model(root,str(spec.file),str(entry.name),Vector3.ZERO)
		item.transform = old.transform
		assert(item.global_transform == old.global_transform and item.scale.is_equal_approx(Vector3.ONE))
		var nodes: Dictionary = _source_nodes(item,spec)
		_check_meshes(item,spec,nodes)
		assert(item.find_children("*","CollisionObject3D",true,false).is_empty())
		assert(item.find_children("*","Light3D",true,false).is_empty())
		item.set_meta("persistent_id","grand_pool_features_"+str(entry.name)+"_001")
		item.set_meta("placement_support",entry.support)
		item.set_meta("replaces_instance",str(old.get_path()))
		item.set_meta("collision_contract","visual_only")
		for marker in entry.soil_markers:
			var node: Node3D = nodes[str(marker.name)]
			assert(node.position == xyz(marker.translation_xyz))
			node.set_meta("source_physical_part",marker.physical_part)
			node.set_meta("placement_support",entry.support)
			soil_markers += 1
		hidden.append(old)
	var hardware_spec: Dictionary = data.models[str(data.hardware.asset)]
	var hardware: Node3D = ship.model(root,str(hardware_spec.file),str(data.hardware.name),Vector3.ZERO)
	assert(hardware.transform == Transform3D.IDENTITY)
	var hardware_nodes: Dictionary = _source_nodes(hardware,hardware_spec)
	_check_meshes(hardware,hardware_spec,hardware_nodes)
	var hardware_parts: int = 0
	for entry in hardware_spec.meshes:
		var mesh := hardware_nodes[str(entry.name)] as MeshInstance3D
		hardware_parts += entry.source_part_names.size()
		var contact := mesh.get_node_or_null("StaticContact") as StaticBody3D
		assert(contact != null)
		if str(entry.collision) == "visual_lens_no_contact":
			# ship.model attaches contacts to every non-botanical mesh. Remove only
			# this new lens batch immediately, before any physics step can see it.
			assert(not bool(entry.cast_shadow))
			mesh.remove_child(contact)
			contact.free()
			assert(mesh.find_children("*","CollisionObject3D",true,false).is_empty())
		else:
			assert(str(entry.collision) == "concave_static_surface")
			assert(contact.transform == Transform3D.IDENTITY and contact.get_child_count() == 1)
			var shape := contact.get_child(0) as CollisionShape3D
			assert(shape != null and shape.shape is ConcavePolygonShape3D and not shape.disabled)
	assert(hardware_parts == 12 and hardware.find_children("*","StaticBody3D",true,false).size() == 2)
	for entry in data.fixtures:
		var marker: Node3D = hardware_nodes[str(entry.marker_name)]
		var light := SpotLight3D.new()
		light.name = str(entry.name)
		root.add_child(light)
		light.global_position = marker.global_position
		var direction: Vector3 = (root.global_basis*xyz(entry.direction_xyz)).normalized()
		light.look_at(light.global_position+direction,root.global_basis.y)
		ship.apply_light_profile(light,str(entry.profile))
		light.light_energy = float(entry.energy)
		light.spot_range = float(entry.range_m)
		light.spot_angle = float(entry.spot_angle_degrees)
		assert(light.shadow_enabled)
		light.set_meta("source_marker",entry.marker_name)
		light.set_meta("physical_housing",entry.physical_housing)
		light.set_meta("physical_lens",entry.physical_lens)
		light.set_meta("physical_receiver_xyz",root.global_transform*xyz(entry.receiver_xyz))
		light.set_meta("illumination_anchor",root.global_transform*xyz(entry.visibility_sample_xyz))
		light.set_meta("fixture_powered",true)
		light.set_meta("source_export_sha256",hardware_spec.sha256)
		# Keep the profile's requested shadow bit true for configure(). No direct
		# budget-source append, priority exemption, unshadowed fallback or retuning.
	assert(hidden.size() == 6 and soil_markers == 30)
	assert(root.get_child_count() == 10 and root.find_children("*","MeshInstance3D",true,false).size() == 33)
	assert(root.find_children("*","Light3D",true,false).size() == 3)
	assert(root.find_children("*","CollisionObject3D",true,false).size() == 2)
	# Hide only the six originals once all additions are built; preserve nodes,
	# transforms, source files and original identities for inspection/reversal.
	for old in hidden:
		old.visible = false
	assert(architecture.get_children() == old_children and architecture.get_child_count() == 15)
	for entry in preserved:
		var old: Node3D = entry.node
		assert(old.transform == entry.transform and old.global_transform == entry.global_transform)
		assert(old.visible == (bool(entry.visible) if bool(entry.basal) else false))
	assert(architecture.find_children("*","Light3D",true,false).is_empty())
