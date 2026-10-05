extends RefCounted
# First connected aft house platform. Accommodation, private upper and finish remain incomplete.
static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json"))
	assert(data.catalogue_id == "AST-RES-006")
	assert(data.exported_walkable_floor_meshes == 0, "Only the structural compiler owns the slab")
	assert(data.units_preserved.size() == 16)
	var root := Node3D.new()
	root.name = "D17ConnectedHouse_WIP"
	root.set_meta("persistent_id", "D17_connected_aft_house_platform")
	root.set_meta("source_guest_index", 790)
	root.set_meta("scope", "Connected court and lower platform; no completed accommodation, private upper or separate service network")
	parent.add_child(root)
	var architecture: Node3D = ship.model(root, "AST-RES-006.glb", "D17ConnectedArchitecture", Vector3.ZERO)
	var glass := ShaderMaterial.new()
	glass.shader = load("res://shaders/hospitality_glass.gdshader")
	for mesh in architecture.find_children("*", "MeshInstance3D", true, false):
		if "glass" in str(mesh.name).to_lower():
			mesh.material_override = glass
	for fixture in data.fixtures:
		var marker := architecture.find_child(str(fixture.name), true, false) as Node3D
		assert(marker != null, "Visible source fixture marker required")
		var p: Array = fixture.position_world
		assert(marker.global_position.distance_to(Vector3(p[0], p[1], p[2])) < .002)
		var light := SpotLight3D.new()
		root.add_child(light)
		light.name = "D17HouseSource_" + str(fixture.name)
		light.global_position = marker.global_position
		light.rotation.x = -PI / 2
		light.light_color = Color(1.0, .86, .68)
		light.light_energy = 1.15
		light.spot_range = 12.0
		light.spot_angle = 78.0
		light.shadow_enabled = true
