extends SceneTree
# Bounded actual-engine candidate fixture, never a full-main acceptance substitute.
var world: Node3D
var player: CharacterBody3D
var checks: Array = []
func _initialize() -> void:
	call_deferred("run")
func record(label: String, ok: bool, detail: Variant = null) -> void:
	checks.append({"check": label, "pass": ok, "detail": detail})
func key(down: bool) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = KEY_W
	event.pressed = down
	Input.parse_input_event(event)
func walk_to(target: Vector3) -> bool:
	for frame in range(500):
		var offset := target - player.global_position
		offset.y = 0
		if offset.length() < 0.12:
			key(false)
			for settle in range(12): await physics_frame
			return absf(player.global_position.y - target.y) < 0.23
		player.rotation.y = atan2(-offset.x, -offset.z)
		key(true)
		await physics_frame
	key(false)
	return false
func run() -> void:
	world = Node3D.new()
	root.add_child(world)
	# Exact retained lower-platform polygon supplied only for the isolated fixture.
	# Production lower floor stays owned by its existing compiler.
	var boundary := [Vector2(94,29),Vector2(107,29),Vector2(110,30),Vector2(115,33),Vector2(118,38),Vector2(118,42),Vector2(115,47),Vector2(110,50),Vector2(108,51),Vector2(94,51)]
	var points := PackedVector3Array()
	for y in [101.76,102.0]:
		for p in boundary: points.append(Vector3(p.x,y,p.y))
	var shape := ConvexPolygonShape3D.new()
	shape.points = points
	shape.margin = 0.001
	var body := StaticBody3D.new()
	body.name = "IsolatedExactLowerPlatformFixture"
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	world.add_child(body)
	var candidate: Node3D = load("res://royalty_790_completion_20261020/package.gd").build_candidate(world, false)
	player = load("res://scripts/player.gd").new()
	player.position = Vector3(95.7,102.03,40.7)
	world.add_child(player)
	for frame in range(20): await physics_frame
	record("lower_floor_same_datum", absf(player.position.y - 102.0) < 0.04, str(player.position))
	var targets := [Vector3(95.7,102,41.9),Vector3(95.7,104.25,47.1),Vector3(97.8,104.25,47.1),Vector3(97.8,106.5,41.5),Vector3(100.5,106.5,41.5),Vector3(106.5,106.5,42)]
	for i in range(targets.size()):
		var passed := await walk_to(targets[i])
		record("ordinary_player_up_segment_" + str(i), passed, {"target": str(targets[i]), "actual": str(player.position)})
		if not passed: break
	if checks.all(func(row): return row.pass):
		targets.reverse()
		for i in range(targets.size()):
			var passed := await walk_to(targets[i])
			record("ordinary_player_down_segment_" + str(i), passed, str(player.position))
			if not passed: break
	# Pitless platform arithmetic and guarded unavailable operation are separate.
	var lift: Node3D = candidate.find_child("Royalty790PrivateLift",true,false)
	record("no_shaft_pit", absf(lift.floor_heights[0] - 0.18 - 102.02) < 0.0001)
	record("upper_stop_unchanged", is_equal_approx(lift.floor_heights[1],106.5))
	record("admission_hold_active", not lift.operation_ready and lift.phase == "held_receivers_and_private_access")
	var result := {"status":"PASS" if checks.all(func(row): return row.pass) else "FAIL", "checks":checks, "scope":"Isolated exact lower-platform fixture, generated successor, unchanged player and retained cabin/gate controller. No full-main integration, cart/species or lift-travel acceptance.", "engine":Engine.get_version_info().string}
	var f := FileAccess.open("res://royalty_790_completion_20261020/evidence/ENGINE_CANDIDATE_CHECKS.json",FileAccess.WRITE)
	f.store_string(JSON.stringify(result,"\t") + "\n")
	print("ROYALTY_ENGINE_CHECKS ",result.status," ",checks.size())
	quit(0 if result.status == "PASS" else 1)
