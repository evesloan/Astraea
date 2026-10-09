extends "res://tests/validate_botanical_receiving_access.gd"
# Independent bounded Nursery invocation. It does not skip or replace the full
# historical Botanical/Moss exercise, which retains its original frame cap.
func _initialize() -> void:
	test_name="botanical_nursery_access";call_deferred("run")

func write_receipt(status: String,detail: String="") -> void:
	metrics["initialization_wall_msec"]=pair_initialization_msec
	metrics["exercise_wall_msec"]=Time.get_ticks_msec()-started if started>0 else 0
	if receipt_path.is_empty(): return
	var out: Dictionary={"test":test_name,"status":status,"detail":detail,"metrics":metrics,"physics_frames":frames,"ordinary_walk_frames":walked_frames,"walked_metres":travelled_m,"support_samples":support_samples,"nursery_entry_crossings":nursery_entry_crossings,"seams_crossed":crossed_seams,"nursery_route_completed":nursery_route_completed,"pair_clearance_queries":pair_clearance_queries,"initial_verified_arrivals":1 if track_motion else 0,"later_teleports":0,"fixture_sha256":FileAccess.get_sha256(BOTANICAL_CONTRACT),"pair_geometry_runtime":pair_geometry_proof,"scope":"Separate actual ordinary-input Nursery six-metre court opening and four-metre source-throat entry/return. Complete Moss loop, retained guard bumps, Cloud and loaded carts are separate gates; no whole-room, visual or species acceptance."}
	var file:=FileAccess.open(receipt_path,FileAccess.WRITE)
	if file!=null: file.store_string(JSON.stringify(out,"  ")+"\n")

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
	var room: Dictionary=data.rooms.nursery
	built=ship.get_node(NodePath(str(data.guard_root))) as Node3D
	space=ship.get_world_3d().direct_space_state
	if not require(actor!=null and cart!=null and floors!=null and built!=null,"Actual Nursery player, loaded cart, guard and floors required"): return
	for body in built.find_children("*","StaticBody3D",true,false): guard_probe_exclusions.append(body.get_rid())
	if not pin_imports(): return
	loaded_proof=load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
	if not require(bool(loaded_proof.get("validation_completed",false)),"Complete predecessor/court runtime proof required"): return
	if not require(load("res://tests/botanical_pair_court_guard.gd").physical_validation_succeeded(),"Actual court and Moss physical successor validation did not finish"): return
	if not pair_runtime_geometry(): return
	if not require(actor.get_script().resource_path=="res://scripts/player.gd" and actor.gameplay_input_enabled,"Unchanged active production player required"): return
	var shapes: Array=actor.find_children("*","CollisionShape3D",true,false)
	if not require(shapes.size()==1 and shapes[0].shape is CapsuleShape3D and absf(shapes[0].shape.radius-.3)<.000001 and absf(shapes[0].shape.height-1.8)<.000001 and absf(actor.camera.position.y-1.65)<.000001,"Original capsule and eye height required"): return
	if not require(ship.arrive_at(Vector3(0,27.1,-216),0.0),"Initial supported Nursery arrival refused"): return
	if not await advance(45,false): return
	if not support_at(Vector3(0,27,-216),"D06_fore_route"): return
	track_motion=true
	if not pair_entry_checks(room): return
	if not await route([[0,-216],[6,-216]]): return
	if not await nursery_interior(): return
	if not await route([[0,-216]]): return
	if not require(nursery_route_completed and int(nursery_entry_crossings.out)>=1 and int(nursery_entry_crossings.back)>=1 and int(crossed_seams.get("starboard",0))>=2,"Actual Nursery room entry and supported court link must be crossed both ways"): return
	if failed: return
	release_inputs();write_receipt("PASS")
	print("BOTANICAL_NURSERY_ACCESS PASS: actual ordinary-input bounded Nursery source-throat entry/return and supported court link. Retained guard bumps, Moss, Cloud and carts have separate checks.")
	main.queue_free();await process_frame;quit(0)
