extends "res://tests/validate_living_gifts.gd"
func segment(ship:Node3D,cart:RigidBody3D,a:Vector2,b:Vector2,y:float,excluded:Array[RID]) -> void:
	var direction:Vector2=(b-a).normalized()
	var yaw:float=atan2(-direction.x,-direction.y)
	var steps:int=ceili(a.distance_to(b)/.1)
	for i in range(steps+1):
		var p:Vector2=a.lerp(b,float(i)/steps)
		driver_pose(ship,cart,Vector3(p.x,y+.03,p.y),yaw,excluded)
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	# Continuous poses with changing position AND heading, not a stationary spin.
	for level in [88.5,97.5]:
		segment(ship,cart,Vector2(84,12.65),Vector2(90.8,12.65),level,excluded)
		for i in range(41):
			var angle:float=PI/2*(1-float(i)/40)
			driver_pose(ship,cart,Vector3(90.8+1.5*cos(angle),level+.03,11.15+1.5*sin(angle)),-angle,excluded)
		segment(ship,cart,Vector2(92.3,11.15),Vector2(92.3,4.8),level,excluded)
		for i in range(41):
			var angle:float=-PI/2*float(i)/40
			driver_pose(ship,cart,Vector3(90.8+1.5*cos(angle),level+.03,4.8+1.5*sin(angle)),-angle,excluded)
		segment(ship,cart,Vector2(90.8,3.3),Vector2(90.5,3.3),level,excluded)
		for i in range(41):
			var angle:float=PI/2+PI/2*float(i)/40
			driver_pose(ship,cart,Vector3(90.5+1.5*cos(angle),level+.03,1.8+1.5*sin(angle)),PI-angle,excluded)
		segment(ship,cart,Vector2(89,1.8),Vector2(89,0),level,excluded)
	print("STARBOARD HOUSE CLEARANCE PASS:",samples,"changing-position cart/load and driver poses through the two east-stair perimeter returns. Geometric swept-route sampling only; force-driven steering, reverse flow and complete access network pending.")
	main.queue_free()
	await process_frame
	quit()
