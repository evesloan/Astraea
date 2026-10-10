extends RefCounted
static func build(ship:Node3D)->void:
	assert(bool(ship.get_meta("central_residential_streets_installed",false)))
	for script in ["star_atlas_rooms","night_garden_rooms"]:
		var homes:Node3D=load("res://scripts/"+script+".gd").build(ship)
		homes.set_meta("default_scene_enabled",true)
		homes.set_meta("acceptance","integrated_construction_wip")
		homes.set_meta("receiving_structure_accepted",false)
		homes.set_meta("occupied_capacity_accepted",false)
	load("res://scripts/star_atlas_specialty_first.gd").build(ship)
	load("res://scripts/star_atlas_specialty_second.gd").build(ship)
	load("res://scripts/star_atlas_eight_habitats.gd").build(ship)
	load("res://scripts/star_atlas_specialty_third.gd").build(ship)
	load("res://scripts/star_atlas_specialty_fourth.gd").build(ship)
	load("res://scripts/star_atlas_specialty_fifth.gd").build(ship)
	load("res://scripts/star_atlas_specialty_sixth.gd").build(ship)
	load("res://scripts/star_atlas_specialty_seventh.gd").build(ship)
	load("res://scripts/star_atlas_specialty_eighth.gd").build(ship)
	load("res://scripts/star_atlas_specialty_ninth.gd").build(ship)
