extends SceneTree
func _initialize() -> void:call_deferred("run")
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
		for i in range(actor.get_slide_collision_count()):
			var c:=actor.get_slide_collision(i)
			print("BLOCKER ",c.get_collider().get_path()," normal ",c.get_normal())
	assert(reached,"Commons route stalled at %s toward %s"%[actor.position,destination])
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	# Probe all reviewer-identified escape edges against actual exported contacts.
	for z in [-24.0,-20.0,-16.0]:
		for x in [81.8,86.2]:
			var ray:=PhysicsRayQueryParameters3D.create(Vector3(x-.4,84.7,z),Vector3(x+.4,84.7,z))
			assert(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Residential branch side must be guarded")
	for y in [85.0,86.9]:
		for x in [64.15,69.25]:
			var ray:=PhysicsRayQueryParameters3D.create(Vector3(x-.35,y,-3.6),Vector3(x+.35,y,-3.6))
			assert(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Intermediate landing side/under-soffit must be closed")
	for x in [66.7,68.2]:
		var ray:=PhysicsRayQueryParameters3D.create(Vector3(x,85,-10.1),Vector3(x,85,-9.2))
		assert(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Under-flight/inter-flight access must be closed")
	for y in [86.4,86.9,87.2]:
		var ray:=PhysicsRayQueryParameters3D.create(Vector3(66.7,y,-3.6),Vector3(66.7,y,-5.4))
		assert(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Landing inter-flight well edge must be guarded")
	actor.set_physics_process(false)
	actor.position=Vector3(50.5,84.1,0)
	actor.velocity=Vector3.ZERO
	for destination in [Vector2(60,0),Vector2(70,0),Vector2(70,-11),Vector2(65.2,-11),Vector2(65.2,-3.8),Vector2(68.2,-3.8),Vector2(68.2,-11)]:await walk(actor,destination)
	assert(abs(actor.position.y-88.5)<.12,"Upper arrival must reach D14 datum")
	for destination in [Vector2(63,-11.8),Vector2(59,-11.8),Vector2(54,0),Vector2(50.5,0)]:await walk(actor,destination)
	assert(abs(actor.position.y-88.5)<.12)
	actor.position=Vector3(84,84.1,-28)
	actor.velocity=Vector3.ZERO
	for destination in [Vector2(84,-18),Vector2(84,-12),Vector2(89,-9),Vector2(89,0)]:await walk(actor,destination)
	assert(abs(actor.position.y-84)<.12,"Residential branch should remain level")
	print("VERTICAL COMMONS PASS: actual capsule travels lower atrium arrival, two-flight stair, offset upper return and opened residential junction. Reviewer-identified branch/landing/under-stair escape edges now have contact coverage. Separate lift/load tests apply; final visual and species acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
