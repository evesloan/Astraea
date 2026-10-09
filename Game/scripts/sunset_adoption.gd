extends RefCounted
# Retained residential construction; remaining receiving review stays in Group 1.
# This is not structural, visual, occupancy or traversal acceptance.
static func build(ship:Node3D)->Node3D:
	if OS.get_environment("ASTRAEA_SUNSET_CANDIDATE_ISOLATION")=="1":return null
	var house:Node3D=load("res://scripts/sunset_receiving.gd").build(ship)
	house.set_meta("persistent_id","sunset_house_001")
	load("res://scripts/sunset_lift.gd").build(house)
	house.set_meta("acceptance","integrated_construction_wip")
	house.set_meta("receiving_structure_accepted",false)
	house.set_meta("open_construction_hold","SUNSET_BASE_RECEIVING_HOLD")
	load("res://scripts/sunset_receiving_frame.gd").build(house)
	load("res://scripts/sunset_vesper_receiver.gd").build(house)
	var homes:Node3D=load("res://scripts/sunset_rooms.gd").build(ship)
	homes.set_meta("default_scene_enabled",true)
	homes.set_meta("installed_source_units",83)
	homes.set_meta("occupied_capacity_accepted",false)
	house.set_meta("installed_guest_units",83)
	return house
