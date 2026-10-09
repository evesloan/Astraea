extends "res://tests/validate_botanical_receiving_access.gd"
var cloud_crossings: Dictionary={"link_out":0,"link_back":0,"entry_out":0,"entry_back":0}
var cloud_bumps: Array=[]
var cloud_route_completed: bool=false

func _initialize() -> void:
	test_name="botanical_cloud_access";call_deferred("run")

func write_receipt(status: String,detail: String="") -> void:
	metrics["initialization_wall_msec"]=pair_initialization_msec
	metrics["exercise_wall_msec"]=Time.get_ticks_msec()-started if started>0 else 0
	metrics["cloud_crossings"]=cloud_crossings
	metrics["cloud_actual_guard_bumps"]=cloud_bumps
	metrics["cloud_route_completed"]=cloud_route_completed
	metrics["cloud_initial_arrival_xyz"]=[0,27.1,-456]
	metrics["scope"]="Separate actual unchanged-player Cloud supported link, source throat and bounded entry/return; no whole-room, cart, species or visual acceptance."
	if receipt_path.is_empty(): return
	var out: Dictionary={"test":test_name,"status":status,"detail":detail,"physics_frames":frames,"ordinary_walk_frames":walked_frames,"walked_metres":travelled_m,"support_samples":support_samples,"guard_rays":guard_rays,"pair_clearance_queries":pair_clearance_queries,"initial_verified_arrivals":1 if track_motion else 0,"later_teleports":0,"fixture_sha256":FileAccess.get_sha256(BOTANICAL_CONTRACT),"pair_geometry_runtime":pair_geometry_proof,"metrics":metrics,"scope":metrics.scope}
	var file:=FileAccess.open(receipt_path,FileAccess.WRITE)
	if file!=null: file.store_string(JSON.stringify(out,"  ")+"\n")

func cloud_guard_bump(label: String,direction: Vector2) -> bool:
	release_inputs();actor.rotation.y=atan2(-direction.x,-direction.y)
	actor.set("pitch",0.0);actor.camera.rotation.x=0
	var touched: bool=false
	key(KEY_W,true)
	for frame in range(45):
		if not await advance(1,true): return false
		if not require(actor.global_position.x>4.3 and actor.global_position.x<7.7 and actor.global_position.z> -458.0 and actor.global_position.z< -454.0,"Player escaped Cloud supported link"): return false
		for i in range(actor.get_slide_collision_count()):
			var contact: KinematicCollision3D=actor.get_slide_collision(i)
			var body: Object=contact.get_collider()
			if body is Node and built.is_ancestor_of(body as Node) and absf(contact.get_normal().y)<.7: touched=true
	key(KEY_W,false)
	if not await advance(15,true): return false
	if not require(touched,"Actual Cloud guard bump missing: "+label): return false
	cloud_bumps.append(label)
	return true

func run() -> void:
	pair_initialization_started_msec=Time.get_ticks_msec()
	started=0 # Original exercise watchdog starts after synchronous main construction.
	receipt_path="res://artifacts/"+test_name+"_attempt_"+str(Time.get_unix_time_from_system()).replace(".","_")+".json"
	if not require(FileAccess.get_sha256(BOTANICAL_CONTRACT)==BOTANICAL_CONTRACT_SHA,"Exact botanical successor fixture required"): return
	data=JSON.parse_string(FileAccess.get_file_as_string(BOTANICAL_CONTRACT))
	for path in data.unchanged_input_sha256:
		if not require(FileAccess.get_sha256("res://"+str(path))==str(data.unchanged_input_sha256[path]),"Changed retained input: "+str(path)): return
	if not pair_source_preflight(): return
	main=(load("res://scenes/main.tscn") as PackedScene).instantiate();root.add_child(main)
	pair_initialization_msec=Time.get_ticks_msec()-pair_initialization_started_msec
	started=Time.get_ticks_msec()
	print("BOTANICAL_MAIN_READY initialization_msec=",pair_initialization_msec," exercise_watchdog_msec=480000")
	for frame in range(150): await physics_frame
	ship=main.get_node("World360/Astraea") as Node3D
	actor=ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	cart=ship.find_child("CustodialCart",true,false) as RigidBody3D
	floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	var room: Dictionary=data.rooms.cloud
	built=ship.get_node(NodePath(str(room.guard_root))) as Node3D
	space=ship.get_world_3d().direct_space_state
	if not require(actor!=null and cart!=null and floors!=null and built!=null,"Actual Cloud player, loaded cart, guard and floors required"): return
	for body in built.find_children("*","StaticBody3D",true,false): guard_probe_exclusions.append(body.get_rid())
	if not pin_imports(): return
	loaded_proof=load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
	if not require(bool(loaded_proof.get("validation_completed",false)),"Complete predecessor/court runtime proof required"): return
	if not require(load("res://tests/botanical_pair_court_guard.gd").physical_validation_succeeded(),"Actual court and Moss physical successor validation did not finish"): return
	if not pair_runtime_geometry(): return
	if not require(actor.get_script().resource_path=="res://scripts/player.gd" and actor.gameplay_input_enabled,"Unchanged active production player required"): return
	var shapes: Array=actor.find_children("*","CollisionShape3D",true,false)
	if not require(shapes.size()==1 and shapes[0].shape is CapsuleShape3D and absf(shapes[0].shape.radius-.3)<.000001 and absf(shapes[0].shape.height-1.8)<.000001 and absf(actor.camera.position.y-1.65)<.000001,"Original capsule and eye height required"): return
	if not require(ship.arrive_at(xyz(room.initial_arrival_xyz),0.0),"Initial supported Cloud arrival refused"): return
	if not await advance(45,false): return
	if not support_at(Vector3(0,27,-456),"D06_fore_route"): return
	track_motion=true
	if not pair_entry_checks(room): return
	for x in [4.1,5.0,6.0,7.0,7.9]:
		for sign in [-1,1]:
			for y in [27.10,27.4,28.0,28.1]:
				if not guard_contact(Vector3(float(x),float(y),-456+float(sign)*1.8),Vector3(float(x),float(y),-456+float(sign)*2.3),"Cloud continuous side guard"): return
	for point in room.entry_return_route:
		var before: Vector3=actor.global_position
		if not await walk(Vector2(float(point[0]),float(point[1]))): return
		var after: Vector3=actor.global_position
		for spec in [[4,"link"],[8,"entry"]]:
			if before.x<float(spec[0]) and after.x>=float(spec[0]): cloud_crossings[str(spec[1])+"_out"]+=1
			if before.x>float(spec[0]) and after.x<=float(spec[0]): cloud_crossings[str(spec[1])+"_back"]+=1
		if after.x>8 and not support_at(Vector3(after.x,27,after.z),str(room.floor_owner)): return
	if not await route([[6,-456],[6,-457.5]]): return
	if not await cloud_guard_bump("Cloud forward side",Vector2(0,-1)): return
	if not await route([[6,-456],[6,-454.5]]): return
	if not await cloud_guard_bump("Cloud aft side",Vector2(0,1)): return
	if not await route([[6,-456],[0,-456]]): return
	for count in cloud_crossings.values():
		if not require(int(count)>=1,"Cloud link and actual entry must be crossed both ways"): return
	if not require(cloud_bumps.size()==2,"Both actual Cloud side guards must stop the unchanged capsule"): return
	cloud_route_completed=true
	if failed: return
	release_inputs();write_receipt("PASS")
	print("BOTANICAL_CLOUD_ACCESS PASS: actual ordinary-input bounded Cloud entry/return and both guard bumps. Separate cart and whole-room gates.")
	main.queue_free();await process_frame;quit(0)
