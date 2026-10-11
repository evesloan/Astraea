extends SceneTree
# Original RMB/E controller, one source-backed stationary entry fixture.
# These poses do not establish an integrated receiving/walking/cart route.
func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var world := Node3D.new()
	root.add_child(world)
	var section: Node3D = load("res://scripts/group2_completion/package.gd").build_section(world, "781")
	var contract: Dictionary = section.get_meta("source_contract")
	var polygon := PackedVector2Array()
	for p in contract.floor_proposal.boundary:
		polygon.append(Vector2(p[0], p[1]))
	var indices := Geometry2D.triangulate_polygon(polygon)
	var faces := PackedVector3Array()
	for i in range(0, indices.size(), 3):
		var points: Array[Vector3] = []
		for k in range(3):
			var p: Vector2 = polygon[indices[i+k]]
			points.append(Vector3(p.x, 102, p.y))
		# Godot uses clockwise front faces (opposite mathematical cross normal).
		if (points[1]-points[0]).cross(points[2]-points[0]).y > 0:
			points.reverse()
		faces.append_array(PackedVector3Array(points))
	var floor_body := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var triangles := ConcavePolygonShape3D.new()
	triangles.set_faces(faces)
	floor_shape.shape = triangles
	floor_body.add_child(floor_shape)
	world.add_child(floor_body)
	var actor: CharacterBody3D = load("res://scripts/player.gd").new()
	actor.position = Vector3(-96.65, 102.05, -42.7)
	world.add_child(actor)
	var entry: Node3D
	for child in section.get_children():
		if child.get_script() != null and child.get_script().resource_path.ends_with("fitted_entry.gd"):
			entry = child
	assert(entry != null)
	for frame in range(20):
		await physics_frame
	var diagnostic := PhysicsRayQueryParameters3D.create(Vector3(-96.65, 103, -42.7), Vector3(-96.65, 99, -42.7))
	diagnostic.exclude = [actor.get_rid()]
	print("SOURCE FLOOR FIXTURE position=", actor.global_position, " velocity=", actor.velocity, " on_floor=", actor.is_on_floor(), " ray=", actor.get_world_3d().direct_space_state.intersect_ray(diagnostic))
	assert(actor.is_on_floor(), "Original player supported on source floor fixture")
	var call := entry.find_child("PrivateEntry_01_DATUM_call_button", true, false) as Node3D
	assert(call != null)
	var delta: Vector3 = call.global_position - actor.camera.global_position
	actor.rotation.y = atan2(-delta.x, -delta.z)
	actor.pitch = atan2(delta.y, Vector2(delta.x, delta.z).length())
	actor.camera.rotation.x = actor.pitch
	assert(actor.target_from_view() == entry, "Actual fixed call plate is selectable")
	var focus := InputEventMouseButton.new()
	focus.button_index = MOUSE_BUTTON_RIGHT
	focus.pressed = true
	Input.parse_input_event(focus.duplicate())
	var key := InputEventKey.new()
	key.keycode = KEY_E
	key.physical_keycode = KEY_E
	key.pressed = true
	Input.parse_input_event(key.duplicate())
	for frame in range(10):
		await physics_frame
	assert(entry.access_refused and not entry.desired_open, "Unknown private visit refused through RMB/E")
	key.pressed = false
	Input.parse_input_event(key.duplicate())
	var visit: RefCounted = load("res://scripts/d04_court_service_visit.gd").new()
	visit.actor = weakref(actor)
	visit.request_id = "group2-interaction-fixture"
	visit.court_ids.append(entry.persistent_id)
	visit.consent_known = true
	visit.consent_allowed = true
	visit.active = true
	entry.visit = visit
	key.pressed = true
	Input.parse_input_event(key.duplicate())
	for frame in range(85):
		await physics_frame
	assert(entry.open_fraction > .999, "Original RMB/E opens exact source fitting")
	key.pressed = false
	Input.parse_input_event(key.duplicate())
	assert(actor.target_from_view() == entry, "Fixed plate remains selectable with retracted leaves")
	key.pressed = true
	Input.parse_input_event(key.duplicate())
	for frame in range(85):
		await physics_frame
	assert(entry.open_fraction < .001, "Original RMB/E closes source fitting")
	key.pressed = false
	Input.parse_input_event(key.duplicate())
	focus.pressed = false
	Input.parse_input_event(focus.duplicate())
	key.pressed = true
	Input.parse_input_event(key.duplicate())
	for frame in range(10):
		await physics_frame
	assert(entry.open_fraction < .001, "Unfocused E does not open source fitting")
	key.pressed = false
	Input.parse_input_event(key.duplicate())
	entry.visit = null
	var file := FileAccess.open("res://artifacts/group2_completion_interaction.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass": true, "source_index": 781, "original_player": true,
		"supported_stationary_fixture": true, "RMB_E": true, "fixed_plate_after_retraction": true,
		"unknown_visit_refused": true, "unfocused_E_refused": true, "visit_cleared": true,
		"doors_end_closed": true, "integrated_route_accepted": false}, "\t") + "\n")
	print("GROUP2 INTERACTION PASS: original player, supported source fixture, actual fixed plate, RMB/E, unknown visit and unfocused rejection; ends closed")
	quit()
