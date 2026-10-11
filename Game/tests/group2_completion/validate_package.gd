extends SceneTree
# Real imported-source and controller checks in a scoped construction fixture.
# No shared ship edits, capacity adoption, physical cart or final-art claim.
var checks := 0
var doors_checked := 0
var motion_samples := 0
var room_rows: Array = []
var failures: Array = []

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		push_error(message)

func v(a: Array) -> Vector3:
	return Vector3(a[0], a[1], a[2])

func run() -> void:
	var directory := DirAccess.open("res://data/group2_completion/contracts")
	var keys: Array = []
	for file in directory.get_files():
		if file.ends_with(".json"):
			keys.append(file.trim_suffix(".json"))
	keys.sort()
	var smoke := "--group2-smoke" in OS.get_cmdline_user_args()
	check((keys.size() == 4 if smoke else keys.size() == 86) and "790" not in keys, "Expected source count; protected790 excluded")
	var floor_data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_completion/FLOOR_INTERFACE.json"))
	var actor := CharacterBody3D.new()
	actor.position = Vector3(0, 200, 0)
	root.add_child(actor)
	var district := Node3D.new()
	root.add_child(district)
	var floors := Node3D.new()
	root.add_child(floors)
	for row in floor_data.rows:
		var faces := PackedVector3Array()
		for triangle in row.triangles:
			# Up-facing physics triangles from the actual missing-only interface.
			var points: Array[Vector3] = []
			for p in triangle:
				points.append(Vector3(p[0], row.floor_y, p[1]))
			if (points[1] - points[0]).cross(points[2] - points[0]).y > 0:
				points.reverse()
			faces.append_array(PackedVector3Array(points))
		var body := StaticBody3D.new()
		var collision := CollisionShape3D.new()
		var shape := ConcavePolygonShape3D.new()
		shape.set_faces(faces)
		collision.shape = shape
		body.add_child(collision)
		floors.add_child(body)
	for key in keys:
		var section: Node3D = load("res://scripts/group2_completion/package.gd").build_section(district, key)
		var contract: Dictionary = section.get_meta("source_contract")
		var visual: Node3D = section.get_node("RetainedSource")
		var section_checks_before := checks
		for marker in contract.get("markers", []):
			var source := visual.find_child(str(marker.name), true, false) as Node3D
			check(source != null, key + " marker " + str(marker.name))
			if source != null:
				check(source.global_position.distance_to(v(marker.world_xyz)) < .002, key + " marker pose")
		var lights: Array[Node] = section.find_children("*", "OmniLight3D", true, false)
		for light in lights:
			check(not light.visible and light.shadow_enabled and light.omni_range == 10.0, key + " light admission state")
		for frame in range(3):
			await physics_frame
		var manager: Node = load("res://scripts/lighting_budget.gd").new()
		section.add_child(manager)
		var review_views: Array = contract.get("source_views", [])
		if not review_views.is_empty():
			actor.global_position = v(review_views[0].camera_world_xyz) - Vector3(0, 1.65, 0)
			for frame in range(2):
				await physics_frame
			manager.configure(section, actor)
			check(manager.sources.size() == lights.size(), key + " existing light manager discovers all fixtures")
			var admitted := 0
			for light in lights:
				if light.visible:
					admitted += 1
					check(light.shadow_enabled, key + " admitted fixture retains shadows")
			check(admitted <= 8, key + " eight-shadow-source budget preserved")
			actor.global_position = Vector3(0, 200, 0)
			for frame in range(2):
				await physics_frame
		for door in section.get_children():
			if not door.has_method("interact"):
				continue
			doors_checked += 1
			check(door.open_fraction == 0.0 and not door.desired_open, key + " source door starts closed")
			if door.get_script().resource_path.ends_with("fitted_entry.gd"):
				door.interact(actor)
				check(door.access_refused and not door.desired_open, key + " unknown private visit rejected")
				var visit: RefCounted = load("res://scripts/d04_court_service_visit.gd").new()
				visit.actor = weakref(actor)
				visit.request_id = "group2-scoped-test"
				visit.court_ids.append(door.persistent_id)
				visit.consent_known = true
				visit.consent_allowed = true
				visit.active = true
				door.visit = visit
			var closed: Array[Transform3D] = []
			for leaf in door.leaves:
				closed.append(leaf.global_transform)
			# Exercise inherited motion with actual source fittings; record clipping
			# rather than masking it or silently accepting an untested pose.
			door.interact(actor)
			for frame in range(80):
				await physics_frame
				if frame % 10 == 0:
					for leaf in door.leaves:
						motion_samples += 1
						for collision in leaf.get_children():
							if not collision is CollisionShape3D:
								continue
							var query := PhysicsShapeQueryParameters3D.new()
							query.shape = collision.shape
							query.transform = collision.global_transform
							query.margin = .001
							query.exclude = [leaf.get_rid()]
							for hit in section.get_world_3d().direct_space_state.intersect_shape(query, 64):
								# Floor/header seals intentionally contact when closed.
								# Only interior motion is required to clear fixed source.
								if door.open_fraction > .02 and door.open_fraction < .98:
									check(not (hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D), key + " moving fitting clips fixed " + str(hit.collider.get_path()))
			check(door.open_fraction > .999, key + " actual source fitting opens")
			door.interact(actor)
			for frame in range(80):
				await physics_frame
			check(door.open_fraction < .001, key + " source fitting closes")
			for i in range(door.leaves.size()):
				check(door.leaves[i].global_transform.is_equal_approx(closed[i]), key + " exact closed transform restored")
			if door.get_script().resource_path.ends_with("fitted_entry.gd"):
				door.visit = null
		room_rows.append({"key": key, "checks": checks - section_checks_before, "lights": lights.size()})
		section.free()
		await physics_frame
		print("GROUP2 SECTION ", key, " checks=", checks - section_checks_before)
	var output := {"pass": failures.is_empty(), "checks": checks, "sections": room_rows,
		"smoke_only": smoke,
		"door_fittings": doors_checked, "motion_samples": motion_samples, "failures": failures,
		"scope": "Opt-in imported source/controller fixtures; main unchanged; no cart/occupancy/engineering/final visual acceptance"}
	var file := FileAccess.open("res://artifacts/group2_completion_package.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(output, "\t") + "\n")
	print("GROUP2 PACKAGE ", "PASS" if failures.is_empty() else "HOLD", " ", checks, " checks ", doors_checked, " doors ", motion_samples, " motion samples")
	quit(0 if failures.is_empty() else 1)
