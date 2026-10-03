extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(20): await physics_frame
	var world: Node3D = main.get_node("World360/Astraea")
	var actor: CharacterBody3D = world.get_node("ShipSpace/PersistentActors/Player")
	var control: Node3D = world.find_child("SharedStudyLightSwitch",true,false)
	var budget: Node = world.find_child("LocalShadowSourceBudget",true,false)
	assert(control.persistent_id == &"D09_salon5_shared_study_light")
	assert(control.diffuser_materials.size() > 0,"Fixture diffuser must respond visibly")
	# Stand in the existing side approach, aim precisely at the actual control datum.
	assert(world.arrive_at(Vector3(65.5,52.6,-21.5),0))
	for frame in range(15): await physics_frame
	actor.camera.look_at(control.global_position,Vector3.UP)
	assert(actor.target_from_view() == control,"Physical switch must be reachable through the shared ray dispatcher")
	var focus := InputEventMouseButton.new()
	focus.button_index = MOUSE_BUTTON_RIGHT
	focus.pressed = true
	Input.parse_input_event(focus)
	var press := InputEventKey.new()
	press.keycode = KEY_E
	press.physical_keycode = KEY_E
	press.pressed = true
	Input.parse_input_event(press)
	for frame in range(20): await physics_frame
	assert(not control.powered and not control.source.visible)
	for attempt in range(3): budget.refresh()
	assert(not control.source.visible and not control.source.shadow_enabled,"Budget must not resurrect switched-off lights")
	assert(not control.diffuser_materials[0].emission_enabled)
	press.pressed = false
	Input.parse_input_event(press)
	focus.pressed = false
	Input.parse_input_event(focus)
	press = press.duplicate()
	press.pressed = true
	Input.parse_input_event(press)
	for frame in range(5): await physics_frame
	assert(not control.powered,"Unfocused E must remain ignored")
	control.interact(actor)
	budget.refresh()
	assert(control.powered and control.source.visible and control.diffuser_materials[0].emission_enabled)
	# A solid obstacle must block the control, even though targets are Areas.
	var blocker := StaticBody3D.new()
	world.add_child(blocker)
	blocker.global_position = actor.camera.global_position.lerp(control.global_position,.5)
	var contact := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(.4,.4,.4)
	contact.shape = box
	blocker.add_child(contact)
	for frame in range(3): await physics_frame
	assert(actor.target_from_view() != control,"Controls cannot be selected through opaque objects")
	print("FIXTURE PASS: actual control datum, shared RMB/E selection, unfocused rejection, visible diffuser, power-aware shadow budget and solid occlusion. No save/DOF acceptance.")
	main.queue_free()
	await process_frame
	quit(0)
