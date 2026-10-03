extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var actor: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var door: Node3D = ship.find_child("Suite13017BathDoor",true,false)
	assert(door != null and door.leaves.size()==1)
	door.interact(actor)
	for frame in range(100):
		await physics_frame
		assert_clear(ship,door)
	assert(door.open_fraction<.001)
	assert(ship.arrive_at(Vector3(79.05,84.1,-42.8),PI))
	for frame in range(15):await physics_frame
	assert(actor.target_from_view()==door,"Shared precise camera ray selects the bathroom door")
	var focus := InputEventMouseButton.new()
	focus.button_index=MOUSE_BUTTON_RIGHT
	focus.pressed=true
	Input.parse_input_event(focus)
	var press := InputEventKey.new()
	press.keycode=KEY_E
	press.physical_keycode=KEY_E
	press.pressed=true
	Input.parse_input_event(press)
	for frame in range(100):
		await physics_frame
		assert_clear(ship,door)
	assert(door.open_fraction>.999,"Shared RMB/E opens bathroom door")
	press.pressed=false
	Input.parse_input_event(press)
	focus.pressed=false
	Input.parse_input_event(focus)
	door.interact(actor)
	for frame in range(100):
		await physics_frame
		assert_clear(ship,door)
	press.pressed=true
	Input.parse_input_event(press)
	for frame in range(10):await physics_frame
	assert(door.open_fraction<.001,"Unfocused E must not operate privacy door")
	assert(ship.arrive_at(Vector3(79.05,84.1,-40.65),0))
	for frame in range(10):await physics_frame
	door.interact(actor)
	assert(door.obstructed and not door.desired_open,"Occupied privacy-door swing is inhibited")
	print("PRIVACY DOOR PASS:300 motion samples clear of fixed room/frame, shared RMB/E targeting, unfocused rejection and occupied swing stop. No save, latch lock or loaded-cart acceptance.")
	main.queue_free()
	await process_frame
	quit()
func assert_clear(ship: Node3D,door: Node3D) -> void:
	for leaf in door.leaves:
		for collider in leaf.get_children():
			if not collider is CollisionShape3D:continue
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape=collider.shape
			query.transform=collider.global_transform
			query.margin=.001
			query.exclude=[leaf.get_rid()]
			for hit in ship.get_world_3d().direct_space_state.intersect_shape(query,64):
				assert(not (hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Privacy leaf clips %s at %.3f" % [hit.collider.get_path(),door.open_fraction])
