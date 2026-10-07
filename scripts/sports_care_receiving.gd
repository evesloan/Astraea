extends RefCounted
# Whole retained WP02 room plus bounded receiving floor/guards; original source geometry remains exact.
# Parent must add reviewed compiler floor owners and call before the sole lighting-budget configure.
const CONTRACT := "res://data/architecture/D07_SPORTS_CARE_RECEIVING.json"

static func xyz(a: Array) -> Vector3:
	return Vector3(float(a[0]), float(a[1]), float(a[2]))

static func unique(root: Node, label: String) -> Node:
	var hits: Array = root.find_children(label, "", true, false)
	assert(hits.size() == 1, "One exact Sports Care identity required: " + label)
	return hits[0]

static func model_ready(filename: String, expected: String) -> void:
	var path := "res://assets/models/" + filename
	assert(FileAccess.get_sha256(path) == expected, "Receiving model pin changed: " + filename)
	var options := ConfigFile.new()
	assert(options.load(path + ".import") == OK)
	assert(bool(options.get_value("params", "meshes/force_disable_compression", false)), "New model precision import must disable compression")
	assert(not bool(options.get_value("params", "meshes/generate_lods", true)))
	assert(str(options.get_value("params", "nodes/root_type", "")) == "Node3D")

static func build(parent: Node3D, ship: Node3D) -> void:
	var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	assert(d.programme_key == "D07_directory_10" and not bool(d.first_pass_quality_accepted))
	assert(parent.get_node_or_null(str(d.root_name)) == null, "Never duplicate the destination")
	model_ready(str(d.model_file), str(d.model_sha256))
	model_ready(str(d.guard_file), str(d.guard_sha256))
	for identity in d.floor_owners:
		var owner := unique(ship, str(identity))
		assert(str(owner.get_meta("region_id", "")) == str(identity), "Compiler owns each floor, never the imported preview")
	var axis := unique(ship, str(d.existing_axis_owner))
	assert(str(axis.get_meta("region_id", "")) == str(d.existing_axis_owner))
	var root := Node3D.new()
	root.name = str(d.root_name)
	root.set_meta("programme_key", str(d.programme_key))
	root.set_meta("persistent_id", str(d.persistent_id))
	root.set_meta("first_pass_quality_accepted", false)
	root.set_meta("capacity_accepted", false)
	parent.add_child(root)
	var room: Node3D = ship.model(root, str(d.model_file), "WholeRetainedSportsCare", xyz(d.placement))
	assert(room.find_children("*", "Light3D", true, false).is_empty(), "Punctual emitters are separately adapted, never double-lit")
	assert(room.find_children("*", "MeshInstance3D", true, false).size() == int(d.mesh_instances))
	var guards: Node3D = ship.model(root, str(d.guard_file), "SourceDerivedReceivingGuards", Vector3.ZERO)
	assert(guards.find_children("*", "MeshInstance3D", true, false).size() == int(d.guard_mesh_instances))
	# Modify only existing compiler top surfaces for this new owner. No visual/collision floor duplication.
	var finish := ShaderMaterial.new()
	finish.shader = load(str(d.floor_shader))
	finish.set_shader_parameter("warm_stone_texture", load("res://assets/models/WP02_receiving_warm_stone.png"))
	finish.set_shader_parameter("oatmeal_texture", load("res://assets/models/WP02_receiving_oatmeal_weave.png"))
	finish.set_shader_parameter("enamel_texture", load("res://assets/models/WP02_receiving_ivory_enamel.png"))
	var floor_owner := unique(ship, str(d.floor_owners[0]))
	var top_chunks := 0
	for node in floor_owner.find_children("cell_*", "MeshInstance3D", true, false):
		var chunk := node as MeshInstance3D
		assert(chunk.mesh.get_surface_count() == 1)
		chunk.set_surface_override_material(0, finish)
		top_chunks += 1
	assert(top_chunks > 0, "Four-metre receiving render cells required for bounded local light influence")
	for spec in d.lights:
		var fixture := unique(room, str(spec.fixture_node)) as MeshInstance3D
		assert(fixture != null)
		var lamp := SpotLight3D.new()
		lamp.name = str(spec.id)
		# No source becomes visible before the existing global budget scans it.
		lamp.visible = false
		lamp.shadow_enabled = true
		lamp.spot_range = float(spec.spot_range)
		lamp.spot_angle = float(spec.spot_angle_degrees)
		lamp.light_energy = float(spec.spot_energy)
		lamp.light_color = Color(float(spec.color[0]), float(spec.color[1]), float(spec.color[2]))
		lamp.rotation.x = -PI / 2.0
		lamp.position = xyz(spec.world)
		lamp.set_meta("source_light_id", str(spec.source_id))
		lamp.set_meta("fixture_node", str(spec.fixture_node))
		lamp.set_meta("receiving_calibration_unaccepted", true)
		root.add_child(lamp)
		var delta := fixture.global_transform * fixture.get_aabb()
		assert(lamp.global_position.y < delta.position.y and delta.position.y-lamp.global_position.y < 0.12, "Light must exit its physical underside")
	var info: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/packages/sports_care/INFORMATION_TARGETS.json"))
	var result: Dictionary = load("res://scripts/sports_care/bind_information.gd").bind(room, info)
	assert(result.rejected.is_empty() and result.bound.size() == 2)
	root.set_meta("source_receiving_contract", d)
