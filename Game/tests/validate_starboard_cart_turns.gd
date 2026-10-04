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
	line(Vector2(84,12.65),Vector2(90.8,12.65))
	for i in range(41):
		var a:float=PI/2*(1-float(i)/40)
		poses.append(Vector3(90.8+1.5*cos(a),11.15+1.5*sin(a),-a))
	line(Vector2(92.3,11.15),Vector2(92.3,4.8))
	for i in range(41):
		var a:float=-PI/2*float(i)/40
		poses.append(Vector3(90.8+1.5*cos(a),4.8+1.5*sin(a),-a))
	line(Vector2(90.8,3.3),Vector2(90.5,3.3))
	for i in range(41):
		var a:float=PI/2+PI/2*float(i)/40
		poses.append(Vector3(90.5+1.5*cos(a),1.8+1.5*sin(a),PI-a))
	line(Vector2(89,1.8),Vector2(89,0))
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var locals:Array[Vector3]=[]
	for product in cart.products:locals.append(cart.to_local(product.global_position))
	actor.set_physics_process(false)
	for level in [88.5,97.5]:
		cart.release_grab()
		cart.position=Vector3(84,level+.04,12.65)
		cart.rotation=Vector3(0,-PI/2,0)
		cart.linear_velocity=Vector3.ZERO
		cart.angular_velocity=Vector3.ZERO
		cart.sleeping=false
		for i in range(4):
			cart.products[i].global_position=cart.global_transform*locals[i]
			cart.products[i].linear_velocity=Vector3.ZERO
			cart.products[i].angular_velocity=Vector3.ZERO
			cart.products[i].sleeping=false
		actor.position=Vector3(82.38,level+.03,12.65)
		actor.rotation.y=-PI/2
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
			var expected:Vector2=Vector2(89,0) if direction==1 else Vector2(84,12.65)
			assert(Vector2(cart.position.x,cart.position.z).distance_to(expected)<.65,"Physical cart must finish near the route endpoint")
			for product in cart.products:
				var p:Vector3=cart.to_local(product.global_position)
				assert(p.y>.8 and p.y<1.3 and abs(p.x)<.4 and abs(p.z)<.6,"Loose products must survive physical steering")
			print("PHYSICAL TURN LEVEL PASSED:",level," direction:",direction," cart:",cart.position)
	cart.release_grab()
	print("STARBOARD CART TURNS PASS: real capsule movement steers the force-tethered loaded cart forward and back through both east-stair perimeter returns. Cart transforms are never set during travel. Scripted1m/s route only; freehand input feel and full network acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
