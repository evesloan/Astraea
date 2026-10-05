extends RefCounted
# Architectural bridge shell; operational controls and role permissions are unfinished.
static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/BRIDGE_ENCLOSURE_RUNTIME.json"))
	var root := Node3D.new()
	root.name = "BridgeEnclosure_WIP"
	root.set_meta("persistent_id", "D18_directory_01")
	root.set_meta("programme_key", "D18_directory_01")
	root.set_meta("scope", "Unfurnished bridge enclosure; operational systems and role permissions unfinished")
	root.set_meta("controlled_spine_subregion", data.controlled_spine_subregion)
	parent.add_child(root)
	var shell: Node3D = ship.model(root, "AST-CMD-004.glb", "BridgeEnclosureArchitecture", Vector3.ZERO)
	var glass := ShaderMaterial.new()
	glass.shader = load("res://shaders/hospitality_glass.gdshader")
	for mesh in shell.find_children("*", "MeshInstance3D", true, false):
		if "glass" in str(mesh.name).to_lower():
			mesh.material_override = glass
	for entry in data.doors:
		assert(entry.reuse_catalogue_id == "AST-STF-008")
		var door: Node3D = load("res://scripts/service_door.gd").new()
		door.name = "BridgeEnclosureDoor_" + str(entry.id).capitalize()
		door.persistent_id = StringName("bridge_enclosure_" + str(entry.id))
		door.position = Vector3(entry.position[0], entry.position[1], entry.position[2])
		door.rotation.y = float(entry.yaw_radians)
		door.open_fraction = 0.0
		door.desired_open = false
		root.add_child(door)
	# This kit has no light sources; the platform's twenty fixtures remain unchanged.
	assert(data.light_markers.is_empty())
