extends "res://tests/validate_cart_clearance.gd"
func driver_pose(ship:Node3D,cart:RigidBody3D,p:Vector3,yaw:float,excluded:Array[RID]) -> void:
	check_pose(ship,cart,p,yaw,excluded)
	var basis:=Basis(Vector3.UP,yaw)
	var capsule:=CapsuleShape3D.new()
	capsule.radius=.3
	capsule.height=1.8
	var q:=PhysicsShapeQueryParameters3D.new()
	q.shape=capsule
	q.transform=Transform3D(basis,p+basis*Vector3(0,.91,1.62))
	q.exclude=excluded
	var hits:=ship.get_world_3d().direct_space_state.intersect_shape(q)
	for hit in hits:print("DRIVER BLOCK:",p," yaw:",yaw," ",hit.collider.get_path())
	assert(hits.is_empty(),"Full cart/driver envelope blocked")
	var feet:Vector3=p+basis*Vector3(0,0,1.62)
	var ray:=PhysicsRayQueryParameters3D.create(feet+Vector3.UP*.2,feet-Vector3.UP*.2)
	ray.exclude=excluded
	assert(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Driver left supported floor")
func walk(actor:CharacterBody3D,destination:Vector2) -> void:
	var reached:=false
	for frame in range(700):
		var delta:=Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
		if delta.length()<.09:
			reached=true
			break
		var movement:=delta.normalized()*3.1
		actor.velocity.x=movement.x
		actor.velocity.z=movement.z
		actor.velocity.y=-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60
		actor.move_and_slide()
		await physics_frame
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("WALK BLOCK:",actor.get_slide_collision(i).get_collider().get_path())
	assert(reached,"Florist walk stalled at %s toward %s"%[actor.position,destination])
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var room:Node3D=ship.find_child("LivingGiftsInterior_WIP",true,false)
	assert(room.get_meta("programme_key")=="D09_directory_08" and room.get_meta("historical_room_id")=="D09_florist7")
	var architecture:Node3D=room.find_child("LivingGiftsAuthoredInterior",true,false)
	var frame_ray:=PhysicsRayQueryParameters3D.create(Vector3(13,45.65,218),Vector3(46.88,56.45,236))
	assert(ship.get_world_3d().direct_space_state.intersect_ray(frame_ray).is_empty(),"Upper florist framing obscured from original aquatic arrival")
	for i in range(4):
		var light:Node3D=room.find_child("LivingGiftsSource_"+str(i),true,false)
		var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.04)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Florist emitter exit blocked")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	for center in [Vector2(51.5,247),Vector2(50.8,235.7),Vector2(46.7,227.5),Vector2(44.5,236)]:
		for i in range(40):driver_pose(ship,cart,Vector3(center.x,52.53,center.y),TAU*i/40,excluded)
	for i in range(49):
		for yaw in [0.0,PI]:driver_pose(ship,cart,Vector3(52.4,52.53,247-i*.20),yaw,excluded)
	for i in range(4):
		var marker:=architecture.find_child("DATUM_flora_"+str(i),true,false)as Node3D
		var plant:Node3D=room.find_child("LivingGiftsSpecimen_"+str(i),true,false)
		var ray:=PhysicsRayQueryParameters3D.create(marker.global_position+Vector3.UP*.06,marker.global_position-Vector3.UP*.02)
		var omit:Array[RID]=[]
		for body in plant.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		ray.exclude=omit
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty() and abs(hit.position.y-marker.global_position.y)<.012,"Plant lacks fitted soil support")
	for i in range(4):
		var pot:Node3D=room.find_child("LivingGiftsShelfPot_"+str(i),true,false)
		var flower:Node3D=room.find_child("LivingGiftsShelfFlower_"+str(i),true,false)
		var omit:Array[RID]=[]
		for host in [pot,flower]:
			for body in host.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		for j in range(16):
			var p:Vector3=pot.global_position+Vector3(cos(TAU*j/16)*.074,0,sin(TAU*j/16)*.074)
			var q:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.03,p-Vector3.UP*.03)
			q.exclude=omit
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q)
			assert(not hit.is_empty() and abs(hit.position.y-p.y)<.008,"Nursery pot foot is unsupported")
		for mesh in flower.find_children("*","MeshInstance3D",true,false):
			for surface in range(mesh.mesh.get_surface_count()):
				var arrays:Array=mesh.mesh.surface_get_arrays(surface)
				for vertex in arrays[Mesh.ARRAY_VERTEX]:
					var endpoint:Vector3=mesh.global_transform*vertex
					if endpoint.distance_to(flower.global_position)<.015:continue
					var q:=PhysicsRayQueryParameters3D.create(flower.global_position,endpoint)
					q.exclude=omit
					var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q)
					if not hit.is_empty():print("FLOWER CLIP:",i," ",hit.collider.get_path()," at ",hit.position)
					assert(hit.is_empty(),"Shelf foliage clips display geometry")
	actor.set_physics_process(false)
	actor.position=Vector3(52,52.6,216)
	actor.velocity=Vector3.ZERO
	for target in [Vector2(52,225),Vector2(46.7,227.5),Vector2(44.5,232),Vector2(44.5,236),Vector2(48.2,236),Vector2(50.8,235.7),Vector2(52.4,237.8),Vector2(52.4,241),Vector2(52.4,245),Vector2(51.5,247),Vector2(52.4,242.4),Vector2(52.4,237.8),Vector2(50.5,238),Vector2(50.5,241),Vector2(48.9,241)]:await walk(actor,target)
	assert(abs(actor.position.y-52.5)<.12)
	print("LIVING GIFTS PASS:",samples,"compound cart/load plus driver poses, four soil supports, four supported potted shelf specimens, canonical/historical identity and actual public/shop/service/wrapping walk. Driven cart turning, transactions, NPC use and final art remain pending.")
	main.queue_free()
	await process_frame
	quit()
