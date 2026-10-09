extends RefCounted
# Exact retained source plus separately owned floors. Installed construction WIP; operational and final-art acceptance remain open.
static func build(ship: Node3D) -> Node3D:
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STILLROOM_RECEIVING_FLOORS_CANDIDATE.json"))
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==str(definition.source_checks.baseline_structural_sha256))
	assert(FileAccess.get_sha256("res://data/generated/received_structural_meshes.json")==str(definition.source_checks.preceding_receiving_sha256))
	assert(FileAccess.get_sha256("res://data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json")==str(definition.source_checks.salon_receiving_sha256))
	var file := "res://assets/models/SOL_D12_directory_04_remaining_r001.glb"
	assert(FileAccess.get_sha256(file)=="59e42624070aa9c4004ad6fb082cc90be998a9ccc25b6908468c50a981b6da97")
	var districts := ship.get_node("ShipSpace/Districts")
	assert(districts.get_node_or_null("StillroomReceiving_WIP")==null)
	var room := Node3D.new()
	room.name = "StillroomReceiving_WIP"
	room.position = Vector3.ZERO
	room.set_meta("programme_key","D12_directory_04")
	room.set_meta("installed_acceptance",false)
	room.set_meta("quiet_grove_interface","source_static_clearance_checked")
	var source: Node3D = (load(file) as PackedScene).instantiate()
	var lights: Array[Light3D] = load("res://scripts/receiving_source_lights.gd").normalize(source,12)
	room.add_child(source)
	districts.add_child(room)
	var meshes := source.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==234)
	for mesh: MeshInstance3D in meshes:
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,definition.regions,{},"StillroomCandidateStructuralFloors")
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	room.set_meta("normalized_source_count",lights.size())
	return room
