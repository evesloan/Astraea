extends RefCounted
# Named residency successor; original r003 builder and native sources remain immutable.
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	assert(not districts.has_node("NightGardenD15SpecialtyReceiving20261020"))
	var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_specialty_d15_20261020/PACKAGE_R003.json"))
	assert(ship.private_detail_residency!=null)
	assert(FileAccess.get_sha256("res://assets/models/AST-COM-003.glb")==package.receiving.commons_source_sha256)
	var commons:Node3D=districts.get_node("D13_D14_StarboardCommons_WIP/D15_D17_StarboardHouseUpper_WIP/StarboardHouseUpperArchitecture")
	assert(commons.find_children("RoomStaticContacts","StaticBody3D",true,false).is_empty(),"Commons contacts changed ownership; bounded wall replacement refused")
	for patch in package.receiving.commons_patch:
		var predecessor:=commons.find_child(patch.source_mesh,true,false) as MeshInstance3D
		assert(predecessor!=null and predecessor.mesh!=null)
		assert(predecessor.find_children("StaticContact","StaticBody3D",true,false).size()==1,"Exact per-mesh commons contact required")
	for room in package.rooms:
		assert(ship.private_detail_residency.accepts(room.model_file),"No eager-detail fallback permitted")
		assert(ship.private_detail_residency.index[room.model_file].sha256==room.model_sha256)
	var root:=Node3D.new();root.name=package.root_name;districts.add_child(root)
	root.set_meta("new_units",0);root.set_meta("reserved_rest_count",40);root.set_meta("finished",false)
	root.set_meta("authorship","new_fitted_construction_20261020");root.set_meta("occupied_capacity_accepted",false);root.set_meta("species_environment_accepted",false)
	var helper:Script=load("res://scripts/night_garden_residency_20261022/source_visual.gd")
	for room in package.rooms:
		assert(FileAccess.get_sha256("res://assets/models/"+str(room.model_file))==room.model_sha256)
		var home:=Node3D.new();home.name=room.allocation.proposed_runtime_id;root.add_child(home)
		home.set_meta("allocation_sha256",room.allocation.allocation_sha256);home.set_meta("census_source_index",room.allocation.source_envelope_index)
		home.set_meta("rest_slot_ids",room.allocation.proposed_rest_slot_ids);home.set_meta("reserved_rest_count",room.allocation.proposed_rest_place_count)
		home.set_meta("historical_bed_anchor_markers",room.allocation.historical_bed_anchor_markers)
		home.set_meta("species_ready",false);home.set_meta("historical_save_identity_recovered",false);home.set_meta("finished",false)
		ship.register_private_interior(home,room.model_file)
		for d in room.doors:
			var door:Node3D=load("res://scripts/"+str(d.controller)).new();door.name=d.name;door.persistent_id=d.persistent_id;door.position=vec(d.position);door.rotation.y=d.yaw;home.add_child(door)
		for item in room.lights:
			var light:=SpotLight3D.new();light.name=item.name;light.position=vec(item.position);light.rotation.x=-PI/2;light.light_color=Color(1,.93,.8);light.light_energy=item.energy;light.spot_range=item.range;light.spot_angle=70;light.shadow_enabled=false;home.add_child(light)
	assert(package.rooms.size()==30)
	var receiving:Dictionary=package.receiving
	assert(FileAccess.get_sha256("res://assets/models/"+str(receiving.model_file))==receiving.model_sha256)
	assert(FileAccess.get_sha256("res://assets/models/AST-COM-003.glb")==receiving.commons_source_sha256)
	# Validate every exact source before removing any of the four bounded wall pieces.
	for patch in receiving.commons_patch:
		var mesh:=commons.find_child(patch.source_mesh,true,false) as MeshInstance3D
		assert(mesh!=null and mesh.mesh!=null,"Night Garden portal predecessor unavailable: "+str(patch.source_mesh))
	var street:=Node3D.new();street.name="ConnectedStreetsAndPortalSuccessors";root.add_child(street)
	var receiving_visual:Node3D=helper.contact_visual(street,receiving.model_file)
	if receiving_visual==null:
		street.free();return null
	for patch in receiving.commons_patch:commons.find_child(patch.source_mesh,true,false).free()
	street.set_meta("engineering_load_capacity_accepted",false)
	for sign in [-1,1]:
		for z in [19,28,35,42,56.8,71.6,86.4,94]:
			var x:=90.5 if z<26 else (87.0 if z==28 else 84.0)
			var light:=SpotLight3D.new();light.name="StreetFixture_%s_%s"%[sign,z];light.position=Vector3(x,96.4,z*sign);light.rotation.x=-PI/2;light.light_color=Color(1,.94,.82);light.light_energy=1.1;light.spot_range=8;light.spot_angle=72;light.shadow_enabled=false;street.add_child(light)
	return root
static func vec(v:Array)->Vector3:return Vector3(v[0],v[1],v[2])
