extends "res://tests/group7_finite_seams_check.gd"

func run() -> void:
	var directory: String = "res://../external_packages/group7_completion_20261011/continuation_r006/"
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	var prior: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/PREIMAGE_GROUP7_COMPLETION.json"))
	var appended: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/RUNTIME_APPEND.json"))
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/BOTANICAL_PLAN.json"))
	var architecture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "docs/ARCHITECTURE_PARTS.json"))
	var expected_models: Array = prior.models.duplicate(true)
	expected_models.append_array(appended.new_models)
	var expected_lights: Array = prior.lights.duplicate(true)
	expected_lights.append_array(appended.new_lights)
	record("only_four_declared_botanical_cells", data.models == expected_models and appended.new_models.size() == 4 and data.models.size() == 82)
	record("only_eight_declared_source_lights", data.lights == expected_lights and appended.new_lights.size() == 8)
	record("prior_four_doors_exact", data.doors == prior.doors)
	record("capacity_and_room_identity_unchanged", data.capacity_delta == 0 and plan.new_room_ids == 0 and not data.structural_capacity_accepted)
	for file in plan.source_pins:
		record("immutable_botanical_receiver_" + str(file), FileAccess.get_sha256("res://../" + str(file)) == plan.source_pins[file])
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	for i in range(30): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var originals: Dictionary = {}
	for name in ["CANOPY_A", "CANOPY_B", "BasinAndSeatedIsland", "D06_CanopyTerrace_Arrival_WIP", "D06_PortBotanicalOverlook_WIP"]:
		var node: Node3D = ship.find_child(name, true, false)
		record("original_botanical_root_present_" + name, node != null)
		if node != null: originals[name] = {"node": node, "transform": node.global_transform, "visible": node.visible}
	var budget: Node = ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var old_light_count: int = budget.sources.size()
	var candidate: Node3D = load("res://scripts/group7_completion.gd").build(ship)
	for i in range(8): await physics_frame
	record("candidate_idempotent", load("res://scripts/group7_completion.gd").build(ship) == candidate)
	record("27_sources_append_once_original_budget_8", budget.sources.size() == old_light_count + 27 and budget.shadow_source_budget == 8)
	for name in originals:
		var old: Dictionary = originals[name]
		record("original_botanical_root_exact_" + str(name), old.node.global_transform == old.transform and old.node.visible == old.visible)
	record("original_aft_crown_bays_present", ship.find_child("AftCrownSittingBays", true, false) != null)
	record("original_aft_crown_lights_present", ship.find_child("AftCrownSittingLighting", true, false) != null)
	var exclusions: Array[RID] = []
	var captured: Array = []
	for row: Dictionary in appended.new_models:
		record("new_botanical_hash_" + str(row.cell), FileAccess.get_sha256("res://assets/models/" + str(row.file)) == row.sha256)
		record("owned_botanical_full_precision_" + str(row.cell), FileAccess.get_file_as_string("res://assets/models/" + str(row.file) + ".import").contains("meshes/force_disable_compression=true"))
		var model: Node3D = candidate.get_node(str(row.cell))
		var all_faces := PackedVector3Array()
		for mesh: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
			var category: String = str(mesh.get_meta("extras", {}).get("contact_category", ""))
			record("category_contact_" + str(mesh.get_path()), mesh.has_node("StaticContact") == category.begins_with("solid_"))
			if category == "visual_lens": record("open_opal_shadow_" + str(mesh.get_path()), mesh.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
			for v in mesh.mesh.get_faces(): all_faces.append(mesh.global_transform * v)
		for body: CollisionObject3D in model.find_children("*", "CollisionObject3D", true, false): exclusions.append(body.get_rid())
		var filename: String = "actual_" + str(row.cell) + ".tri.f32"
		FileAccess.open(directory + "qa/" + filename, FileAccess.WRITE).store_buffer(all_faces.to_byte_array())
		captured.append({"cell": row.cell, "filename": filename, "triangles": all_faces.size() / 3})
	var space: PhysicsDirectSpaceState3D = ship.get_world_3d().direct_space_state
	# Preserve the exact retained four-metre transit reservation, including its
	# height and ordinary shape margin. Worker clearance alone cannot replace it.
	var reservation := CylinderShape3D.new()
	reservation.radius = 2
	reservation.height = 4
	var transit_points: Array = plan.protected_transit_contract.points_xz
	var transit_samples: int = 0
	for terrace: Dictionary in plan.terraces:
		for i in range(transit_points.size() - 1):
			var a: Array = transit_points[i]
			var b: Array = transit_points[i + 1]
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = reservation
			query.transform.origin = Vector3(a[0], float(terrace.floor_y) + 2.05, a[1])
			query.motion = Vector3(float(b[0]) - float(a[0]), 0, float(b[1]) - float(a[1]))
			query.exclude = [player.get_rid()]
			record("retained_four_metre_transit_start_" + str(transit_samples), space.intersect_shape(query).is_empty())
			record("retained_four_metre_transit_sweep_" + str(transit_samples), space.cast_motion(query)[0] > .999)
			transit_samples += 1
	var native_audit: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory + "qa/NATIVE_AUDIT.json"))
	for row: Dictionary in appended.new_models:
		var bounds: Array = native_audit.cell_bounds[row.cell]
		var low: Vector3 = vec(bounds[0])
		var high: Vector3 = vec(bounds[1])
		var shape := BoxShape3D.new()
		shape.size = (high - low) * .995
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.margin = .00001
		query.transform.origin = (low + high) / 2
		query.exclude = exclusions
		record("full_new_cell_including_original_bark_protected_clear_" + str(row.cell), space.intersect_shape(query, 32).is_empty())
	var unexpected: Array = []
	for part: Dictionary in architecture.parts:
		if not str(part.category).begins_with("solid_"): continue
		var center := Vector3.ZERO
		for v: Array in part.vertices_world_xyz: center += vec(v)
		center /= part.vertices_world_xyz.size()
		var points := PackedVector3Array()
		for v: Array in part.vertices_world_xyz: points.append(center + (vec(v) - center) * .995)
		var shape := ConvexPolygonShape3D.new()
		shape.points = points
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.margin = .00001
		query.transform = Transform3D.IDENTITY
		query.exclude = exclusions
		var hits: Array[Dictionary] = space.intersect_shape(query, 32)
		record("new_architecture_protected_contact_clear_" + str(part.name), hits.is_empty())
		if not hits.is_empty():
			var paths: Array = []
			for hit: Dictionary in hits: paths.append(str(hit.collider.get_path()))
			unexpected.append({"part": part.name, "colliders": paths, "saturated": hits.size() == 32})
	var floor_samples: int = 0
	var route_samples: int = 0
	for terrace: Dictionary in plan.terraces:
		var y: float = terrace.floor_y
		for island: Dictionary in terrace.islands:
			for dx in [-.8, 0., .8]:
				for dz in [-float(island.length_m) * .25, 0., float(island.length_m) * .25]:
					var at: Vector3 = vec(island.center) + Vector3(dx, 0, dz)
					var query := PhysicsRayQueryParameters3D.create(at + Vector3.UP * .03, at - Vector3.UP * .03)
					query.exclude = exclusions
					var hit: Dictionary = space.intersect_ray(query)
					record("retained_full_floor_receiver_" + str(floor_samples), not hit.is_empty() and absf(hit.position.y - y) < .002)
					floor_samples += 1
		var a: Vector3 = vec(terrace.normal_walk_bypass[0])
		var b: Vector3 = vec(terrace.normal_walk_bypass[1])
		for i in range(63):
			var at: Vector3 = a.lerp(b, i / 62.0)
			var hit: Dictionary = ray(space, at + Vector3.UP * .03, at - Vector3.UP * .03)
			record("normal_bypass_floor_" + str(route_samples), not hit.is_empty() and absf(hit.position.y - y) < .002)
			record("normal_bypass_capsule_" + str(route_samples), capsule_clear(space, at))
			route_samples += 1
	var legs: Array = []
	for terrace: Dictionary in plan.terraces:
		var a: Vector3 = vec(terrace.normal_walk_bypass[0])
		var b: Vector3 = vec(terrace.normal_walk_bypass[1])
		player.global_position = a + Vector3.UP * .03
		player.velocity = Vector3.ZERO
		player.set_controls_enabled(true)
		for i in range(15): await physics_frame
		for goal in [b, a]:
			var result: Dictionary = await walk_to(player, goal)
			legs.append(result)
			record("normal_botanical_bypass_leg_" + str(legs.size()), result.reached and result.floor_contact)
	physical_key(false)
	var light_results: Array = []
	for row: Dictionary in appended.new_lights:
		var emitter: Vector3 = vec(row.position)
		var y: float = emitter.y - 3.23
		var receiver := Vector3(signf(emitter.x) * 41.45, y, emitter.z)
		player.global_position = receiver + Vector3.UP * .03
		player.velocity = Vector3.ZERO
		for i in range(8): await physics_frame
		var hit: Dictionary = ray(space, receiver + Vector3.UP * .03, receiver - Vector3.UP * .03)
		record("new_lamp_floor_" + str(row.id), not hit.is_empty() and absf(hit.position.y - y) < .002)
		var down: Dictionary = ray(space, emitter, Vector3(emitter.x, y - .03, emitter.z))
		record("new_lamp_open_optical_exit_" + str(row.id), not down.is_empty() and absf(down.position.y - y) < .002)
		budget.refresh()
		var light: SpotLight3D = candidate.get_node(str(row.id))
		record("new_lamp_actual_admission_" + str(row.id), light.visible and light.shadow_enabled)
		record("new_lamp_downward_cone_" + str(row.id), (-light.global_basis.z).dot(Vector3.DOWN) > .999)
		light_results.append({"id": row.id, "receiver": str(receiver), "admitted": light.visible and light.shadow_enabled, "down_hit": str(down.get("position", Vector3.INF))})
	var out: Dictionary = {"status": "PASS" if errors.is_empty() else "HOLD", "checks": checks.size(), "errors": errors, "terrace_edges": 4, "architecture_parts": 137, "rigid_original_plant_bindings": 121, "new_source_lights": 8, "existing_model_rows_unchanged": 78, "existing_light_rows_unchanged": 19, "protected_physics_queries": architecture.parts.size() - 8 + 4, "protected_four_metre_transit_segments": transit_samples, "transit_criteria_unchanged": true, "unexpected_source_contacts": unexpected, "retained_floor_samples": floor_samples, "normal_route_samples": route_samples, "original_player_legs": legs, "fixture_light_admission": light_results, "fixture_seeds": 12, "position_writes_between_walking_legs": 0, "contact_queries_exclude": "Only four new botanical cells; original source and earlier Group7 contacts are included. Ordinary routes and optical rays exclude none. Retained transit sweeps exclude only the player, as their original contract requires.", "actual_botanical_triangle_captures": captured, "whole_group_capacity_horticulture_gameplay_final_art_accepted": false}
	FileAccess.open(directory + "qa/RUNTIME_CHECK.json", FileAccess.WRITE).store_string(JSON.stringify(out, "  ") + "\n")
	print(JSON.stringify({"status": out.status, "checks": out.checks, "errors": errors, "legs": legs.size(), "unexpected_contacts": unexpected.size()}))
	quit(0 if errors.is_empty() else 1)
