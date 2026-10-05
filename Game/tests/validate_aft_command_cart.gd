extends "res://tests/validate_living_gifts.gd"
var poses:Array[Vector3]=[]
func line(a:Vector2,b:Vector2)->void:
	var d:Vector2=(b-a).normalized();var yaw:float=atan2(-d.x,-d.y);var n:=ceili(a.distance_to(b)/.1)
	for i in range(n+1):
		var p:=a.lerp(b,float(i)/n);poses.append(Vector3(p.x,p.y,yaw))
func run()->void:
	line(Vector2(-7.5,57),Vector2(-7.5,82))
	for i in range(41):poses.append(Vector3(-7.5,82,PI-PI/2*i/40.0))
	line(Vector2(-7.5,82),Vector2(-18,82))
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(150):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var central:Node3D=ship.find_child("CentralCommandCrown_WIP",true,false)
	var aft:Node3D=ship.find_child("AftCommandCrown_WIP",true,false)
	assert(central!=null and aft!=null)
	var doors:=central.find_children("CrownDoor_*","Node3D",true,false)
	doors.append_array(aft.find_children("AftCommandDoor_*","Node3D",true,false))
	assert(doors.size()==16)
	for door in doors:door.interact(actor)
	for frame in range(110):await physics_frame
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if body is RigidBody3D or body is CharacterBody3D:excluded.append(body.get_rid())
	for door in doors:
		assert(door.open_fraction>.999)
		for i in range(51):
			var p:Vector3=door.global_position+door.global_basis.z*(2.0-.1*i)+Vector3.UP*.03
			driver_pose(ship,cart,p,door.rotation.y,excluded)
	# Preserve the entire six-metre public aft belt as a physically supported cart street.
	for x in range(-44,45,2):
		for yaw in [PI/2,-PI/2]:driver_pose(ship,cart,Vector3(float(x),106.53,63),yaw,excluded)
	var locals:Array[Vector3]=[]
	for product in cart.products:locals.append(cart.to_local(product.global_position))
	actor.set_physics_process(false)
	cart.position=Vector3(-7.5,106.54,57);cart.rotation=Vector3(0,PI,0)
	cart.linear_velocity=Vector3.ZERO;cart.angular_velocity=Vector3.ZERO;cart.sleeping=false
	for i in range(4):
		cart.products[i].global_position=cart.global_transform*locals[i]
		cart.products[i].linear_velocity=Vector3.ZERO;cart.products[i].angular_velocity=Vector3.ZERO;cart.products[i].sleeping=false
	actor.position=Vector3(-7.5,106.53,55.38);actor.rotation.y=PI;actor.velocity=Vector3.ZERO
	for frame in range(90):await physics_frame
	cart.toggle_grab(actor)
	for direction in [1,-1]:
		var route:Array[Vector3]=poses.duplicate()
		if direction<0:route.reverse()
		for pose in route:
			var target:=Vector3(pose.x,106.5,pose.y)+Basis(Vector3.UP,pose.z)*Vector3(0,0,1.62)
			actor.rotation.y=pose.z
			var reached:=false
			for frame in range(90):
				var offset:Vector3=target-actor.position;offset.y=0
				if offset.length()<.025:reached=true;break
				var speed:=offset.limit_length(1.0/60)*60
				actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60,speed.z)
				actor.move_and_slide();await physics_frame
				assert(cart.driver==actor and cart.global_basis.y.dot(Vector3.UP)>.90,"Loaded crown cart remains tethered and upright")
				assert(absf(cart.position.y-106.5)<.14,"Crown cart remains supported on D18")
			assert(reached,"Crown driver stalled at %s toward %s; cart %s"%[actor.position,target,cart.position])
		actor.velocity=Vector3.ZERO
		for frame in range(90):await physics_frame
		var expected:=Vector2(-18,82) if direction==1 else Vector2(-7.5,57)
		assert(Vector2(cart.position.x,cart.position.z).distance_to(expected)<.65)
		for product in cart.products:
			var p:Vector3=cart.to_local(product.global_position)
			assert(p.y>.8 and p.y<1.3 and abs(p.x)<.4 and abs(p.z)<.6,"Four loose products survive crown doorway/turn traversal")
	cart.release_grab()
	print("AFT COMMAND CART PASS:",samples," compound cart/load/driver poses across all sixteen open command doors and revised public aft street; actual loaded forward/reverse trip from the old screened corridor, across the public street, through new controlled entry and a right-angle turn into Ship status. Scripted1m/s steering only; freehand feel and occupied-room capacity remain pending.")
	main.queue_free();await process_frame;quit()
