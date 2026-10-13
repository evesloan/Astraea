extends RefCounted
# Opt-in source construction package. The shared ship root does not call this.
# The integrator must first adopt supported compiler floor/void interfaces.
static func v(a: Array) -> Vector3:
	return Vector3(a[0], a[1], a[2])

static func build_section(parent: Node3D, key: String) -> Node3D:
	assert(key != "790", "Protected 790 roof/stair/lift hold remains")
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_completion/contracts/" + key + ".json"))
	var root := Node3D.new()
	root.name = "Group2_" + key
	root.set_meta("group2_source_key", key)
	root.set_meta("installed_acceptance", false)
	root.set_meta("capacity_migrated", false)
	parent.add_child(root)
	var visual := (load("res://assets/group2_completion/" + key + ".glb") as PackedScene).instantiate() as Node3D
	root.add_child(visual)
	visual.name = "RetainedSource"
	# Delivered GLBs contain complete named source hierarchies, not batched node aliases.
	for fitting in contract.get("imports", []):
		if fitting.catalogue_id not in ["AST-DOR-001", "AST-DOR-002"]:
			continue
		var door := Node3D.new()
		door.name = "Fitting_" + str(fitting.part_names[0]).split("_")[0]
		door.set_script(load("res://scripts/group2_completion/fitted_entry.gd" if fitting.catalogue_id == "AST-DOR-002" else "res://scripts/group2_completion/fitted_privacy.gd"))
		door.source_visual = visual
		door.fitting = fitting
		door.persistent_id = StringName("group2-construction:" + key + ":" + str(fitting.part_names[0]))
		door.position = v(fitting.world_xyz)
		door.rotation.y = float(fitting.source_yaw)
		root.add_child(door)
	var fixed: Array[Node] = visual.find_children("*", "MeshInstance3D", true, false)
	# Moving source parts are already reparented under fitted controllers.
	load("res://scripts/static_contact_cache.gd").attach_group(visual, fixed)
	var markers: Array = contract.get("markers", []).duplicate()
	if FileAccess.file_exists("res://data/group2_completion/LIGHTING_ADDENDUM.json"):
		var addendum: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_completion/LIGHTING_ADDENDUM.json"))
		for row in addendum.rows:
			if row.key == key:
				assert(row.export_sha256 == contract.export_sha256)
				markers.append_array(row.fixtures)
	for marker in markers:
		if marker.get("kind", "") != "fixture_light":
			continue
		var datum := visual.find_child(str(marker.name), true, false) as Node3D
		if datum == null and marker.get("original_exit_omitted_from_glb", false):
			assert(visual.find_child(str(marker.source_fixture_part), true, false) != null)
			datum = Marker3D.new()
			datum.name = str(marker.name)
			visual.add_child(datum)
			datum.global_position = v(marker.world_xyz)
		assert(datum != null and datum.global_position.distance_to(v(marker.world_xyz)) < .002)
		var light := OmniLight3D.new()
		light.name = "SourceLight_" + str(marker.name)
		root.add_child(light)
		light.global_position = datum.global_position
		light.light_color = Color(marker.color[0], marker.color[1], marker.color[2]) if marker.has("color") else Color(1.0, .86, .68)
		# Source Blender watts are not treated as Godot radiometric energy.
		light.light_energy = 1.0
		light.omni_range = 10.0
		light.omni_shadow_mode = OmniLight3D.SHADOW_CUBE
		light.shadow_enabled = true
		light.visible = false
		light.set_meta("group2_fixture", true)
	root.set_meta("source_contract", contract)
	return root

static func build(parent: Node3D, keys: Array) -> Node3D:
	var root := Node3D.new()
	root.name = "Group2LuxuryAndPrivateAdjuncts_WIP"
	parent.add_child(root)
	for key in keys:
		build_section(root, str(key))
	return root
