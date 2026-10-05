extends "res://tests/validate_living_gifts.gd"
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var network:Node3D=ship.find_child("LowerStaffNetwork_WIP",true,false)
	var lights:=network.find_children("StaffRouteLight_*","Light3D",true,false)
	assert(lights.size()==99,"All exact source fixture anchors must reach runtime")
	for light in lights:
		var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.04)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Staff fixture emitter exit blocked")
	for sign in network.find_children("StaffDeckSign_*","Label3D",true,false):
		var ray:=PhysicsRayQueryParameters3D.create(sign.global_position,sign.global_position+Vector3.RIGHT*.3)
		assert(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Staff sign requires actual wall backing")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	for level in [0.0,6.0,12.0]:
		for corner in [Vector3(-21.4,-500,0),Vector3(-57,-499.6,PI/2)]:
			for i in range(41):driver_pose(ship,cart,Vector3(corner.x,level+.03,corner.y),corner.z+PI/2*i/40.0,excluded)
		var end_z:float=-60 if level==0 else (-432 if level==6 else -216)
		for i in range(41):driver_pose(ship,cart,Vector3(-56.6,level+.03,end_z),PI+PI/2*i/40.0,excluded)
		for z in range(-495,int(end_z)-3,4):
			for yaw in [0.0,PI]:driver_pose(ship,cart,Vector3(-57,level+.03,float(z)),yaw,excluded)
		for x in range(-53,-25,2):
			for yaw in [PI/2,-PI/2]:driver_pose(ship,cart,Vector3(float(x),level+.03,-500),yaw,excluded)
	for z in [-432.0,-216.0]:
		for i in range(81):driver_pose(ship,cart,Vector3(-51,12.03,z),TAU*i/80.0,excluded)
	# The actual pre-existing synthesis approach remains a narrower 2.4m throat.
	for i in range(41):driver_pose(ship,cart,Vector3(-46,.03,-60),PI/2+PI/2*i/40.0,excluded)
	print("LOWER STAFF CART CLEARANCE PASS:",samples," compound cart/load and driver poses, including lower corner turns, long service streets, existing spine junction and bounded D03 thresholds. Geometric checks only; physical steering is separate.")
	quit(0)
