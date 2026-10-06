extends RefCounted
# Hash-pinned additive static contents and local fixture trial only.
const CONTRACT := "res://data/architecture/SECONDARY_ENGINEERING_ESSENTIALS_TRIAL.json"
static func build(parent: Node3D) -> Dictionary:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(data.adoption_gate_accepted and data.light_trial_values_accepted_for_test)
	assert(str(data.retained_source_commit).length() == 40, "Independent source retention must precede runtime trial")
	assert(data.catalogue_id == "AST-ENG-008" and not data.first_pass_essentials_accepted)
	assert(FileAccess.get_sha256("res://assets/models/" + str(data.model_file)) == str(data.model_sha256))
	var wrapper := Node3D.new()
	wrapper.name = "SecondaryEngineeringEssentials_Trial"
	wrapper.set_meta("catalogue_file", str(data.model_file))
	wrapper.set_meta("persistent_id", str(data.representation))
	wrapper.set_meta("scope", "Static additive scene essentials; no operating plant or first-pass acceptance")
	parent.add_child(wrapper)
	var visual := (load("res://assets/models/" + str(data.model_file)) as PackedScene).instantiate()
	wrapper.add_child(visual)
	var seen: Dictionary = {}
	for item in visual.find_children("*", "MeshInstance3D", true, false):
		var part := item as MeshInstance3D
		var label := str(part.name)
		assert(data.groups.has(label) and not seen.has(label), "Unexpected/duplicate imported furnishing group")
		seen[label] = true
		var expected: Dictionary = data.groups[label]
		assert(part.mesh != null and part.mesh.get_faces().size() == int(expected.triangles)*3)
		assert(part.material_override == null and part.get_node_or_null("StaticContact") == null)
		if part.has_meta("collision_contract"):
			assert(str(part.get_meta("collision_contract")) == str(expected.collision_contract))
		assert(str(expected.collision_contract) in ["static_surface", "none"])
		part.set_meta("validated_contact_policy", str(expected.collision_contract))
		if str(expected.collision_contract) == "static_surface":
			load("res://scripts/static_contact_cache.gd").attach(part)
	assert(seen.size() == 9)
	return data

static func apply_light_trial(light: SpotLight3D, marker_name: String, data: Dictionary) -> void:
	for item in data.local_light_trial:
		if str(item.marker) != marker_name: continue
		var expected := Vector3(item.expected_emitter_xyz[0],item.expected_emitter_xyz[1],item.expected_emitter_xyz[2])
		assert(light.global_position.distance_to(expected) < .0001)
		var target := Vector3(item.aim_xyz[0],item.aim_xyz[1],item.aim_xyz[2])
		light.look_at(target, Vector3.UP)
		light.spot_range = float(item.range_m)
		light.light_energy = float(item.energy)
		light.spot_angle = float(item.spot_angle)
		light.shadow_enabled = true
		light.set_meta("engineering_local_source_trial", true)
		light.set_meta("source_trial_aim", target)
		# No new source, receiver-through-wall workaround, material override or
		# shared profile/selector edit. Selection and real receivers are tested.
		return
