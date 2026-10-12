extends "res://tests/validate_d04_port_forward_commons_service.gd"

func normal_guard_stop(player: CharacterBody3D, goal: Vector3, expected: String) -> Dictionary:
	var start: Vector3 = player.global_position
	var delta: Vector3 = goal-start
	delta.y = 0
	player.rotation.y = atan2(-delta.x, -delta.z)
	var contacts: Dictionary = {}
	physical_key(true)
	for i in range(120):
		await physics_frame
		for k in range(player.get_slide_collision_count()):
			contacts[str(player.get_slide_collision(k).get_collider().get_path())] = true
	physical_key(false)
	for i in range(15): await physics_frame
	var guard_contact: bool = false
	for path: String in contacts: guard_contact = guard_contact or path.contains(expected)
	return {"start": [start.x, start.y, start.z], "goal": [goal.x, goal.y, goal.z],
		"final": [player.global_position.x, player.global_position.y, player.global_position.z],
		"guard_contact": guard_contact, "floor_contact": player.is_on_floor(),
		"contacts": contacts.keys(), "normal_original_controller_input": true}

func run() -> void:
	var directory: String = "res://../external_packages/group7_completion_20261011/continuation_r010/"
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"))
	var prior: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory+"docs/PREIMAGE_GROUP7_COMPLETION.json"))
	var appended: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory+"docs/RUNTIME_APPEND.json"))
	var plan: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(directory+"docs/GUARD_PLAN.json"))
	record("exact_previous86_models_two_new_guards", data.models == prior.models + appended.new_models and data.models.size() == 88)
	record("all39_lights_exact", data.lights == prior.lights and data.lights.size() == 39)
	record("all8_doors_exact", data.doors == prior.doors and data.doors.size() == 8)
	record("room_capacity_unchanged", data.capacity_delta == 0 and not data.structural_capacity_accepted)
	for file: String in plan.source_pins: record("original_pin_"+file, FileAccess.get_sha256("res://../"+file) == plan.source_pins[file])
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
	record("same_sources_budget8", budget.sources.size() == before_lights+39 and budget.shadow_source_budget == 8)
	record("aft_bays_present", ship.find_child("AftCrownSittingBays", true, false) != null)
	record("aft_lights_present", ship.find_child("AftCrownSittingLighting", true, false) != null)
	var owned: Array[RID] = []
	var captures: Array = []
	var collision_margins: Array = []
	for row: Dictionary in appended.new_models:
		record("guard_model_hash_"+str(row.cell), FileAccess.get_sha256("res://assets/models/"+str(row.file)) == row.sha256)
		record("guard_full_precision_"+str(row.cell), FileAccess.get_file_as_string("res://assets/models/"+str(row.file)+".import").contains("meshes/force_disable_compression=true"))
		var model: Node3D = candidate.get_node(str(row.cell))
		for body: CollisionObject3D in model.find_children("*", "CollisionObject3D", true, false): owned.append(body.get_rid())
		var faces := PackedVector3Array()
		for mesh: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
			record("real_guard_static_contact_"+str(mesh.get_path()), mesh.has_node("StaticContact"))
			var shape: CollisionShape3D = mesh.get_node("StaticContact/SharedShape")
			collision_margins.append({"mesh": str(mesh.get_path()), "ordinary_retained_cache_margin": shape.shape.margin})
			for point: Vector3 in mesh.mesh.get_faces(): faces.append(mesh.global_transform*point)
		var filename: String = "actual_"+str(row.cell)+".tri.f32"
		FileAccess.open(directory+"qa/"+filename, FileAccess.WRITE).store_buffer(faces.to_byte_array())
		captures.append({"cell": row.cell, "filename": filename, "triangles": faces.size()/3})
	var space: PhysicsDirectSpaceState3D = ship.get_world_3d().direct_space_state
	var unexpected: Array = []
	var floor_plates: Dictionary = {}
	for contact: Dictionary in plan.floor_contacts: floor_plates[contact.part] = contact
	for part: Dictionary in plan.parts:
		var center := Vector3.ZERO
		for point: Array in part.vertices_world_xyz: center += vec(point)
		center /= part.vertices_world_xyz.size()
		var points := PackedVector3Array()
		for point: Array in part.vertices_world_xyz: points.append(center+(vec(point)-center)*.99)
		var shape := ConvexPolygonShape3D.new()
		shape.points = points
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape
		query.margin = .00001
		query.exclude = owned
		var hits: Array[Dictionary] = space.intersect_shape(query, 16)
		var paths: Array = []
		for hit: Dictionary in hits: paths.append(str(hit.collider.get_path()))
		var ok: bool = hits.is_empty()
		if floor_plates.has(part.name):
			ok = hits.size() < 16
			for path: String in paths: ok = ok and path.contains("/CompiledStructuralFloors_NotFinishedRooms/"+str(floor_plates[part.name].floor_id)+"/")
		record("guard_protected_source_clear_or_own_floor_plate_"+str(part.name), ok)
		if not ok: unexpected.append({"part": part.name, "paths": paths, "saturated": hits.size() == 16})
	var underside_witnesses: Array = []
	for contact: Dictionary in plan.floor_contacts:
		var point: Vector3 = vec(contact.witness_world_xyz)
		var query := PhysicsRayQueryParameters3D.create(point-Vector3.UP*.05, point+Vector3.UP*.05)
		query.exclude = owned
		var hit: Dictionary = space.intersect_ray(query)
		var path: String = str(hit.collider.get_path()) if not hit.is_empty() else "NONE"
		record("actual_retained_floor_underside_"+str(contact.part), not hit.is_empty() and path.contains("/CompiledStructuralFloors_NotFinishedRooms/"+str(contact.floor_id)+"/") and absf(hit.position.y-106.26) < .0001)
		underside_witnesses.append({"part": contact.part, "floor_id": contact.floor_id, "actual_hit_path": path, "actual_hit_y": hit.position.y if not hit.is_empty() else -INF, "primary_connection_capacity_accepted": false})
	var air: int = 0
	for sign_z: int in [-1, 1]:
		for i in range(83):
			var distance: float = 509.375+i*.25
			var shape := BoxShape3D.new()
			shape.size = Vector3(8, 4, .25)
			shape.margin = 0
			var query := PhysicsShapeQueryParameters3D.new()
			query.shape = shape
			query.margin = 0
			query.exclude = [player.get_rid()]
			query.transform = Transform3D(Basis.IDENTITY, Vector3(0, 108.502, distance*sign_z))
			var hits: Array[Dictionary] = space.intersect_shape(query, 16)
			record("same_full8m_four_metre_air_"+str(air), hits.is_empty())
			if not hits.is_empty():
				var paths: Array = []
				for hit: Dictionary in hits: paths.append(str(hit.collider.get_path()))
				unexpected.append({"air_distance": distance*sign_z, "paths": paths})
			air += 1
	var floor_poses: int = 0
	for sign_z: int in [-1, 1]:
		for x: float in [-3.5, 0, 3.5]:
			for distance: float in [509.5, 510.5, 517, 525, 529.5]:
				var at := Vector3(x, 106.5, distance*sign_z)
				var hit: Dictionary = ray(space, at+Vector3.UP*.05, at-Vector3.UP*.05)
				record("same_original_floor_"+str(floor_poses), not hit.is_empty() and absf(hit.position.y-106.5) < .002)
				record("ordinary_original_worker_"+str(floor_poses), capsule_clear(space, at))
				floor_poses += 1
	var legs: Array = []
	var stops: Array = []
	for sign_z: int in [-1, 1]:
		var term: String = "Fore" if sign_z == -1 else "Aft"
		var cell: String = "G7C10_"+term+"_D18FloorEdges"
		player.global_position = Vector3(0, 106.53, 517*sign_z)
		player.velocity = Vector3.ZERO
		player.set_controls_enabled(true)
		for i in range(15): await physics_frame
		for side: int in [1, -1]:
			var leg: Dictionary = await walk_to(player, Vector3(side*3.1, 106.5, 517*sign_z))
			legs.append(leg)
			record("normal_guard_approach_"+str(legs.size()), leg.reached and leg.floor_contact)
			var stopped: Dictionary = await normal_guard_stop(player, Vector3(side*4.8, 106.5, 517*sign_z), "/"+cell+"/")
			stops.append(stopped)
			record("normal_side_guard_stops_worker_"+str(stops.size()), stopped.guard_contact and stopped.floor_contact and absf(float(stopped.final[1])-106.5) < .12 and absf(float(stopped.final[0])) > 3.6 and absf(float(stopped.final[0])) < 3.99)
			leg = await walk_to(player, Vector3(0, 106.5, 517*sign_z))
			legs.append(leg)
			record("normal_side_guard_return_"+str(legs.size()), leg.reached and leg.floor_contact)
		var leg: Dictionary = await walk_to(player, Vector3(0, 106.5, 529*sign_z))
		legs.append(leg)
		record("normal_end_guard_approach_"+str(legs.size()), leg.reached and leg.floor_contact)
		var stopped: Dictionary = await normal_guard_stop(player, Vector3(0, 106.5, 531*sign_z), "/"+cell+"/")
		stops.append(stopped)
		record("normal_end_guard_stops_worker_"+str(stops.size()), stopped.guard_contact and stopped.floor_contact and absf(float(stopped.final[1])-106.5) < .12 and absf(float(stopped.final[2])) > 529.5 and absf(float(stopped.final[2])) < 529.99)
		leg = await walk_to(player, Vector3(0, 106.5, 517*sign_z))
		legs.append(leg)
		record("normal_end_guard_return_"+str(legs.size()), leg.reached and leg.floor_contact)
	physical_key(false)
	var out: Dictionary = {"status": "PASS" if errors.is_empty() else "HOLD", "checks": checks.size(), "errors": errors,
		"new_guard_models": 2, "new_closed_parts": plan.parts.size(), "new_floor_or_room_ids": 0,
		"protected_source_queries": plan.parts.size(), "unexpected_source_contacts": unexpected,
		"actual_retained_floor_underside_witnesses": underside_witnesses,
		"unchanged_full8m_four_metre_air_slices": air, "normal_floor_worker_poses": floor_poses,
		"normal_original_player_walking_legs": legs, "normal_guard_contact_stops": stops,
		"fixture_seeds": 2, "position_writes_between_walking_legs_and_guard_stops": 0,
		"actual_body_triangle_captures": captures, "ordinary_cache_collision_margins": collision_margins,
		"query_exclusions": "Only two new guard model RIDs for source/underside identification. Air slices exclude only player. Ordinary floor/worker/walking/guard contact excludes none.",
		"primary_connection_capacity_species_cart_pressure_current_main_graphical_or_whole_group_accepted": false}
	FileAccess.open(directory+"qa/RUNTIME_CHECK.json", FileAccess.WRITE).store_string(JSON.stringify(out, "  ")+"\n")
	print(JSON.stringify({"status": out.status, "checks": out.checks, "errors": errors.size(), "unexpected": unexpected.size(), "air": air, "legs": legs.size(), "stops": stops.size()}))
	quit(0 if errors.is_empty() else 1)
