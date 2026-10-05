extends "res://tests/validate_aft_crown_platform_access.gd"
# Two continuous loaded circuits through both L-routes, one in each direction.
# Driven centreline length417.2m =>25032 straight frames at1m/s, plus six real
# heading changes per circuit. Predeclared100000 driven-frame /600s watchdog
# covers turns, on-foot opening and settling without relaxing speed or physics.
# Initial fixture placement below is the only cart/product/actor translation.
const MAX_DRIVEN_FRAMES := 100000
var driven_frames := 0
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

func build_path(points:Array,initial_yaw:float) -> void:
	cart_poses.clear()
	var start:Vector2=points.front()
	cart_poses.append(Vector3(start.x,start.y,initial_yaw))
	for i in range(points.size()-1):add_segment(points[i],points[i+1])

func check_load(cart:RigidBody3D) -> void:
	assert(cart.products.size()==4)
	for product in cart.products:
		var p:Vector3=cart.to_local(product.global_position)
		assert(p.y>.8 and p.y<1.3 and absf(p.x)<.4 and absf(p.z)<.6,"Four loose products must survive the complete aft staff circuit")

func drive(ship:Node3D,actor:CharacterBody3D,cart:RigidBody3D,excluded:Array[RID]) -> void:
	for pose in cart_poses:
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
			driven_frames+=1;assert(driven_frames<=MAX_DRIVEN_FRAMES,"Predeclared aft cart simulation budget exceeded")
			for door in bridge_doors:
				if not platform_doors.values().has(door):assert(not door.desired_open and door.open_fraction<.001,"Unrelated command doors remain closed during staff cart travel")
			assert(cart.driver==actor and cart.global_basis.y.dot(Vector3.UP)>.90,"Loaded aft cart must remain force-tethered and upright")
			assert(absf(cart.position.y-FLOOR)<.14 and absf(actor.position.y-FLOOR)<.14,"Cart and driver must stay supported on D18")
		assert(reached,"Aft cart driver stalled at %s toward %s; cart %s"%[actor.position,target,cart.position])
	actor.velocity=Vector3.ZERO
	for frame in range(90):await physics_frame
	var end:Vector3=cart_poses.back()
	assert(Vector2(cart.position.x,cart.position.z).distance_to(Vector2(end.x,end.y))<.65,"Force-tethered cart missed its actual route endpoint")
	check_load(cart)

func open_threshold(ship:Node3D,actor:CharacterBody3D,door:Node3D) -> void:
	assert(not door.desired_open and door.open_fraction<.001)
	await press(actor,door,false);assert(not door.desired_open,"Unfocused E must not open the staff threshold")
	await press(actor,door);assert(door.desired_open)
	await animate(ship,door);assert(door.open_fraction>.999)

func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(150):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	collect_platform_doors(ship);assert_closed()
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if body is RigidBody3D or body is CharacterBody3D:excluded.append(body.get_rid())
	var locals:Array[Vector3]=[]
	for product in cart.products:locals.append(cart.to_local(product.global_position))
	assert(locals.size()==4)
	actor.set_physics_process(false)
	cart.position=Vector3(-7.5,FLOOR+.04,98);cart.rotation=Vector3(0,PI,0)
	cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*locals[i]
		cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
	actor.position=Vector3(0,FLOOR+.03,95);actor.velocity=Vector3.ZERO
	for frame in range(90):await physics_frame
	check_load(cart)
	# Reach each door on foot via the actual public bypass; no remote interact calls.
	await walk_route(actor,[Vector2(0,108),Vector2(5.5,108),Vector2(5.5,137),Vector2(0,137),Vector2(0,145)])
	for side in [1.0,-1.0]:
		var prefix:String="port" if side<0 else "starboard"
		var terminal:Node3D=platform_doors[prefix+"_exit"]
		var corridor:Node3D=platform_doors[prefix+"_return"]
		await walk_route(actor,[Vector2(side*32,145)])
		await go_local(actor,terminal,2.0);await open_threshold(ship,actor,terminal)
		await walk_route(actor,[Vector2(side*32,104),Vector2(side*7.5,104)])
		await go_local(actor,corridor,2.0);await open_threshold(ship,actor,corridor)
		if side>0:
			await walk_route(actor,[Vector2(side*32,104),Vector2(side*32,145),Vector2(0,145)])
		else:
			await go_local(actor,corridor,-2.0)
			await walk_route(actor,[Vector2(-6,99.92),Vector2(-6,96.38),Vector2(-7.5,96.38)])
	actor.rotation.y=PI;cart.toggle_grab(actor);assert(cart.driver==actor)
	# Source-proven asymmetric turns: outwardZ104.2, inwardZ103.8/X31.8.
	# A naïve centrelineZ104 in-place turn clips the screened lane with the driver.
	var yaw:float=PI
	for side in [-1.0,1.0]:
		var route:Array=[Vector2(side*7.5,98),Vector2(side*7.5,104.2),Vector2(side*32,104.2),Vector2(side*32,146),Vector2(-side*31.8,146),Vector2(-side*31.8,103.8),Vector2(-side*7.5,103.8),Vector2(-side*7.5,98)]
		build_path(route,yaw)
		await drive(ship,actor,cart,excluded)
		yaw=cart_poses.back().z
	cart.release_grab();check_load(cart)
	print("AFT CROWN PLATFORM CART PASS: ",samples," compound cart/load/operator poses and ",driven_frames," actual1m/s driver frames; four shared doors opened by precise RMB/E, both screened staff L-routes physically driven both ways with tight asymmetric turns and four loose products retained. Scripted force tether only; freehand feel and traffic capacity remain pending.")
	main.queue_free();await process_frame;quit()
