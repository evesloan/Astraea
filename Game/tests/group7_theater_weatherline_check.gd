extends "res://tests/validate_d04_port_forward_commons_service.gd"

func run() -> void:
	var directory: String = "res://../external_packages/group7_completion_20261011/continuation_r008/"
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	var prior: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/PREIMAGE_GROUP7_COMPLETION.json"))
	var replacements: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/RUNTIME_REPLACEMENTS.json"))
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/THEATER_SEAM_PLAN.json"))
	var expected: Array = prior.models.duplicate(true)
	for replacement: Dictionary in replacements.replacements:
		var found: bool = false
		for i in range(expected.size()):
			if expected[i].cell == replacement.previous.cell:
				record("exact_preimage_" + str(replacement.previous.cell), expected[i] == replacement.previous)
				expected[i] = replacement.successor
				found = true
		record("found_previous_cell_" + str(replacement.previous.cell), found)
	record("only_three_declared_successors", replacements.replacements.size() == 3 and data.models == expected)
	record("previous_86_models", data.models.size() == 86)
	record("previous_39_sources_exact", data.lights == prior.lights and data.lights.size() == 39)
	record("previous_eight_doors_exact", data.doors == prior.doors and data.doors.size() == 8)
	record("capacity_unchanged", data.capacity_delta == 0 and not data.structural_capacity_accepted)
	for file: String in plan.source_pins:
		record("source_pin_" + file, FileAccess.get_sha256("res://../" + file) == plan.source_pins[file])
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var old_light_count: int = budget.sources.size()
	var candidate: Node3D = load("res://scripts/group7_completion.gd").build(ship)
	for i in range(8): await physics_frame
	record("candidate_idempotent", load("res://scripts/group7_completion.gd").build(ship) == candidate)
	record("same_sources_and_budget", budget.sources.size() == old_light_count + 39 and budget.shadow_source_budget == 8)
	record("aft_sitting_bays_preserved", ship.find_child("AftCrownSittingBays", true, false) != null)
	record("aft_sitting_lights_preserved", ship.find_child("AftCrownSittingLighting", true, false) != null)
	var owned: Array[RID] = []
	for body: CollisionObject3D in candidate.find_children("*", "CollisionObject3D", true, false): owned.append(body.get_rid())
	var captured: Array = []
	for replacement: Dictionary in replacements.replacements:
		var row: Dictionary = replacement.successor
		record("successor_hash_" + str(row.cell), FileAccess.get_sha256("res://assets/models/" + str(row.file)) == row.sha256)
		record("owned_full_precision_" + str(row.cell), FileAccess.get_file_as_string("res://assets/models/" + str(row.file) + ".import").contains("meshes/force_disable_compression=true"))
		var model: Node3D = candidate.get_node(str(row.cell))
		var faces := PackedVector3Array()
		for mesh: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
			record("actual_static_contact_" + str(mesh.get_path()), mesh.has_node("StaticContact"))
			for point: Vector3 in mesh.mesh.get_faces(): faces.append(mesh.global_transform * point)
		var filename: String = "actual_" + str(row.cell) + ".tri.f32"
		FileAccess.open(directory + "qa/" + filename, FileAccess.WRITE).store_buffer(faces.to_byte_array())
		captured.append({"cell": row.cell, "filename": filename, "triangles": faces.size() / 3})
	var space: PhysicsDirectSpaceState3D = ship.get_world_3d().direct_space_state
	var unexpected: Array = []
	var deliberate_cap_contacts: Array = []
	for part: Dictionary in plan.corrected_owned_parts + plan.added_parts:
		var center := Vector3.ZERO
		for point: Array in part.vertices_world_xyz: center += vec(point)
		center /= part.vertices_world_xyz.size()
		var points := PackedVector3Array()
		for point: Array in part.vertices_world_xyz: points.append(center + (vec(point) - center) * .99)
		var shape := ConvexPolygonShape3D.new()
		shape.points = points
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.margin = .00001
		query.transform = Transform3D.IDENTITY
		query.exclude = owned
		var hits: Array[Dictionary] = space.intersect_shape(query, 16)
		var paths: Array = []
		for hit: Dictionary in hits: paths.append(str(hit.collider.get_path()))
		var ok: bool = hits.is_empty()
		if part.has("permitted_original_contact_node"):
			ok = not hits.is_empty() and hits.size() < 16
			for path: String in paths: ok = ok and path.contains("/" + str(part.permitted_original_contact_node) + "/")
			deliberate_cap_contacts.append({"part": part.name, "original_source_paths": paths, "primary_bearing_accepted": false})
		record("protected_receiver_clear_or_declared_cap_" + str(part.name), ok)
		if not ok: unexpected.append({"part": part.name, "source_paths": paths})
	var seam_rays: int = 0
	var cap_rays: int = 0
	for panel: Dictionary in plan.panels:
		for u: float in [.2, .5, .8]:
			var z: float = lerpf(float(panel.z[0]), float(panel.z[1]), u)
			for y: float in [92.005, 92.1, 92.5, 92.999, 93.001, 94.2, 97.49]:
				var hit: Dictionary = ray(space, Vector3(-111, y, z), Vector3(-106, y, z))
				var expected_x: float = -109.6 + .4 * (y-92)
				record("finite_weather_and_corrected_foot_" + str(seam_rays), not hit.is_empty() and str(hit.collider.get_path()).contains("/Group7CompletionCandidate/" + str(panel.cell) + "/") and absf(hit.position.x - expected_x) < .0002)
				seam_rays += 1
			# Identify the exact retained skin cap, excluding only the new owned candidate.
			var cap_query := PhysicsRayQueryParameters3D.create(Vector3(-109.51, 92.2, z), Vector3(-109.51, 91.8, z))
			cap_query.exclude = owned
			var cap: Dictionary = space.intersect_ray(cap_query)
			record("retained_skin_cap_" + str(cap_rays), not cap.is_empty() and str(cap.collider.get_path()).contains("/HUL2_FullShoulderSkin/") and absf(cap.position.y-92) < .0002)
			cap_rays += 1
	# The original operational D11 bridge remains clear. All route queries and
	# walking use ordinary collision, with no exclusions and no intervening writes.
	var route_poses: int = 0
	for z: float in [-125.0, -127.0]:
		for x: float in [-8.0, -10.0, -12.0, -14.0, -16.0, -18.0, -20.0, -22.0, -24.0, -26.0, -28.0, -30.0]:
			var at := Vector3(x, 69.5, z)
			var floor_hit: Dictionary = ray(space, at + Vector3.UP * .05, at - Vector3.UP * .05)
			record("original_bridge_floor_" + str(route_poses), not floor_hit.is_empty() and absf(floor_hit.position.y-69.5) < .002)
			record("original_bridge_worker_" + str(route_poses), capsule_clear(space, at))
			route_poses += 1
	var legs: Array = []
	for z: float in [-125.0, -127.0]:
		player.global_position = Vector3(-8, 69.53, z)
		player.velocity = Vector3.ZERO
		player.set_controls_enabled(true)
		for i in range(15): await physics_frame
		for goal in [Vector3(-30, 69.5, z), Vector3(-8, 69.5, z)]:
			var result: Dictionary = await walk_to(player, goal)
			legs.append(result)
			record("normal_theater_bridge_leg_" + str(legs.size()), result.reached and result.floor_contact)
	physical_key(false)
	var out: Dictionary = {"status": "PASS" if errors.is_empty() else "HOLD", "checks": checks.size(), "errors": errors,
		"corrected_owned_parts": plan.corrected_owned_parts.size(), "finite_added_parts": plan.added_parts.size(),
		"protected_source_queries": plan.corrected_owned_parts.size() + plan.added_parts.size(),
		"unexpected_source_contacts": unexpected, "deliberate_nonprimary_skin_cap_contacts": deliberate_cap_contacts,
		"weatherline_and_body_finite_rays": seam_rays, "retained_original_cap_rays": cap_rays,
		"actual_body_triangle_captures": captured, "original_bridge_route_poses": route_poses,
		"original_player_legs": legs, "fixture_seeds": 2, "position_writes_between_walking_legs": 0,
		"physics_exclusions": "Owned candidate RIDs only for original-receiver queries. Ordinary seam surface rays, routes and walking exclude none.",
		"acceptance_limits": "Baseline-main opt-in physical seam and preserved D11 worker bridge only. Original cap contact is weather construction, not primary load capacity. Closed upper/secondary theater interfaces, largest-species/cart, pressure, current-main adoption, gameplay and final-art acceptance remain unfinished."}
	FileAccess.open(directory + "qa/RUNTIME_CHECK.json", FileAccess.WRITE).store_string(JSON.stringify(out, "  ") + "\n")
	print(JSON.stringify({"status": out.status, "checks": out.checks, "errors": errors.size(), "unexpected": unexpected.size(), "seam_rays": seam_rays, "legs": legs.size()}))
	quit(0 if errors.is_empty() else 1)
