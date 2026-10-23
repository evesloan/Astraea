extends RefCounted
# Reuse the ship's compiled floor owner; never install another slab.
static func build(ship:Node3D)->Node3D:
	assert(FileAccess.get_sha256("res://scripts/structural_floor_builder.gd") == "d322e784d268ff22035649f6fe3dd8325ef6600407c018a83557c4376f234b4f", "Retained floor owner changed")
	assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json") == "cf82a8439d40401deba4200dc79ea8f75565fd0efc9acb0edd98c513202f7f11", "Retained floor owner changed")
	assert(FileAccess.get_sha256("res://scripts/night_garden_residency_20261022/district.gd") == "1628e5e29ae72e9db1ec70d8e1c2bb87c7bbdeb8928a2024b2748d4008fa4967")
	var floor_owner:=ship.get_node_or_null("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/D15_starboard_house_extension")
	assert(floor_owner!=null and floor_owner.get_meta("region_id","")=="D15_starboard_house_extension","Existing structural floor owner required")
	assert(floor_owner.find_children("*","StaticBody3D",true,false).size()==1,"Expected existing structural floor contact")
	var district:Node3D=load("res://scripts/night_garden_residency_20261022/district.gd").build(ship)
	if district==null:return null
	district.set_meta("integration_state","integrated_construction_wip")
	district.set_meta("existing_floor_owner",str(floor_owner.get_path()))
	district.set_meta("visual_acceptance",false)
	return district
