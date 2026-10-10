extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("D04PortForwardReceiving"):return districts.get_node("D04PortForwardReceiving")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_RECEIVING.json"))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==p.model_sha256)
	var root:=Node3D.new();root.name="D04PortForwardReceiving";districts.add_child(root)
	root.set_meta("house_id",p.house_id);root.set_meta("commons_programme_key",p.commons_programme_key)
	root.set_meta("new_guest_units",0);root.set_meta("new_rest_places",0);root.set_meta("rooms_adopted",0)
	root.set_meta("primary_load_accepted",false);root.set_meta("public_core_walls_unchanged",true)
	root.set_meta("staff_shaft_D04_D07_blank",true);root.set_meta("staff_gateway_adopted",p.open_staff_gateway)
	var visual:Node3D=load("res://assets/models/"+str(p.model_file)).instantiate();visual.name="ReceivedSourceGeometry";root.add_child(visual)
	var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		var extra:Dictionary=mesh.get_meta("extras",{})
		if extra.get("role","")=="hospitality_glass":mesh.material_override=glass
		if extra.get("runtime_collision",true):load("res://scripts/static_contact_cache.gd").attach(mesh)
		if not extra.get("runtime_visual",true):mesh.visible=false
	if p.open_staff_gateway:
		assert(p.has("sealed_stage_receipt_sha256"),"Staff wall remains sealed until receiving geometry passes")
		assert(FileAccess.get_sha256("res://artifacts/d04_port_forward_sealed.json")==p.sealed_stage_receipt_sha256)
		var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_port_forward_sealed.json"))
		assert(receipt.status=="PASS"and receipt.model_sha256==p.model_sha256)
		assert(FileAccess.get_sha256("res://assets/models/"+str(p.staff_wall_cut.source_model))==p.source_pins["Game/assets/models/"+str(p.staff_wall_cut.source_model)])
		assert(FileAccess.get_sha256("res://assets/models/"+str(p.staff_patch_model))==p.staff_patch_sha256)
		var old:Node3D=ship.find_child("LowerStaffEnclosure",true,false);assert(old!=null)
		for name in p.staff_wall_cut.meshes:
			var mesh:MeshInstance3D=old.find_child(str(name),true,false);assert(mesh!=null)
			var bounds:AABB=mesh.global_transform*mesh.get_aabb();var expected:Dictionary=p.wall_preimage_bounds[name]
			assert(bounds.position.distance_to(vec(expected.min))<.00005 and bounds.end.distance_to(vec(expected.max))<.00005)
			mesh.free()
		var patch:Node3D=load("res://assets/models/"+str(p.staff_patch_model)).instantiate();patch.name="BoundedStaffWallSuccessor";root.add_child(patch)
		for mesh:MeshInstance3D in patch.find_children("*","MeshInstance3D",true,false):load("res://scripts/static_contact_cache.gd").attach(mesh)
	var door:Node3D=load("res://scripts/guest_entry_door.gd").new();door.name="D03StaffReceivingDoor"
	door.persistent_id=StringName(p.staff_door.persistent_id);door.door_description="habitat staff door"
	door.position=vec(p.staff_door.origin);door.rotation.y=float(p.staff_door.yaw);door.desired_open=false;door.open_fraction=0;root.add_child(door)
	for item in p.lights:
		assert(visual.find_child(str(item.name),true,false)!=null)
		var light:=SpotLight3D.new();root.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2
		light.light_color=Color(1,.92,.81);light.light_energy=.9;light.spot_range=11;light.spot_angle=75;light.shadow_enabled=false
	return root
