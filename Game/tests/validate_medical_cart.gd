extends "res://tests/medical_test_scene.gd"
# One initial D01 fixture. Afterwards the original cart/products move only through
# production physics, the existing lift and original tether. No later transforms.
var lift: Node3D
var probe=preload("res://tests/grand_pool_cart_probe.gd").new()
var product_ids: Array[String]=[]
var product_instances: Array[int]=[]
var driven_frames: int=0
var driven_metres: float=0
var turn_poses: int=0

func _initialize() -> void:
	test_name="medical_cart";call_deferred("run")

func product_state() -> bool:
	if not require(cart.products.size()==4,"Original four products required"): return false
	for i in range(4):
		var product: RigidBody3D=cart.products[i] as RigidBody3D
		if not require(product.get_instance_id()==product_instances[i] and str(product.get("persistent_id"))==product_ids[i],"Product identity changed"): return false
		var p: Vector3=cart.to_local(product.global_position)
		if not require(p.y>.78 and p.y<1.35 and absf(p.x)<.43 and absf(p.z)<.62,"A loose product left the tray"): return false
	return true

func settle(count: int) -> bool:
	actor.velocity=Vector3.ZERO
	for i in range(count):
		if not await advance(1,true): return false
		if not product_state(): return false
	return true

func drive_pose(center: Vector2,yaw: float) -> bool:
	probe.check_pose(ship,actor,cart,Vector3(center.x,21.03,center.y),yaw,21.0)
	if failed: return false
	var target: Vector3=Vector3(center.x,21,center.y)+Basis(Vector3.UP,yaw)*Vector3(0,0,1.62)
	actor.rotation.y=yaw;actor.set("pitch",0.0);actor.camera.rotation.x=0
	var reached: bool=false
	for frame in range(150):
		var delta: Vector3=target-actor.global_position;delta.y=0
		if delta.length()<.035: reached=true;break
		var velocity: Vector3=delta.limit_length(1.0/60.0)*60.0
		actor.velocity=Vector3(velocity.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60.0,velocity.z)
		var before: Vector3=actor.global_position;actor.move_and_slide()
		driven_metres+=Vector2(actor.global_position.x-before.x,actor.global_position.z-before.z).length()
		if not await advance(1,true): return false
		driven_frames+=1
		if not product_state(): return false
		if not require(cart.get("driver")==actor,"Original cart tether lost its operator"): return false
		if driven_frames%6==0:
			for wheel in probe.wheel_specs:
				var q: Array=wheel.center
				var point: Vector3=cart.global_transform*Vector3(float(q[0]),0,float(q[2]))
				probe.floor_at(space,point,21.0,exclusions(),"medical actual wheel")
			if failed: return false
	return require(reached,"Force-guided operator stalled toward "+str(target))

func line_to(endpoint: Vector2,yaw: float) -> bool:
	var start: Vector2=Vector2(cart.global_position.x,cart.global_position.z)
	var steps: int=maxi(1,ceili(start.distance_to(endpoint)/.08))
	for i in range(1,steps+1):
		if not await drive_pose(start.lerp(endpoint,float(i)/steps),yaw): return false
	if not await settle(75): return false
	return require(Vector2(cart.global_position.x,cart.global_position.z).distance_to(endpoint)<.65,"Physical cart missed line endpoint")

func turn_to(yaw: float) -> bool:
	var center: Vector2=Vector2(cart.global_position.x,cart.global_position.z)
	var from: float=cart.global_rotation.y
	var angle: float=wrapf(yaw-from,-PI,PI)
	var steps: int=maxi(1,ceili(absf(angle)/.035))
	for i in range(1,steps+1):
		if not await drive_pose(center,from+angle*float(i)/steps): return false
		turn_poses+=1
	return await settle(90)

func raw_e_handle(expected_held: bool) -> bool:
	release_inputs();actor.velocity=Vector3.ZERO;actor.set_physics_process(true)
	var handle: Node3D=cart.get_node("PhysicalCartHandle") as Node3D
	var delta: Vector3=handle.global_position-actor.camera.global_position
	actor.rotation.y=atan2(-delta.x,-delta.z)
	var pitch: float=atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.set("pitch",pitch);actor.camera.rotation.x=pitch
	if not is_instance_valid(cart.get("driver")) and not require(actor.call("target_from_view")==handle,"Regrip must target actual visible handle"): return false
	focus(true)
	if not await advance(2,true): return false
	key(KEY_E,true)
	if not await advance(2,true): return false
	key(KEY_E,false)
	if not await advance(2,true): return false
	focus(false)
	if not require(is_instance_valid(cart.get("driver"))==expected_held,"Original RMB/E handle state mismatch"): return false
	actor.set_physics_process(false)
	return await settle(45)

func exercise() -> bool:
	probe.failed.connect(func(message: String) -> void: require(false,"Physical cart preflight/support: "+message))
	lift=ship.find_child("ForwardPublicLift",true,false) as Node3D
	if not require(lift!=null,"Existing forward public lift required"): return false
	var offsets: Array[Vector3]=[]
	for product in cart.products:
		offsets.append(cart.to_local(product.global_position));product_ids.append(str(product.get("persistent_id")));product_instances.append(product.get_instance_id())
	# Sole initial fixture placement, at the existing D01 boarding approach.
	cart.position=Vector3(-3.8,.04,-438);cart.rotation=Vector3(0,-PI/2,0);cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*offsets[i];cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
	actor.position=Vector3(-5.42,.1,-438);actor.rotation.y=-PI/2;actor.set("pitch",0.0);actor.camera.rotation.x=0;actor.velocity=Vector3.ZERO
	if not await advance(60): return false
	cart.toggle_grab(actor);key(KEY_W,true)
	var boarded: bool=false
	for frame in range(450):
		if not await advance(1): return false
		if actor.position.x>=-1.58: boarded=true;break
	key(KEY_W,false)
	if not require(boarded,"Actual loaded D01 boarding stalled"): return false
	if not await advance(90): return false
	if not require(cart.global_position.x>-.4 and cart.global_position.x<.5,"Cart must be physically inside cabin"): return false
	cart.release_grab();key(KEY_W,true)
	for frame in range(90):
		if not await advance(1): return false
		if actor.position.x>=-1.05: break
	key(KEY_W,false)
	if not await advance(30): return false
	if not require(not lift.cabin_gate.threshold_occupied(),"Clear actual cabin gate before movement"): return false
	lift.request_floor(4)
	var arrived: bool=false
	for frame in range(3500):
		if not await advance(1): return false
		if lift.phase=="idle" and lift.current_floor==4: arrived=true;break
	if not require(arrived and absf(cart.global_position.y-21.0)<.12,"Actual loaded D05 arrival failed"): return false
	if not product_state(): return false
	key(KEY_S,true)
	for frame in range(120):
		if not await advance(1): return false
		if actor.position.x<=cart.position.x-1.58: break
	key(KEY_S,false);cart.toggle_grab(actor);key(KEY_S,true)
	var exited: bool=false
	for frame in range(550):
		if not await advance(1): return false
		if actor.position.x<=-6.85: exited=true;break
	key(KEY_S,false)
	if not require(exited,"Same loaded cart could not back onto D05 bypass"): return false
	if not await settle(75): return false
	actor.set_physics_process(false)
	# Small continuous operator poses drive the original force/torque tether;
	# cart/product transforms, velocity, ownership and collisions are never edited.
	if not await turn_to(PI): return false
	if not await line_to(Vector2(-5.3,-432),PI): return false
	if not await turn_to(PI/2): return false
	if not await line_to(Vector2(-11,-432),PI/2): return false
	if not await turn_to(0): return false
	if not await line_to(Vector2(-11,-446),0): return false
	if not await turn_to(PI/2): return false
	if not await line_to(Vector2(-23,-446),PI/2): return false
	if not await raw_e_handle(false): return false
	if not await raw_e_handle(true): return false
	if not await turn_to(-PI/2): return false
	if not await line_to(Vector2(-11,-446),-PI/2): return false
	if not await turn_to(PI): return false
	if not await line_to(Vector2(-11,-432),PI): return false
	if not await turn_to(-PI/2): return false
	if not await line_to(Vector2(-5.3,-432),-PI/2): return false
	if not await raw_e_handle(false): return false
	if not product_state(): return false
	metrics={"initial_fixture_placements":1,"later_cart_or_product_transform_writes":0,"loaded_D05_lift_arrivals":1,"force_guided_frames":driven_frames,"operator_metres":driven_metres,"gradual_turn_poses":turn_poses,"compound_clearance_poses":probe.sampled_poses,"wheel_operator_support_samples":probe.floor_rays,"unchanged_loose_product_identities":4,"original_RMB_E_release_regrip":true,"diagnostic_privacy_dogleg_cart_acceptance":false,"scope":"Scripted production-physics waiting route and return, not freehand comfort, clinical/robot fit or diagnostic cart access. Current bottle script has no fill model; no fill-conservation claim."}
	return true
