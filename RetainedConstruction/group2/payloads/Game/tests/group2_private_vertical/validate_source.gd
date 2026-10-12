extends SceneTree
# Actual retained suite shafts and original moving cabin/controller, isolated floors.
var checks := 0
var samples := 0
func _initialize() -> void:
	call_deferred("run")

func floor_fixture(parent: Node3D, row: Dictionary) -> void:
	var faces := PackedVector3Array()
	for triangle in row.triangles:
		var points: Array[Vector3] = []
		for p in triangle:
			points.append(Vector3(p[0], row.floor_y, p[1]))
		if (points[1]-points[0]).cross(points[2]-points[0]).y > 0:
			points.reverse()
		faces.append_array(PackedVector3Array(points))
	var body := StaticBody3D.new()
	body.name = str(row.id)
	var shape := ConcavePolygonShape3D.new()
	shape.set_faces(faces)
	var contact := CollisionShape3D.new()
	contact.shape = shape
	body.add_child(contact)
	parent.add_child(body)

func moving_clear(lift: Node3D) -> void:
	var contacts: Array[Node] = lift.cabin.find_children("*", "CollisionShape3D", true, false)
	contacts.append_array(lift.cabin_gate.find_children("*", "CollisionShape3D", true, false))
	for gate in lift.landing_gates:
		contacts.append_array(gate.find_children("*", "CollisionShape3D", true, false))
	for contact in contacts:
		if not contact.get_parent() is AnimatableBody3D:
			continue
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = contact.shape
		query.transform = contact.global_transform
		query.margin = .0001
		query.exclude = [lift.cabin.get_rid()]
		for hit in lift.get_world_3d().direct_space_state.intersect_shape(query, 64):
			if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D:
				assert(false, "Moving source component clips fixed source: suite %s Y%.4f %s position=%s phase=%s fraction=%s -> %s" % [lift.get_meta("source_index"),lift.cabin.position.y,contact.get_path(),contact.global_position,lift.phase,lift.landing_gates[0].open_fraction,hit.collider.get_path()])
		checks += 1
	samples += 1

func select_button(lift: Node3D, actor: CharacterBody3D, goal: int) -> void:
	var button: Node3D = lift.find_child(lift.identity_prefix + "_cabin_" + lift._stop_id(goal), true, false)
	var delta: Vector3 = button.global_position - actor.camera.global_position
	actor.rotation.y = atan2(-delta.x, -delta.z)
	actor.pitch = atan2(delta.y, Vector2(delta.x,delta.z).length())
	actor.camera.rotation.x = actor.pitch
	assert(actor.target_from_view() == button, "Actual authored panel button selectable")
	var key := InputEventKey.new()
	key.keycode = KEY_E;key.physical_keycode = KEY_E;key.pressed = true
	Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(3): await physics_frame
	assert(lift.phase == "idle", "Unfocused E refused")
	key.pressed = false;Input.parse_input_event(key.duplicate())
	var focus := InputEventMouseButton.new()
	focus.button_index = MOUSE_BUTTON_RIGHT;focus.pressed = true
	Input.parse_input_event(focus.duplicate())
	key.pressed = true;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(3): await physics_frame
	assert(lift.destination_floor == goal and lift.phase == "closing")
	key.pressed = false;Input.parse_input_event(key.duplicate())
	focus.pressed = false;Input.parse_input_event(focus.duplicate());Input.flush_buffered_events()
	checks += 3

func trip(lift: Node3D, actor: CharacterBody3D, payload: RigidBody3D, goal: int) -> void:
	await select_button(lift,actor,goal)
	var reached := false
	var previous := 0.0
	for frame in range(1500):
		await physics_frame
		assert(abs(lift.travel_velocity) <= lift.maximum_speed + .001)
		if lift.phase == "moving":
			assert(lift.cabin_gate.open_fraction < .001)
			for gate in lift.landing_gates:
				assert(gate.open_fraction < .001 and not gate.cabin_present_and_stopped)
			assert(abs(lift.travel_velocity-previous) < .025)
		moving_clear(lift)
		previous = lift.travel_velocity
		assert(actor.get_parent().name == "PersistentActors" and payload.get_parent() == actor.get_parent())
		assert(abs(actor.global_position.y-lift.cabin.global_position.y)<.18, "Original capsule remains physically supported")
		assert(abs(payload.global_position.y-lift.cabin.global_position.y-.13)<.12, "Independent loose body support: suite=%s payload=%s cabin=%s velocity=%s sleeping=%s phase=%s wakes=%s count=%s" % [lift.get_meta("source_index"),payload.global_position,lift.cabin.global_position,payload.linear_velocity,payload.sleeping,lift.phase,lift.departure_wake_events,lift.last_woken_body_count])
		checks += 4
		if lift.current_floor == goal and lift.phase == "idle":
			reached = true
			break
	assert(reached)

func walk_source(actor: CharacterBody3D, target: Vector3) -> void:
	var key := InputEventKey.new();key.keycode=KEY_W;key.physical_keycode=KEY_W;key.pressed=true
	Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	var reached := false
	for frame in range(300):
		var delta := target-actor.global_position
		if Vector2(delta.x,delta.z).length()<.09: reached=true;break
		actor.rotation.y=atan2(-delta.x,-delta.z)
		await physics_frame
		assert(abs(actor.global_position.y-target.y)<.12,"Source cabin/landing seam supports original capsule")
		checks += 1
	key.pressed=false;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(15):await physics_frame
	assert(reached and actor.is_on_floor())
	checks += 2

func board_and_leave(lift: Node3D, actor: CharacterBody3D) -> void:
	await walk_source(actor,lift.cabin.to_global(Vector3(0,0,-.65)))
	await walk_source(actor,lift.cabin.to_global(Vector3(0,0,.75)))
	await walk_source(actor,lift.cabin.to_global(Vector3(0,0,-.65)))
	await walk_source(actor,lift.cabin.to_global(Vector3(.90,0,-1.0)))

func run() -> void:
	var world := Node3D.new();root.add_child(world)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_private_vertical/INTERFACES.json"))
	var floors: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_completion/FLOOR_INTERFACE.json"))
	var results: Array = []
	for row in data.suites:
		var key := str(int(row.source_index))
		assert(key != "790")
		var section: Node3D = load("res://scripts/group2_completion/package.gd").build_section(world,key)
		floor_fixture(section,row.lower_successor)
		for floor in floors.rows:
			if floor.source_owner == key and floor.floor_y == 106.5:
				floor_fixture(section,floor)
		var pit: Node3D = (load("res://assets/group2_private_vertical/PIT_"+key+"_r001.glb") as PackedScene).instantiate()
		section.add_child(pit)
		load("res://scripts/static_contact_cache.gd").attach_group(pit,pit.find_children("*","MeshInstance3D",true,false))
		var lift: Node3D = load("res://scripts/group2_private_vertical/package.gd").build_for_section(section,key)
		for frame in range(5): await physics_frame
		assert(not lift.operation_ready and not lift.request_floor(1))
		assert(lift.cabin_gate.open_fraction == 0)
		for gate in lift.landing_gates: assert(gate.open_fraction == 0)
		assert(lift.deck_numbers == [17,17] and lift.stop_ids == ["private_lower","private_upper"])
		assert(abs(lift.cabin.rotation.y + lift.rotation.y - float(row.cabin_yaw)) < .00001)
		lift.operation_ready = true
		lift.phase = "opening";lift._set_present()
		for frame in range(100): await physics_frame
		assert(lift.phase == "idle")
		var actors := Node3D.new();actors.name = "PersistentActors";world.add_child(actors)
		var actor: CharacterBody3D = load("res://scripts/player.gd").new()
		actors.add_child(actor)
		actor.spawn_position = lift.cabin.to_global(Vector3(.90,.05,-1.0))
		actor.global_position = actor.spawn_position
		var payload := RigidBody3D.new();payload.mass = 1.0
		var shape := BoxShape3D.new();shape.size = Vector3(.25,.25,.25)
		var contact := CollisionShape3D.new();contact.shape = shape;payload.add_child(contact)
		actors.add_child(payload);payload.global_position = lift.cabin.to_global(Vector3(-.8,.16,-1.8))
		for frame in range(30): await physics_frame
		assert(actor.is_on_floor())
		moving_clear(lift)
		assert(not lift.request_floor(-1) and not lift.request_floor(2))
		await trip(lift,actor,payload,1)
		await board_and_leave(lift,actor)
		await trip(lift,actor,payload,0)
		await board_and_leave(lift,actor)
		assert(lift.departure_wake_events == 2 and lift.last_woken_body_count >= 1)
		# Actual dynamic threshold blocker must keep both source gates from departing.
		var blocker := RigidBody3D.new();blocker.gravity_scale = 0
		var block_contact := CollisionShape3D.new();var sphere := SphereShape3D.new();sphere.radius = .18
		block_contact.shape = sphere;blocker.add_child(block_contact);actors.add_child(blocker)
		blocker.global_position = lift.landing_gates[0].to_global(Vector3(0,1,0))
		for frame in range(5): await physics_frame
		lift.request_floor(1)
		for frame in range(100): await physics_frame
		assert(lift.phase == "closing" and abs(lift.cabin.position.y-102) < .001)
		blocker.free();lift.request_floor(0)
		for frame in range(100): await physics_frame
		assert(lift.phase == "idle")
		results.append({"source_index":row.source_index,"two_trips":true,"actual_source_shaft_clearance":true,
			"original_player_RMB_E":true,"capsule_and_unparented_loose_body_supported":true,
			"obstruction_holds_departure":true,"initial_default_held":true,
			"lower_and_upper_source_boarding_WASD":true})
		actors.free();section.free()
		await physics_frame
		print("PRIVATE VERTICAL suite "+key+" passed")
	var file := FileAccess.open("res://artifacts/group2_private_vertical.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass":true,"checks":checks,"moving_samples":samples,"suites":results,
		"production_adoption":false,"790_excluded":true,"physical_cart_or_integrated_boarding_route_accepted":false,
		"source_lower_upper_boarding_fixtures_pass":true,
		"scope":"Exact source/controller/pit fixtures; not shared support, occupant/save/species/engineering/final game acceptance"},"\t")+"\n")
	print("GROUP2 PRIVATE VERTICAL PASS five exact-source suites, original controls, physical capsule/loose-body carry, all moving source clearance")
	quit()
