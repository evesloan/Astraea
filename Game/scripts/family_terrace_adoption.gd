extends RefCounted
# Integrate retained construction first; receiving-frame hold remains open under hull work.
# This is not structural, visual, occupancy or traversal acceptance.
static func build(ship:Node3D)->Node3D:
	if OS.get_environment("ASTRAEA_FAMILY_CANDIDATE_ISOLATION")=="1":return null
	var house:Node3D=load("res://scripts/family_terrace_receiving.gd").build(ship)
	house.set_meta("persistent_id","family_terrace_house_001")
	house.set_meta("acceptance","integrated_construction_wip")
	house.set_meta("receiving_structure_accepted",false)
	house.set_meta("open_construction_hold","FT_BASE_RECEIVING_HOLD")
	var homes:Node3D=load("res://scripts/family_terrace_rooms.gd").build(ship)
	homes.set_meta("default_scene_enabled",true)
	homes.set_meta("installed_source_units",82)
	homes.set_meta("occupied_capacity_accepted",false)
	house.set_meta("installed_guest_units",82)
	return house
