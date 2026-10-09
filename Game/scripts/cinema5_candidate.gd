extends RefCounted
# Exact retained source plus separately owned floors. Installed construction WIP; operational and final-art acceptance remain open.
static func build(ship: Node3D) -> Node3D:
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CINEMA5_RECEIVING_FLOORS_CANDIDATE.json"))
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==str(definition.source_checks.baseline_structural_sha256))
	assert(FileAccess.get_sha256("res://data/generated/received_structural_meshes.json")==str(definition.source_checks.preceding_receiving_sha256))
	assert(FileAccess.get_sha256("res://data/architecture/SALON_RECEIVING_FLOORS_CANDIDATE.json")==str(definition.source_checks.salon_receiving_sha256))
	assert(FileAccess.get_sha256("res://data/architecture/STILLROOM_RECEIVING_FLOORS_CANDIDATE.json")==str(definition.source_checks.stillroom_receiving_sha256))
	var file := "res://assets/models/SOL_D11_directory_06_remaining_r001.glb"
	assert(FileAccess.get_sha256(file)=="803ddfe94bc772a001a8d07d5c922c8b845262defb7d5fc3a0ce2242ef623548")
	var districts := ship.get_node("ShipSpace/Districts")
	assert(districts.get_node_or_null("Cinema5Receiving_WIP")==null)
	var room := Node3D.new()
	room.name = "Cinema5Receiving_WIP"
	room.position = Vector3.ZERO
	room.set_meta("programme_key","D11_directory_06")
	room.set_meta("installed_acceptance",false)
	room.set_meta("east_portal","temporary_closed_until_external_route_exists")
	var source: Node3D = (load(file) as PackedScene).instantiate()
	var lights: Array[Light3D] = load("res://scripts/receiving_source_lights.gd").normalize(source,25)
	room.add_child(source)
	districts.add_child(room)
	var meshes := source.find_children("*","MeshInstance3D",true,false)
	assert(meshes.size()==1469)
	var visual_markings:=0
	for mesh: MeshInstance3D in meshes:
		if str(mesh.name) in ["E_transfer_place_marker","E_transfer_place_marker_001","E_transfer_place_marker.001"]:
			# Exact pinned source marks these two 1mm inlays as visible-only.
			mesh.set_meta("receiving_collision_policy","visual_transfer_marking_excluded")
			visual_markings+=1
			continue
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	assert(visual_markings==2)
	room.set_meta("visual_only_transfer_markings",visual_markings)
	load("res://scripts/structural_floor_builder.gd").build_regions(ship.get_node("ShipSpace"),ship.stone,ship.ivory,definition.regions,{},"Cinema5CandidateStructuralFloors")
	# Reversible receiving closure: no external east floor exists yet.
	# Preserve all original doorway source meshes and the internal aisle.
	var closure := MeshInstance3D.new()
	closure.name="EastPortalTemporaryReceivingClosure"
	var panel := BoxMesh.new()
	panel.size=Vector3(.18,2.66,4.24)
	closure.mesh=panel
	closure.material_override=ship.ivory
	closure.position=Vector3(60.55,70.83,280)
	closure.set_meta("temporary_receiving_boundary",true)
	closure.set_meta("removal_gate","Verified supported external connection and traversal")
	room.add_child(closure)
	load("res://scripts/static_contact_cache.gd").attach(closure)
	load("res://scripts/receiving_source_lights.gd").register(lights,ship)
	room.set_meta("normalized_source_count",lights.size())
	return room
