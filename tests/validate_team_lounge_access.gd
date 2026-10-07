extends "res://tests/medical_test_scene.gd"
# Actual unchanged player, one verified arrival, then W-input traversal only.
const ROUTE := "res://tests/fixtures/team_lounge_access001.json"
const ROUTE_SHA := "e05fc4b7181ed1645acaec9025f3cce7e6cfc7dc353a5e707ff38b1e63c54e01"
var travelled_m := 0.0
var walked_frames := 0

func _initialize() -> void:
	test_name = "team_lounge_access"
	call_deferred("run")

func write_receipt(status: String, detail: String = "") -> void:
	if receipt_path.is_empty(): return
	var out := {"test":test_name,"status":status,"detail":detail,"physics_frames":frames,"walked_frames":walked_frames,"walked_m":travelled_m,"support_samples":support_samples,"route_sha256":FileAccess.get_sha256(ROUTE),"runtime_sha256":FileAccess.get_sha256("res://data/architecture/team_lounge/runtime_manifest.json"),"scope":"Actual player arrival, public threshold, both source cleaning circuits, refreshment/return approach and return to D07 spine. No loaded-cart, staff workpoint, species, performance or final art acceptance."}
	var file := FileAccess.open(receipt_path, FileAccess.WRITE)
	if file != null: file.store_string(JSON.stringify(out, "  ") + "\n")

func walk(point: Vector2) -> bool:
	release_inputs()
	var start := Vector2(actor.global_position.x, actor.global_position.z)
	var allowance := ceili(start.distance_to(point) / 3.1 * 60.0) + 240
	for frame in range(allowance):
		var delta := point - Vector2(actor.global_position.x, actor.global_position.z)
		var speed := Vector2(actor.velocity.x, actor.velocity.z).length()
		if delta.length() < .16 and speed < .08:
			key(KEY_W, false)
			return support_at(Vector3(point.x, 35.5, point.y))
		if delta.length() > .025: actor.rotation.y = atan2(-delta.x, -delta.y)
		actor.set("pitch", 0.0)
		actor.camera.rotation.x = 0.0
		key(KEY_W, delta.length() > maxf(.11, speed * speed / 32.0 + .035))
		var previous: Vector3 = actor.global_position
		if not await advance(1, false): return false
		if not require(actor.global_position.distance_to(previous) < .25, "Unexpected displacement after arrival"): return false
		if not require(absf(actor.global_position.y - 35.5) < .08, "Player left D07 floor datum"): return false
		if not support_at(Vector3(actor.global_position.x, 35.5, actor.global_position.z)): return false
		travelled_m += Vector2(actor.global_position.x - previous.x, actor.global_position.z - previous.z).length()
		walked_frames += 1
	return require(false, "W-input route blocked at " + str(actor.global_position) + " toward " + str(point))

func run() -> void:
	started = Time.get_ticks_msec()
	receipt_path = "res://artifacts/" + test_name + "_attempt_" + str(Time.get_unix_time_from_system()).replace(".", "_") + ".json"
	if not require(FileAccess.get_sha256(ROUTE) == ROUTE_SHA, "Pinned Team Lounge route required"): return
	data = JSON.parse_string(FileAccess.get_file_as_string(ROUTE))
	main = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150): await physics_frame
	ship = main.get_node("World360/Astraea") as Node3D
	actor = ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	cart = ship.find_child("CustodialCart", true, false) as RigidBody3D
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms", true, false) as Node3D
	built = ship.get_node("ShipSpace/D07_TeamLounge_Receiving_WIP") as Node3D
	space = ship.get_world_3d().direct_space_state
	if not require(actor != null and cart != null and floors != null and built != null, "Actual installed main-scene nodes required"): return
	var proof: Dictionary = load("res://tests/medical_triage_successor_guard.gd").validate_current(floors)
	if not require(bool(proof.get("validation_completed", false)), "Complete predecessor and Team Lounge proof failed"): return
	if not require(actor.get_script().resource_path == "res://scripts/player.gd" and actor.gameplay_input_enabled, "Original production player required"): return
	if not require(ship.arrive_at(Vector3(0, 35.6, 216), -PI / 2), "Initial D07 spine arrival refused"): return
	if not await advance(45, false): return
	if not support_at(Vector3(0, 35.5, 216), "D07_aft_route"): return
	for point in data.ordinary_player_waypoints_xz:
		if not await walk(Vector2(point[0], point[1])): return
	release_inputs()
	write_receipt("PASS")
	print("TEAM_LOUNGE_ACCESS PASS: ", travelled_m, " metres; ", walked_frames, " ordinary-input frames")
	main.queue_free()
	await process_frame
	quit(0)
