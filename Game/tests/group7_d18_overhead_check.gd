extends "res://tests/validate_d04_port_forward_commons_service.gd"

func run() -> void:
	var directory: String = "res://../external_packages/group7_completion_20261011/continuation_r009/"
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	var prior: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/PREIMAGE_GROUP7_COMPLETION.json"))
	var replacements: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/RUNTIME_REPLACEMENTS.json"))
	var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/AUTHORED_D18_SUCCESSOR.json"))
	var source_preimage: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/OWNED_NECK_PREIMAGE.json"))
	var inherited: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/INHERITED_LOWER_JAMB_JOINTS.json"))
	var expected: Array = prior.models.duplicate(true)
	for replacement: Dictionary in replacements.models:
		var found: bool = false
		for i in range(expected.size()):
			if expected[i].cell == replacement.previous.cell:
				record("previous_cell_" + str(replacement.previous.cell), expected[i] == replacement.previous)
				expected[i] = replacement.successor
				found = true
		record("found_cell_" + str(replacement.previous.cell), found)
	record("only_four_model_successors", replacements.models.size() == 4 and data.models == expected and data.models.size() == 86)
	var expected_lights: Array = prior.lights.duplicate(true)
	for replacement: Dictionary in replacements.lights:
		for i in range(expected_lights.size()):
			if expected_lights[i].id == replacement.previous.id:
				record("previous_light_" + str(replacement.previous.id), expected_lights[i] == replacement.previous)
				expected_lights[i] = replacement.successor
	record("only_four_source_positions", replacements.lights.size() == 4 and data.lights == expected_lights and data.lights.size() == 39)
	record("all_doors_exact", data.doors == prior.doors and data.doors.size() == 8)
	record("no_capacity_acceptance", data.capacity_delta == 0 and not data.structural_capacity_accepted)
	for row: Dictionary in source.immutable_sources:
		record("immutable_native_" + str(row.base_native), FileAccess.get_sha256("res://../" + str(row.base_native)) == row.sha256)
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var before_lights: int = budget.sources.size()
	var candidate: Node3D = load("res://scripts/group7_completion.gd").build(ship)
	for i in range(8): await physics_frame
	record("candidate_idempotent", load("res://scripts/group7_completion.gd").build(ship) == candidate)
	record("same_budget_sources", budget.sources.size() == before_lights + 39 and budget.shadow_source_budget == 8)
	record("aft_sitting_bays_retained", ship.find_child("AftCrownSittingBays", true, false) != null)
	record("aft_sitting_lights_retained", ship.find_child("AftCrownSittingLighting", true, false) != null)
	var changed_rids: Array[RID] = []
	var captured: Array = []
	for replacement: Dictionary in replacements.models:
		var row: Dictionary = replacement.successor
		record("new_model_hash_" + str(row.cell), FileAccess.get_sha256("res://assets/models/" + str(row.file)) == row.sha256)
		record("owned_full_precision_" + str(row.cell), FileAccess.get_file_as_string("res://assets/models/" + str(row.file) + ".import").contains("meshes/force_disable_compression=true"))
		var model: Node3D = candidate.get_node(str(row.cell))
		for body: CollisionObject3D in model.find_children("*", "CollisionObject3D", true, false): changed_rids.append(body.get_rid())
		var faces := PackedVector3Array()
		for mesh: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
			var category: String = str(mesh.get_meta("extras", {}).get("contact_category", ""))
			record("new_collision_category_" + str(mesh.get_path()), mesh.has_node("StaticContact") == category.begins_with("solid_"))
			for point: Vector3 in mesh.mesh.get_faces(): faces.append(mesh.global_transform * point)
		var filename: String = "actual_" + str(row.cell) + ".tri.f32"
		FileAccess.open(directory + "qa/" + filename, FileAccess.WRITE).store_buffer(faces.to_byte_array())
		captured.append({"cell": row.cell, "filename": filename, "triangles": faces.size() / 3})
	var space: PhysicsDirectSpaceState3D = ship.get_world_3d().direct_space_state
	var unexpected: Array = []
	var inherited_contacts: Array = []
	for part: Dictionary in source.corrected_owned_parts:
		var center := Vector3.ZERO
		for point: Array in part.vertices_world_xyz: center += vec(point)
		center /= part.vertices_world_xyz.size()
		var points := PackedVector3Array()
		for point: Array in part.vertices_world_xyz: points.append(center + (vec(point)-center)*.99)
		var shape := ConvexPolygonShape3D.new()
		shape.points = points
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.margin = .00001
		query.exclude = changed_rids
		var hits: Array[Dictionary] = space.intersect_shape(query, 16)
		var paths: Array = []
		for hit: Dictionary in hits: paths.append(str(hit.collider.get_path()))
		var ok: bool = hits.is_empty()
		for joint: Dictionary in inherited.joints:
			if joint.part != part.name: continue
			var allowed: Array = []
			for receiver: Dictionary in joint.receivers:
				allowed.append("/Group7CompletionCandidate/" + str(receiver.cell) + "/")
				for current: Dictionary in data.models:
					if current.cell == receiver.cell: record("exact_lower_receiver_" + str(part.name) + "_" + str(receiver.cell), current == receiver)
			var old_part: Dictionary = {}
			for row: Dictionary in source_preimage.parts:
				if row.name == part.name: old_part = row
			var old_center := Vector3.ZERO
			for point: Array in old_part.vertices_world_xyz: old_center += vec(point)
			old_center /= old_part.vertices_world_xyz.size()
			var old_points := PackedVector3Array()
			for point: Array in old_part.vertices_world_xyz: old_points.append(old_center + (vec(point)-old_center)*.99)
			var old_shape := ConvexPolygonShape3D.new()
			old_shape.points = old_points
			query.shape = old_shape
			var old_hits: Array[Dictionary] = space.intersect_shape(query, 16)
			var old_paths: Array = []
			for hit: Dictionary in old_hits: old_paths.append(str(hit.collider.get_path()))
			paths.sort(); old_paths.sort()
			ok = paths == old_paths and paths.size() == allowed.size() and hits.size() < 16 and old_hits.size() < 16
			for path: String in paths:
				var declared: bool = false
				for prefix: String in allowed: declared = declared or path.contains(prefix)
				ok = ok and declared
			record("whole_jamb_inherited_contacts_exact_" + str(part.name), ok)
			var extension := PackedVector3Array()
			for point: Array in part.vertices_world_xyz:
				var at: Vector3 = vec(point)
				at.y = maxf(at.y, float(joint.original_jamb_head_y)+.0001)
				extension.append(at)
			var extension_shape := ConvexPolygonShape3D.new()
			extension_shape.points = extension
			query.shape = extension_shape
			var extension_hits: Array[Dictionary] = space.intersect_shape(query, 16)
			record("new_raised_jamb_extension_clear_" + str(part.name), extension_hits.is_empty())
			ok = ok and extension_hits.is_empty()
			inherited_contacts.append({"part": part.name, "old_receiver_paths": old_paths, "new_receiver_paths": paths, "raised_extension_hits": extension_hits.size(), "primary_bearing_accepted": false})
		record("changed_part_original_clear_or_verified_inherited_joint_" + str(part.name), ok)
		if not ok:
			unexpected.append({"part": part.name, "original_source_paths": paths, "saturated": hits.size() == 16})
	var air_probes: int = 0
	var actual_minimum_overhead: float = INF
	var floor_worker_poses: int = 0
	for sign_z: int in [-1, 1]:
		# Full original eight-metre route width; contiguous250mm slices. The2mm
		# floor standoff avoids surface coincidence, and no criterion is reduced.
		for i in range(83):
			var distance: float = 509.375 + i*.25
			var shape := BoxShape3D.new()
			shape.size = Vector3(8, 4, .25)
			shape.margin = 0
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = shape
			query.margin = 0
			query.transform = Transform3D(Basis.IDENTITY, Vector3(0, 108.502, distance*sign_z))
			query.exclude = [player.get_rid()]
			var hits: Array[Dictionary] = space.intersect_shape(query, 16)
			record("additional_full_width_four_metre_air_" + str(air_probes), hits.is_empty())
			if not hits.is_empty():
				var paths: Array = []
				for hit: Dictionary in hits: paths.append(str(hit.collider.get_path()))
				unexpected.append({"air_distance": distance*sign_z, "source_paths": paths})
			air_probes += 1
		for x: float in [-3.5, 0, 3.5]:
			for distance: float in [509.5, 510, 510.5, 517.5, 525, 529.5]:
				var at := Vector3(x, 106.5, distance*sign_z)
				var floor_hit: Dictionary = ray(space, at+Vector3.UP*.05, at-Vector3.UP*.05)
				record("original_d18_floor_" + str(floor_worker_poses), not floor_hit.is_empty() and absf(floor_hit.position.y-106.5) < .002)
				record("original_d18_worker_" + str(floor_worker_poses), capsule_clear(space, at))
				var overhead: Dictionary = ray(space, at+Vector3.UP*2.5, at+Vector3.UP*5)
				record("owned_overhead_above_four_metre_air_" + str(floor_worker_poses), not overhead.is_empty() and overhead.position.y >= 110.4999)
				if not overhead.is_empty(): actual_minimum_overhead = minf(actual_minimum_overhead, overhead.position.y)
				floor_worker_poses += 1
	var optical: Array = []
	for replacement: Dictionary in replacements.lights:
		var row: Dictionary = replacement.successor
		var emitter := vec(row.position)
		record("owned_emitter_y110_5_" + str(row.id), absf(emitter.y-110.5) < .00001)
		var hit: Dictionary = ray(space, emitter-Vector3.UP*.02, emitter-Vector3.UP*4.1)
		record("source_optical_exit_to_original_floor_" + str(row.id), not hit.is_empty() and absf(hit.position.y-106.5) < .002)
		player.global_position = Vector3(emitter.x, 106.53, emitter.z)
		player.velocity = Vector3.ZERO
		for i in range(8): await physics_frame
		budget.refresh()
		var light: SpotLight3D = candidate.get_node(str(row.id))
		record("raised_source_budget_admission_" + str(row.id), light.visible and light.shadow_enabled)
		optical.append({"id": row.id, "emitter": row.position, "first_receiver": str(hit.collider.get_path()) if not hit.is_empty() else "NONE", "budget_admitted": light.visible and light.shadow_enabled})
	var legs: Array = []
	for sign_z: int in [-1, 1]:
		player.global_position = Vector3(0, 106.53, 508*sign_z)
		player.velocity = Vector3.ZERO
		player.set_controls_enabled(true)
		for i in range(15): await physics_frame
		for goal in [Vector3(0, 106.5, 512*sign_z), Vector3(0, 106.5, 529*sign_z), Vector3(0, 106.5, 512*sign_z), Vector3(0, 106.5, 508*sign_z)]:
			var result: Dictionary = await walk_to(player, goal)
			legs.append(result)
			record("ordinary_d18_seam_neck_leg_" + str(legs.size()), result.reached and result.floor_contact)
	physical_key(false)
	var out: Dictionary = {"status": "PASS" if errors.is_empty() else "HOLD", "checks": checks.size(), "errors": errors,
		"changed_owned_parts": source.corrected_owned_parts.size(), "original_landing_feet_exact": 4,
		"unexpected_source_contacts": unexpected, "protected_source_queries": source.corrected_owned_parts.size(),
		"verified_inherited_lower_jamb_contacts": inherited_contacts,
		"additional_full_width_4m_air_slices": air_probes, "original_floor_worker_overhead_poses": floor_worker_poses,
		"actual_sampled_collision_overhead_min_y": actual_minimum_overhead, "source_optical_witnesses": optical,
		"actual_body_triangle_captures": captured, "original_player_legs": legs,
		"fixture_seeds": 6, "position_writes_between_walking_legs": 0,
		"physics_exclusions": "Changed four model RIDs only for source-receiver queries. Additional air slices exclude only player. Ordinary floor/worker/overhead/optical rays and walking exclude none.",
		"acceptance_limits": "Additional4m air in owned neck fromabsZ509.25to530, separate from unchanged original route criterion. Baseline opt-in construction only; protected roofs unchanged. Primary capacity, pressure, largest-species/cart and final graphical/current-main adoption remain unfinished."}
	FileAccess.open(directory + "qa/RUNTIME_CHECK.json", FileAccess.WRITE).store_string(JSON.stringify(out, "  ")+"\n")
	print(JSON.stringify({"status": out.status, "checks": out.checks, "errors": errors.size(), "unexpected": unexpected.size(), "air": air_probes, "legs": legs.size()}))
	quit(0 if errors.is_empty() else 1)
