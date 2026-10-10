extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("StarAtlasD17ReceivingFirst"):return districts.get_node("StarAtlasD17ReceivingFirst")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_D17_RECEIVING_FIRST.json"))
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.model_file))==p.model_sha256)
	var root:=Node3D.new();root.name="StarAtlasD17ReceivingFirst";districts.add_child(root)
	root.set_meta("source_connected_geometric_receiving",true);root.set_meta("primary_engineering_load_accepted",false)
	root.set_meta("new_guest_units",0);root.set_meta("new_rest_places",0);root.set_meta("first_room_adopted",false)
	var visual:Node3D=load("res://assets/models/"+str(p.model_file)).instantiate();root.add_child(visual)
	if p.open_gateway:
		assert(p.has("sealed_stage_receipt_sha256"),"Onward floor must be verified while the original wall remains sealed")
		assert(FileAccess.get_sha256("res://artifacts/d17_receiving_sealed.json")==p.sealed_stage_receipt_sha256)
		var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d17_receiving_sealed.json"))
		assert(receipt.status=="PASS"and receipt.model_sha256==p.model_sha256)
		var original:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_UPPER_COMMONS.json"))
		assert(FileAccess.get_sha256("res://assets/models/"+str(original.model_file))==original.model_sha256)
		for name in p.source_wall_replacements:
			var wall:MeshInstance3D=ship.find_child(str(name),true,false)
			assert(wall!=null and wall.get_meta("extras",{}).source_plan_sha256==original.plan_sha256)
			wall.free()
	var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader")
	for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
		var extra:Dictionary=mesh.get_meta("extras",{})
		if extra.category=="wall_replacement"and not p.open_gateway:
			mesh.free();continue
		if extra.role=="hospitality_glass":mesh.material_override=glass
		load("res://scripts/static_contact_cache.gd").attach(mesh)
	var door:Node3D=load("res://scripts/guest_entry_door.gd").new()
	door.name="StandardHouseReceivingDoor";door.persistent_id=StringName(p.commons_door.persistent_id)
	door.position=vec(p.commons_door.origin);door.rotation.y=float(p.commons_door.yaw)
	door.desired_open=false;door.open_fraction=0;root.add_child(door)
	root.set_meta("gateway_opening_adopted",p.open_gateway)
	# First823 remains a guarded reservation. Its fitted native entry is verified
	# separately before interior/support/garden adoption; no room is created here.
	for item in p.lights:
		var at:Vector3=vec(item.position)
		assert(visual.find_child(str(item.name),true,false)!=null)
		var light:=SpotLight3D.new();root.add_child(light);light.position=at;light.rotation.x=-PI/2
		light.light_color=Color(1,.91,.78);light.light_energy=.9;light.spot_range=7;light.spot_angle=75;light.shadow_enabled=false
	return root
