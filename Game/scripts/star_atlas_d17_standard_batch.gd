extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func remove_preimage(owner:Node3D,p:Dictionary)->void:
	var mesh:MeshInstance3D=owner.find_child(p.name,true,false);assert(mesh!=null)
	var lo:=Vector3(INF,INF,INF);var hi:=-lo
	for v in p.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
	var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(lo)<.00005 and b.end.distance_to(hi)<.00005);mesh.free()
static func build(ship:Node3D,validation_only:bool=false)->Node3D:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/STAR_ATLAS_D17_STANDARD_BATCH.json"))
	if not p.active and not validation_only:return null
	var districts:Node3D=ship.get_node("ShipSpace/Districts");var name:String="StarAtlasD17StandardBatchValidation"if validation_only else"StarAtlasD17StandardBatch"
	if districts.has_node(name):return districts.get_node(name)
	for f in p.model_pins:assert(FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
	assert(FileAccess.get_sha256("res://artifacts/star_atlas_d17_standard_batch_native.json")==p.native_audit_sha256)
	assert(ship.find_child("StarAtlasD17Standard823",true,false)!=null)
	if not validation_only:
		assert(FileAccess.get_sha256("res://artifacts/star_atlas_d17_standard_batch_sealed.json")==p.sealed_receipt_sha256)
		assert(JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/star_atlas_d17_standard_batch_sealed.json")).status=="PASS")
		assert(FileAccess.get_sha256("res://assets/models/STAR_ATLAS_UPPER_COMMONS_r001.glb")==p.upper_commons_model_sha256)
		for record in p.north_wall_preimages:remove_preimage(ship,record)
	var prior:Node3D=ship.find_child("StarAtlasD17ReceivingFirst",true,false)
	assert(FileAccess.get_sha256("res://assets/models/STAR_ATLAS_D17_RECEIVING_FIRST_r001.glb")==p.source_pins["Game/assets/models/STAR_ATLAS_D17_RECEIVING_FIRST_r001.glb"])
	for record in p.aft_end_guard_preimages:remove_preimage(prior,record)
	var n:=Node3D.new();n.name=name;districts.add_child(n);n.set_meta("physical_standard_candidates",9);n.set_meta("port_central_standard_candidates_after_batch",10);n.set_meta("new_units",0);n.set_meta("new_rest_places",0);n.set_meta("species_ready_rooms",0);n.set_meta("primary_structural_capacity_accepted",false)
	var structure:Node3D=load("res://scripts/d04_port_forward_homes_fifth.gd").visual(n,p.structure_file,p.structure.collision_policy)
	if validation_only:
		for mesh:MeshInstance3D in structure.find_children("*","MeshInstance3D",true,false):
			if p.structure.collision_policy[str(mesh.name)].category=="wall_replacement":mesh.free()
	var door:Node3D=load("res://scripts/guest_entry_door.gd").new();door.name="ForeHouseReceivingDoor";door.persistent_id=StringName(p.north_gateway.persistent_id);door.position=vec(p.north_gateway.origin);door.rotation.y=p.north_gateway.yaw;door.desired_open=false;door.open_fraction=0;n.add_child(door)
	for r in p.rooms:
		assert(FileAccess.get_sha256("res://assets/models/"+str(r.source_model))==r.source_model_sha256)
		var home:=Node3D.new();home.name=r.allocation.proposed_runtime_id;home.position=vec(r.translation);n.add_child(home);home.set_meta("allocation_sha256",r.allocation.allocation_sha256);home.set_meta("rest_slot_ids",r.allocation.proposed_rest_slot_ids);home.set_meta("reserved_rest_count",2);home.set_meta("historical_save_identity_recovered",false);home.set_meta("species_ready",false)
		var room:Node3D=load("res://assets/models/"+str(r.source_model)).instantiate();room.name="RetainedFittedInterior";home.add_child(room);load("res://scripts/static_contact_cache.gd").attach_group(room,room.find_children("*","MeshInstance3D",true,false))
		for spec in [{"name":"HomeEntry","script":"guest_entry_door","at":Vector3(-63.175,102,35.6),"yaw":r.entry_yaw},{"name":"BathroomDoor","script":"guest_privacy_door","at":Vector3(-65.95,102,36.3),"yaw":r.bath_yaw}]:
			var fitting:Node3D=load("res://scripts/"+str(spec.script)+".gd").new();fitting.name=spec.name;fitting.persistent_id=StringName(str(r.allocation.proposed_runtime_id)+":"+str(spec.name));fitting.position=spec.at;fitting.rotation.y=spec.yaw;fitting.desired_open=false;fitting.open_fraction=0;home.add_child(fitting)
	for item in p.fixture_instances:
		var marker:Node3D=n.find_child(item.name+"__LightExit",true,false);assert(marker!=null)
		var light:=OmniLight3D.new();light.name=item.name+"__Light";n.add_child(light);light.global_position=marker.global_position;light.light_color=Color(item.color[0],item.color[1],item.color[2]);light.light_energy=item.energy;light.omni_range=item.range;light.visible=false;light.shadow_enabled=true;light.omni_shadow_mode=OmniLight3D.SHADOW_CUBE;light.shadow_bias=.03;light.shadow_normal_bias=.3;light.set_meta("fixture_powered",true);light.set_meta("source_fixture",item.name)
	for item in p.street_lights:
		assert(n.find_child(item.name,true,false)!=null);var light:=SpotLight3D.new();light.name=item.name+"__Light";n.add_child(light);light.position=vec(item.at);light.rotation.x=-PI/2;light.light_energy=item.energy;light.light_color=Color(1,.91,.78);light.spot_range=item.range;light.spot_angle=75;light.visible=false;light.shadow_enabled=true;light.set_meta("fixture_powered",true)
	return n
