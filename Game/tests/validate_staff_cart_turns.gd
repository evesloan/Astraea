extends SceneTree
var poses:Array[Vector3]=[]
func _initialize() -> void:call_deferred("run")
func line(a:Vector2,b:Vector2) -> void:
	var d:Vector2=(b-a).normalized()
	var yaw:float=atan2(-d.x,-d.y)
	var n:int=ceili(a.distance_to(b)/.1)
	for i in range(n+1):
		var p:Vector2=a.lerp(b,float(i)/n)
		poses.append(Vector3(p.x,p.y,yaw))
func run() -> void:
	line(Vector2(-21.4,-497),Vector2(-21.4,-500))
	for i in range(41):poses.append(Vector3(-21.4,-500,PI/2*i/40.0))
	line(Vector2(-21.4,-500),Vector2(-27,-500))
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var locals:Array[Vector3]=[]
	for product in cart.products:locals.append(cart.to_local(product.global_position))
	actor.set_physics_process(false)
	for level in [0.0,6.0,12.0]:
		cart.release_grab()
		cart.position=Vector3(-21.4,level+.04,-497)
		cart.rotation=Vector3.ZERO
		cart.linear_velocity=Vector3.ZERO
		cart.angular_velocity=Vector3.ZERO
		cart.sleeping=false
		for i in range(4):
			cart.products[i].global_position=cart.global_transform*locals[i]
			cart.products[i].linear_velocity=Vector3.ZERO
			cart.products[i].angular_velocity=Vector3.ZERO
			cart.products[i].sleeping=false
		actor.position=Vector3(-21.4,level+.03,-495.38)
		actor.rotation.y=0
		actor.velocity=Vector3.ZERO
		for frame in range(90):await physics_frame
		cart.toggle_grab(actor)
		for direction in [1,-1]:
			var route:Array[Vector3]=poses.duplicate()
			if direction<0:route.reverse()
			for pose in route:
				var target:Vector3=Vector3(pose.x,level,pose.y)+Basis(Vector3.UP,pose.z)*Vector3(0,0,1.62)
				actor.rotation.y=pose.z
				var reached:=false
				for frame in range(90):
					var offset:Vector3=target-actor.position
					offset.y=0
					if offset.length()<.025:
						reached=true
						break
					var speed:Vector3=offset.limit_length(1.0/60)*60
					actor.velocity=Vector3(speed.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,speed.z)
					actor.move_and_slide()
					await physics_frame
					assert(cart.driver==actor and cart.global_basis.y.dot(Vector3.UP)>.90,"Physical cart must remain tethered and upright through the turn")
					assert(abs(cart.position.y-level)<.14,"Cart must remain on the intended level")
				assert(reached,"Actual driver stalled at %s toward %s; cart %s"%[actor.position,target,cart.position])
			actor.velocity=Vector3.ZERO
			for frame in range(90):await physics_frame
			print("TURN END STATE:",cart.position," actor:",actor.position," rotation:",cart.rotation," driver yaw:",actor.rotation.y," grip:",cart.global_transform*cart.grip_local)
			var expected:Vector2=Vector2(-27,-500) if direction==1 else Vector2(-21.4,-497)
			assert(Vector2(cart.position.x,cart.position.z).distance_to(expected)<.65,"Physical cart must finish near the route endpoint")
			for product in cart.products:
				var p:Vector3=cart.to_local(product.global_position)
				assert(p.y>.8 and p.y<1.3 and abs(p.x)<.4 and abs(p.z)<.6,"Loose products must survive physical steering")
			print("PHYSICAL TURN LEVEL PASSED:",level," direction:",direction," cart:",cart.position)
	cart.release_grab()
	print("STAFF CART TURNS PASS: real capsule movement steers the force-tethered loaded cart forward and back through the first staff lobby corner on all three lower decks. Cart transforms are never set during travel. Scripted1m/s route only; freehand input feel and full network acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
