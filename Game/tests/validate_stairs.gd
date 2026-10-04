extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(8): await physics_frame
	var actor: CharacterBody3D = main.get_node("World360/Astraea/ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	actor.global_position = Vector3(11.25,44.1,202)
	actor.velocity = Vector3.ZERO
	for level in range(2):
		for destination in [Vector2(11.25,191.5),Vector2(14.75,191.5),Vector2(14.75,202),Vector2(11.25,202)]:
			var reached := false
			for frame in range(400):
				var difference := Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
				if difference.length() < 0.09:
					reached = true
					break
				var movement := difference.normalized()*3.1
				actor.velocity.x = movement.x
				actor.velocity.z = movement.z
				actor.velocity.y = -0.1 if actor.is_on_floor() else actor.velocity.y-9.8/60.0
				actor.move_and_slide()
				await physics_frame
			assert(reached,"Actual capsule stalled on stair or landing")
		assert(absf(actor.position.y-(52.5+level*8.5)) < 0.12,"Stair arrived at wrong floor")
	print("STAIR PASS: actual character capsule traverses two switchbacks from D08 to D10. No cart, accessibility, rail or visual acceptance implied.")
	main.queue_free()
	await process_frame
	quit(0)
