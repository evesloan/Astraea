extends RefCounted
# Physical source completion for two retained dining rooms; cached room residency owns lifetime.
static func build(ship:Node3D,room:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_fixture_adaptation.json"));var key:=str(room.get_meta("programme_key"));var record:Dictionary={}
	for row in p.rooms:
		if str(row.programme_key)==key:record=row
	assert(not record.is_empty()and not room.has_node(str(p.root_name)))
	assert(FileAccess.get_sha256("res://assets/models/"+str(record.runtime_file))==str(record.runtime_sha256))
	var n:=Node3D.new();n.name=str(p.root_name);room.add_child(n);n.set_meta("programme_key",key);n.set_meta("new_capacity",0);n.set_meta("new_physical_fixtures",0);n.set_meta("operational_acceptance",false)
	for row in record.lights:
		var lens:MeshInstance3D=room.find_child(str(row.physical_lens_name),true,false);assert(lens!=null)
		var at:=Vector3(row.at[0],row.at[1],row.at[2]);assert((lens.global_transform*lens.get_aabb()).grow(.025).has_point(at),"Exact retained dining lens required")
		var light:=SpotLight3D.new();light.name=str(row.name);n.add_child(light);light.global_position=at;light.rotation.x=-PI/2;light.spot_range=float(row.range);light.spot_angle=float(row.angle);light.light_energy=float(row.energy);light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.visible=false;light.shadow_enabled=true
		light.set_meta("fixture_powered",true);light.set_meta("retained_physical_lens",str(row.physical_lens_name));light.set_meta("illumination_anchor",Vector3(row.aim[0],row.aim[1],row.aim[2]));light.set_meta("final_visual_acceptance",false)
		var budget:Node=ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
		if budget!=null:
			budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.shadow_enabled=false
	return n
