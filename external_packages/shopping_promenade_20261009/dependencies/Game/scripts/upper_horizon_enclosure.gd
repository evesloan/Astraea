extends RefCounted
# Supported public enclosure; open onward boundary and occupation remain unfinished.
static func build(parent: Node3D, ship: Node3D) -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/UPPER_HORIZON_ENCLOSURE_RUNTIME.json"))
	assert(data.catalogue_id == "AST-CMD-006")
	assert(data.doors.is_empty() and data.light_markers.is_empty())
	var root := Node3D.new()
	root.name = "UpperHorizonEnclosure_WIP"
	root.set_meta("persistent_id", "D18_upper_horizon_enclosure_001")
	root.set_meta("programme_key_reserved", "D18_directory_09")
	root.set_meta("scope", "Foyer and observation enclosure; onward closure, furnishing and operating systems unfinished")
	parent.add_child(root)
	var shell: Node3D = ship.model(root, "AST-CMD-006.glb", "UpperHorizonEnclosureArchitecture", Vector3.ZERO)
	var glass := ShaderMaterial.new()
	glass.shader = load("res://shaders/hospitality_glass.gdshader")
	for mesh in shell.find_children("*", "MeshInstance3D", true, false):
		if "glass" in str(mesh.name).to_lower():
			mesh.material_override = glass
