extends "res://tests/validate_d04_port_forward_commons_service.gd"
var seam_target_exclusions: Array[RID] = []

func seam_hit(space: PhysicsDirectSpaceState3D, a: Vector3, b: Vector3, expected: String, label: String) -> void:
	# Isolate only this imported collar's contact shape from its overlapping
	# retained receivers. Ordinary route/floor/capsule queries below exclude none.
	var query := PhysicsRayQueryParameters3D.create(a, b)
	query.exclude = seam_target_exclusions
	var hit: Dictionary = space.intersect_ray(query)
	var path: String = str(hit.collider.get_path()) if not hit.is_empty() else ""
	record(label, not hit.is_empty() and path.contains(expected))
	if hit.is_empty() or not path.contains(expected): print("SEAM_RAY_HOLD ", label, " ", path)

func corner_outer_width(plan: Dictionary, term: String, side: int, y: float, z: float) -> float:
	for part: Dictionary in plan.parts:
		if not str(part.name).contains(term + "_CornerSeal_" + str(side) + "_"): continue
		if y < float(part.y_interval[0]) or y > float(part.y_interval[1]): continue
		var lower: Array = part.section_polygons_xz[0]
		var upper: Array = part.section_polygons_xz[1]
		var t: float = (y - float(part.y_interval[0])) / (float(part.y_interval[1]) - float(part.y_interval[0]))
		var a: Vector2 = Vector2(lower[0][0], lower[0][1]).lerp(Vector2(upper[0][0], upper[0][1]), t)
		var b: Vector2 = Vector2(lower[1][0], lower[1][1]).lerp(Vector2(upper[1][0], upper[1][1]), t)
		return absf(a.lerp(b, (z - a.y) / (b.y - a.y)).x)
	assert(false, "Missing authored corner section")
	return 0.0

func run() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	var prior: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../external_packages/group7_completion_20261011/continuation_r004/docs/PREIMAGE_GROUP7_COMPLETION.json"))
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../external_packages/group7_completion_20261011/continuation_r004/docs/SEAM_PLAN.json"))
	var appended: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../external_packages/group7_completion_20261011/continuation_r004/docs/RUNTIME_APPEND.json"))
	var expected_prior: Array = prior.models.duplicate(true)
	if data.has("body_source_successor"):
		var successors: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../external_packages/group7_completion_20261011/continuation_r005/docs/RUNTIME_REPLACEMENTS.json"))
		for replacement: Dictionary in successors.replacements:
			for i in range(expected_prior.size()):
				if expected_prior[i].cell == replacement.previous.cell:
					record("declared_body_source_preimage_" + str(replacement.previous.cell), expected_prior[i] == replacement.previous)
					expected_prior[i] = replacement.successor
	record("prior_74_layout_or_declared_source_preserving_body_successors", data.models.slice(0, 74) == expected_prior)
	record("only_four_models_appended", data.models.size() == 78 and appended.new_models.size() == 4)
	record("prior_doors_exact", data.doors == prior.doors)
	record("prior_lights_exact", data.lights == prior.lights)
	record("capacity_unchanged", data.capacity_delta == 0 and not data.structural_capacity_accepted)
	for file in plan.source_pins:
		record("immutable_source_pin_" + str(file), FileAccess.get_sha256("res://../" + str(file)) == plan.source_pins[file])
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var before_lights: int = budget.sources.size()
	var candidate: Node3D = load("res://scripts/group7_completion.gd").build(ship)
	for i in range(8): await physics_frame
	for body: StaticBody3D in candidate.find_children("*", "StaticBody3D", true, false):
		if not str(body.get_path()).contains("/G7C4_"): seam_target_exclusions.append(body.get_rid())
	record("candidate_idempotent", load("res://scripts/group7_completion.gd").build(ship) == candidate)
	record("same_19_lights_append_once", budget.sources.size() == before_lights + 19 and budget.shadow_source_budget == 8)
	record("aft_bays_preserved", ship.find_child("AftCrownSittingBays", true, false) != null)
	record("aft_bay_lights_preserved", ship.find_child("AftCrownSittingLighting", true, false) != null)
	for row in data.models:
		record("retained_or_new_model_hash_" + str(row.cell), FileAccess.get_sha256("res://assets/models/" + str(row.file)) == row.sha256)
	for row in appended.new_models:
		var model: Node3D = candidate.get_node(str(row.cell))
		for mesh: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
			record("new_static_contact_" + str(mesh.get_path()), mesh.has_node("StaticContact"))
	for row in data.doors:
		var door: Node3D = candidate.get_node(str(row.id))
		record("original_door_closed_" + str(row.id), not door.desired_open and door.open_fraction == 0.0)
	var space: PhysicsDirectSpaceState3D = ship.get_world_3d().direct_space_state
	for sign_z in [-1, 1]:
		var term: String = "Fore" if sign_z == -1 else "Aft"
		var end: float = 510.0 * sign_z
		for side in [-1, 1]:
			for y in [61.2, 65.0, 69.8, 80.0, 90.0, 103.0, 106.4]:
				var z: float = end - sign_z * .5
				var width: float = corner_outer_width(plan, term, side, y, z)
				seam_hit(space, Vector3(side * (width - 1.2), y, z), Vector3(side * (width - .2), y, z), "G7C4_" + term + "_BodySeals", "actual_corner_receiver_" + term + "_" + str(side) + "_" + str(y))
			for y in [69.6, 106.4]:
				seam_hit(space, Vector3(side * 20.0, y, end - sign_z * 1.2), Vector3(side * 20.0, y, end - sign_z * .5), "G7C4_" + term + "_BodySeals", "actual_headwall_lap_" + term + "_" + str(side) + "_" + str(y))
		seam_hit(space, Vector3(0, 109.0, end - sign_z * .5), Vector3(0, 111.0, end - sign_z * .5), "G7C4_" + term + "_NeckLanding", "actual_landing_header_" + term)
		for distance in [509.5, 510.0, 510.2, 510.6, 511.0]:
			for x in [-3.0, 0.0, 3.0]:
				var at := Vector3(x, 106.5, distance * sign_z)
				var floor_hit: Dictionary = ray(space, at + Vector3.UP * .05, at - Vector3.UP * .05)
				record("seam_original_floor_" + str(at), not floor_hit.is_empty() and absf(floor_hit.position.y - 106.5) < .002)
				record("seam_worker_capsule_" + str(at), capsule_clear(space, at))
				var overhead: Dictionary = ray(space, at + Vector3.UP * 2.5, at + Vector3.UP * 5)
				record("seam_headroom_" + str(at), not overhead.is_empty() and overhead.position.y >= 110.299)
	var legs: Array = []
	# One fixture for each disconnected terminal. All following legs use the
	# original player controller, with no intervening position writes.
	for sign_z in [-1, 1]:
		player.global_position = Vector3(0, 106.53, 508.0 * sign_z)
		player.velocity = Vector3.ZERO
		player.set_controls_enabled(true)
		for i in range(15): await physics_frame
		for goal in [Vector3(0, 106.5, 512.0 * sign_z), Vector3(0, 106.5, 508.0 * sign_z)]:
			var result: Dictionary = await walk_to(player, goal)
			legs.append(result)
			record("normal_player_crosses_seam_" + str(legs.size()), result.reached and result.floor_contact)
	physical_key(false)
	var out: Dictionary = {"status": "PASS" if errors.is_empty() else "HOLD", "checks": checks.size(), "errors": errors, "new_models": 4, "retained_models": 74, "new_lights": 0, "new_doors": 0, "original_player_legs": legs, "fixture_seeds": 2, "position_writes_between_walking_legs": 0, "minimum_new_central_overhead_y": 110.3, "targeted_new_mesh_probe_exclusions": "Retained candidate StaticBody3D RIDs only; ordinary route/floor/capsule and walking collision excludes none and is unchanged", "acceptance_limits": "Actual baseline-main opt-in contact and worker traversal of both local terminal/body seams. Newer Group1 source bounds separately checked. No full body-route roof, pressure, structural capacity, largest-species/cart, graphical/final-art or whole-group acceptance."}
	FileAccess.open("res://../external_packages/group7_completion_20261011/continuation_r004/qa/RUNTIME_CHECK.json", FileAccess.WRITE).store_string(JSON.stringify(out, "  ") + "\n")
	print(JSON.stringify({"status": out.status, "checks": out.checks, "errors": errors, "legs": legs.size()}))
	quit(0 if errors.is_empty() else 1)
