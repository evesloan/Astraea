extends SceneTree
# Actual main scene, existing cart, four loose bottles, capsule, tether, doors and
# staff lift. One initial fixture placement only. No later cart/product transform,
# velocity reset, freeze, parenting change, collision edit or controller change.
# 1m/s refers to bounded scripted operator movement; changing headings/positions
# drive the cart entirely through the existing physical force/torque controller.
# Ordinary 2m/s W input across BOTH wide service doors is a separate bounded smoke.
const CONTRACT := "res://data/architecture/GRAND_POOL_SECTION_RUNTIME.json"
const CONTRACT_SHA := "7173bdd7e5213059dcc48b74d596b2589ab805dea5d839ce1e8dda6044b458dd"
const RECEIPT := "res://docs/GRAND_POOL_SERVICE_CART_VALIDATION.json"
const SOURCE_QA_SHA := "457e35214b9d1c6bcbf92b95bf53ca5ab9048575d355e1c48d02db57e41a303e"
const MODEL_PINS := {
	"AST-AQU-016.glb": "95a72a20bd0ed653bb10622ff025b1003386020063587828b29efe5e8e40a481",
	"AST-STF-009_pool_market.glb": "5e1995b9e0114e8a4f28d9cd5d9c00efbb44ff2fb504d8a965eba613b0e7467a",
	"AST-CIR-005_forward_pool_market.glb": "538f8c6d1a3a075b48cdd63a8cb375c83b07f8100987e193b2efbfd39d134667",
	"AST-CIR-003_five_stop.glb": "6e2fa392f1cc84da8fa80e9b38ddf117a587fc4c4f4a47b631fd0143561eb19b",
	"AST-DOR-002_wide.glb": "f57ceb601ee3c625b0b5953d9d449527a30216ac5671f184cb98fd727cf0c49e"
}
const DRIVER_OFFSET := 1.62
# About450m of actual operator routes at1m/s, plus~50s initial call, two6.3m
# trips, released controls and settles. 1000s/60000 frames allow bounded route,
# control and contact overhead, but never an unbounded stalled bend/call.
const MAX_TRACKED_FRAMES := 60000
const WALL_WATCHDOG_MSEC := 1000000
var probe = preload("res://tests/grand_pool_cart_probe.gd").new()
var ship: Node3D
var actor: CharacterBody3D
var cart: RigidBody3D
var lift: Node3D
var built: Node3D
var floor_y := 46.2
var frames := 0
var driven_frames := 0
var walked_frames := 0
var input_frames := 0
var waiting_frames := 0
var support_samples := 0
var moving_turn_samples := 0
var ordinary_peak_mps := 0.0
var ordinary_smokes := 0
var loaded_trips := 0
var route_operator_metres := 0.0
var checkpoint := "prepared/unrun"
var started_msec := 0
var riding := false
var maximum_route_error := 0.0
var failure_recorded := false
var prior_attempts: Array = []
var ordinary_clearance_checks: Array = []
var interaction_ray_checks: Array = []

func _initialize() -> void:
	started_msec = Time.get_ticks_msec()
	probe.connect("failed", Callable(self, "record_failure"))
	var saved: Variant = JSON.parse_string(FileAccess.get_file_as_string(RECEIPT))
	if saved is Dictionary and saved.has("prior_attempts"): prior_attempts = saved.prior_attempts.duplicate()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if Time.get_ticks_msec() - started_msec > WALL_WATCHDOG_MSEC:
		write_receipt("FAIL", "1000-second wall-clock watchdog at " + checkpoint)
		push_error("Grand Pool service-cart watchdog: " + checkpoint)
		quit(1)
	return false

func record_failure(message: String) -> void:
	if failure_recorded: return
	failure_recorded = true
	write_receipt("FAIL", message + " at " + checkpoint)
	push_error("Grand Pool service cart: " + message)
	quit(1)

func require(condition: bool, message: String = "Grand Pool assertion failed") -> bool:
	# Every caller must return onfalse. A failed helper assertion does not
	# unwind the caller and previously allowed a misleading PASS log line.
	if condition: return true
	record_failure(message)
	return false

func tick() -> void:
	if failure_recorded: return
	frames += 1
	if not require(frames < MAX_TRACKED_FRAMES, "Grand Pool cart exceeded derived frame allowance at " + checkpoint): return

func write_receipt(status: String, detail: String = "") -> void:
	if failure_recorded and status != "FAIL": return
	var result := {
		"schema": 1, "test": "grand_pool_service_cart", "status": status,
		"checkpoint": checkpoint, "detail": detail, "prior_attempts": prior_attempts,
		"test_sha256": FileAccess.get_sha256("res://tests/validate_grand_pool_service_cart.gd"),
		"probe_sha256": FileAccess.get_sha256("res://tests/grand_pool_cart_probe.gd"),
		"runtime_contract_sha256": CONTRACT_SHA, "source_pins": MODEL_PINS,
		"source_geometric_evidence": {"catalogue_commit": "c333b25", "qa_sha256": SOURCE_QA_SHA, "retained_poses": 532, "minimum_proxy_clearance_m": .13951491439718214, "scope": "Retained source geometric evidence only; not replayed or counted as force-driven proof"},
		"planned_live_compound_poses": probe.sampled_poses, "planned_support_rays": probe.floor_rays,
		"actual_wheel_operator_support_samples": support_samples, "verified_sill_bridge_rays": probe.sill_bridge_rays,
		"scripted_operator_speed_limit_mps": 1.0, "ordinary_held_input_speed_mps": 2.0,
		"driven_frames": driven_frames, "released_walk_frames": walked_frames,
		"ordinary_input_and_control_frames": input_frames, "waiting_frames": waiting_frames,
		"tracked_frames": frames, "maximum_frames": MAX_TRACKED_FRAMES, "wall_watchdog_seconds": 1000,
		"scripted_operator_route_metres": route_operator_metres, "moving_turn_pose_samples": moving_turn_samples,
		"ordinary_input_peak_mps": ordinary_peak_mps, "ordinary_service_door_smokes": ordinary_smokes,
		"ordinary_actual_clearance_checks": ordinary_clearance_checks,
		"actual_interaction_ray_checks": interaction_ray_checks,
		"actual_loaded_upper_staff_lift_trips": loaded_trips, "maximum_cart_route_error_m": maximum_route_error,
		"loose_products": 4, "initial_fixture_placements": 1,
		"limits": "Scripted operator route plus bounded ordinary straight2m/s input; no freehand turning comfort, traffic/species fitting, water physics, stock, local public lift/full five-stop regression, visual acceptance or full programme completion is certified. Collisions, source fittings and the eight-light cap are unchanged."
	}
	if is_instance_valid(cart):
		result["cart_world"] = [cart.global_position.x, cart.global_position.y, cart.global_position.z]
		result["cart_rotation_radians"] = [cart.rotation.x, cart.rotation.y, cart.rotation.z]
		result["cart_linear_velocity"] = [cart.linear_velocity.x, cart.linear_velocity.y, cart.linear_velocity.z]
		result["cart_angular_velocity"] = [cart.angular_velocity.x, cart.angular_velocity.y, cart.angular_velocity.z]
	if is_instance_valid(actor): result["operator_world"] = [actor.global_position.x, actor.global_position.y, actor.global_position.z]
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	if not require(file != null, "Grand Pool cart receipt must be writable"): return
	file.store_string(JSON.stringify(result, "\t") + "\n")
	file.close()

func mark(label: String) -> void:
	if failure_recorded: return
	checkpoint = label
	write_receipt("RUNNING")
	print("GRAND POOL CART CHECKPOINT: ", label)

func append_pose(path: Array[Vector3], pose: Vector3) -> void:
	path.append(pose)

func line(path: Array[Vector3], a: Vector2, b: Vector2, backing := false) -> void:
	var delta := b - a
	if not require(delta.length() > .001): return
	var yaw := atan2(-delta.x, -delta.y) + (PI if backing else 0.0)
	if not path.is_empty():
		var previous: Vector3 = path.back()
		if not require(Vector2(previous.x, previous.y).distance_to(a) < .001, "Continuous Grand Pool cart route required"): return
		if not require(absf(wrapf(previous.z - yaw, -PI, PI)) < .001, "No fixed-centre heading snap"): return
	var count := maxi(1, ceili(delta.length() / .08))
	for index in range(count + 1):
		var p := a.lerp(b, float(index) / count)
		append_pose(path, Vector3(p.x, p.y, yaw))

func arc(path: Array[Vector3], centre: Vector2, radius: float, start: float, finish: float) -> void:
	var count := maxi(1, ceili(absf(finish - start) * sqrt(radius * radius + DRIVER_OFFSET * DRIVER_OFFSET) / .055))
	for index in range(count + 1):
		var angle := lerpf(start, finish, float(index) / count)
		var p := centre + Vector2(cos(angle), sin(angle)) * radius
		var direction := Vector2(-sin(angle), cos(angle)) * signf(finish - start)
		var yaw := atan2(-direction.x, -direction.y)
		if index == 0 and not path.is_empty():
			var previous: Vector3 = path.back()
			if not require(Vector2(previous.x, previous.y).distance_to(p) < .001): return
			if not require(absf(wrapf(previous.z - yaw, -PI, PI)) < .001): return
		append_pose(path, Vector3(p.x, p.y, yaw))
		if index > 0: moving_turn_samples += 1

func street_outbound() -> Array[Vector3]:
	var path: Array[Vector3] = []
	line(path, Vector2(-21,-491.5), Vector2(-21,-498.5))
	arc(path, Vector2(-22.5,-498.5), 1.5, 0, -PI/2)
	line(path, Vector2(-22.5,-500), Vector2(-55.5,-500))
	arc(path, Vector2(-55.5,-498.5), 1.5, -PI/2, -PI)
	line(path, Vector2(-57,-498.5), Vector2(-57,-464.5))
	arc(path, Vector2(-55.5,-464.5), 1.5, PI, PI/2)
	return path

func street_return() -> Array[Vector3]:
	var path: Array[Vector3] = []
	# Park0.7m farther west than outbound so the released operator can close
	# the real door while still safely outside its leaf/capsule sweep.
	arc(path, Vector2(-56.2,-464.6), .8, PI/2, PI)
	line(path, Vector2(-57,-464.6), Vector2(-57,-498.5))
	arc(path, Vector2(-55.5,-498.5), 1.5, PI, PI*1.5)
	line(path, Vector2(-55.5,-500), Vector2(-22.5,-500))
	arc(path, Vector2(-22.5,-498.5), 1.5, -PI/2, 0)
	line(path, Vector2(-21,-498.5), Vector2(-21,-491.5))
	return path

func vestibule_outbound() -> Array[Vector3]:
	var path: Array[Vector3] = []
	arc(path, Vector2(-52.95,-462), 1.0, -PI/2, 0)
	line(path, Vector2(-51.95,-462), Vector2(-51.95,-459.2))
	arc(path, Vector2(-50.75,-459.2), 1.2, PI, PI/2)
	line(path, Vector2(-50.75,-458), Vector2(-46.6,-458))
	return path

func receiving_turn() -> Array[Vector3]:
	var path: Array[Vector3] = []
	# Bounded destination manoeuvre, only1.2m north of the receiving line.
	# Both floor polygons and all source solids pass independent geometric
	# checking; actual dynamics still decide whether this manoeuvre is usable.
	arc(path, Vector2(-46.6,-457.4), .6, -PI/2, PI/2)
	arc(path, Vector2(-46.6,-457.2), .4, PI/2, PI)
	line(path, Vector2(-47,-457.2), Vector2(-47,-457.4))
	arc(path, Vector2(-47.6,-457.4), .6, 0, -PI/2)
	line(path, Vector2(-47.6,-458), Vector2(-49,-458))
	return path

func vestibule_return() -> Array[Vector3]:
	var path: Array[Vector3] = []
	# Forward return places the operator on the opposite side from outbound.
	# Reversing the1m outbound bend made that capsule cross the privacy screen.
	# This supported1.7m/4.1m pair keeps the actual operator envelope west of
	# the baffle and crosses the real open service aperture, with no wall edits.
	line(path, Vector2(-49,-458), Vector2(-50.25,-458))
	arc(path, Vector2(-50.25,-459.7), 1.7, PI/2, PI)
	arc(path, Vector2(-56.05,-459.7), 4.1, 0, -PI/2)
	line(path, Vector2(-56.05,-463.8), Vector2(-56.2,-463.8))
	return path

func reversed_backing(path: Array[Vector3]) -> Array[Vector3]:
	var result: Array[Vector3] = []
	for index in range(path.size() - 1, -1, -1): append_pose(result, path[index])
	return result

func check_load() -> void:
	if failure_recorded: return
	if not require(cart.products.size() == 4): return
	for product in cart.products:
		if not require(product.get_parent() == cart.get_parent(), "Loose products must stay independent of cart/lift"): return
		var p: Vector3 = cart.to_local(product.global_position)
		if not require(p.is_finite() and p.y > .8 and p.y < 1.3 and absf(p.x) < .4 and absf(p.z) < .6, "Grand Pool loose product escaped tray: " + str(p)): return

func state(held: bool) -> void:
	if failure_recorded: return
	if not require(cart.global_position.is_finite() and cart.linear_velocity.length() < 8): return
	if not require(cart.global_basis.y.dot(Vector3.UP) > .90, "Grand Pool cart tipped"): return
	var expected_y: float = lift.cabin.global_position.y if riding else floor_y
	if not require(absf(cart.global_position.y - expected_y) < .16 and absf(actor.global_position.y - expected_y) < .18, "Cart/operator left supported floor or actual lift: cart=%s actor=%s expectedY=%s checkpoint=%s" % [cart.global_position,actor.global_position,expected_y,checkpoint]): return
	if not require(cart.get_parent().name == "PersistentActors"): return
	if held:
		if not require(cart.driver == actor and actor.held_interaction == cart.interaction_owner, "Grand Pool physical tether lost"): return
	else:
		if not require(cart.driver == null and actor.held_interaction == null, "Precise controls require handle release"): return
	check_load()

func support(at_lift := false) -> void:
	if failure_recorded: return
	var space := ship.get_world_3d().direct_space_state
	var excluded: Array[RID] = probe.controlled_exclusions(actor, cart)
	var expected_y: float = lift.cabin.global_position.y if riding else floor_y
	var cabin: Node3D = lift.cabin if riding else null
	for index in range(probe.wheel_specs.size()):
		var p: Array = probe.wheel_specs[index].center
		probe.floor_at(space, cart.global_transform * Vector3(p[0],p[1],p[2]), expected_y, excluded, "live wheel " + str(index), at_lift, cabin)
		support_samples += 1
	probe.floor_at(space, actor.global_position, expected_y, excluded, "live operator foot", at_lift, cabin)
	support_samples += 1

func light_cap() -> void:
	if failure_recorded: return
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	if not require(budget.shadow_source_budget == 8): return
	budget.refresh()
	var active := 0
	for light in budget.sources:
		if light.visible and light.shadow_enabled: active += 1
	if not require(active <= 8, "Grand Pool service route must retain the existing eight-light cap"): return

func sweep(path: Array[Vector3], label: String, at_lift := false) -> void:
	if failure_recorded: return
	mark("Y%s %s geometric preflight" % [floor_y,label])
	for pose in path:
		probe.check_pose(ship, actor, cart, Vector3(pose.x,floor_y+.03,pose.y), pose.z, floor_y, at_lift)
		if failure_recorded: return
	print("GRAND POOL CART GEOMETRY: ", label, " poses:", path.size(), " all active contacts retained")

func settle(count: int, held: bool, at_lift := false) -> void:
	if failure_recorded: return
	actor.velocity = Vector3.ZERO
	for frame in range(count):
		await physics_frame
		if failure_recorded: return
		waiting_frames += 1
		tick()
		state(held)
		if failure_recorded: return
		if frame % 6 == 0: support(at_lift)

func drive(path: Array[Vector3], label: String, at_lift := false) -> void:
	if failure_recorded: return
	mark(label)
	for pose in path:
		var target := Vector3(pose.x,floor_y,pose.y) + Basis(Vector3.UP,pose.z) * Vector3(0,0,DRIVER_OFFSET)
		actor.rotation.y = pose.z
		var reached := false
		for frame in range(120):
			var delta := target - actor.global_position
			delta.y = 0
			if delta.length() < .025:
				reached = true
				break
			var speed := delta.limit_length(1.0/60) * 60
			actor.velocity = Vector3(speed.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,speed.z)
			var old_position := actor.global_position
			actor.move_and_slide()
			route_operator_metres += Vector2(actor.global_position.x-old_position.x,actor.global_position.z-old_position.z).length()
			await physics_frame
			if failure_recorded: return
			driven_frames += 1
			tick()
			state(true)
			if failure_recorded: return
			maximum_route_error = maxf(maximum_route_error, Vector2(cart.global_position.x-pose.x,cart.global_position.z-pose.y).length())
			if driven_frames % 6 == 0: support(at_lift)
		if not reached:
			for index in range(actor.get_slide_collision_count()): print("GRAND POOL CART DRIVER BLOCK: ",actor.get_slide_collision(index).get_collider().get_path())
			write_receipt("FAIL", "%s driver stalled at%s toward%s; cart%s" % [label,actor.global_position,target,cart.global_position])
		if not require(reached, "%s driver stalled at%s toward%s; cart%s" % [label,actor.global_position,target,cart.global_position]): return
	await settle(75,true,at_lift)
	if failure_recorded: return
	var end: Vector3 = path.back()
	var error := Vector2(cart.global_position.x,cart.global_position.z).distance_to(Vector2(end.x,end.y))
	if not require(error < .65, label + " cart missed actual endpoint; error=" + str(error)): return
	support(at_lift)
	if failure_recorded: return
	light_cap()
	if failure_recorded: return
	print("GRAND POOL CART DRIVEN: ",label," cart:",cart.global_position," operator:",actor.global_position)

func released_walk_preflight(target: Vector2) -> void:
	if failure_recorded: return
	# Use the actual parked cart/load transforms, not the ideal route endpoint.
	# Only the current capsule is excluded. The parked cart and loose products,
	# every door leaf/pocket and all walls/gates remain collision-query targets.
	var start := Vector2(actor.global_position.x,actor.global_position.z)
	var count := maxi(1,ceili(start.distance_to(target)/.05))
	var capsule := CapsuleShape3D.new()
	capsule.radius = .3
	capsule.height = 1.8
	var excluded: Array[RID] = [actor.get_rid()]
	var space := ship.get_world_3d().direct_space_state
	for index in range(count+1):
		var p := start.lerp(target,float(index)/count)
		probe.clear_shape(space,capsule,Transform3D(Basis.IDENTITY,Vector3(p.x,floor_y+.91,p.y)),excluded,"Released operator path at " + str(p))
		if failure_recorded: return

func walk(target: Vector2, at_lift := false) -> void:
	if failure_recorded: return
	released_walk_preflight(target)
	if failure_recorded: return
	var reached := false
	var span := Vector2(actor.global_position.x,actor.global_position.z).distance_to(target)
	var allowance := ceili(span/3.1*60) + 240
	for frame in range(allowance):
		var delta := Vector3(target.x-actor.global_position.x,0,target.y-actor.global_position.z)
		if delta.length() < .025:
			reached = true
			break
		var speed := delta.limit_length(3.1/60) * 60
		actor.velocity = Vector3(speed.x,-.1 if actor.is_on_floor() else actor.velocity.y-9.8/60,speed.z)
		actor.move_and_slide()
		await physics_frame
		if failure_recorded: return
		walked_frames += 1
		tick()
		state(false)
		if failure_recorded: return
		if walked_frames % 6 == 0: support(at_lift)
	if not reached:
		print("GRAND POOL RELEASED OPERATOR DIAGNOSIS: cart:",cart.global_transform," velocity:",cart.linear_velocity," operator_cart_local:",cart.to_local(actor.global_position))
		for index in range(actor.get_slide_collision_count()): print("GRAND POOL RELEASED OPERATOR BLOCK: ",actor.get_slide_collision(index).get_collider().get_path())
		write_receipt("FAIL", "Released operator stalled at%s toward%s" % [actor.global_position,target])
	if not require(reached, "Released operator stalled at%s toward%s" % [actor.global_position,target]): return
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

func aim(point: Vector3) -> void:
	var delta: Vector3 = point - actor.camera.global_position
	actor.rotation.y = atan2(-delta.x,-delta.z)
	actor.pitch = atan2(delta.y,Vector2(delta.x,delta.z).length())
	actor.camera.rotation.x = actor.pitch

func interaction_view_probe(target: Node3D, point: Vector3) -> Dictionary:
	# Match the ordinary player's exact2.5m ray and collision/area policy.
	var origin: Vector3 = actor.camera.global_position
	var endpoint: Vector3 = origin-actor.camera.global_basis.z*2.5
	var query := PhysicsRayQueryParameters3D.create(origin,endpoint)
	query.exclude = [actor.get_rid()]
	query.collide_with_areas = true
	var hit := ship.get_world_3d().direct_space_state.intersect_ray(query)
	var resolved: Node = actor.target_from_view()
	var result := {"checkpoint":checkpoint,"expected_target":str(target.get_path()),"aim_world":[point.x,point.y,point.z],"camera_world":[origin.x,origin.y,origin.z],"ray_end_world":[endpoint.x,endpoint.y,endpoint.z],"aim_distance_m":origin.distance_to(point),"resolved_target":str(resolved.get_path()) if resolved != null else "none"}
	if not hit.is_empty():
		result["first_collider"] = str(hit.collider.get_path())
		result["first_hit_world"] = [hit.position.x,hit.position.y,hit.position.z]
	return result

func press(target: Node3D, point: Vector3, focused := true, held_release := false) -> void:
	if failure_recorded: return
	aim(point)
	if not held_release:
		var view := interaction_view_probe(target,point)
		interaction_ray_checks.append(view)
		if actor.target_from_view() != target:
			print("GRAND POOL PRECISE VIEW RAY BLOCK: ",view)
			write_receipt("FAIL", "Precise RMB/E target unavailable: " + str(target.get_path()))
		if not require(actor.target_from_view() == target, "Precise Grand Pool target unavailable: " + str(target.get_path())): return
	actor.velocity = Vector3.ZERO
	actor.set_physics_process(true)
	focus(focused)
	key(KEY_E,true)
	for frame in range(3):
		await physics_frame
		if failure_recorded: return
		input_frames += 1
		tick()
	key(KEY_E,false)
	focus(false)
	actor.set_physics_process(false)
	actor.velocity = Vector3.ZERO

func grip(yaw: float) -> void:
	if failure_recorded: return
	await press(cart.interaction_owner,cart.interaction_owner.global_position)
	if failure_recorded: return
	if not require(cart.driver == actor and actor.held_interaction == cart.interaction_owner): return
	actor.rotation.y = yaw
	actor.pitch = 0
	actor.camera.rotation.x = 0

func door_for() -> Node3D:
	return built.get_node(NodePath(("GrandPoolDoor_service_" + ("46.2" if floor_y < 50 else "52.5")).validate_node_name()))

func door_point(door: Node3D) -> Vector3:
	# The fully retracted leaf centre sits behind the retained staff north wall.
	# Aim at a real leaf point nearer its aperture-facing edge instead. The
	# existing2.5m view ray remains intact and may hit its own fitted pocket skin.
	# This works geometrically from either side without reaching through a wall.
	return door.leaves[0].global_transform * Vector3(door.leaf_width*.4,1.26,0)

func operate_door(opened: bool, held_yaw: float) -> void:
	if failure_recorded: return
	var door := door_for()
	if not require(door.visual_file == "AST-DOR-002_wide.glb"): return
	var before: bool = door.desired_open
	await press(door,door_point(door),true,true)
	if failure_recorded: return
	state(false)
	if failure_recorded: return
	if not require(door.desired_open == before, "Held RMB/E must release rather than remotely toggle door"): return
	var parked: Vector3 = cart.global_position
	var behind := Vector2(actor.global_position.x,actor.global_position.z)
	# Extra clearance for the actual0.185m northward parked-cart offset inRun001.
	# Z-461.85 stays0.53m inside the retained upper-street north wall plane.
	print("GRAND POOL DOOR WALK-AROUND: cart:",cart.global_transform," velocity:",cart.linear_velocity," operator:",actor.global_position)
	await walk(Vector2(behind.x,-461.85))
	if failure_recorded: return
	await walk(Vector2(-55.2,-461.85))
	if failure_recorded: return
	await press(door,door_point(door),false)
	if failure_recorded: return
	if not require(door.desired_open == before, "Unfocused E must not operate service door"): return
	await press(door,door_point(door))
	if failure_recorded: return
	if not require(door.desired_open == opened, "Released focused RMB/E must operate actual wide door"): return
	var reached := false
	for frame in range(180):
		await physics_frame
		if failure_recorded: return
		waiting_frames += 1
		tick()
		state(false)
		if failure_recorded: return
		if frame % 6 == 0: support()
		if (opened and door.open_fraction > .999) or (not opened and door.open_fraction < .001):
			reached = true
			break
	if not require(reached, "Service door failed bounded physical movement"): return
	if not require(cart.global_position.distance_to(parked) < .20, "Released cart drifted during door control"): return
	await walk(Vector2(behind.x,-461.85))
	if failure_recorded: return
	await walk(behind)
	if failure_recorded: return
	await grip(held_yaw)
	if failure_recorded: return

func ordinary_door_smoke() -> void:
	if failure_recorded: return
	mark("Y%s ordinary2m/s W across actual wide service door" % floor_y)
	actor.rotation.y = -PI/2
	actor.pitch = 0
	actor.camera.rotation.x = 0
	actor.set_physics_process(true)
	key(KEY_W,true)
	var reached := false
	var local_peak := 0.0
	for frame in range(300):
		await physics_frame
		if failure_recorded: return
		input_frames += 1
		tick()
		state(true)
		if failure_recorded: return
		support()
		if failure_recorded: return
		local_peak = maxf(local_peak,Vector2(actor.velocity.x,actor.velocity.z).length())
		if actor.global_position.x >= -54.57:
			reached = true
			break
	key(KEY_W,false)
	for frame in range(90):
		await physics_frame
		if failure_recorded: return
		input_frames += 1
		tick()
		state(true)
		if failure_recorded: return
		if frame % 6 == 0: support()
	actor.set_physics_process(false)
	actor.velocity = Vector3.ZERO
	if not require(reached, "Ordinary2m/s W stalled at actual wide service door"): return
	if not require(local_peak > 1.95 and local_peak < 2.01, "Smoke must exercise real2m/s held-cart input"): return
	# Geometry, not an arbitrary cart-centre stopping window, decides clearance.
	# Include every actual cart contact and all four independent product shapes.
	var loaded_bounds: Vector2 = probe.actual_loaded_cart_x_bounds(cart)
	var fitting_bounds: Vector2 = probe.collision_world_x_bounds(door_for())
	var passed_door_clearance := loaded_bounds.x-fitting_bounds.y
	var before_baffle_clearance := -51.2-loaded_bounds.y
	ordinary_peak_mps = maxf(ordinary_peak_mps,local_peak)
	ordinary_clearance_checks.append({"floor_y":floor_y,"peak_mps":local_peak,"loaded_world_x":[loaded_bounds.x,loaded_bounds.y],"actual_fitting_world_x":[fitting_bounds.x,fitting_bounds.y],"baffle_west_face_x":-51.2,"past_fitting_clearance_m":passed_door_clearance,"before_baffle_clearance_m":before_baffle_clearance,"required_query_margin_m":.001})
	if not require(loaded_bounds.is_finite() and fitting_bounds.is_finite(), "Actual loaded-cart/fitting geometry bounds unavailable"): return
	if not require(passed_door_clearance > .001 and before_baffle_clearance > .001, "Actual loaded cart/products must clear the complete door fitting and remain before the baffle: " + str(ordinary_clearance_checks.back())): return
	ordinary_peak_mps = maxf(ordinary_peak_mps,local_peak)
	ordinary_smokes += 1
	print("GRAND POOL ORDINARY INPUT PASS: Y",floor_y," peak:",local_peak," cart:",cart.global_position)

func service_round_trip(outgoing: Array[Vector3], returning: Array[Vector3], vestibule: Array[Vector3], back_home: Array[Vector3], turn: Array[Vector3]) -> void:
	if failure_recorded: return
	mark("Y%s upper-street outbound preflight" % floor_y)
	sweep(outgoing,"upper-street outbound")
	await drive(outgoing,"Y%s upper-street outbound" % floor_y)
	if failure_recorded: return
	await operate_door(true,-PI/2)
	if failure_recorded: return
	var backing: Array[Vector3] = []
	line(backing,Vector2(-46.6,-458),Vector2(-48,-458),true)
	var recovering: Array[Vector3] = []
	line(recovering,Vector2(-48,-458),Vector2(-46.6,-458))
	for entry in [[vestibule,"screened vestibule forward"],[backing,"1.4m backing recovery"],[recovering,"forward recovery"],[turn,"bounded programme turnaround"],[back_home,"screened vestibule forward return"],[returning,"upper-street forward return"]]: sweep(entry[0],entry[1])
	await ordinary_door_smoke()
	if failure_recorded: return
	await drive(vestibule,"Y%s screened vestibule into actual programme" % floor_y)
	if failure_recorded: return
	await drive(backing,"Y%s 1.4m public-mouth backing recovery" % floor_y)
	if failure_recorded: return
	await drive(recovering,"Y%s public-mouth forward recovery" % floor_y)
	if failure_recorded: return
	await drive(turn,"Y%s bounded moving programme turnaround" % floor_y)
	if failure_recorded: return
	await drive(back_home,"Y%s screened vestibule forward return" % floor_y)
	if failure_recorded: return
	await operate_door(false,PI/2)
	if failure_recorded: return
	await drive(returning,"Y%s upper-street forward return to staff lift" % floor_y)
	if failure_recorded: return
	if not require(not door_for().desired_open and door_for().open_fraction < .001): return

func wait_lift(goal: int, carrying: bool) -> void:
	if failure_recorded: return
	var travel: float = absf(lift.floor_heights[goal]-lift.cabin.position.y)
	var allowance := ceili((travel/lift.maximum_speed + lift.maximum_speed/lift.acceleration + 2.0/.75 + 4.0)*60)
	var reached := false
	var previous_speed := 0.0
	if carrying:
		riding = true
		actor.set_physics_process(true)
	for frame in range(allowance):
		await physics_frame
		if failure_recorded: return
		waiting_frames += 1
		tick()
		state(false)
		if failure_recorded: return
		if not require(absf(lift.travel_velocity) <= lift.maximum_speed+.001): return
		if lift.phase == "moving":
			if not require(lift.cabin_gate.open_fraction < .001): return
			for gate in lift.landing_gates:
				if not require(gate.open_fraction < .001, "All existing staff landing gates must stay closed during actual transfer"): return
			if not require(absf(lift.travel_velocity-previous_speed) < .025): return
		previous_speed = lift.travel_velocity
		if frame % 6 == 0: support(carrying)
		if lift.current_floor == goal and lift.phase == "idle":
			reached = true
			break
	if not reached: write_receipt("FAIL", "Staff lift stalled: phase%s goal%s current%s" % [lift.phase,goal,lift.current_floor])
	if not require(reached, "Staff lift failed bounded real call/loaded transfer"): return
	if carrying:
		floor_y = lift.cabin.global_position.y
		riding = false
		actor.set_physics_process(false)
		actor.velocity = Vector3.ZERO
		loaded_trips += 1
	if not require(lift.cabin_gate.open_fraction > .999 and lift.landing_gates[goal].open_fraction > .999): return

func call_wet_staff_lift() -> void:
	if failure_recorded: return
	mark("Released precise D08_WET staff lift call")
	var button: Node3D = lift.get_node("D08_WET_forward_staff_lift_call")
	var old_goal: int = lift.destination_floor
	await press(button,button.global_position,true,true)
	if failure_recorded: return
	state(false)
	if failure_recorded: return
	if not require(lift.destination_floor == old_goal, "Held RMB/E must release without remotely calling lift"): return
	var parked: Vector3 = cart.global_position
	var behind := Vector2(actor.global_position.x,actor.global_position.z)
	await walk(Vector2(-22,-493.12))
	if failure_recorded: return
	await walk(Vector2(-22,-492.9))
	if failure_recorded: return
	await press(button,button.global_position,false)
	if failure_recorded: return
	if not require(lift.destination_floor == old_goal): return
	await press(button,button.global_position)
	if failure_recorded: return
	if not require(lift.destination_floor == 3): return
	await wait_lift(3,false)
	if failure_recorded: return
	if not require(cart.global_position.distance_to(parked) < .20, "Released cart moved during actual staff lift call"): return
	await walk(Vector2(-22,-493.12))
	if failure_recorded: return
	await walk(behind)
	if failure_recorded: return
	await grip(PI)
	if failure_recorded: return

func upper_transfer(goal: int) -> void:
	if failure_recorded: return
	mark("Y%s actual loaded staff lift boarding/transfer to index%s" % [floor_y,goal])
	if not require(lift.current_floor == (3 if floor_y < 50 else 4) and lift.phase == "idle"): return
	var approach: Array[Vector3] = []
	arc(approach,Vector2(-22.5,-491.5),1.5,0,PI/2)
	line(approach,Vector2(-22.5,-490),Vector2(-25.6,-490))
	var exiting := reversed_backing(approach)
	sweep(approach,"actual staff lift curved boarding",true)
	await drive(approach,"actual curved loaded staff lift boarding",true)
	if failure_recorded: return
	await press(cart.interaction_owner,cart.interaction_owner.global_position,true,true)
	if failure_recorded: return
	state(false)
	if failure_recorded: return
	if not require(not lift.cabin_gate.threshold_occupied() and not lift.landing_gates[lift.current_floor].threshold_occupied(), "Actual loose cart/operator must fully clear both gate planes before departure"): return
	var behind := Vector2(actor.global_position.x,actor.global_position.z)
	var button: Node3D = lift.cabin.get_node("forward_staff_cabin_" + ("D09" if goal == 4 else "D08_WET"))
	await walk(Vector2(behind.x,-491.10),true)
	if failure_recorded: return
	await walk(Vector2(button.global_position.x,-491.10),true)
	if failure_recorded: return
	await press(button,button.global_position,false)
	if failure_recorded: return
	if not require(lift.phase == "idle", "Unfocused E must not select upper staff destination"): return
	await press(button,button.global_position)
	if failure_recorded: return
	if not require(lift.destination_floor == goal and lift.phase == "closing"): return
	await wait_lift(goal,true)
	if failure_recorded: return
	await walk(Vector2(behind.x,-491.10),true)
	if failure_recorded: return
	await walk(behind,true)
	if failure_recorded: return
	await grip(PI/2)
	if failure_recorded: return
	sweep(exiting,"actual loaded staff lift backing exit",true)
	await drive(exiting,"actual loaded staff lift backing exit to supported upper lobby",true)
	if failure_recorded: return
	if not require(Vector2(cart.global_position.x+21,cart.global_position.z+491.5).length() < .65): return

func lobby_handle_walkaround() -> void:
	if failure_recorded: return
	# Additional real handle-around reorientation after backing out of the cabin.
	# The planned cart centre is stationary here, but the operator walks1.62m
	# radius; no cart angle/position is assigned. This is not counted as a moving
	# cart-turn proof; the programme/street/vestibule curves supply that proof.
	var path: Array[Vector3] = []
	for index in range(101): append_pose(path,Vector3(-21,-491.5,lerpf(PI,0,float(index)/100)))
	sweep(path,"bounded physical lobby handle walk-around")
	await drive(path,"bounded physical upper-lobby handle walk-around")
	if failure_recorded: return

func run() -> void:
	if failure_recorded: return
	if not require(FileAccess.get_sha256(CONTRACT) == CONTRACT_SHA): return
	for file in MODEL_PINS:
		if not require(FileAccess.get_sha256("res://assets/models/"+str(file)) == MODEL_PINS[file], "Frozen model pin changed: "+str(file)): return
	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150): await physics_frame
	ship = main.get_node("World360/Astraea")
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	cart = ship.find_child("CustodialCart",true,false)
	lift = ship.find_child("ForwardStaffLift",true,false)
	built = ship.find_child("GrandPoolOrchardSection_WIP",true,false)
	if not require(lift.persistent_id == &"forward_staff_lift_001" and lift.floor_heights == [0.0,6.0,12.0,46.2,52.5]): return
	if not require(lift.stop_ids == ["D01","D02","D03","D08_WET","D09"] and lift.cabin_file == "AST-CIR-003_five_stop.glb"): return
	if not require(lift.current_floor == 0 and lift.phase == "idle"): return
	var local_products: Array[Vector3] = []
	for product in cart.products: local_products.append(cart.to_local(product.global_position))
	if not require(local_products.size() == 4): return
	actor.set_physics_process(false)
	# Sole initial fixture placement. Nothing below resets these rigid bodies.
	cart.global_position = Vector3(-21,46.24,-491.5)
	cart.rotation = Vector3.ZERO
	cart.linear_velocity = Vector3.ZERO
	cart.angular_velocity = Vector3.ZERO
	cart.sleeping = false
	for index in range(4):
		cart.products[index].global_position = cart.global_transform * local_products[index]
		cart.products[index].linear_velocity = Vector3.ZERO
		cart.products[index].angular_velocity = Vector3.ZERO
		cart.products[index].sleeping = false
	actor.global_position = Vector3(-21,46.23,-489.88)
	actor.rotation.y = 0
	actor.velocity = Vector3.ZERO
	await settle(90,false)
	if failure_recorded: return
	mark("Loaded wet-staff fixture settled once on real compiler floor")
	light_cap()
	if failure_recorded: return
	var outgoing := street_outbound()
	var returning := street_return()
	var vestibule := vestibule_outbound()
	var back_home := vestibule_return()
	var turn := receiving_turn()
	await press(cart.interaction_owner,cart.interaction_owner.global_position,false)
	if failure_recorded: return
	if not require(cart.driver == null, "Unfocused E must not grip cart"): return
	await grip(0)
	if failure_recorded: return
	await service_round_trip(outgoing,returning,vestibule,back_home,turn)
	if failure_recorded: return
	await call_wet_staff_lift()
	if failure_recorded: return
	await upper_transfer(4)
	if failure_recorded: return
	await lobby_handle_walkaround()
	if failure_recorded: return
	await service_round_trip(outgoing,returning,vestibule,back_home,turn)
	if failure_recorded: return
	await upper_transfer(3)
	if failure_recorded: return
	await press(cart.interaction_owner,cart.interaction_owner.global_position,true,true)
	if failure_recorded: return
	state(false)
	if failure_recorded: return
	support()
	if failure_recorded: return
	light_cap()
	if failure_recorded: return
	if not require(ordinary_smokes == 2 and loaded_trips == 2 and moving_turn_samples > 500): return
	checkpoint = "both upper service routes returned forward; actual loaded staff lift up/down complete"
	write_receipt("PASS")
	print("GRAND POOL SERVICE CART PASS: actual four-loose-product cart through both upper streets and screened vestibules; ordinary2m/s W across both wide service doors; precise RMB/E release/control/regrip;1.4m backing/forward recovery; bounded moving programme turn and forward-facing returns; physical curved boarding, two loaded staff-lift transfers and backing exits; ",support_samples," actual wheel/operator support samples. Scripted/freehand comfort and full programme acceptance remain separate.")
	main.queue_free()
	await process_frame
	if failure_recorded: return
	quit(0)
