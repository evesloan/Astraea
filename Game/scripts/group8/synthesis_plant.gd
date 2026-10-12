extends RefCounted
# New local plant construction. Group1 must first adopt its supporting floor counterpart.
static func build(ship:Node3D,supporting_floor_adopted:bool=false)->Node3D:
	assert(supporting_floor_adopted,"Group1 supporting floor adoption required before synthesis installation")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/synthesis_plant.json"));var parent:Node3D=ship.get_node("ShipSpace/Districts")
	assert(not parent.has_node(str(p.root_name))and FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==str(p.model_sha256))
	assert(FileAccess.get_sha256("res://assets/models/AST-STF-008.glb")==str(p.retained_standard_door_source.runtime_sha256))
	var n:=Node3D.new();n.name=str(p.root_name);parent.add_child(n);n.set_meta("programme_key","D01_directory_05");n.set_meta("new_capacity",0);n.set_meta("supporting_floor_adoption_required",true);n.set_meta("plant_or_final_acceptance",false)
	var visual:Node3D=(load("res://assets/models/"+str(p.model_file))as PackedScene).instantiate();n.add_child(visual)
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		assert(p.collision_policy.has(str(mesh.name)))
		if bool(p.collision_policy[str(mesh.name)].collide):load("res://scripts/static_contact_cache.gd").attach(mesh)
	for row in p.doors:
		var marker:Node3D=visual.find_child(str(row.marker),true,false);assert(marker!=null)
		var door:Node3D=load("res://scripts/service_door.gd").new();door.name=str(row.name);door.persistent_id=StringName(str(row.persistent_id));door.position=marker.global_position;door.rotation.y=float(row.yaw);door.scale=Vector3(row.scale[0],row.scale[1],row.scale[2]);n.add_child(door)
		var label:=Label3D.new();label.name=str(row.name)+"Purpose";label.text="CLEAN OUTPUT / PACKING"if "Clean"in str(row.name)else"WASH / USED RETURN";label.position=Vector3(row.at[0],2.97,row.at[2]-.14);label.font_size=32;label.pixel_size=.004;label.modulate=Color(.12,.22,.24);n.add_child(label)
	for row in p.lights:
		var marker:Node3D=visual.find_child(str(row.name),true,false);assert(marker!=null)
		var light:=SpotLight3D.new();light.name=str(row.name);n.add_child(light);light.global_position=marker.global_position;light.rotation.x=-PI/2;light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.light_energy=float(row.energy);light.spot_range=float(row.range);light.spot_angle=float(row.spot_angle);light.shadow_enabled=true;light.set_meta("fixture_powered",true);light.set_meta("illumination_anchor",Vector3(row.aim[0],row.aim[1],row.aim[2]))
		var budget:Node=ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
		if budget!=null:budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.visible=false;light.shadow_enabled=false
	return n
