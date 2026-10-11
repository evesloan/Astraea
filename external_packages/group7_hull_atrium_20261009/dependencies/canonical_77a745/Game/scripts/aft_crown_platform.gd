extends RefCounted
# Supported receiving foyer and fan platform; enclosure and occupation remain unfinished.
static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_CROWN_PLATFORM_RUNTIME.json"))
	var root := Node3D.new()
	root.name = "AftCrownPlatform_WIP"
	root.set_meta("persistent_id", "D18_aft_crown_platform_001")
	root.set_meta("programme_key_reserved", "D18_directory_09")
	root.set_meta("scope", "Supported foyer and Upper Horizon platform; enclosure, furnishing and operating systems unfinished")
	parent.add_child(root)
	var shell: Node3D = ship.model(root, "AST-CMD-005.glb", "AftCrownPlatformArchitecture", Vector3.ZERO)
	var glass := ShaderMaterial.new()
	glass.shader = load("res://shaders/hospitality_glass.gdshader")
	for mesh in shell.find_children("*", "MeshInstance3D", true, false):
		if "glass" in str(mesh.name).to_lower():
			mesh.material_override = glass
	for entry in data.doors:
		assert(entry.file == "AST-STF-008.glb")
		var door: Node3D = load("res://scripts/service_door.gd").new()
		door.name = "AftPlatformDoor_" + str(entry.name)
		door.persistent_id = StringName(str(entry.name))
		door.position = Vector3(entry.position[0], entry.position[1], entry.position[2])
		door.rotation.y = float(entry.yaw)
		door.open_fraction = 0.0
		door.desired_open = false
		root.add_child(door)
	for item in data.light_markers:
		var marker := shell.find_child(str(item.name), true, false) as Node3D
		assert(marker != null, "Every route light needs its actual exported fixture marker")
		var light := SpotLight3D.new()
		root.add_child(light)
		light.name = "AftPlatformSource_" + str(item.name)
		light.global_position = marker.global_position
		var color: Array = item.get("suggested_color", [1.0, .78, .5])
		light.light_color = Color(color[0], color[1], color[2])
		light.light_energy = 1.1
		light.spot_range = float(item.get("suggested_range", 11.0))
		light.spot_angle = float(item.get("suggested_spot_angle_degrees", 82.0))
		light.rotation.x = -PI / 2
		light.shadow_enabled = true
