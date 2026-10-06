extends SceneTree
# UNRUN actual-world integration draft, following validate_d17_connected_cart.
# Sole initial fixture placement. The cart and its four loose products are never
# teleported, frozen, reparented, velocity-reset or collision-exempted in travel.
const FLOOR := 69.5
const DRIVER_OFFSET := 1.62
const MAX_FRAMES := 20000
var probe = preload("res://tests/theater_stage_probe.gd").new()
var sweep_probe = preload("res://tests/d17_cart_route_probe.gd").new()
var frames := 0
var driven_frames := 0
var input_frames := 0
var support_samples := 0
var peak_input_speed := 0.0
var started := 0
var last_actor := Vector3.ZERO
var last_cart := Vector3.ZERO
var cart_distance := 0.0
var fixture_placed := false
func _initialize() -> void:
	started = Time.get_ticks_msec()
	call_deferred("run")
func _process(_delta: float) -> bool:
	if Time.get_ticks_msec()-started > 600000:
		key(KEY_W,false)
		push_error("Theater loaded cart 600-second watchdog")
		quit(1)
	return false
func key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()
func focus(pressed: bool) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_RIGHT
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()
func aim_handle() -> void:
	var actor: CharacterBody3D = probe.actor
	var cart: RigidBody3D = probe.cart
	var delta: Vector3 = cart.global_transform*cart.grip_local-actor.camera.global_position
	actor.rotation.y = atan2(-delta.x,-delta.z)
	actor.pitch = atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.camera.rotation.x = actor.pitch
func live_state(held: bool = true) -> void:
	frames += 1
	assert(frames < MAX_FRAMES)
	var actor: CharacterBody3D = probe.actor
	var cart: RigidBody3D = probe.cart
	assert(cart.global_position.is_finite() and cart.linear_velocity.length() < 8)
	assert(cart.global_basis.y.dot(Vector3.UP) > .90)
	assert(absf(cart.global_position.y-FLOOR) < .14 and absf(actor.global_position.y-FLOOR) < .14)
	assert(cart.get_parent().name == "PersistentActors" and cart.products.size() == 4)
	if held: assert(cart.driver == actor and actor.held_interaction == cart.interaction_owner)
	else: assert(cart.driver == null and actor.held_interaction == null)
	for product in cart.products:
		assert(product.get_parent() == cart.get_parent())
		var p: Vector3 = cart.to_local(product.global_position)
		assert(p.is_finite() and p.y > .8 and p.y < 1.3 and absf(p.x) < .4 and absf(p.z) < .6,"Loose product escaped tray")
	var displacement := cart.global_position.distance_to(last_cart)
	assert(displacement < .15 and actor.global_position.distance_to(last_actor) < .12,"Teleport/unchecked discontinuity is not traversal")
	cart_distance += displacement
	last_cart = cart.global_position
	last_actor = actor.global_position
	for identity in probe.held_poses:
		var node: Node3D = probe.motion.find_child(str(probe.data.motion_node_names[identity]),true,false)
		probe.assert_transform(node.global_transform,probe.held_poses[identity],"Locked theater mechanism moved")
func actual_supports() -> void:
	for spec in sweep_probe.wheel_specs:
		var c: Array = spec.center
		probe.floor_at(probe.cart.global_transform*Vector3(c[0],0,c[2]))
	probe.floor_at(probe.actor.global_position)
	support_samples += 5
func press_handle(focused: bool) -> void:
	var actor: CharacterBody3D = probe.actor
	aim_handle()
	assert(actor.target_from_view() == probe.cart.interaction_owner,"Precise real handle must be selectable")
	actor.set_physics_process(true)
	focus(focused)
	key(KEY_E,true)
	for frame in range(3): await physics_frame
	key(KEY_E,false)
	focus(false)
func drive(poses: Array) -> void:
	var actor: CharacterBody3D = probe.actor
	var cart: RigidBody3D = probe.cart
	actor.set_physics_process(false)
	for raw in poses:
		var pose := Vector3(raw[0],raw[1],raw[2])
		var target := Vector3(pose.x,FLOOR,pose.y) + Basis(Vector3.UP,pose.z)*Vector3(0,0,DRIVER_OFFSET)
		actor.rotation.y = pose.z
		var reached := false
		for frame in range(120):
			var delta := target-actor.global_position
			delta.y = 0
			if delta.length() < .025:
				reached = true
				break
			var velocity := delta.limit_length(1.0/60)*60
			actor.velocity = Vector3(velocity.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,velocity.z)
			actor.move_and_slide()
			await physics_frame
			driven_frames += 1
			live_state()
			actual_supports()
		assert(reached,"Theater cart driver stalled at %s toward %s; cart %s" % [actor.global_position,target,cart.global_position])
	actor.velocity = Vector3.ZERO
	for frame in range(90):
		await physics_frame
		live_state()
		actual_supports()
	var end: Array = poses.back()
	assert(Vector2(cart.global_position.x,cart.global_position.z).distance_to(Vector2(end[0],end[1])) < .65)
func run() -> void:
	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150): await physics_frame
	probe.configure(main.get_node("World360/Astraea"))
	probe.check_motion_poses_and_barriers()
	var actor: CharacterBody3D = probe.actor
	var cart: RigidBody3D = probe.cart
	var product_local: Array[Vector3] = []
	for product in cart.products: product_local.append(cart.to_local(product.global_position))
	actor.set_physics_process(false)
	assert(not fixture_placed)
	cart.global_position = Vector3(-2,FLOOR+.04,-126)
	cart.rotation = Vector3(0,PI/2,0)
	cart.linear_velocity = Vector3.ZERO
	cart.angular_velocity = Vector3.ZERO
	cart.sleeping = false
	for index in range(4):
		cart.products[index].global_position = cart.global_transform*product_local[index]
		cart.products[index].linear_velocity = Vector3.ZERO
		cart.products[index].angular_velocity = Vector3.ZERO
		cart.products[index].sleeping = false
	assert(probe.ship.arrive_at(Vector3(-.38,FLOOR+.1,-126),PI/2))
	actor.set_physics_process(true)
	actor.set_controls_enabled(true)
	for frame in range(90): await physics_frame
	fixture_placed = true
	last_actor = actor.global_position
	last_cart = cart.global_position
	live_state(false)
	actual_supports()
	# Actual compound cart contacts, four wheel supports, load reserve, and real
	# operator capsule are swept along the same continuously curved centreline.
	var path: Array = probe.fixture.cart_forward_poses_xzyaw
	assert(path.size() == 1448)
	for raw in path:
		sweep_probe.check_pose(probe.ship,actor,cart,Vector3(raw[0],FLOOR+.03,raw[1]),float(raw[2]),FLOOR)
	assert(sweep_probe.sampled_poses == path.size())
	await press_handle(false)
	assert(cart.driver == null and actor.held_interaction == null,"Unfocused E cannot grab")
	await press_handle(true)
	assert(cart.driver == actor and actor.held_interaction == cart.interaction_owner)
	actor.rotation.y = PI/2
	actor.pitch = 0
	actor.camera.rotation.x = 0
	last_actor = actor.global_position
	last_cart = cart.global_position
	probe.check_lights("loaded cart at D11 fore spine")
	# Ordinary 2m/s held-cart W input covers the full 30m bridge and both sides
	# of the held-open entrance. It is not replaced by transform choreography.
	key(KEY_W,true)
	var crossed := false
	for frame in range(1800):
		await physics_frame
		input_frames += 1
		live_state()
		actual_supports()
		peak_input_speed = maxf(peak_input_speed,Vector2(actor.velocity.x,actor.velocity.z).length())
		if input_frames%180 == 0: probe.check_lights("loaded bridge input " + str(input_frames))
		if actor.global_position.x <= -36.38:
			crossed = true
			break
	key(KEY_W,false)
	assert(crossed and peak_input_speed > 1.95 and peak_input_speed < 2.01)
	for frame in range(90):
		await physics_frame
		live_state()
		actual_supports()
	assert(cart.global_position.x < -37.5 and cart.global_position.x > -39)
	probe.check_lights("cart and operator physically inside held-open entrance")
	# Rejoin the remaining straight segment ahead of the actual settled cart.
	# Skipping already traversed targets does not move either physical body.
	var remaining: Array = []
	var found := false
	for raw in path:
		if not found and float(raw[0]) <= cart.global_position.x-.20: found = true
		if found: remaining.append(raw)
	assert(not remaining.is_empty() and float(remaining[0][0]) > -40)
	await drive(remaining)
	assert(cart_distance > 105 and driven_frames > 3500 and input_frames > 900)
	assert(Vector2(cart.global_position.x+77.5,cart.global_position.z+137).length() < .65)
	probe.check_motion_poses_and_barriers()
	probe.check_lights("loaded south-route foyer arrival")
	# Release through the same ordinary focus/E convention; no cart relocation.
	actor.set_physics_process(true)
	focus(true)
	key(KEY_E,true)
	for frame in range(3): await physics_frame
	key(KEY_E,false)
	focus(false)
	assert(cart.driver == null and actor.held_interaction == null)
	for frame in range(30):
		await physics_frame
		live_state(false)
		actual_supports()
	print("THEATER CART PASS: one fixture placement, actual compound 1448-pose sweep, normal 2m/s loaded input over the bridge and open door, continuous 1m/s force-tether south bends, four loose products, ",support_samples," actual wheel/operator support checks, ",cart_distance,"m cart displacement. Actual selected lights <=8; 32-candidate selector unchanged. Scripted turns are not freehand feel; no door/lift operation, underside-census, appearance or aggregate acceptance claimed.")
	main.queue_free()
	await process_frame
	quit(0)
