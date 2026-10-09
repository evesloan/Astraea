extends RefCounted
# Exact retained source plus separately owned floors. Installed construction WIP; operational and final-art acceptance remain open.
static func build(ship: Node3D) -> Node3D:
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/EQUIPMENT_RECEIVING_FLOORS_CANDIDATE.json"))
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==str(definition.source_checks.baseline_structural_sha256))
	assert(FileAccess.get_sha256("res://data/generated/received_structural_meshes.json")==str(definition.source_checks.preceding_receiving_sha256))
	var file := "res://assets/models/SOL_D03_directory_03_remaining_r001.glb"
	assert(FileAccess.get_sha256(file)=="75b158772963f78eedd2e1a5391580267d7ca009e734dcb978cb507046758c22")
	var districts := ship.get_node("ShipSpace/Districts")
	assert(districts.get_node_or_null("EquipmentDepotReceiving_WIP")==null)
	var room := Node3D.new()
	room.name = "EquipmentDepotReceiving_WIP"
	room.position = Vector3.ZERO
	room.set_meta("programme_key","D03_directory_03")
	room.set_meta("installed_acceptance",false)
	room.set_meta("stock_operations","not_implemented")
	var source: Node3D = (load(file) as PackedScene).instantiate()
	var lights: Array[Light3D] = source_fixture_lights(source)
	room.add_child(source)
	districts.add_child(room)
	var meshes := source.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==447)
	for mesh: MeshInstance3D in meshes:
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,definition.regions,{"staff_floor":ship.surface("staff_floor",Color.WHITE)},"EquipmentCandidateStructuralFloors")
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	room.set_meta("normalized_source_count",lights.size())
	return room

static func source_fixture_lights(source: Node3D) -> Array[Light3D]:
	assert(source.find_children("*","Light3D",true,false).is_empty())
	var specs: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/EQUIPMENT_FIXTURE_LIGHTS.json"))
	assert(specs.size()==19)
	var lights: Array[Light3D]=[]
	for item in specs:
		var lens:=source.find_child(str(item.lens_node),true,false) as MeshInstance3D
		assert(lens!=null)
		var light:=OmniLight3D.new()
		light.name=str(item.fixture)+"_PhysicalSource"
		var xyz: Array=item.emitter_xyz
		light.position=Vector3(xyz[0],xyz[1],xyz[2])
		light.light_color=Color(.82,.90,1.0)
		light.light_energy=1.2
		light.omni_range=8.0
		light.omni_attenuation=1.0
		light.visible=false
		light.shadow_enabled=false
		light.set_meta("fixture_powered",true)
		light.set_meta("source_lens",str(item.lens_node))
		light.set_meta("calibration","bounded_initial_unaccepted")
		source.add_child(light)
		lights.append(light)
	return lights
