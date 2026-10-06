extends RefCounted
# Faithful additive exports. Original section, 51 furnishings and floors remain owned.
const CONTRACT := "res://data/architecture/GRAND_POOL_FINISH_RUNTIME.json"

static func vector(p: Array) -> Vector3:
	return Vector3(p[0], p[1], p[2])

static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(parent.get_node_or_null("GrandPoolFinish_WIP") == null)
	for key in data.models:
		var spec: Dictionary = data.models[key]
		assert(FileAccess.get_sha256("res://assets/models/" + str(spec.file)) == spec.sha256, "Checked pool derivative changed: " + str(spec.file))
	var root := Node3D.new()
	root.name = "GrandPoolFinish_WIP"
	root.set_meta("persistent_id", "grand_pool_finish_001")
	root.set_meta("scope", "Checked finish, signs, stock and comfort derivatives; visual composition remains under review")
	parent.add_child(root)
	for entry in data.assemblies:
		var item: Node3D = ship.model(root, str(entry.model_file), str(entry.name), Vector3.ZERO)
		var spec: Dictionary = data.models[str(entry.asset)]
		var seen: Array[String] = []
		for mesh in item.find_children("*", "MeshInstance3D", true, false):
			var key := str(mesh.name)
			assert(spec.meshes.has(key), "Unrecognized checked mesh: " + key)
			var part: Dictionary = spec.meshes[key]
			var contact := mesh.get_node_or_null("StaticContact")
			assert(contact != null)
			if not bool(part.physical): contact.free()
			mesh.set_meta("runtime_collision_contract", part.collision_contract)
			if not bool(part.cast_shadow): mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			seen.append(key)
		assert(seen.size() == spec.meshes.size())
		item.set_meta("checked_source_sha256", spec.source_sha256)
	for entry in data.placements:
		var item: Node3D = ship.model(root, str(entry.model_file), str(entry.name), vector(entry.position_xyz), float(entry.yaw_radians))
		item.set_meta("persistent_id", "grand_pool_finish_" + str(entry.name) + "_001")
		item.set_meta("placement_support", entry.support)
		item.set_meta("programme_key", "D08_directory_01" if float(entry.position_xyz[1]) < 52.5 else "D09_directory_01")
		var spec: Dictionary = data.models[str(entry.asset)]
		if spec.collision == "concave_static_surface" and str(entry.model_file).begins_with("AST-BOT"):
			ship._static_contacts(item)
		item.set_meta("collision_contract", spec.collision)
	var envelope := root.get_node("GrandPoolFinishEnvelope")
	for entry in data.fixtures:
		var marker := envelope.find_child(str(entry.name), true, false) as Node3D
		assert(marker != null, "Source-backed pool light lost its physical marker")
		assert(marker.global_position.distance_to(vector(entry.position_xyz)) < .00005)
		var light := SpotLight3D.new()
		light.name = "GrandPoolFinishSource_" + str(entry.name)
		root.add_child(light)
		light.global_position = marker.global_position
		var direction := vector(entry.direction_xyz).normalized()
		light.look_at(light.global_position + direction, Vector3.FORWARD if absf(direction.y) > .98 else Vector3.UP)
		ship.apply_light_profile(light, "aquatic_edge" if "WetRest" in str(entry.name) else "guest_lounge")
		light.light_energy = float(entry.suggested_energy)
		light.spot_range = float(entry.suggested_range_m)
		light.spot_angle = float(entry.suggested_spot_angle_degrees)
		light.shadow_enabled = true
		light.set_meta("source_marker", entry.name)
		# Visibility samples must be in free space just lightward of the physical receiver.
		light.set_meta("illumination_anchor", vector(entry.visibility_sample_xyz))
		light.set_meta("physical_receiver_xyz", vector(entry.receiver_xyz))
		light.set_meta("physical_housing", entry.physical_housing)
	assert(root.find_children("*", "Light3D", true, false).size() == 14)
