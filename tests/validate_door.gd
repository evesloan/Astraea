extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30): await physics_frame
	var world: Node3D = main.get_node("World360/Astraea")
	var actor: CharacterBody3D = world.get_node("ShipSpace/PersistentActors/Player")
	var door: Node3D = world.find_child("SynthesisServiceDoor",true,false)
	assert(door != null and door.leaves.size()==2)
	# Check the actual animated sweep against fixed architecture.
	door.interact(actor)
	for frame in range(100):
		await physics_frame
		assert_clear(world,door)
	assert(door.open_fraction < 0.001)
	assert(world.arrive_at(Vector3(-59,0.1,0),PI/2))
	for frame in range(15): await physics_frame
	assert(actor.target_from_view()==door,"Precise camera ray must select service door")
	var focus := InputEventMouseButton.new()
	focus.button_index = MOUSE_BUTTON_RIGHT
	focus.pressed = true
	Input.parse_input_event(focus)
	var press := InputEventKey.new()
	press.keycode = KEY_E
	press.physical_keycode = KEY_E
	press.pressed = true
	Input.parse_input_event(press)
	for frame in range(100):
		await physics_frame
		assert_clear(world,door)
	assert(door.open_fraction > 0.999,"RMB plus E must open selected door")
	press.pressed = false
	Input.parse_input_event(press)
	focus.pressed = false
	Input.parse_input_event(focus)
	door.interact(actor)
	for frame in range(100):
		await physics_frame
		assert_clear(world,door)
	press.pressed = true
	Input.parse_input_event(press)
	for frame in range(10): await physics_frame
	assert(door.open_fraction < 0.001,"E without focus must not interact")
	assert(world.arrive_at(Vector3(-62,0.1,0),0.0))
	for frame in range(10): await physics_frame
	door.interact(actor)
	assert(door.obstructed and not door.desired_open,"Actor in swept space must inhibit motion")
	print("DOOR PASS: fixed-architecture sweep samples; exact camera target; RMB/E open; unfocused E ignored; occupied sweep inhibited. No loaded-cart or target-GPU acceptance.")
	main.queue_free()
	await process_frame
	quit(0)

func assert_clear(world: Node3D, door: Node3D) -> void:
	for leaf in door.leaves:
		for shape in leaf.get_children():
			if not shape is CollisionShape3D: continue
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = shape.shape
			query.transform = shape.global_transform
			query.margin = 0.001
			query.exclude = [leaf.get_rid()]
			for hit in world.get_world_3d().direct_space_state.intersect_shape(query,64):
				assert(not (hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Door swing clips fixed architecture: %s / %s / fraction %.4f" % [str(hit.collider.get_path()),shape.name,door.open_fraction])
