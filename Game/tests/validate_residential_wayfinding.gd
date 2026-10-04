extends "res://tests/validate_living_gifts.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var nook:Node3D=ship.find_child("ResidentialWayfindingArchitecture",true,false)
	assert(nook!=null)
	for part in nook.find_children("*","MeshInstance3D",true,false):
		var b:AABB=part.global_transform*part.get_aabb()
		assert(b.position.x>=71.79 and b.end.x<=77.21 and b.position.z>=(-27.701 if str(part.name).begins_with("RES_VisualFloor") else -27.151) and b.end.z<=-26.029)
		assert(b.end.y<88.26,"Residential bay must remain below protected D14")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	for i in range(129):
		for yaw in [-PI/2,PI/2]:driver_pose(ship,cart,Vector3(52+i*.25,84.03,-28.7),yaw,excluded)
	for i in range(40):driver_pose(ship,cart,Vector3(84,84.03,-28),TAU*i/40,excluded)
	for i in range(2):
		var seat:Node3D=nook.find_child("DATUM_seat_"+str(i),true,false)
		var ray:=PhysicsRayQueryParameters3D.create(seat.global_position+Vector3.UP*.05,seat.global_position-Vector3.UP*.05)
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty() and "RES_SeatCushion" in str(hit.collider.get_path()))
		var source:Node3D=nook.find_child("DATUM_light_"+str(i),true,false)
		ray=PhysicsRayQueryParameters3D.create(source.global_position,source.global_position+Vector3.DOWN*.08)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty())
	actor.set_physics_process(false)
	actor.position=Vector3(84,84.1,-28.7)
	actor.velocity=Vector3.ZERO
	await walk(actor,Vector2(52,-28.7))
	for i in range(2):
		var approach:Node3D=nook.find_child("DATUM_approach_"+str(i),true,false)
		await walk(actor,Vector2(approach.global_position.x,-28.7))
		await walk(actor,Vector2(approach.global_position.x,approach.global_position.z))
		await walk(actor,Vector2(approach.global_position.x,-28.7))
	await walk(actor,Vector2(84,-28.7))
	assert(absf(actor.position.y-84)<.12)
	print("RESIDENTIAL WAYFINDING PASS:",samples,"cart/load+driver poses; actual connector and two resting-approach walks; seat contacts, fixture exits and D14 clearance. Map is a static local route diagram; species-wide seating, seated animation and interactive directory behavior are not claimed.")
	main.queue_free()
	await process_frame
	quit()
