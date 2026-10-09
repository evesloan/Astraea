extends RefCounted
# Retained house and83source homes; construction installation, not final acceptance.
static func build(ship:Node3D)->Node3D:
	if OS.get_environment("ASTRAEA_QUIET_CANDIDATE_ISOLATION")=="1":return null
	var house:Node3D=load("res://scripts/quiet_grove_receiving.gd").build(ship)
	house.set_meta("persistent_id","quiet_grove_house_001")
	load("res://scripts/quiet_grove_lift.gd").build(house)
	house.set_meta("acceptance","installed_construction_wip")
	house.set_meta("receiving_exception","current_library_roof_composite_successor")
	var support:=Node3D.new()
	support.name="LongLibraryCompositeReceivingCore"
	house.add_child(support)
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/QUIET_GROVE_COMPOSITE_SUPPORT.json"))
	assert(FileAccess.get_sha256("res://assets/models/WP06_long_library.glb")==str(plan.retained_library_sha256))
	for item in plan.parts:
		var lo:=Vector3(item.min[0],item.min[1],item.min[2])
		var hi:=Vector3(item.max[0],item.max[1],item.max[2])
		var part:=MeshInstance3D.new()
		part.name=str(item.name)
		var box:=BoxMesh.new()
		box.size=hi-lo
		part.mesh=box
		part.position=(lo+hi)*.5
		part.material_override=ship.ivory
		part.set_meta("construction_role",item.role)
		support.add_child(part)
		load("res://scripts/static_contact_cache.gd").attach(part)
	assert(support.get_child_count()==143)
	var homes:Node3D=load("res://scripts/quiet_grove_rooms.gd").build(ship)
	homes.set_meta("default_scene_enabled",true)
	homes.set_meta("installed_source_units",83)
	homes.set_meta("occupied_capacity_accepted",false)
	house.set_meta("installed_guest_units",83)
	return house
