extends RefCounted
# Three local dining service belts; original source-room streamer owns lifecycle.
static func build(ship:Node3D,room:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_service.json"));var key:=str(room.get_meta("programme_key"))
	assert(p.programme_keys.has(key)and not room.has_node(str(p.root_name)))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.retained_contracts[key].runtime_file))==str(p.retained_contracts[key].runtime_sha256))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==str(p.model_sha256))
	assert(FileAccess.get_sha256("res://assets/models/AST-STF-008.glb")==str(p.retained_standard_door_source.runtime_sha256))
	var root:=Node3D.new();root.name=str(p.root_name);room.add_child(root);root.top_level=true;root.global_transform=Transform3D.IDENTITY
	root.set_meta("programme_key",key);root.set_meta("new_capacity",0);root.set_meta("new_floor_owners",0);root.set_meta("new_shared_backends",0);root.set_meta("food_hygiene_species_pressure_engineering_final_art_accepted",false)
	var visual:Node3D=(load("res://assets/models/"+str(p.model_file))as PackedScene).instantiate();root.add_child(visual);var keep:Dictionary={}
	for row in p.runtime_batches:
		if str(row.programme_key)==key:keep[str(row.name)]=row
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		if not keep.has(str(mesh.name)):mesh.free();continue
		if bool(keep[str(mesh.name)].collide):load("res://scripts/static_contact_cache.gd").attach(mesh)
	for row in p.doors:
		if str(row.programme_key)!=key:continue
		var marker:Node3D=visual.find_child(str(row.marker),true,false);assert(marker!=null)
		var d:Node3D=load("res://scripts/service_door.gd").new();d.name=str(row.name);d.persistent_id=StringName(str(row.persistent_id));d.position=marker.global_position;d.rotation.y=float(row.yaw);d.scale=Vector3(row.scale[0],row.scale[1],row.scale[2]);root.add_child(d)
		d.set_meta("programme_key",key);d.set_meta("source_instance_scale",row.scale);d.set_meta("new_authored_local_utility_instance",true)
	for row in p.lights:
		if str(row.programme_key)!=key:continue
		var marker:Node3D=visual.find_child(str(row.name),true,false);assert(marker!=null)
		var light:=SpotLight3D.new();light.name=str(row.name);root.add_child(light);light.global_position=marker.global_position;light.look_at(Vector3(row.aim[0],row.aim[1],row.aim[2]),Vector3.FORWARD if absf((Vector3(row.aim[0],row.aim[1],row.aim[2])-light.global_position).normalized().dot(Vector3.UP))>.95 else Vector3.UP)
		light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.light_energy=float(row.energy);light.spot_range=float(row.range);light.spot_angle=float(row.spot_angle);light.shadow_enabled=true;light.set_meta("fixture_powered",true)
		var budget:Node=ship.get_node_or_null("ShipSystems/LocalShadowSourceBudget")
		if budget!=null:budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.visible=false;light.shadow_enabled=false
	return root
