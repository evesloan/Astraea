extends "res://tests/validate_botanical_receiving_access.gd"
# Separate bounded gate per room. Exactly one initial fixture placement, then
# unchanged ordinary W/S input drives the original force tether and loose load.
# No actor.move_and_slide(), custom velocity driving or post-start transforms.
var cart_probe=preload("res://tests/grand_pool_cart_probe.gd").new()
var cart_room: Dictionary={}
var cart_room_key: String=""
var product_instances: Array[int]=[]
var product_ids: Array[String]=[]
var cart_crossings: Dictionary={"cart_out":0,"cart_back":0,"operator_out":0,"operator_back":0}
var cart_input_frames: int=0
var track_cart: bool=false
var initial_fixture_placed: bool=false
var cart_route_completed: bool=false

func _initialize() -> void:
	test_name="botanical_pair_cart";call_deferred("run")

func write_receipt(status: String,detail: String="") -> void:
	metrics["initialization_wall_msec"]=pair_initialization_msec
	metrics["exercise_wall_msec"]=Time.get_ticks_msec()-started if started>0 else 0
	metrics["cart_room"]=cart_room_key
	metrics["cart_crossings"]=cart_crossings
	metrics["cart_input_frames"]=cart_input_frames
	metrics["loaded_cart_route_completed"]=cart_route_completed
	metrics["initial_fixture_placements"]=1 if initial_fixture_placed else 0
	metrics["later_actor_cart_product_transform_writes"]=0
	metrics["initial_verified_arrivals"]=0
	metrics["cart_actual_pose_queries"]=cart_probe.sampled_poses
	metrics["scope"]="One-room actual four-loose-product cart W-input entry and S-input back-out through a source-open throat; no room turns, freehand comfort, remote lift transfer, species or whole-room acceptance."
	if receipt_path.is_empty(): return
	var out: Dictionary={"test":test_name,"status":status,"detail":detail,"physics_frames":frames,"support_samples":support_samples,"pair_clearance_queries":pair_clearance_queries,"initial_verified_arrivals":0,"initial_fixture_placements":1 if initial_fixture_placed else 0,"later_teleports":0,"fixture_sha256":FileAccess.get_sha256(BOTANICAL_CONTRACT),"pair_geometry_runtime":pair_geometry_proof,"metrics":metrics,"scope":metrics.scope}
	var file:=FileAccess.open(receipt_path,FileAccess.WRITE)
	if file!=null: file.store_string(JSON.stringify(out,"  ")+"\n")

func product_state() -> bool:
	if not require(cart.products.size()==4,"Original four loose products required"): return false
	for i in range(4):
		var product: RigidBody3D=cart.products[i] as RigidBody3D
		if not require(product.get_instance_id()==product_instances[i] and str(product.get("persistent_id"))==product_ids[i] and product.get_parent()==cart.get_parent(),"Loose product identity/ownership changed"): return false
		var p: Vector3=cart.to_local(product.global_position)
		if not require(p.is_finite() and p.y>.78 and p.y<1.35 and absf(p.x)<.43 and absf(p.z)<.62,"A loose product left the tray"): return false
	return true

func cart_support_and_pose() -> bool:
	if not require(cart.global_position.is_finite() and cart.global_basis.y.dot(Vector3.UP)>.98 and absf(cart.global_position.y-27)<.12,"Actual loaded cart tipped or left D06"): return false
	if not require(cart.get_script().resource_path=="res://scripts/cleaning_cart.gd" and cart.get_parent().name=="PersistentActors","Original persistent production cart required"): return false
	for wheel in cart_probe.wheel_specs:
		var q: Array=wheel.center
		var point: Vector3=cart.global_transform*Vector3(float(q[0]),0,float(q[2]))
		if not support_at(Vector3(point.x,27,point.z)): return false
	if not support_at(Vector3(actor.global_position.x,27,actor.global_position.z)): return false
	# The unchanged complete compound/load/operator probe excludes only controlled
	# bodies. Every real room, guard, neighbouring source and floor stays active.
	cart_probe.check_pose(ship,actor,cart,Vector3(cart.global_position.x,27.03,cart.global_position.z),cart.global_rotation.y,27)
	return not failed

func advance(count: int,check_d06_support: bool=false) -> bool:
	for frame in range(count):
		var previous_cart: Vector3=cart.global_position if is_instance_valid(cart) else Vector3.ZERO
		var previous_actor: Vector3=actor.global_position if is_instance_valid(actor) else Vector3.ZERO
		if not await super.advance(1,check_d06_support): return false
		if not track_cart: continue
		if not require(cart.global_position.distance_to(previous_cart)<.25,"Unexpected loaded-cart displacement; no recovery teleport permitted"): return false
		if not product_state(): return false
		for spec in [[previous_cart,cart.global_position,"cart"],[previous_actor,actor.global_position,"operator"]]:
			if spec[0].x<8 and spec[1].x>=8: cart_crossings[str(spec[2])+"_out"]+=1
			if spec[0].x>8 and spec[1].x<=8: cart_crossings[str(spec[2])+"_back"]+=1
		if not cart_support_and_pose(): return false
	return true

func raw_handle(expected_held: bool) -> bool:
	release_inputs()
	var handle: Node3D=cart.get_node("PhysicalCartHandle")
	var delta: Vector3=handle.global_position-actor.camera.global_position
	actor.rotation.y=atan2(-delta.x,-delta.z)
	var pitch: float=atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.set("pitch",pitch);actor.camera.rotation.x=pitch
	if not is_instance_valid(cart.get("driver")) and not require(actor.call("target_from_view")==handle,"Original visible cart handle must be targeted"): return false
	focus(true)
	if not await advance(2,true): return false
	key(KEY_E,true)
	if not await advance(2,true): return false
	key(KEY_E,false)
	if not await advance(2,true): return false
	focus(false)
	if not require(is_instance_valid(cart.get("driver"))==expected_held,"Original RMB/E handle state mismatch"): return false
	actor.rotation.y=-PI/2;actor.set("pitch",0.0);actor.camera.rotation.x=0
	return await advance(30,true)

func ordinary_cart_line(target_x: float) -> bool:
	release_inputs()
	actor.rotation.y=-PI/2;actor.set("pitch",0.0);actor.camera.rotation.x=0
	for frame in range(1800):
		var delta: float=target_x-actor.global_position.x
		var speed: float=Vector2(actor.velocity.x,actor.velocity.z).length()
		if absf(delta)<.16 and speed<.08:
			release_inputs()
			if not await advance(90,true): return false
			return require(absf(cart.global_position.x-(target_x+1.62))<.65,"Actual physical cart missed endpoint")
		var moving: bool=absf(delta)>maxf(.11,speed*speed/32+.035)
		key(KEY_W,moving and delta>0);key(KEY_S,moving and delta<0)
		if not await advance(1,true): return false
		cart_input_frames+=1
		if not require(cart.get("driver")==actor and actor.get("held_interaction")==cart.get("interaction_owner"),"Original production cart tether lost"): return false
		if not require(absf(cart.global_position.z-float(cart_room.center_z))<1.2,"Loaded cart left the bounded source-open centre route"): return false
	return require(false,"Ordinary cart W/S input stalled at "+str(actor.global_position))

func run() -> void:
	pair_initialization_started_msec=Time.get_ticks_msec()
	started=0 # Original exercise watchdog starts after synchronous main construction.
	for argument in OS.get_cmdline_user_args():
		if str(argument).begins_with("--botanical-cart-room="): cart_room_key=str(argument).trim_prefix("--botanical-cart-room=")
	receipt_path="res://artifacts/botanical_pair_cart_"+cart_room_key+"_attempt_"+str(Time.get_unix_time_from_system()).replace(".","_")+".json"
	if not require(cart_room_key in ["nursery","cloud"],"Choose one separate cart invocation: --botanical-cart-room=nursery or cloud"): return
	test_name="botanical_pair_cart_"+cart_room_key
	if not require(FileAccess.get_sha256(BOTANICAL_CONTRACT)==BOTANICAL_CONTRACT_SHA,"Exact botanical successor fixture required"): return
	data=JSON.parse_string(FileAccess.get_file_as_string(BOTANICAL_CONTRACT));cart_room=data.rooms[cart_room_key]
	for path in data.unchanged_input_sha256:
		if not require(FileAccess.get_sha256("res://"+str(path))==str(data.unchanged_input_sha256[path]),"Changed retained controller/contact input: "+str(path)): return
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
	built=ship.get_node(NodePath(str(data.guard_root if cart_room_key=="nursery" else cart_room.guard_root))) as Node3D
	space=ship.get_world_3d().direct_space_state
	if not require(actor!=null and cart!=null and floors!=null and built!=null,"Actual persistent original player/cart and D06 floors/guards required"): return
	cart_probe.failed.connect(func(message: String) -> void: require(false,"Actual loaded cart compound/support probe: "+message))
	if not pin_imports(): return
	loaded_proof=load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
	if not require(bool(loaded_proof.get("validation_completed",false)),"Complete medical/Moss/court chain required before loaded cart"): return
	if not require(load("res://tests/botanical_pair_court_guard.gd").physical_validation_succeeded(),"Actual court and Moss physical successor validation did not finish"): return
	if not pair_runtime_geometry(): return
	if not pair_entry_checks(cart_room): return
	if not require(actor.get_script().resource_path=="res://scripts/player.gd" and actor.gameplay_input_enabled,"Original active player required"): return
	var shapes: Array=actor.find_children("*","CollisionShape3D",true,false)
	if not require(shapes.size()==1 and shapes[0].shape is CapsuleShape3D and absf(shapes[0].shape.radius-.3)<.000001 and absf(shapes[0].shape.height-1.8)<.000001 and absf(actor.camera.position.y-1.65)<.000001,"Original cart operator capsule and eye height required"): return
	if not require(cart.products.size()==4 and not is_instance_valid(cart.get("driver")),"Initial original cart must be free and loaded"): return
	var offsets: Array[Vector3]=[]
	for product in cart.products:
		offsets.append(cart.to_local(product.global_position));product_instances.append(product.get_instance_id());product_ids.append(str(product.get("persistent_id")))
	# Sole initial bounded fixture placement; no later transform writes exist.
	cart.global_position=Vector3(.8,27.04,float(cart_room.center_z));cart.rotation=Vector3(0,-PI/2,0);cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*offsets[i];cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
	actor.global_position=Vector3(-.82,27.1,float(cart_room.center_z));actor.rotation.y=-PI/2;actor.set("pitch",0.0);actor.camera.rotation.x=0;actor.velocity=Vector3.ZERO
	initial_fixture_placed=true
	if not await advance(60,false): return
	if not product_state() or not cart_support_and_pose(): return
	track_motion=true;track_cart=true
	if not await raw_handle(true): return
	if not await ordinary_cart_line(12.38): return
	if not require(cart.global_position.x>13 and actor.global_position.x>12,"Loaded cart and operator must both actually enter the room"): return
	if not await raw_handle(false): return
	if not await raw_handle(true): return
	if not await ordinary_cart_line(-.82): return
	if not await raw_handle(false): return
	for count in cart_crossings.values():
		if not require(int(count)>=1,"Both actual cart and operator must cross X8 out/back"): return
	if not require(cart.global_position.x<2 and actor.global_position.x<1,"Actual loaded cart and operator must return to the retained axial floor"): return
	cart_route_completed=true
	if failed: return
	release_inputs();write_receipt("PASS")
	print(test_name.to_upper()," PASS: original four-loose-product cart ordinary W-entry/S-back-out, actual support/contact checks, RMB/E release and regrip. No room-turn acceptance.")
	main.queue_free();await process_frame;quit(0)
