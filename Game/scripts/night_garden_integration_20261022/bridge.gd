extends RefCounted
# Reuse the ship's compiled floor owner; never install another slab.
static func build(ship:Node3D)->Node3D:
	assert(FileAccess.get_sha256("res://scripts/structural_floor_builder.gd") == "d322e784d268ff22035649f6fe3dd8325ef6600407c018a83557c4376f234b4f", "Retained floor owner changed")
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json") == "cf82a8439d40401deba4200dc79ea8f75565fd0efc9acb0edd98c513202f7f11", "Retained floor owner changed")
	assert(FileAccess.get_sha256("res://scripts/night_garden_residency_20261022/district.gd") == "967811858d56cf2f9486f3815046dd457f3df10f378a76d9f82127bb6fe79a75")
	var floor_owner:=ship.get_node_or_null("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/D15_starboard_house_extension")
	assert(floor_owner!=null and floor_owner.get_meta("region_id","")=="D15_starboard_house_extension","Existing structural floor owner required")
	assert(floor_owner.find_children("*","StaticBody3D",true,false).size()==1,"Expected existing structural floor contact")
	var district:Node3D=load("res://scripts/night_garden_residency_20261022/district.gd").build(ship)
	district.set_meta("integration_state","integrated_construction_wip")
	district.set_meta("existing_floor_owner",str(floor_owner.get_path()))
	district.set_meta("visual_acceptance",false)
	return district
