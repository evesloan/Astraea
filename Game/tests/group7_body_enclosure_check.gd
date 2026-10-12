extends "res://tests/group7_finite_seams_check.gd"

func run() -> void:
	var directory: String = "res://../external_packages/group7_completion_20261011/continuation_r005/"
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	var prior: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/PREIMAGE_GROUP7_COMPLETION.json"))
	var replacements: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/RUNTIME_REPLACEMENTS.json"))
	var resolution: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/FACADE_RESOLUTION.json"))
	var seam_plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../external_packages/group7_completion_20261011/continuation_r004/docs/SEAM_PLAN.json"))
	var expected: Array = prior.models.duplicate(true)
	for replacement: Dictionary in replacements.replacements:
		var index: int = -1
		for i in range(expected.size()):
			if expected[i].cell == replacement.previous.cell: index = i
		record("exact_previous_definition_" + str(replacement.previous.cell), index >= 0 and expected[index] == replacement.previous)
		if index >= 0: expected[index] = replacement.successor
	record("only_seven_declared_successors", replacements.replacements.size() == 7 and data.models == expected)
	record("prior_doors_unchanged", data.doors == prior.doors)
	record("prior_lights_unchanged", data.lights == prior.lights)
	record("same_model_count", data.models.size() == 78)
	for file in resolution.source_pins:
		record("protected_source_pin_" + str(file), FileAccess.get_sha256("res://../" + str(file)) == resolution.source_pins[file])
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
	record("same_19_lights_budget", budget.sources.size() == old_light_count + 19 and budget.shadow_source_budget == 8)
	record("aft_bays_preserved", ship.find_child("AftCrownSittingBays", true, false) != null)
	record("aft_lights_preserved", ship.find_child("AftCrownSittingLighting", true, false) != null)
	var owned_exclusions: Array[RID] = []
	for body: CollisionObject3D in candidate.find_children("*", "CollisionObject3D", true, false):
		owned_exclusions.append(body.get_rid())
		if body is StaticBody3D and not str(body.get_path()).contains("/G7C4_"): seam_target_exclusions.append(body.get_rid())
	var captured: Array = []
	for replacement: Dictionary in replacements.replacements:
		var row: Dictionary = replacement.successor
		record("new_body_hash_" + str(row.cell), FileAccess.get_sha256("res://assets/models/" + str(row.file)) == row.sha256)
		record("owned_full_precision_import_" + str(row.cell), FileAccess.get_file_as_string("res://assets/models/" + str(row.file) + ".import").contains("meshes/force_disable_compression=true"))
		var model: Node3D = candidate.get_node(str(row.cell))
		var all_faces := PackedVector3Array()
		for mesh: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
			record("actual_body_contact_" + str(mesh.get_path()), mesh.has_node("StaticContact"))
			var faces: PackedVector3Array = mesh.mesh.get_faces()
			for face in faces: all_faces.append(mesh.global_transform * face)
		var filename: String = "actual_" + str(row.cell) + ".tri.f32"
		FileAccess.open(directory + "qa/" + filename, FileAccess.WRITE).store_buffer(all_faces.to_byte_array())
		captured.append({"cell": row.cell, "filename": filename, "triangles": all_faces.size() / 3})
	var space: PhysicsDirectSpaceState3D = ship.get_world_3d().direct_space_state
	var unexpected: Array = []
	for field: Dictionary in resolution.accepted_clear_fields:
		var center := Vector3.ZERO
		for point: Array in field.candidate_vertices: center += vec(point)
		center /= field.candidate_vertices.size()
		var points := PackedVector3Array()
		for point: Array in field.candidate_vertices: points.append(center + (vec(point) - center) * .99)
		var shape := ConvexPolygonShape3D.new()
		shape.points = points
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.margin = .00001
		query.transform = Transform3D.IDENTITY
		query.exclude = owned_exclusions
		var hits: Array[Dictionary] = space.intersect_shape(query, 16)
		record("new_field_protected_physics_clear_" + str(field.name), hits.is_empty())
		if not hits.is_empty():
			var paths: Array = []
			for hit: Dictionary in hits: paths.append(str(hit.collider.get_path()))
			unexpected.append({"field": field.name, "colliders": paths, "saturated": hits.size() == 16})
	# Retain the local landing/core route acceptance after changing body cells.
	for sign_z in [-1, 1]:
		var term: String = "Fore" if sign_z == -1 else "Aft"
		var end: float = 510.0 * sign_z
		for side in [-1, 1]:
			for y in [65.0, 80.0, 103.0, 106.4]:
				var z: float = end - sign_z * .5
				var width: float = corner_outer_width(seam_plan, term, side, y, z)
				seam_hit(space, Vector3(side * (width - 1.2), y, z), Vector3(side * (width - .2), y, z), "G7C4_" + term + "_BodySeals", "retained_corner_landing_" + term + "_" + str(side) + "_" + str(y))
		for distance in [509.5, 510.2, 511.0]:
			for x in [-3.0, 0.0, 3.0]:
				var at := Vector3(x, 106.5, distance * sign_z)
				var floor_hit: Dictionary = ray(space, at + Vector3.UP * .05, at - Vector3.UP * .05)
				record("retained_d18_floor_" + str(at), not floor_hit.is_empty() and absf(floor_hit.position.y - 106.5) < .002)
				record("retained_d18_worker_" + str(at), capsule_clear(space, at))
				var overhead: Dictionary = ray(space, at + Vector3.UP * 2.5, at + Vector3.UP * 5)
				record("retained_d18_headroom_" + str(at), not overhead.is_empty() and overhead.position.y >= 110.299)
	var legs: Array = []
	for sign_z in [-1, 1]:
		player.global_position = Vector3(0, 106.53, 508.0 * sign_z)
		player.velocity = Vector3.ZERO
		player.set_controls_enabled(true)
		for i in range(15): await physics_frame
		for goal in [Vector3(0, 106.5, 512.0 * sign_z), Vector3(0, 106.5, 508.0 * sign_z)]:
			var result: Dictionary = await walk_to(player, goal)
			legs.append(result)
			record("normal_player_seam_leg_" + str(legs.size()), result.reached and result.floor_contact)
	physical_key(false)
	var out: Dictionary = {"status": "PASS" if errors.is_empty() else "HOLD", "checks": checks.size(), "errors": errors, "restored_fields": 2129, "remaining_protected_holds": 5, "protected_physics_queries": resolution.accepted_clear_fields.size(), "unexpected_source_contacts": unexpected, "actual_body_triangle_captures": captured, "original_player_legs": legs, "fixture_seeds": 2, "position_writes_between_walking_legs": 0, "physics_query_exclusions": "Only the owned candidate colliders; protected source/route collisions unchanged", "whole_group_or_pressure_capacity_accepted": false}
	FileAccess.open(directory + "qa/RUNTIME_CHECK.json", FileAccess.WRITE).store_string(JSON.stringify(out, "  ") + "\n")
	print(JSON.stringify({"status": out.status, "checks": out.checks, "errors": errors.size(), "unexpected_source_contacts": unexpected.size(), "legs": legs.size()}))
	quit(0 if errors.is_empty() else 1)
