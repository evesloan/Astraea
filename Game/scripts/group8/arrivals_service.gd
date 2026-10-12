extends RefCounted
# New local architectural holding/handoff suite; no custody,check-in,save or permissions system.
static func build(ship:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/arrivals_service.json"))
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	assert(not districts.has_node(str(p.root_name)),"Duplicate Group8 arrivals-service loader")
	var original:Node3D=districts.get_node("D01_D02_ArrivalsFusion_Integrated_WIP")
	assert(original.get_meta("programme_keys")==["D01_directory_01","D02_directory_01"],"Original arrivals/fusion programmes required")
	assert(original.has_node("ArrivalsVisitorLift")and original.has_node("ArrivalsCrescentReception")and original.has_node("ArrivalsFittedReceptionAlcove"))
	for existing:Node in ship.find_children("*","Node3D",true,false):
		if existing.get_script()==load("res://scripts/service_door.gd"):assert(str(existing.persistent_id)!=str(p.door.persistent_id),"New authored door identity must be unique")
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==str(p.model_sha256))
	var n:=Node3D.new();n.name=str(p.root_name);districts.add_child(n)
	n.set_meta("programme_key","D01_directory_01");n.set_meta("new_floor_owners",0);n.set_meta("new_capacity",0);n.set_meta("new_controllers",0)
	n.set_meta("operational_acceptance",false);n.set_meta("new_local_door_identity_authored",true)
	var visual:Node3D=load("res://scripts/d04_port_forward_homes_fifth.gd").visual(n,str(p.model_file),p.collision_policy)
	var marker:Node3D=visual.find_child(str(p.door.marker),true,false);assert(marker!=null,"Actual exported door datum required")
	var d:Node3D=load("res://scripts/service_door.gd").new();d.name=str(p.door.name);d.persistent_id=StringName(str(p.door.persistent_id))
	d.position=marker.global_position;d.rotation.y=float(p.door.yaw);d.open_fraction=0;d.desired_open=false;n.add_child(d)
	for row in p.lights:
		var exit:Node3D=visual.find_child(str(row.name),true,false);assert(exit!=null,"Physical source fixture required")
		var light:=SpotLight3D.new();light.name=str(row.name);n.add_child(light);light.global_position=exit.global_position;light.rotation.x=-PI/2
		light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.light_energy=float(row.energy);light.spot_range=float(row.range);light.spot_angle=70;light.shadow_enabled=true;light.set_meta("fixture_powered",true)
		var budget:Node=ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
		if budget!=null:
			budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.visible=false;light.shadow_enabled=false
	return n
