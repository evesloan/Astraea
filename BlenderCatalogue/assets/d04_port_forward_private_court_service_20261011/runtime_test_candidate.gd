extends "res://tests/validate_d04_port_forward_commons_service.gd"
func run()->void:
	var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_FORWARD_PRIVATE_COURT_SERVICE_CANDIDATE.json"))
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");player.global_position=Vector3(-43.8,16.53,-331.7);player.velocity=Vector3.ZERO;player.set_controls_enabled(true)
	for i in range(15):await physics_frame
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	record("production_candidate_inactive",not p.production_active and ship.find_child("D04PrivateCourtServiceCandidate",true,false)==null)
	for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256("res://../"+str(f))==p.source_pins[f])
	for f in p.model_pins:record("model_pin_"+str(f),FileAccess.get_sha256("res://assets/models/"+str(f))==p.model_pins[f])
	# Exact preimages are verified before removal only in this test's scene.
	for row in p.preimages:
		var q:Dictionary=row.preimage;var mesh:MeshInstance3D=ship.find_child(str(q.name),true,false);record("preimage_present_"+str(q.name),mesh!=null)
		if mesh==null:continue
		var lo:=Vector3(INF,INF,INF);var hi:=-lo
		for v in q.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
		var b:AABB=mesh.global_transform*mesh.get_aabb();record("preimage_bounds_"+str(q.name),b.position.distance_to(lo)<.00004 and b.end.distance_to(hi)<.00004)
		mesh.free()
	var candidate:Node3D=load("res://assets/models/"+str(p.structure.model_file)).instantiate();candidate.name="D04PrivateCourtServiceCandidateTestOnly";ship.add_child(candidate)
	for mesh:MeshInstance3D in candidate.find_children("*","MeshInstance3D",true,false):
		var spec:Dictionary=p.structure.collision_policy[str(mesh.name)]
		if spec.collide:load("res://scripts/static_contact_cache.gd").attach(mesh)
	for i in range(5):await physics_frame
	for b in p.bridges:
		for x in [-28.6,-28.1,-27.6]:
			for z in [b.bounds[0][2]+.02,(b.bounds[0][2]+b.bounds[1][2])*.5,b.bounds[1][2]-.02]:
				var at:=Vector3(x,16.5,z);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("bridge_bearing_"+str(b.index)+"_"+str(x)+"_"+str(z),not h.is_empty() and str(h.collider.get_parent().name)=="D04PCS_LinkFloor_"+str(int(b.index)) and absf(h.position.y-16.5)<.002)
	for gate in p.gates:
		var at:=vec(gate.pivot)+Vector3(.6,1.0,0);var h:=ray(space,at+Vector3(0,0,.4),at-Vector3(0,0,.4));record("opaque_closed_gate_"+str(gate.name),not h.is_empty() and str(h.collider.get_parent().name)==str(gate.name))
		var hinge:=Node3D.new();candidate.add_child(hinge);hinge.global_position=vec(gate.pivot)
		for name in gate.members:candidate.find_child(str(name),true,false).reparent(hinge,true)
		hinge.rotation.y=deg_to_rad(float(gate.candidate_open_degrees))
	for i in range(5):await physics_frame
	var samples:=0
	for z in range(-4440,-4055,2):
		var at:=Vector3(-28.1,16.5,float(z)/10);var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02);record("continuous_candidate_floor_"+str(z),not h.is_empty() and absf(h.position.y-16.5)<.002);record("continuous_candidate_worker_"+str(z),capsule_clear(space,at));samples+=1
	for b in p.bridges:
		for x in [-28.65,-27.45]:
			for z in [b.bounds[0][2]-.2,b.bounds[1][2]+.2]:
				var at:=Vector3(x,16.26,z);var h:=ray(space,at-Vector3.UP*.02,at+Vector3.UP*.02);record("bearer_endpoint_contact_"+str(b.index)+"_"+str(x)+"_"+str(z),not h.is_empty() and absf(h.position.y-16.26)<.002)
	# One initial test placement; subsequent travel uses the original W controller.
	player.global_position=vec(p.worker_route[0])+Vector3.UP*.03;player.velocity=Vector3.ZERO
	for i in range(15):await physics_frame
	var walks:Array=[]
	for goal in p.worker_route.slice(1):
		var w:Dictionary=await walk_to(player,vec(goal));walks.append(w);record("candidate_actual_worker_walk_"+str(walks.size()),w.reached and w.floor_contact)
	var back:Dictionary=await walk_to(player,vec(p.worker_route[0]));walks.append(back);record("candidate_actual_worker_return",back.reached and back.floor_contact)
	var result:Dictionary={"status":"PASS"if errors.is_empty()else"FAIL","check_count":checks.size(),"checks":checks,"errors":errors,"worker_capsule_samples":samples,"candidate_player_walks":walks,"test_only_preimage_removal":true,"gate_open_pose_fixture_only":true,"production_active":false,"normal_gate_controls_accepted":false,"private_court_service_complete":false,"dedicated_clean_used_routes_accepted":false,"primary_load_accepted":false,"model_pins":p.model_pins}
	FileAccess.open("res://artifacts/d04_private_court_service_candidate.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors}));quit(0 if errors.is_empty()else 1)
