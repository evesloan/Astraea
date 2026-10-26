extends RefCounted
# Exact retained source plus separately owned floors. Installed construction WIP; operational and final-art acceptance remain open.
static func build(ship: Node3D) -> Node3D:
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CUSTODIAL_RECEIVING_FLOORS_CANDIDATE.json"))
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==str(definition.source_checks.baseline_structural_sha256))
	assert(FileAccess.get_sha256("res://data/generated/received_structural_meshes.json")==str(definition.source_checks.preceding_receiving_sha256))
	assert(FileAccess.get_sha256("res://data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json")==str(definition.source_checks.salon_receiving_sha256))
	assert(FileAccess.get_sha256("res://data/architecture/CINEMA5_RECEIVING_FLOORS_CANDIDATE.json")==str(definition.source_checks.cinema5_receiving_sha256))
	var file := "res://assets/models/SOL_D01_directory_10_remaining_r001.glb"
	assert(FileAccess.get_sha256(file)=="076365a7d65e5b6381799fab3cd3e3d75ad75aca4370291150dac8e78df0c299")
	var districts := ship.get_node("ShipSpace/Districts")
	assert(districts.get_node_or_null("CustodialDepotReceiving_WIP")==null)
	var room := Node3D.new()
	room.name = "CustodialDepotReceiving_WIP"
	room.position = Vector3(8,0,460)
	room.set_meta("programme_key","D01_directory_10")
	room.set_meta("installed_acceptance",false)
	room.set_meta("stock_operations","not_implemented")
	var packed:PackedScene=load(file) as PackedScene
	var source: Node3D = packed.instantiate()
	var lights: Array[Light3D] = load("res://scripts/receiving_source_lights.gd").normalize(source,35)
	room.add_child(source)
	districts.add_child(room)
	var bound:bool=load("res://group2_resource_lifetime_20261025/mesh_lease.gd").bind(room,source,packed,file,true)
	if not bound:push_error("Custodial source mesh lease binding failed");return null
	room.set_meta("source_mesh_lease_host",weakref(ship))
	var meshes := source.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==7400)
	for mesh: MeshInstance3D in meshes:
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,definition.regions,{"staff_floor":ship.surface("staff_floor",Color.WHITE)},"CustodialCandidateStructuralFloors")
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	room.set_meta("normalized_source_count",lights.size())
	return room
