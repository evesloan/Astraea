extends RefCounted
# Local construction in the existing food-hall programme. No stock/diet/food controller.
static func build(ship:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/orchard_service.json"))
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	assert(not districts.has_node(str(p.root_name)),"Duplicate Group8 Orchard service loader")
	var existing:Node3D=districts.get_node("D10_OrchardFoodHall_WIP")
	assert(existing.get_meta("programme_key")=="D10_directory_04" and existing.get_meta("candidate_places")==240,"Original Orchard programme/candidate seats must remain")
	assert(existing.find_children("OrchardChair_*","Node3D",false,false).size()==240)
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==str(p.model_sha256))
	var node:=Node3D.new();node.name=str(p.root_name);districts.add_child(node)
	node.set_meta("programme_key","D10_directory_04");node.set_meta("historical_room_id","D10_banquet3")
	node.set_meta("new_capacity",0);node.set_meta("new_floor_owners",0);node.set_meta("new_controllers",0)
	node.set_meta("operational_acceptance",false);node.set_meta("hygiene_and_species_acceptance",false)
	var source:Node3D=load("res://scripts/d04_port_forward_homes_fifth.gd").visual(node,str(p.model_file),p.collision_policy)
	for row in p.lights:
		var marker:Node3D=source.find_child(str(row.name),true,false);assert(marker!=null,"Actual physical galley fixture marker required")
		var lamp:=SpotLight3D.new();lamp.name=str(row.name);node.add_child(lamp)
		lamp.global_position=marker.global_position;lamp.rotation.x=-PI/2
		lamp.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);lamp.light_energy=float(row.energy)
		lamp.spot_range=float(row.range);lamp.spot_angle=70;lamp.shadow_enabled=true;lamp.set_meta("fixture_powered",true)
		var budget:Node=ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
		if budget!=null:
			budget.sources.append(lamp);budget.requested_shadow[lamp.get_instance_id()]=true;lamp.visible=false;lamp.shadow_enabled=false
	return node
