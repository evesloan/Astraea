extends "res://tests/validate_bridge_enclosure_access.gd"
# Existing compound cart/load/driver envelopes and real 1 m/s force-driven steering.
# Initial fixture placement is the only actor/cart/product translation assignment.
# Public path is735m each way; all driven legs total1937.4m (116244 straight
# simulation frames at1m/s). Predeclared180000-frame /900s real watchdog includes
# actual turns, on-foot door operation and settling; not a performance acceptance.
var cart_poses:Array[Vector3]=[]

func add_segment(a:Vector2,b:Vector2) -> void:
	var direction:Vector2=(b-a).normalized()
	var yaw:=atan2(-direction.x,-direction.y)
	if not cart_poses.is_empty():
		var previous:Vector3=cart_poses.back()
		assert(Vector2(previous.x,previous.y).distance_to(a)<.001)
		var turn:=wrapf(yaw-previous.z,-PI,PI)
		var turns:=maxi(1,ceili(absf(turn)/.04))
		for i in range(1,turns+1):cart_poses.append(Vector3(a.x,a.y,previous.z+turn*float(i)/turns))
	var count:=maxi(1,ceili(a.distance_to(b)/.1))
	for i in range(count+1):
		var p:=a.lerp(b,float(i)/count);cart_poses.append(Vector3(p.x,p.y,yaw))

func build_path(points:Array) -> void:
	cart_poses.clear()
	for i in range(points.size()-1):add_segment(points[i],points[i+1])

func check_load(cart:RigidBody3D) -> void:
	assert(cart.products.size()==4)
	for product in cart.products:
		var p:Vector3=cart.to_local(product.global_position)
		assert(p.y>.8 and p.y<1.3 and absf(p.x)<.4 and absf(p.z)<.6,"Four loose products must survive the complete bridge/public journey")

func drive(ship:Node3D,actor:CharacterBody3D,cart:RigidBody3D,route:Array[Vector3],excluded:Array[RID]) -> void:
	for pose in route:
		driver_pose(ship,cart,Vector3(pose.x,FLOOR+.03,pose.y),pose.z,excluded)
		var target:=Vector3(pose.x,FLOOR,pose.y)+Basis(Vector3.UP,pose.z)*Vector3(0,0,1.62)
		actor.rotation.y=pose.z
		var reached:=false
		for frame in range(90):
			var offset:Vector3=target-actor.position;offset.y=0
			if offset.length()<.025:reached=true;break
			var speed:=offset.limit_length(1.0/60)*60
			actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,speed.z)
			actor.move_and_slide();await physics_frame
			assert(cart.driver==actor and cart.global_basis.y.dot(Vector3.UP)>.90,"Loaded bridge cart must remain tethered and upright")
			assert(absf(cart.position.y-FLOOR)<.14 and absf(actor.position.y-FLOOR)<.14,"Cart and driver must stay supported on D18")
			if require_closed:assert_closed()
		assert(reached,"Bridge cart driver stalled at %s toward %s; cart %s"%[actor.position,target,cart.position])
	actor.velocity=Vector3.ZERO
	for frame in range(90):await physics_frame
	var end:Vector3=route.back()
	assert(Vector2(cart.position.x,cart.position.z).distance_to(Vector2(end.x,end.y))<.65,"Cart failed to follow the physical driver to its route endpoint")
	check_load(cart)

func operate_parked(ship:Node3D,actor:CharacterBody3D,cart:RigidBody3D,door:Node3D,side:float) -> void:
	cart.release_grab()
	var parked:Vector3=cart.global_position
	var driver_position:Vector2=Vector2(actor.position.x,actor.position.z)
	var driver_yaw:float=actor.rotation.y
	# Parked cart is ahead of its driver: walk around its side, never through it.
	var approach:Vector3=door.to_global(Vector3(0,0,side*2.0))
	await walk_route(actor,[Vector2(1.5,actor.position.z),Vector2(1.5,approach.z),Vector2(approach.x,approach.z)])
	await press(actor,door);assert(door.desired_open)
	await animate(ship,door);assert(door.open_fraction>.999)
	await walk_route(actor,[Vector2(1.5,approach.z),Vector2(1.5,driver_position.y),driver_position])
	assert(cart.global_position.distance_to(parked)<.20,"Parked cart moved during normal threshold operation")
	actor.rotation.y=driver_yaw;cart.toggle_grab(actor)
	assert(cart.driver==actor)

func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(150):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var enclosure:Node3D=ship.find_child("BridgeEnclosure_WIP",true,false)
	assert(enclosure!=null)
	var aft:Node3D=enclosure.get_node("BridgeEnclosureDoor_Aft")
	var fore:Node3D=enclosure.get_node("BridgeEnclosureDoor_Fore")
	bridge_doors.assign([aft,fore]);assert_closed()
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if body is RigidBody3D or body is CharacterBody3D:excluded.append(body.get_rid())
	var locals:Array[Vector3]=[]
	for product in cart.products:locals.append(cart.to_local(product.global_position))
	actor.set_physics_process(false)
	cart.position=Vector3(0,FLOOR+.04,-520);cart.rotation=Vector3(0,PI,0)
	cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*locals[i]
		cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
	actor.position=Vector3(0,FLOOR+.03,-521.62);actor.rotation.y=PI;actor.velocity=Vector3.ZERO
	for frame in range(90):await physics_frame
	check_load(cart);cart.toggle_grab(actor)
	require_closed=true
	build_path(PUBLIC_ROUTE)
	await drive(ship,actor,cart,cart_poses,excluded)
	var reversed:Array[Vector3]=cart_poses.duplicate();reversed.reverse()
	await drive(ship,actor,cart,reversed,excluded)
	require_closed=false
	build_path([Vector2(0,-520),Vector2(0,-177)])
	await drive(ship,actor,cart,cart_poses,excluded)
	assert_closed()
	await operate_parked(ship,actor,cart,fore,1.0)
	build_path([Vector2(0,-177),Vector2(0,-122.5)])
	await drive(ship,actor,cart,cart_poses,excluded)
	assert(not aft.desired_open and aft.open_fraction<.001)
	await operate_parked(ship,actor,cart,aft,-1.0)
	build_path([Vector2(0,-122.5),Vector2(0,-114.8)])
	await drive(ship,actor,cart,cart_poses,excluded)
	# Pull back continuously through both open thresholds, including their handles.
	build_path([Vector2(0,-177),Vector2(0,-114.8)])
	reversed=cart_poses.duplicate();reversed.reverse()
	await drive(ship,actor,cart,reversed,excluded)
	cart.release_grab();check_load(cart)
	print("BRIDGE ENCLOSURE CART PASS: ",samples," compound cart/load/operator poses; actual full Z-520 bypass, fore street and primary core/lift approach journey both ways with both bridge doors closed, then normal RMB/E opening and loaded passage through both thresholds both ways. Four loose products retained; scripted1m/s steering, not freehand or traffic acceptance.")
	main.queue_free();await process_frame;quit()
