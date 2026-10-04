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
	actor.set_physics_process(false)
	for base in [88.5,97.5]:
		actor.position=Vector3(87.25,base+.1,3.8)
		actor.velocity=Vector3.ZERO
		for destination in [Vector2(87.25,10.3),Vector2(89.65,10.3),Vector2(89.65,3.6)]:await walk(actor,destination)
		assert(abs(actor.position.y-base-4.5)<.12,"East stair must reach next deck")
		for destination in [Vector2(89.65,10.3),Vector2(87.25,10.3),Vector2(87.25,3.8)]:await walk(actor,destination)
		assert(abs(actor.position.y-base)<.12,"East stair must return to lower deck")
	actor.position=Vector3(65.2,93.1,-11)
	actor.velocity=Vector3.ZERO
	for destination in [Vector2(65.2,-3.8),Vector2(68.2,-3.8),Vector2(68.2,-11)]:await walk(actor,destination)
	assert(abs(actor.position.y-97.5)<.12,"West stair must reach D16")
	for destination in [Vector2(68.2,-3.8),Vector2(65.2,-3.8),Vector2(65.2,-11)]:await walk(actor,destination)
	assert(abs(actor.position.y-93)<.12)
	# Each actual upper arrival connects its atrium seam to the shared lift foyer.
	for level in [93.0,97.5,102.0]:
		actor.position=Vector3(50.5,level+.1,0)
		actor.velocity=Vector3.ZERO
		var route:Array[Vector2]=[]
		if level==93.0:route.assign([Vector2(54,0),Vector2(59,9.5),Vector2(65,9.5),Vector2(72,10),Vector2(83,10),Vector2(84.5,3.3),Vector2(89,3.3),Vector2(89,0)])
		elif level==97.5:route.assign([Vector2(63,0),Vector2(68,0),Vector2(68,9),Vector2(72,12),Vector2(85,12.65),Vector2(90.8,12.65),Vector2(92.3,11.15),Vector2(92.3,3.3),Vector2(89,3.3),Vector2(89,0)])
		else:route.assign([Vector2(54,0),Vector2(59,-11.8),Vector2(65,-11.8),Vector2(75,-11),Vector2(86,-8),Vector2(89,0)])
		for destination in route:await walk(actor,destination)
		assert(abs(actor.position.y-level)<.12,"Upper commons route must stay on its assigned floor")
	print("STARBOARD HOUSE STAIRS PASS: three new stair pairs traversed up/down by actual capsule; broader routes, furnishings and final visual acceptance pending.")
	main.queue_free()
	await process_frame
	quit()
