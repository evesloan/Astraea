extends RefCounted
static func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func visual(parent:Node3D,file:String,policy:Dictionary)->Node3D:
	var node:Node3D=load("res://assets/models/"+file).instantiate();parent.add_child(node)
	for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
		assert(policy.has(str(mesh.name)))
		var spec:Dictionary=policy[str(mesh.name)]
		if spec.role=="hospitality_glass":var mat:=ShaderMaterial.new();mat.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=mat
		if spec.category=="light_source":mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		if spec.collide:load("res://scripts/static_contact_cache.gd").attach(mesh)
	return node
static func build(ship:Node3D)->Node3D:
	var districts:Node3D=ship.get_node("ShipSpace/Districts")
	if districts.has_node("D04PortForwardFourthHomeCandidates"):return districts.get_node("D04PortForwardFourthHomeCandidates")
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_HOMES_FOURTH.json"))
	assert(p.rooms.size()==4 and p.all_twenty_allocations_unchanged.size()==20)
	var original:Node3D=districts.get_node("D04PortForwardNorthernReceiving")
	if p.open_room_entries:
		assert(FileAccess.get_sha256("res://artifacts/d04_port_forward_homes_fourth_sealed.json")==p.sealed_receipt_sha256)
		var gate:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://artifacts/d04_port_forward_homes_fourth_sealed.json"));assert(gate.status=="PASS"and gate.model_pins==p.model_pins)
		assert(FileAccess.get_sha256("res://assets/models/D04_PORT_FORWARD_NORTHERN_RECEIVING_r003.glb")==p.source_pins["Game/assets/models/D04_PORT_FORWARD_NORTHERN_RECEIVING_r003.glb"])
		for record in p.guard_preimages:
			var mesh:MeshInstance3D=original.find_child(str(record.name),true,false);assert(mesh!=null)
			var low:=Vector3(INF,INF,INF);var high:=-low
			for v in record.preimage.verts:low=low.min(vec(v));high=high.max(vec(v))
			var b:AABB=mesh.global_transform*mesh.get_aabb();assert(b.position.distance_to(low)<.00004 and b.end.distance_to(high)<.00004);mesh.free()
	var structure:=Node3D.new();structure.name="D04PortForwardFourthHomesStructure";districts.add_child(structure)
	assert(FileAccess.get_sha256("res://assets/models/"+str(p.structure.model_file))==p.structure.model_sha256)
	visual(structure,p.structure.model_file,p.structure.collision_policy);structure.set_meta("always_present_floor_support_and_courts",true);structure.set_meta("primary_load_accepted",false)
	if p.open_room_entries:
		assert(FileAccess.get_sha256("res://assets/models/"+str(p.entry_guard_successor.model_file))==p.entry_guard_successor.model_sha256)
		visual(structure,p.entry_guard_successor.model_file,p.entry_guard_successor.collision_policy)
	var homes:=Node3D.new();homes.name="D04PortForwardFourthHomeCandidates";districts.add_child(homes)
	homes.set_meta("house_id",p.house_id);homes.set_meta("new_guest_units",0);homes.set_meta("new_rest_places",0);homes.set_meta("physical_candidates",4);homes.set_meta("species_ready_rooms",0);homes.set_meta("total_house_reservation_count",20);homes.set_meta("capacity_preserved",25)
	for r in p.rooms:
		assert(FileAccess.get_sha256("res://assets/models/"+str(r.model_file))==r.model_sha256)
		var home:=Node3D.new();home.name=r.allocation.proposed_runtime_id;homes.add_child(home)
		home.set_meta("allocation_sha256",r.allocation.allocation_sha256);home.set_meta("rest_slot_ids",r.allocation.proposed_rest_slot_ids);home.set_meta("reserved_rest_count",1);home.set_meta("proposed_design_species",r.proposed_design_species);home.set_meta("species_ready",false);home.set_meta("historical_save_identity_recovered",false)
		ship.stream_private_visual(home,r.model_file,r.collision_policy)
		var door:Node3D=load("res://scripts/guest_entry_door.gd").new();door.name="HomeEntry";door.open_fraction=0.0;door.desired_open=false;door.persistent_id=StringName(r.entry.persistent_id);door.position=vec(r.entry.origin);door.rotation.y=float(r.entry.yaw);door.door_description="habitat entry";home.add_child(door)
		for j in range(r.lights.size()):
			var item:Dictionary=r.lights[j];var lamp:=SpotLight3D.new();lamp.name=item.name;home.add_child(lamp);lamp.position=vec(item.at);lamp.rotation.x=-PI/2;lamp.light_color=Color(1,.92,.81);lamp.light_energy=.8;lamp.spot_range=7;lamp.spot_angle=75;lamp.shadow_enabled=j==0
	homes.set_meta("physical_proposals_after_batch",14);homes.set_meta("remaining_interiors",6)
	return homes
