extends "res://tests/validate_cart_clearance.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var lift:Node3D=ship.find_child("AquaticPassengerLift",true,false)
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	# Full moving cabin contact geometry must clear all fixed construction.
	var sweep_samples:=0
	for i in range(171):
		var pose:Transform3D=lift.cabin.global_transform
		pose.origin.y=44.0+i*.1
		for part in lift.cabin.get_children():
			if not part is CollisionShape3D:continue
			var query:=PhysicsShapeQueryParameters3D.new()
			query.shape=part.shape
			query.transform=pose*part.transform
			query.margin=0.001
			query.exclude=excluded
			var hits:=ship.get_world_3d().direct_space_state.intersect_shape(query,16)
			for hit in hits:print("SWEEP CONTACT:",hit.collider.get_path()," part:",part.name," y:",pose.origin.y)
			assert(hits.is_empty(),"Aquatic cabin contacts fixed structure: %s at %.2f"%[part.name,pose.origin.y])
			sweep_samples+=1
	# Compound loaded-cart clearance, including the aft bypass around the existing column.
	for floor_y in [44.0,52.5,61.0]:
		for i in range(66):check_pose(ship,cart,Vector3(9.8,floor_y+.03,223.2+i*.25),0,excluded)
		for i in range(31):check_pose(ship,cart,Vector3(9.8,floor_y+.03,239.5),PI*.5*i/30,excluded)
		for i in range(42):check_pose(ship,cart,Vector3(9.8+i*.24,floor_y+.03,239.5),PI/2,excluded)
		for i in range(31):check_pose(ship,cart,Vector3(20,floor_y+.03,239.5),PI*.5*i/30,excluded)
		for i in range(23):check_pose(ship,cart,Vector3(20,floor_y+.03,239.5+i*.25),0,excluded)
	print("AQUATIC ACCESS PASS:",sweep_samples,"full cabin-shape sweep samples;",samples,"compound cart and upper-load approach poses. Geometric clearance only; driven boarding turns and final art remain pending.")
	main.queue_free()
	await process_frame
	quit()
