extends SceneTree
# Actual main-scene cart, four loose products, capsule, force tether and lift.
# Only place the fixture once. Never assign cart/product transforms during travel.
# The 1 m/s changing-position/heading route is followed by ordinary 2 m/s W input
# across both actual D17 gate planes. This does not certify freehand turning feel.
const FLOOR := 102.0
const DRIVER_OFFSET := 1.62
const MAX_TRACKED_FRAMES := 24000
const RECEIPT := "res://docs/D17_CONNECTED_CART_VALIDATION.json"
const PLATFORM_SHA := "5375179c3d89b92a4f950b7fad0a0936aafdeca37797aa388264f9bdf6d8e664"
const COMMONS_SHA := "6b559b69c13d0ea2e5cb16e42791aec6af495c377fcfbf074ebfb36f7e57ff18"
var probe = preload("res://tests/d17_cart_route_probe.gd").new()
var driven_frames := 0
var walked_frames := 0
var input_frames := 0
var waiting_frames := 0
var support_samples := 0
var sill_bridge_samples := 0
var moving_turn_samples := 0
var keyboard_peak_speed := 0.0

func _initialize() -> void:
	call_deferred("run")

func frame_budget() -> void:
	assert(driven_frames + walked_frames + input_frames + waiting_frames < MAX_TRACKED_FRAMES, "Predeclared D17 cart frame budget exceeded")

func line(path: Array[Vector3], a: Vector2, b: Vector2, backing := false) -> void:
	var delta := b - a
	assert(delta.length() > .001)
	var yaw := atan2(-delta.x, -delta.y) + (PI if backing else 0.0)
	var count := maxi(1, ceili(delta.length() / .08))
	if not path.is_empty():
		var previous: Vector3 = path.back()
		assert(Vector2(previous.x, previous.y).distance_to(a) < .001, "Continuous cart route required")
		assert(absf(wrapf(previous.z - yaw, -PI, PI)) < .001, "No fixed-centre heading snap")
	for index in range(count + 1):
		var p := a.lerp(b, float(index) / count)
		path.append(Vector3(p.x, p.y, yaw))

func arc(path: Array[Vector3], centre: Vector2, radius: float, start: float, finish: float) -> void:
	var count := maxi(1, ceili(absf(finish - start) * radius / .06))
	for index in range(count + 1):
		var angle := lerpf(start, finish, float(index) / count)
		var p := centre + Vector2(cos(angle), sin(angle)) * radius
		var direction := Vector2(-sin(angle), cos(angle)) * signf(finish - start)
		var yaw := atan2(-direction.x, -direction.y)
		if index == 0 and not path.is_empty():
			var previous: Vector3 = path.back()
			assert(Vector2(previous.x, previous.y).distance_to(p) < .001)
			assert(absf(wrapf(previous.z - yaw, -PI, PI)) < .001)
		path.append(Vector3(p.x, p.y, yaw))
		if index > 0:
			moving_turn_samples += 1

func outbound_route() -> Array[Vector3]:
	var path: Array[Vector3] = []
	line(path, Vector2(89, 0), Vector2(86, 0))
	arc(path, Vector2(86, 1.5), 1.5, -PI / 2, -PI)
	line(path, Vector2(84.5, 1.5), Vector2(84.5, 6.5))
	arc(path, Vector2(83, 6.5), 1.5, 0, PI / 2)
	line(path, Vector2(83, 8), Vector2(81.5, 8))
	arc(path, Vector2(81.5, 9.5), 1.5, -PI / 2, -PI)
	line(path, Vector2(80, 9.5), Vector2(80, 23.5))
	arc(path, Vector2(81.5, 23.5), 1.5, PI, PI / 2)
	line(path, Vector2(81.5, 25), Vector2(91, 25))
	arc(path, Vector2(91, 26.5), 1.5, -PI / 2, 0)
	line(path, Vector2(92.5, 26.5), Vector2(92.5, 30.9))
	arc(path, Vector2(94, 30.9), 1.5, PI, PI / 2)
	line(path, Vector2(94, 32.4), Vector2(98.7, 32.4))
	return path

func forward_return(outbound: Array[Vector3]) -> Array[Vector3]:
	var path: Array[Vector3] = []
	for index in range(outbound.size() - 1, -1, -1):
		var pose := outbound[index]
		path.append(Vector3(pose.x, pose.y, wrapf(pose.z + PI, -PI, PI)))
	return path

func check_load(cart: RigidBody3D) -> void:
	assert(cart.products.size() == 4)
	for product in cart.products:
		assert(product.get_parent() == cart.get_parent(), "Loose products must not be parented to the cart or lift")
		var p: Vector3 = cart.to_local(product.global_position)
		assert(p.is_finite() and p.y > .8 and p.y < 1.3 and absf(p.x) < .4 and absf(p.z) < .6, "D17 loose product escaped upper tray: " + str(p))

func live_state(actor: CharacterBody3D, cart: RigidBody3D, held: bool) -> void:
	assert(cart.global_position.is_finite() and cart.linear_velocity.length() < 8)
	assert(cart.global_basis.y.dot(Vector3.UP) > .90, "D17 cart tipped")
	assert(absf(cart.global_position.y - FLOOR) < .14 and absf(actor.global_position.y - FLOOR) < .14, "D17 cart/operator left their intended floor")
	assert(cart.get_parent().name == "PersistentActors")
	if held:
		assert(cart.driver == actor and actor.held_interaction == cart.interaction_owner, "D17 force tether lost")
	else:
		assert(cart.driver == null and actor.held_interaction == null, "On-foot control operation requires handle release")
	check_load(cart)

func live_support(ship: Node3D, actor: CharacterBody3D, cart: RigidBody3D, at_lift := false) -> void:
	var space := ship.get_world_3d().direct_space_state
	var excluded: Array[RID] = probe.controlled_exclusions(actor, cart)
	var points: Array[Vector3] = []
	for spec in probe.wheel_specs:
		var p: Array = spec.center
		points.append(cart.global_transform * Vector3(p[0], 0, p[2]))
	points.append(actor.global_position)
	for index in range(points.size()):
		var p := points[index]
		var query := PhysicsRayQueryParameters3D.create(Vector3(p.x, FLOOR + .20, p.z), Vector3(p.x, FLOOR - .20, p.z), 1)
		query.exclude = excluded
		var hit := space.intersect_ray(query)
		if hit.is_empty() and at_lift and p.x > 92.185 and p.x < 92.205 and absf(p.z) < 1.2:
			# The retained cabin has a physical 10 mm sill gap. A spherical wheel
			# or capsule bridges it; demand same-level support on BOTH sides within
			# 20 mm of its centre rather than pretending a floor ray hits the gap.
			probe.floor_at(space, p + Vector3.LEFT * .02, FLOOR, excluded, "D17 sill west bearing")
			probe.floor_at(space, p + Vector3.RIGHT * .02, FLOOR, excluded, "D17 sill east bearing")
			sill_bridge_samples += 1
		else:
			assert(not hit.is_empty(), "D17 actual wheel/operator unsupported at " + str(p))
			assert(absf(hit.position.y - FLOOR) < .015, "D17 actual wheel/operator has wrong-level support")
		support_samples += 1

func sweep(ship: Node3D, actor: CharacterBody3D, cart: RigidBody3D, path: Array[Vector3], label: String) -> void:
	for pose in path:
		probe.check_pose(ship, actor, cart, Vector3(pose.x, FLOOR + .03, pose.y), pose.z, FLOOR)
	print("D17 CART SWEEP: ", label, " poses:", path.size())

func drive(ship: Node3D, actor: CharacterBody3D, cart: RigidBody3D, path: Array[Vector3], label: String) -> void:
	for pose in path:
		var target := Vector3(pose.x, FLOOR, pose.y) + Basis(Vector3.UP, pose.z) * Vector3(0, 0, DRIVER_OFFSET)
		actor.rotation.y = pose.z
		var reached := false
		for frame in range(120):
			var offset := target - actor.global_position
			offset.y = 0
			if offset.length() < .025:
				reached = true
				break
			var speed := offset.limit_length(1.0 / 60) * 60
			actor.velocity = Vector3(speed.x, -.1 if actor.is_on_floor() else actor.velocity.y - 9.8 / 60, speed.z)
			actor.move_and_slide()
			await physics_frame
			driven_frames += 1
			frame_budget()
			live_state(actor, cart, true)
			if driven_frames % 6 == 0:
				live_support(ship, actor, cart)
		if not reached:
			for index in range(actor.get_slide_collision_count()):
				print("D17 CART DRIVER BLOCK: ", actor.get_slide_collision(index).get_collider().get_path())
		assert(reached, "%s driver stalled at %s toward %s; cart %s" % [label, actor.global_position, target, cart.global_position])
	actor.velocity = Vector3.ZERO
	for frame in range(90):
		await physics_frame
		waiting_frames += 1
		live_state(actor, cart, true)
	var end: Vector3 = path.back()
	assert(Vector2(cart.global_position.x, cart.global_position.z).distance_to(Vector2(end.x, end.y)) < .65, label + " cart missed endpoint")
	live_support(ship, actor, cart)
	print("D17 CART DRIVEN: ", label, " cart:", cart.global_position, " driver:", actor.global_position)

func walk(ship: Node3D, actor: CharacterBody3D, cart: RigidBody3D, target: Vector2, at_lift := false) -> void:
	var reached := false
	for frame in range(900):
		var offset := Vector3(target.x - actor.global_position.x, 0, target.y - actor.global_position.z)
		if offset.length() < .025:
			reached = true
			break
		var speed := offset.limit_length(3.1 / 60) * 60
		actor.velocity = Vector3(speed.x, -.1 if actor.is_on_floor() else actor.velocity.y - 9.8 / 60, speed.z)
		actor.move_and_slide()
		await physics_frame
		walked_frames += 1
		frame_budget()
		live_state(actor, cart, false)
		if walked_frames % 6 == 0:
			live_support(ship, actor, cart, at_lift)
	assert(reached, "D17 released operator stalled at %s toward %s" % [actor.global_position, target])
	actor.velocity = Vector3.ZERO

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

func aim(actor: CharacterBody3D, target: Vector3) -> void:
	var delta: Vector3 = target - actor.camera.global_position
	actor.rotation.y = atan2(-delta.x, -delta.z)
	actor.pitch = atan2(delta.y, Vector2(delta.x, delta.z).length())
	actor.camera.rotation.x = actor.pitch

func press(actor: CharacterBody3D, target: Node3D, focused := true, held_release := false) -> void:
	aim(actor, target.global_position)
	if not held_release:
		assert(actor.target_from_view() == target, "Precise D17 target unavailable: " + str(target.get_path()))
	actor.velocity = Vector3.ZERO
	actor.set_physics_process(true)
	focus(focused)
	key(KEY_E, true)
	for frame in range(3):
		await physics_frame
		input_frames += 1
	key(KEY_E, false)
	focus(false)
	actor.set_physics_process(false)
	actor.velocity = Vector3.ZERO

func grip(actor: CharacterBody3D, cart: RigidBody3D, yaw: float) -> void:
	await press(actor, cart.interaction_owner)
	assert(cart.driver == actor and actor.held_interaction == cart.interaction_owner)
	actor.rotation.y = yaw
	actor.pitch = 0
	actor.camera.rotation.x = 0

func blocked_gate_push(ship: Node3D, actor: CharacterBody3D, cart: RigidBody3D, gate: Node3D) -> void:
	# A zero-width ray through the exact central 5 mm leaf seam is not a valid
	# capsule-closure proof. Drive the actual 600 mm capsule into that seam.
	await walk(ship, actor, cart, Vector2(90.6, 0))
	var gate_contact := false
	for frame in range(90):
		actor.velocity = Vector3(2.0, -.1 if actor.is_on_floor() else actor.velocity.y - 9.8 / 60, 0)
		actor.move_and_slide()
		await physics_frame
		walked_frames += 1
		frame_budget()
		live_state(actor, cart, false)
		assert(actor.global_position.x < 91.85, "Actual capsule crossed absent-cabin D17 gate")
		for index in range(actor.get_slide_collision_count()):
			var collider: Node = actor.get_slide_collision(index).get_collider()
			if gate.is_ancestor_of(collider):
				gate_contact = true
		if frame % 6 == 0:
			live_support(ship, actor, cart)
	assert(gate_contact and actor.global_position.x > 91.55, "Actual capsule must reach and collide with the D17 landing gate")
	actor.velocity = Vector3.ZERO
	await walk(ship, actor, cart, Vector2(90.6, 0))
	await walk(ship, actor, cart, Vector2(90.6, 1.35))

func run() -> void:
	assert(FileAccess.get_sha256("res://assets/models/AST-RES-006.glb") == PLATFORM_SHA)
	assert(FileAccess.get_sha256("res://assets/models/AST-COM-003.glb") == COMMONS_SHA)
	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150):
		await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var actor: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var cart: RigidBody3D = ship.find_child("CustodialCart", true, false)
	var lift: Node3D = ship.find_child("CommonsPassengerLift", true, false)
	var connected: Node3D = ship.find_child("D17ConnectedHouse_WIP", true, false)
	assert(connected != null and connected.get_meta("source_guest_index") == 790)
	assert(lift.floor_heights.size() == 5 and lift.deck_numbers[4] == 17 and lift.floor_heights[4] == FLOOR)
	assert(lift.current_floor == 0 and lift.phase == "idle")
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json"))
	assert(contract.private_arrival.door.status == "OPEN GUARDED THRESHOLD; no moving door installed")
	var local_products: Array[Vector3] = []
	for product in cart.products:
		local_products.append(cart.to_local(product.global_position))
	assert(local_products.size() == 4)
	actor.set_physics_process(false)
	# Sole fixture placement. No later relocation, velocity reset, freeze, collision
	# exclusion or parenting of the cart/products is permitted in this test.
	cart.global_position = Vector3(89, FLOOR + .04, 0)
	cart.rotation = Vector3(0, PI / 2, 0)
	cart.linear_velocity = Vector3.ZERO
	cart.angular_velocity = Vector3.ZERO
	cart.sleeping = false
	for index in range(4):
		cart.products[index].global_position = cart.global_transform * local_products[index]
		cart.products[index].linear_velocity = Vector3.ZERO
		cart.products[index].angular_velocity = Vector3.ZERO
		cart.products[index].sleeping = false
	actor.global_position = Vector3(90.62, FLOOR + .03, 0)
	actor.rotation.y = PI / 2
	actor.velocity = Vector3.ZERO
	for frame in range(90):
		await physics_frame
	check_load(cart)
	var outbound := outbound_route()
	var returning := forward_return(outbound)
	var receiving: Array[Vector3] = []
	line(receiving, Vector2(98.7, 32.4), Vector2(101.3, 32.4))
	var backing: Array[Vector3] = []
	line(backing, Vector2(98.7, 32.4), Vector2(96.9, 32.4), true)
	var recover: Array[Vector3] = []
	line(recover, Vector2(96.9, 32.4), Vector2(98.7, 32.4))
	var turn: Array[Vector3] = []
	arc(turn, Vector2(101.3, 33.7), 1.3, -PI / 2, PI)
	arc(turn, Vector2(98.7, 33.7), 1.3, 0, -PI / 2)
	for entry in [[outbound, "outbound"], [returning, "forward return"], [backing, "short backing recovery"], [recover, "forward recovery"], [receiving, "receiving bay"], [turn, "moving receiving turn"]]:
		sweep(ship, actor, cart, entry[0], entry[1])
	assert(moving_turn_samples > 250, "Both position and heading must change through authored bends")
	await press(actor, cart.interaction_owner, false)
	assert(cart.driver == null, "Unfocused E must not grab the cart")
	await grip(actor, cart, PI / 2)
	await drive(ship, actor, cart, outbound, "commons to Royalty threshold")
	await drive(ship, actor, cart, backing, "1.8 m backing through private threshold")
	await drive(ship, actor, cart, recover, "forward recovery through private threshold")
	await drive(ship, actor, cart, receiving, "receiving bay arrival")
	await press(actor, cart.interaction_owner, true, true)
	live_state(actor, cart, false)
	var parked: Vector3 = cart.global_position
	var behind := Vector2(actor.global_position.x, actor.global_position.z)
	for point in [Vector2(behind.x, 33.65), Vector2(102.6, 33.65), Vector2(102.6, 31.15), Vector2(behind.x, 31.15), behind]:
		await walk(ship, actor, cart, point)
	assert(cart.global_position.distance_to(parked) < .20, "Released receiving-bay cart drifted")
	await grip(actor, cart, -PI / 2)
	await drive(ship, actor, cart, turn, "moving receiving turn to face home")
	await drive(ship, actor, cart, returning, "forward return to D17 lift foyer")
	# While holding the handle, RMB/E remains a release even when looking at the
	# lift plate. Only the released operator can target the actual call control.
	var button: Node3D = lift.get_node("D17_commons_lift_call")
	assert(not lift.landing_gates[4].cabin_present_and_stopped)
	assert(not lift.landing_gates[4].request_open(), "Absent-cabin D17 gate must stay locked")
	for leaf_z in [-.9, -.3, .3, .9]:
		var gate_hit := ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(91.6, FLOOR + .9, leaf_z), Vector3(92.4, FLOOR + .9, leaf_z), 1))
		if gate_hit.is_empty():
			print("D17 ABSENT GATE RAY MISS: Z", leaf_z)
		else:
			print("D17 ABSENT GATE CONTACT: ", gate_hit.collider.get_path())
		assert(not gate_hit.is_empty() and lift.landing_gates[4].is_ancestor_of(gate_hit.collider), "All four absent-cabin D17 leaves require physical closure")
	await press(actor, button, true, true)
	assert(lift.destination_floor == 0, "Held handle must not remotely call the lift")
	live_state(actor, cart, false)
	parked = cart.global_position
	behind = Vector2(actor.global_position.x, actor.global_position.z)
	for point in [Vector2(behind.x, 1.35), Vector2(90.6, 1.35)]:
		await walk(ship, actor, cart, point)
	await blocked_gate_push(ship, actor, cart, lift.landing_gates[4])
	await press(actor, button, false)
	assert(lift.destination_floor == 0, "Unfocused E must not call the D17 cabin")
	await press(actor, button)
	assert(lift.destination_floor == 4, "Released focused operator must call D17")
	var arrived := false
	var travel: float = absf(FLOOR - lift.cabin.global_position.y)
	var budget: int = ceili((travel / lift.maximum_speed + lift.maximum_speed / lift.acceleration + 2.0 / .75 + 3.0) * 60)
	for frame in range(budget):
		await physics_frame
		waiting_frames += 1
		frame_budget()
		live_state(actor, cart, false)
		if lift.phase == "moving":
			assert(lift.cabin_gate.open_fraction < .001)
			for gate in lift.landing_gates:
				assert(gate.open_fraction < .001, "Lift landing gates must remain closed during call travel")
		if lift.current_floor == 4 and lift.phase == "idle":
			arrived = true
			break
	assert(arrived and lift.landing_gates[4].open_fraction > .999 and lift.cabin_gate.open_fraction > .999)
	assert(cart.global_position.distance_to(parked) < .20, "Cart moved while operator called the lift")
	for point in [Vector2(behind.x, 1.35), behind]:
		await walk(ship, actor, cart, point)
	await grip(actor, cart, -PI / 2)
	actor.set_physics_process(true)
	key(KEY_W, true)
	var boarded := false
	for frame in range(450):
		await physics_frame
		input_frames += 1
		frame_budget()
		live_state(actor, cart, true)
		live_support(ship, actor, cart, true)
		keyboard_peak_speed = maxf(keyboard_peak_speed, Vector2(actor.velocity.x, actor.velocity.z).length())
		if actor.global_position.x >= 92.42:
			boarded = true
			break
	key(KEY_W, false)
	assert(boarded, "Ordinary W input stalled while reboarding the D17 cabin")
	assert(keyboard_peak_speed > 1.95 and keyboard_peak_speed < 2.01, "Smoke check must exercise real 2 m/s held-cart speed")
	for frame in range(90):
		await physics_frame
		input_frames += 1
		live_state(actor, cart, true)
	assert(cart.global_position.x > 93.6 and cart.global_position.x < 94.5, "Loaded cart must physically finish inside the D17 cabin")
	actor.set_physics_process(false)
	await press(actor, cart.interaction_owner, true, true)
	await walk(ship, actor, cart, Vector2(92.95, 0), true)
	assert(not lift.cabin_gate.threshold_occupied() and not lift.landing_gates[4].threshold_occupied(), "Released operator and loaded cart must clear both actual gate planes")
	live_state(actor, cart, false)
	live_support(ship, actor, cart, true)
	var receipt := {
		"schema": 1, "status": "PASS", "test": "d17_connected_cart",
		"source_pins": {"AST-RES-006.glb": PLATFORM_SHA, "AST-COM-003.glb": COMMONS_SHA},
		"test_sha256": FileAccess.get_sha256("res://tests/validate_d17_connected_cart.gd"),
		"runtime_contract_sha256": FileAccess.get_sha256("res://data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json"),
		"geometric_poses": probe.sampled_poses, "planned_floor_rays": probe.floor_rays,
		"actual_wheel_operator_support_samples": support_samples, "verified_sill_bridge_samples": sill_bridge_samples,
		"moving_turn_samples": moving_turn_samples, "driven_1mps_frames": driven_frames,
		"on_foot_frames": walked_frames, "ordinary_input_frames": input_frames, "waiting_frames": waiting_frames,
		"ordinary_held_input_peak_mps": keyboard_peak_speed, "retained_loose_products": 4,
		"cart_final_world": [cart.global_position.x, cart.global_position.y, cart.global_position.z],
		"checks": ["source-pinned actual main scene", "compound cart/load/operator moving-pose sweeps", "per-wheel and actual operator floor support", "continuous commons-790 forward journey", "1.8m backing and forward recovery at private threshold", "precise RMB/E release and regrip with physical walk-around", "moving receiving turn and forward same-route return", "absent-cabin D17 four-leaf rays and actual capsule blocked at central seam", "released operator precise RMB/E call with unfocused rejection", "closed gates during D17 call travel", "ordinary 2m/s loaded D17 reboarding and released threshold clearance"],
		"limits": "Scripted 1m/s route plus ordinary straight 2m/s boarding; freehand turning feel, traffic/species capacity, moving suite door (not installed), private upper circulation, separate service network, full regression and final visual acceptance remain separate. No loaded inter-deck trip is claimed by this test."
	}
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	assert(file != null, "D17 cart pass receipt must be writable")
	file.store_string(JSON.stringify(receipt, "\t") + "\n")
	file.close()
	print("D17 CONNECTED CART PASS: ", probe.sampled_poses, " compound moving poses; ", support_samples, " actual wheel/operator support samples; continuous loaded forward round-trip, threshold backing recovery, precise release/regrip, receiving turn, D17 lift call and ordinary 2m/s reboarding. Four loose products retained. Freehand feel and full acceptance remain separate.")
	main.queue_free()
	await process_frame
	quit()
