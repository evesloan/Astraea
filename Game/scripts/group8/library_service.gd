extends RefCounted
# Passive local furnishings; existing source-room streamer owns install/unload lifetime.
static func build(ship:Node3D,room:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/library_service.json"))
	assert(str(room.get_meta("programme_key"))=="D12_directory_02")
	assert(not room.has_node(str(p.root_name)),"Duplicate Group8 library service")
	assert(FileAccess.get_sha256("res://assets/models/WP06_long_library.glb")==str(p.retained_runtime_sha256))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==str(p.model_sha256))
	var n:=Node3D.new();n.name=str(p.root_name);room.add_child(n);n.top_level=true;n.global_transform=Transform3D.IDENTITY
	n.set_meta("programme_key","D12_directory_02");n.set_meta("new_floor_owners",0);n.set_meta("new_capacity",0);n.set_meta("new_controllers",0);n.set_meta("operational_acceptance",false)
	load("res://scripts/d04_port_forward_homes_fifth.gd").visual(n,str(p.model_file),p.collision_policy)
	for row in p.lights:
		var exit:Node3D=n.find_child(str(row.name),true,false);assert(exit!=null,"Exported physical source exit required")
		var light:=SpotLight3D.new();light.name=str(row.name);n.add_child(light);light.global_position=exit.global_position;light.rotation.x=-PI/2
		light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.light_energy=float(row.energy);light.spot_range=float(row.range);light.spot_angle=70;light.shadow_enabled=true;light.set_meta("fixture_powered",true)
		var budget:Node=ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
		if budget!=null:
			budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.visible=false;light.shadow_enabled=false
	return n
