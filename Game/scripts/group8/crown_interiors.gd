extends RefCounted
# Additive fittings in original shells. Shared door identities and floor ownership are retained.
static func build(ship:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/crown_interiors.json"))
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	assert(not districts.has_node(str(p.root_name)),"Duplicate Group8 loader invocation")
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==str(p.model_sha256))
	for node_name in ["BridgeEnclosure_WIP","CentralCommandCrown_WIP","AftCommandCrown_WIP","UpperHorizonEnclosure_WIP"]:
		assert(districts.get_node_or_null(node_name)!=null,"Group8 requires original shell: "+node_name)
	var node:=Node3D.new();node.name=str(p.root_name);districts.add_child(node)
	node.set_meta("programme_keys",p.programme_keys)
	node.set_meta("new_floor_owners",0);node.set_meta("new_capacity",0)
	node.set_meta("operational_acceptance",false)
	var source:Node3D=load("res://scripts/d04_port_forward_homes_fifth.gd").visual(node,str(p.model_file),p.collision_policy)
	for row in p.lights:
		var marker:Node3D=source.find_child(str(row.name),true,false)
		assert(marker!=null,"Group8 light must have actual source fixture marker")
		var lamp:=SpotLight3D.new();lamp.name=str(row.name);node.add_child(lamp)
		lamp.global_position=marker.global_position;lamp.rotation.x=-PI/2
		lamp.light_color=Color(row.colour[0],row.colour[1],row.colour[2])
		lamp.light_energy=float(row.energy);lamp.spot_range=float(row.range);lamp.spot_angle=70
		lamp.shadow_enabled=true;lamp.set_meta("fixture_powered",true)
		# Tests and source inspection may append after main has configured its existing budget.
		var budget:Node=ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
		if budget!=null:
			budget.sources.append(lamp);budget.requested_shadow[lamp.get_instance_id()]=true
			lamp.visible=false;lamp.shadow_enabled=false
	for row in p.labels:
		var label:=Label3D.new();label.name="Programme_"+str(row.programme_key);node.add_child(label)
		label.text=str(row.text);label.font_size=40;label.pixel_size=.006
		label.position=Vector3(row.at[0],row.at[1],row.at[2]);label.rotation.y=float(row.yaw)
		label.modulate=Color(.8,.9,.91)
	return node
