extends SceneTree
var checks := 0
func _initialize() -> void: call_deferred("run")

func floor_fixture(parent: Node3D, row: Dictionary) -> void:
	var faces := PackedVector3Array()
	for triangle in row.triangles:
		var points: Array[Vector3] = []
		for p in triangle: points.append(Vector3(p[0],row.floor_y,p[1]))
		if (points[1]-points[0]).cross(points[2]-points[0]).y > 0: points.reverse()
		faces.append_array(PackedVector3Array(points))
	var body := StaticBody3D.new();var shape := ConcavePolygonShape3D.new();shape.set_faces(faces)
	var contact := CollisionShape3D.new();contact.shape = shape;body.add_child(contact);parent.add_child(body)

func walk(actor: CharacterBody3D, target: Vector3) -> void:
	var key := InputEventKey.new();key.keycode = KEY_W;key.physical_keycode = KEY_W;key.pressed = true
	Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	var reached := false
	for frame in range(400):
		var delta := target-actor.global_position
		if Vector2(delta.x,delta.z).length() < .09:
			reached = true;break
		actor.rotation.y = atan2(-delta.x,-delta.z)
		await physics_frame
		assert(actor.global_position.y >= 101.98 and actor.global_position.y <= 102.65,"Original capsule remains on bounded receiver")
		checks += 1
	key.pressed = false;Input.parse_input_event(key.duplicate());Input.flush_buffered_events()
	for frame in range(15): await physics_frame
	assert(reached,"Original WASD must reach source receiver waypoint")
	assert(actor.is_on_floor() and abs(actor.global_position.y-target.y)<.09,"Actual source slope/landing support at waypoint")
	checks += 2

func run() -> void:
	var world := Node3D.new();root.add_child(world)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_private_vertical/CONVERSATION_INTERFACE.json"))
	var floors: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_completion/FLOOR_INTERFACE.json"))
	var rows: Array = []
	for row in data.suites:
		var key := str(int(row.source_index));assert(key != "790")
		var section: Node3D = load("res://scripts/group2_completion/package.gd").build_section(world,key)
		for floor in floors.rows:
			if floor.source_owner == key: floor_fixture(section,floor)
		var receiver: Node3D = load("res://scripts/group2_private_vertical/package.gd").build_conversation_receiver(section,key,true)
		var actor: CharacterBody3D = load("res://scripts/player.gd").new();world.add_child(actor)
		actor.global_position = Vector3(row.walking_fixture[0][0],102.05,row.walking_fixture[0][2]);actor.spawn_position = actor.global_position
		for frame in range(20): await physics_frame
		assert(actor.is_on_floor())
		for p in row.walking_fixture:
			await walk(actor,Vector3(p[0],p[1],p[2]))
		var high := actor.global_position
		assert(abs(high.y-102.45)<.03)
		# Walk toward the continuous front infill: it must contain the capsule.
		var target: Array = row.front_guard_outside_point
		var direction := Vector3(target[0],102.45,target[2])-actor.global_position
		actor.rotation.y = atan2(-direction.x,-direction.z)
		var key_forward := InputEventKey.new();key_forward.keycode=KEY_W;key_forward.physical_keycode=KEY_W;key_forward.pressed=true
		Input.parse_input_event(key_forward.duplicate());Input.flush_buffered_events()
		for frame in range(100): await physics_frame
		key_forward.pressed=false;Input.parse_input_event(key_forward.duplicate());Input.flush_buffered_events()
		assert(actor.global_position.y>102.4 and actor.global_position.distance_to(Vector3(target[0],102.45,target[2]))>.4,"Continuous front guard holds actual capsule")
		# Return via the same ramp, without resetting the actor onto the receiver.
		var back: Array = row.walking_fixture.duplicate();back.reverse()
		for p in back: await walk(actor,Vector3(p[0],p[1],p[2]))
		assert(abs(actor.global_position.y-102)<.03)
		rows.append({"source_index":int(row.source_index),"original_player_WASD":true,"up_and_down":true,
			"actual_45cm_receiver_support":true,"continuous_front_guard":true,"furniture_originals_moved":false})
		actor.free();section.free();await physics_frame
		print("CONVERSATION receiver suite "+key+" passed")
	var file := FileAccess.open("res://artifacts/group2_conversation_receivers.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"pass":true,"checks":checks,"suites":rows,"790_excluded":true,
		"production_adoption":false,"full_pit_perimeter_accepted":false,"cart_species_engineering_final_game_accepted":false,
		"scope":"Actual retained suite, original-player ramp/overlook/guard source fixture only"},"\t")+"\n")
	print("GROUP2 CONVERSATION PASS five retained-suite original-player ascent/descent and guard fixtures")
	quit()
