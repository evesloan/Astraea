extends "res://tests/validate_d04_port_forward_commons_service.gd"
func model(parent:Node3D,spec:Dictionary)->Node3D:
	var node:Node3D=load("res://assets/models/"+str(spec.model_file)).instantiate();parent.add_child(node)
	for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
		var item:Dictionary=spec.collision_policy[str(mesh.name)]
		if item.collide:load("res://scripts/static_contact_cache.gd").attach(mesh)
		if item.category=="stair_walk_surface":mesh.visible=false
	return node
func key_e()->void:
	var event:=InputEventKey.new();event.keycode=KEY_E;event.physical_keycode=KEY_E;event.pressed=true;Input.parse_input_event(event);await physics_frame;event.pressed=false;Input.parse_input_event(event)
	for i in range(3):await physics_frame
func aim(player:CharacterBody3D,at:Vector3)->void:
	var d:Vector3=at-player.camera.global_position;player.rotation.y=atan2(-d.x,-d.z);player.camera.rotation.x=atan2(d.y,Vector2(d.x,d.z).length())
	var event:=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=true;Input.parse_input_event(event)
	for i in range(4):await physics_frame
func pose_checks(space:PhysicsDirectSpaceState3D,gate:Node3D,spec:Dictionary,label:String)->void:
	var leaf:AnimatableBody3D=gate.leaves[0];record(label+"_hinge_origin",leaf.global_position.distance_to(vec(spec.pivot))<.00004)
	var q:=PhysicsShapeQueryParameters3D.new();var box:=BoxShape3D.new();box.size=Vector3(1.196,2.696,.056);box.margin=.0001;q.shape=box;q.transform=leaf.global_transform*Transform3D(Basis.IDENTITY,Vector3(.6,1.35,float(spec.closed_plane_center_z)-float(spec.pivot[2])));q.exclude=[leaf.get_rid()]
	var hits:=space.intersect_shape(q,64);record(label+"_moving_leaf_clear",hits.is_empty());if not hits.is_empty():print("LEAF_CONTACT ",label," ",hits)
func run()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STAFF_COURT_APPROACH_SEALED.json"));var old:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_PRIVATE_COURT_SERVICE_CANDIDATE.json"))
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-43.8,16.53,-331.7);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
	for i in range(15):await physics_frame
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256("res://../"+str(f))==p.source_pins[f])
	for f in p.model_pins:record("model_pin_"+str(f),FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
	record("production_inactive",not p.production_active and ship.find_child("D04StaffCourtApproachCandidate",true,false)==null)
	var owner:=Node3D.new();owner.name="D04StaffCourtApproachCandidateTestOnly";ship.add_child(owner);var staff:Node3D=model(owner,p.structure)
	for i in range(5):await physics_frame
	for lane in p.lanes:
		for x in range(-530,-339,5):
			var at:=Vector3(float(x)/10,12,float(lane.center_z));var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("lane_floor_"+str(lane.purpose)+"_"+str(x),not h.is_empty() and str(h.collider.get_parent().name)=="D03_protected_crew_cover" and absf(h.position.y-12)<.002);record("lane_worker_"+str(lane.purpose)+"_"+str(x),capsule_clear(space,at));record("lane_cart_shape_"+str(lane.purpose)+"_"+str(x),cart_clear(space,at,PI/2))
	var lane_walks:Array=[]
	for lane in p.lanes:
		var first:=Vector3(-53,12,float(lane.center_z));player.global_position=first+Vector3.UP*.03;player.velocity=Vector3.ZERO
		for i in range(15):await physics_frame
		for goal in [Vector3(-34,12,float(lane.center_z)),first]:
			var w:Dictionary=await walk_to(player,goal);lane_walks.append(w);record("actual_lane_walk_"+str(lane_walks.size()),w.reached and w.floor_contact)
	player.global_position=Vector3(-31.75,12.03,-446.8);player.velocity=Vector3.ZERO
	for i in range(15):await physics_frame
	var stair_walks:Array=[]
	for goal in [Vector3(-31.75,14.25,-455.4),Vector3(-31.75,14.25,-456.3),Vector3(-28.25,14.25,-456.3),Vector3(-28.25,16.5,-447.2),Vector3(-28.25,16.5,-445.75)]:
		var w:Dictionary=await walk_to(player,goal);stair_walks.append(w);record("actual_stair_walk_"+str(stair_walks.size()),w.reached and w.floor_contact)
	record("south_court_threshold_still_sealed",ship.find_child("D04HC3_east_End_0",true,false)!=null)
	# The already retained court preimages are removed only in this test scene.
	for r in old.preimages:
		var mesh:MeshInstance3D=ship.find_child(str(r.preimage.name),true,false);record("retained_preimage_"+str(r.preimage.name),mesh!=null)
		if mesh!=null:mesh.free()
	var court:Node3D=model(owner,p.court_candidate_model);var controls:Array=[]
	for i in range(p.gates.size()):
		var gate:Node3D=load("res://scripts/d04_court_service_gate.gd").new();gate.name="ServiceGate_"+str(i);gate.persistent_id=StringName("D04_southern_east_court_service_gate_"+str(i));gate.authored_visual=court;gate.fitting=p.gates[i];gate.custodian=weakref(player);owner.add_child(gate);controls.append(gate)
	for i in range(5):await physics_frame
	var operations:Array=[];var egress_walks:Array=[]
	for j in range(controls.size()):
		var gate:Node3D=controls[j];var spec:Dictionary=p.gates[j];var stance:=Vector3(-28.1,16.5,float(spec.pivot[2])+1.9);player.global_position=stance+Vector3.UP*.03;player.velocity=Vector3.ZERO
		for i in range(15):await physics_frame
		await aim(player,vec(spec.control_at));record("normal_target_"+str(j),player.interaction_target==gate)
		await key_e();record("unknown_visit_denied_"+str(j),not gate.desired_open and gate.open_fraction==0)
		var visit:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();visit.actor=weakref(player);visit.request_id=&"temporary_validation_visit";visit.court_ids.assign([gate.persistent_id]);visit.active=true;visit.consent_known=true;visit.consent_allowed=false;gate.visit=visit
		await key_e();record("refused_visit_denied_"+str(j),not gate.desired_open)
		visit.consent_allowed=true;var stranger:=CharacterBody3D.new();owner.add_child(stranger);gate.interact(stranger);record("other_actor_denied_"+str(j),not gate.desired_open);stranger.free()
		if j==0:
			var crowded:Array=[]
			for i in range(64):
				var body:=StaticBody3D.new();var contact:=CollisionShape3D.new();var small:=BoxShape3D.new();small.size=Vector3(.02,.02,.02);contact.shape=small;body.add_child(contact);owner.add_child(body);body.global_position=vec(spec.pivot)+Vector3(.6,1,-.6);crowded.append(body)
			for i in range(3):await physics_frame
			await key_e();record("saturated_guard_query_fails_closed",gate.obstructed and not gate.desired_open)
			for body in crowded:body.free()
			for i in range(3):await physics_frame
		var blocker:=RigidBody3D.new();blocker.freeze=true;var col:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=Vector3(.25,.25,.25);col.shape=shape;blocker.add_child(col);owner.add_child(blocker);var direction:float=-1 if spec.candidate_open_degrees>0 else 1;blocker.global_position=vec(spec.pivot)+Vector3(.6,1,direction*.6)
		for i in range(3):await physics_frame
		await key_e();record("load_blocks_open_"+str(j),gate.obstructed and not gate.desired_open);blocker.free()
		for i in range(3):await physics_frame
		record("removed_load_clears_prompt_"+str(j),not gate.obstructed)
		await key_e()
		for i in range(20):await physics_frame
		visit.active=false
		for i in range(100):await physics_frame
		record("revoked_mid_open_returns_closed_"+str(j),not gate.desired_open and gate.open_fraction<.001);visit.active=true
		await key_e()
		for i in range(100):
			await physics_frame
			if i%10==0:pose_checks(space,gate,spec,"opening_"+str(j)+"_"+str(i))
		record("normal_RMB_E_open_"+str(j),gate.desired_open and gate.open_fraction>.999)
		var worker:=CharacterBody3D.new();var c:=CollisionShape3D.new();var capsule:=CapsuleShape3D.new();capsule.radius=.3;capsule.height=1.8;c.shape=capsule;worker.add_child(c);owner.add_child(worker);worker.global_position=vec(spec.pivot)+Vector3(.6,1,direction*.6)
		for i in range(3):await physics_frame
		visit.active=false;await key_e();record("revoked_visit_worker_blocks_close_"+str(j),gate.obstructed and gate.desired_open);worker.free()
		for i in range(3):await physics_frame
		await key_e()
		for i in range(100):
			await physics_frame
			if i%10==0:pose_checks(space,gate,spec,"closing_"+str(j)+"_"+str(i))
		record("revoked_worker_can_close_"+str(j),not gate.desired_open and gate.open_fraction<.001);await key_e();record("revoked_visit_cannot_reopen_"+str(j),not gate.desired_open)
		visit.active=true;await key_e()
		for i in range(100):await physics_frame
		var inside:=Vector3(-28.1,16.5,float(spec.closed_plane_center_z)-1.2);var incoming:Dictionary=await walk_to(player,inside);egress_walks.append(incoming);record("authorized_worker_enters_"+str(j),incoming.reached and incoming.floor_contact);visit.active=false
		await aim(player,vec(spec.inner_control_at));record("inside_fixed_frame_target_"+str(j),player.interaction_target==gate);await key_e()
		for i in range(100):await physics_frame
		record("inside_revoked_worker_closes_"+str(j),not gate.desired_open and gate.open_fraction<.001);await key_e()
		for i in range(100):await physics_frame
		record("inside_revoked_worker_can_exit_"+str(j),gate.desired_open and gate.open_fraction>.999);var leaving:Dictionary=await walk_to(player,stance);egress_walks.append(leaving);record("actual_revoked_worker_egress_"+str(j),leaving.reached and leaving.floor_contact)
		await aim(player,vec(spec.control_at));await key_e()
		for i in range(100):await physics_frame
		await key_e();record("outside_revoked_worker_denied_again_"+str(j),not gate.desired_open and gate.open_fraction<.001)
		operations.append({"gate":str(gate.persistent_id),"normal_RMB_E_open_close":checks["normal_RMB_E_open_"+str(j)] and checks["revoked_worker_can_close_"+str(j)],"unknown_refused_other_actor_revoked_denied":checks["outside_revoked_worker_denied_again_"+str(j)],"worker_load_guards":checks["load_blocks_open_"+str(j)] and checks["revoked_visit_worker_blocks_close_"+str(j)]})
	var result:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","check_count":checks.size(),"checks":checks,"errors":errors,"lane_walks":lane_walks,"stair_walks":stair_walks,"egress_walks":egress_walks,"gate_operations":operations,"gate_motion_samples":60,"production_active":false,"test_only_temporary_visit":true,"staff_wall_and_court_south_junctions_held":true,"loaded_cart_and_vertical_acceptance":false,"guest_occupancy_save_or_authorization_implemented":false,"model_pins":p.model_pins}
	FileAccess.open("res://artifacts/d04_court_controls_staff_candidate.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
