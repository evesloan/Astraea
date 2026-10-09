extends RefCounted
# Default-scene adoption of retained architecture and homes. Final art,
# occupancy, privacy, full service/hull acceptance remain separate.
static func build(ship: Node3D) -> Node3D:
	if OS.get_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION") == "1": return null
	var lift: Node3D = load("res://scripts/tidal_lift_candidate.gd").build(ship)
	var house: Node3D = lift.get_parent()
	house.set_meta("persistent_id", "tidal_garden_house_001")
	house.set_meta("programme_keys", ["D13_directory_02", "D14_directory_01", "D15_directory_01", "D16_directory_01", "D17_directory_01"])
	house.set_meta("acceptance", "installed_construction_wip")
	house.set_meta("listening_transfer", "named_wall_supported_composite_cap")
	var support := Node3D.new()
	support.name = "ListeningSalonCompositeCapReceivingCore"
	house.add_child(support)
	var definition: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/TIDAL_SALON_COMPOSITE_CAP.json"))
	for item in definition.members:
		var lo := Vector3(item.min[0],item.min[1],item.min[2])
		var hi := Vector3(item.max[0],item.max[1],item.max[2])
		var mesh := MeshInstance3D.new()
		mesh.name = str(item.name)
		var box := BoxMesh.new()
		box.size = hi-lo
		mesh.mesh = box
		mesh.position = (lo+hi)*.5
		mesh.material_override = ship.ivory
		mesh.set_meta("construction_role", "named_composite_cap_core")
		support.add_child(mesh)
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	var units: Node3D = load("res://scripts/tidal_room_candidates.gd").build(ship)
	units.set_meta("default_scene_enabled",true)
	units.set_meta("installed_source_units",85)
	units.set_meta("occupied_capacity_accepted",false)
	load("res://scripts/tidal_specialty.gd").build(ship)
	house.set_meta("installed_guest_units",86)
	return house
