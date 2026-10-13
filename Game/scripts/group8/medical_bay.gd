extends RefCounted
# Local surgical privacy construction and directional use of exact existing housings.
# No clinical operation,pressure,staff permissions or shared motion/backend changes.
static func build(ship:Node3D,room:Node3D)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/medical_bay.json"))
	assert(str(room.get_meta("programme_key"))==str(p.programme_key)and not room.has_node(str(p.root_name)))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.original_runtime_file))==str(p.original_runtime_sha256))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==str(p.model_sha256))
	var n:=Node3D.new();n.name=str(p.root_name);room.add_child(n);n.top_level=true;n.global_transform=Transform3D.IDENTITY
	n.set_meta("programme_key",str(p.programme_key));n.set_meta("new_capacity",0);n.set_meta("new_floor_owners",0);n.set_meta("new_shared_backends",0);n.set_meta("new_physical_light_fixtures",0);n.set_meta("clinical_pressure_operation_accepted",false)
	var visual:Node3D=(load("res://assets/models/"+str(p.model_file))as PackedScene).instantiate();n.add_child(visual)
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	var drivers:Dictionary={}
	for row in p.doors:
		var d:Node3D=load("res://scripts/group8/medical_privacy_door.gd").new();d.name=str(row.name);d.persistent_id=StringName(str(row.persistent_id));d.native_architecture=visual;d.binding=row;d.position=Vector3(row.at[0],row.at[1],row.at[2]);d.rotation.y=float(row.yaw);n.add_child(d)
		d.set_meta("programme_child",str(row.programme_child));d.set_meta("new_rigid_source_leaf_copy",true);drivers[str(row.name)]=d
	for row in p.control_targets:
		var marker:Node3D=visual.find_child(str(row.marker),true,false);assert(marker!=null)
		var d:Node3D=drivers[str(row.door_name)];var body:=StaticBody3D.new();body.name=str(row.side)+"PhysicalControl";d.add_child(body);body.position=d.global_transform.affine_inverse()*marker.global_position
		var shape:=BoxShape3D.new();shape.size=Vector3(row.size_door_local[0],row.size_door_local[1],row.size_door_local[2]);shape.margin=.001;var contact:=CollisionShape3D.new();contact.name="PreciseControlContact";contact.shape=shape;body.add_child(contact)
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for row in p.lights:
		var old:OmniLight3D=room.get_node(str(row.original_generic_name));assert(old.global_position.distance_to(Vector3(row.at[0],row.at[1],row.at[2]))<.001)
		# Preserve original intent nodes and their transforms,while retiring their generic emission.
		old.set_meta("fixture_powered",false);old.set_meta("group8_directional_successor",str(row.name));old.visible=false;old.shadow_enabled=false
		var light:=SpotLight3D.new();light.name=str(row.name);n.add_child(light);light.global_position=old.global_position;light.rotation.x=-PI/2;light.spot_range=float(row.range);light.spot_angle=float(row.angle);light.light_energy=float(row.energy);light.light_color=Color(row.colour[0],row.colour[1],row.colour[2]);light.visible=false;light.shadow_enabled=false
		light.set_meta("fixture_powered",true);light.set_meta("retained_physical_lens",str(row.physical_lens_name));light.set_meta("original_fixture_intent",str(row.original_generic_name));light.set_meta("clinical_operation_accepted",false)
		budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true
	budget.refresh()
	return n
