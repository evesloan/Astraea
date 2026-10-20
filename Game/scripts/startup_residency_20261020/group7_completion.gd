extends RefCounted
# Scoped opt-in construction. Shared ship.gd and catalogue adoption belong to root.
static func build(ship: Node3D) -> Node3D:
	var districts: Node3D = ship.get_node("ShipSpace/Districts")
	if districts.has_node("Group7CompletionCandidate"):
		return districts.get_node("Group7CompletionCandidate")
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	var parent := Node3D.new()
	parent.name = "Group7CompletionCandidate"
	districts.add_child(parent)
	parent.set_meta("scope", "Group 7 bounded candidate; integration and whole-group acceptance pending")
	for row in data.models:
		var path := "res://assets/models/" + str(row.file)
		assert(FileAccess.get_sha256(path) == row.sha256, path)
		var visual: Node3D = (load(path) as PackedScene).instantiate()
		visual.name = str(row.cell)
		parent.add_child(visual)
		for mesh: MeshInstance3D in visual.find_children("*", "MeshInstance3D", true, false):
			var category: String = str(mesh.get_meta("extras", {}).get("contact_category", ""))
			if category.begins_with("solid_"):
				load("res://scripts/startup_residency_20261020/group7_contact_source.gd").attach(mesh,path,visual,ship)
			elif category == "visual_lens":
				mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for row in data.doors:
		var door := Node3D.new()
		door.name = str(row.id)
		door.set_script(load("res://scripts/service_door.gd"))
		door.persistent_id = StringName(row.id)
		door.desired_open = false
		door.open_fraction = 0.0
		parent.add_child(door)
		door.position = Vector3(row.origin[0], row.origin[1], row.origin[2])
		door.rotation.y = float(row.yaw)
	for row in data.lights:
		var light := SpotLight3D.new()
		light.name = str(row.id)
		parent.add_child(light)
		light.position = Vector3(row.position[0], row.position[1], row.position[2])
		light.rotation.x = -PI/2
		light.spot_range = float(row.range)
		light.spot_angle = float(row.angle)
		light.light_energy = float(row.energy)
		light.light_color = Color(row.color[0], row.color[1], row.color[2])
		light.shadow_enabled = true
		light.visible = false
		light.set_meta("source_fixture", row.source_hardware)
		# If built after the retained budget's configuration (as in isolated tests),
		# register only this new source; do not rescan or replace the retained budget.
		register_new_light(ship, light)
	return parent

static func register_new_light(ship: Node3D, light: Light3D) -> void:
	var budget := ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
	# Before configure(), its ordinary tree scan will discover this light once.
	# After configure(), append this light without rescanning retained sources.
	if budget != null and is_instance_valid(budget.actor):
		budget.sources.append(light)
		budget.requested_shadow[light.get_instance_id()] = true
