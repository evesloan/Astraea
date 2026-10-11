extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func build(ship:Node3D,validation_only:bool=false)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_D17_STANDARD823.json"))
	if not p.active and not validation_only:return null
	var districts:Node3D=ship.get_node("ShipSpace/Districts");var name:String="StarAtlasD17Standard823Validation"if validation_only else"StarAtlasD17Standard823"
	if districts.has_node(name):return districts.get_node(name)
	for f in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.room_model))==p.room_model_sha256)
	assert(FileAccess.get_sha256("res://artifacts/star_atlas_d17_standard823_native.json")==p.native_audit_sha256)
	if not validation_only:
		assert(FileAccess.get_sha256("res://artifacts/star_atlas_d17_standard823_sealed.json")==p.sealed_receipt_sha256)
		assert(JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/star_atlas_d17_standard823_sealed.json")).status=="PASS")
	var prior:Node3D=ship.find_child("StarAtlasD17ReceivingFirst",true,false)
	assert(FileAccess.get_sha256("res://assets/models/STAR_ATLAS_D17_RECEIVING_FIRST_r001.glb")==p.source_pins["Game/assets/models/STAR_ATLAS_D17_RECEIVING_FIRST_r001.glb"])
	for record in p.guard_preimages:
		var mesh:MeshInstance3D=prior.find_child(record.name,true,false);assert(mesh!=null)
		var low:=Vector3(INF,INF,INF);var high:=-low
		for point in record.verts:low=low.min(vec(point));high=high.max(vec(point))
		var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(low)<.00004 and b.end.distance_to(high)<.00004);mesh.free()
	var n:=Node3D.new();n.name=name;districts.add_child(n);n.set_meta("new_guest_units",0);n.set_meta("new_rest_places",0);n.set_meta("primary_transfer_capacity_accepted",false);n.set_meta("species_ready",false);n.set_meta("historical_save_identity_recovered",false);n.set_meta("rest_slot_ids",p.room_preimage.allocation.proposed_rest_slot_ids);n.set_meta("allocation_sha256",p.room_preimage.allocation.allocation_sha256)
	load("res://scripts/d04_port_forward_homes_fifth.gd").visual(n,p.structure_file,p.structure.collision_policy)
	var room:Node3D=load("res://assets/models/"+str(p.room_model)).instantiate();room.name="RetainedStandard823Interior";n.add_child(room)
	load("res://scripts/static_contact_cache.gd").attach_group(room,room.find_children("*","MeshInstance3D",true,false))
	for spec in [{"name":"HomeEntry","script":"guest_entry_door","at":p.room_preimage.entry_origin,"yaw":p.room_preimage.entry_yaw},{"name":"BathroomDoor","script":"guest_privacy_door","at":p.room_preimage.bath_origin,"yaw":p.room_preimage.bath_yaw}]:
		var door:Node3D=load("res://scripts/"+str(spec.script)+".gd").new();door.name=spec.name;door.persistent_id=StringName(str(p.room_preimage.allocation.proposed_runtime_id)+":"+str(spec.name));door.position=vec(spec.at);door.rotation.y=spec.yaw;door.desired_open=false;door.open_fraction=0;n.add_child(door)
	for item in p.fixture_instances:
		var marker:Node3D=n.find_child(item.name+"__LightExit",true,false);assert(marker!=null)
		var lamp:=OmniLight3D.new();lamp.name=item.name+"__Light";n.add_child(lamp);lamp.global_position=marker.global_position;lamp.light_color=Color(item.color[0],item.color[1],item.color[2]);lamp.light_energy=item.energy;lamp.omni_range=item.range;lamp.visible=false;lamp.shadow_enabled=true;lamp.omni_shadow_mode=OmniLight3D.SHADOW_CUBE;lamp.shadow_bias=.03;lamp.shadow_normal_bias=.3;lamp.set_meta("fixture_powered",true);lamp.set_meta("source_fixture",item.name)
	return n
