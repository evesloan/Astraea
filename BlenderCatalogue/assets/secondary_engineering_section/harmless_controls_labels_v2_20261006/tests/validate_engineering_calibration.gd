extends SceneTree
# SCRATCH DRAFT, UNRUN. Run only after reviewed integration and fresh imports.
# This test uses the real main scene and unchanged physical player. Ten declared
# panel arrivals are diagnostic fixtures; movement within a panel uses ordinary W.
const CONTRACT := "res://data/architecture/ENGINEERING_CALIBRATION_DRAFT.json"
const RECEIPT := "res://artifacts/engineering_calibration_validation.json"
var actor: CharacterBody3D
var ship: Node3D
var bank: Node3D
var gate: Node3D
var floors: Node3D
var data: Dictionary
var main: Node
var failed := false
var records: Array = []
var frames := 0
var arrivals := 0
var walked_frames := 0
var _checkpoint := "start"
var _started := 0
var _gate_state: Array = []

func _initialize() -> void:
	_started = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if not failed and Time.get_ticks_msec() - _started > 600000: require(false, "600-second test watchdog")
	return false

func require(ok: bool, reason: String) -> bool:
	if ok and not failed: return true
	if not failed:
		failed = true
		release_inputs()
		write_receipt("FAIL", reason)
		push_error("CALIBRATION FAIL at " + _checkpoint + ": " + reason)
		quit(1)
	return false

func write_receipt(status: String, reason := "") -> void:
	var result := {"status":status,"checkpoint":_checkpoint,"reason":reason,"frames":frames,
		"panel_diagnostic_arrivals":arrivals,"ordinary_walk_frames":walked_frames,"records":records,
		"contract_sha256":FileAccess.get_sha256(CONTRACT),
		"scope":"Focused original-player first-hit/dispatch, local feedback/rest, gate-preservation and pose tests. Audio listening, full-cell route regression, screenshots and aggregate checks are separate.",
		"listening_accepted":false,"visual_accepted":false,"aggregate_pass":false}
	var file := FileAccess.open(RECEIPT, FileAccess.WRITE)
	if file == null:
		push_error("Cannot write calibration receipt")
		quit(1)
		return
	file.store_string(JSON.stringify(result,"  ") + "\n")

func key(code: Key, down: bool, echo := false) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = down
	event.echo = echo
	Input.parse_input_event(event)

func focus(down: bool) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_RIGHT
	event.pressed = down
	Input.parse_input_event(event)

func release_inputs() -> void:
	for code in [KEY_W,KEY_A,KEY_S,KEY_D,KEY_E,KEY_ESCAPE]: key(code,false)
	focus(false)

func aim(point: Vector3) -> bool:
	var delta: Vector3 = point - actor.camera.global_position
	var pitch := atan2(delta.y, Vector2(delta.x,delta.z).length())
	if not require(absf(pitch) <= 1.35, "Proposed pose requires pitch outside original limit"): return false
	actor.rotation.y = atan2(-delta.x,-delta.z)
	actor.pitch = pitch
	actor.camera.rotation.x = pitch
	return true

func advance(count: int) -> bool:
	for index in range(count):
		if failed: return false
		await physics_frame
		frames += 1
		if not require(frames <= 24000, "Focused test frame budget exceeded"): return false
	return true

func tap_e() -> bool:
	key(KEY_E,true)
	if not await advance(2): return false
	key(KEY_E,false)
	return await advance(2)

func xyz(a: Array) -> Vector3:
	return Vector3(float(a[0]),float(a[1]),float(a[2]))

func as_array(p: Vector3) -> Array:
	return [p.x,p.y,p.z]

func support_and_capsule(expected_owner: String) -> bool:
	if not require(actor.is_physics_processing() and actor.is_on_floor(), "Real original player lost physical support"): return false
	if not require(actor.camera.position.is_equal_approx(Vector3(0,1.65,0)), "Original camera height changed"): return false
	var capsule: CollisionShape3D
	for child in actor.get_children():
		if child is CollisionShape3D: capsule = child
	if not require(capsule != null and capsule.shape is CapsuleShape3D, "Original capsule missing"): return false
	if not require(is_equal_approx(capsule.shape.radius,.3) and is_equal_approx(capsule.shape.height,1.8) and capsule.position.is_equal_approx(Vector3(0,.9,0)), "Original capsule resized or offset"): return false
	var space := actor.get_world_3d().direct_space_state
	var feet := actor.global_position
	var query := PhysicsRayQueryParameters3D.create(feet+Vector3.UP*.15,feet-Vector3.UP*.15,1)
	query.exclude = [actor.get_rid()]
	var hit := space.intersect_ray(query)
	if not require(not hit.is_empty() and hit.normal.y > .99, "No real floor below original feet"): return false
	if not require(floors.is_ancestor_of(hit.collider) and str(hit.collider.get_parent().name) == expected_owner, "Incorrect floor owner under control approach"): return false
	# Lift the QUERY, not the player, 10 mm to exclude normal floor tangency.
	var envelope := PhysicsShapeQueryParameters3D.new()
	envelope.shape = capsule.shape
	envelope.transform = capsule.global_transform.translated(Vector3.UP*.01)
	envelope.exclude = [actor.get_rid()]
	envelope.collision_mask = 1
	var contacts := space.intersect_shape(envelope,128)
	return require(contacts.is_empty(), "Original standing capsule intrudes into architecture/machinery")

func walk_to(point: Vector3, owner: String) -> bool:
	focus(false)
	actor.pitch = 0.0
	actor.camera.rotation.x = 0.0
	var delta := Vector2(point.x-actor.global_position.x,point.z-actor.global_position.z)
	var allowance := ceili(delta.length()/3.1*60.0)+240
	for index in range(allowance):
		delta = Vector2(point.x-actor.global_position.x,point.z-actor.global_position.z)
		var speed := Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length() < .13 and speed < .06:
			key(KEY_W,false)
			return support_and_capsule(owner)
		if delta.length() > .12: actor.rotation.y = atan2(-delta.x,-delta.y)
		key(KEY_W,delta.length() > speed*speed/32.0+.035)
		if not await advance(1): return false
		walked_frames += 1
		if not support_and_capsule(owner): return false
	key(KEY_W,false)
	return require(false,"Ordinary W approach stalled; do not teleport or modify controller to make it pass")

func original_first_hit(control: Node3D, record: Dictionary) -> bool:
	if not aim(xyz(record.target_center_xyz)): return false
	focus(true)
	if not await advance(3): return false
	if not require(actor.target_from_view() == control and actor.interaction_target == control, "Wrong first-hit source target from real original eye"): return false
	var start: Vector3 = actor.camera.global_position
	var query := PhysicsRayQueryParameters3D.create(start,start-actor.camera.global_basis.z*2.5)
	query.exclude = [actor.get_rid()]
	query.collide_with_areas = true
	var hit := actor.get_world_3d().direct_space_state.intersect_ray(query)
	return require(not hit.is_empty() and hit.collider == control.target_area, "First collider must be this precise Area, never an ancestor proxy")

func exercise_control(control: Node3D, record: Dictionary) -> bool:
	_checkpoint = str(record.id)
	if not await walk_to(xyz(record.proposed_approach_xyz),str(record.floor_owner)): return false
	if not await original_first_hit(control,record): return false
	var home: Transform3D = control.actuator.transform
	var before: int = control.activation_count
	if not require(control.get_interaction_label() == str(record.label), "Authored SunCorp prompt identity mismatch"): return false
	focus(false)
	if not await tap_e(): return false
	if not require(control.activation_count == before, "E without RMB activated control"): return false
	focus(true)
	if not await advance(2): return false
	if not await tap_e(): return false
	if not require(control.activation_count == before+1 and control.busy, "Original RMB/E did not start one control activation"): return false
	if not require(control.get_interaction_label() == str(record.faux_status), "Brief authored status identity mismatch"): return false
	if not require(not control.actuator.transform.is_equal_approx(home), "Actuator did not visibly move from its original rest pose"): return false
	key(KEY_E,true,true)
	if not await advance(2): return false
	key(KEY_E,false)
	if not await tap_e(): return false
	if not require(control.activation_count == before+1, "Echo/repeated E queued duplicate active effects"): return false
	# Every control returns to exact pose and original override pointers, not a
	# rounded equivalent; no cumulative drift even after repeated input.
	if not await advance(65): return false
	if not require(not control.busy and control.actuator.transform == home, "Control did not restore its exact imported rest transform"): return false
	if not require(control.get_interaction_label() == str(record.label), "Status did not return to authored prompt"): return false
	for surface in range(control.actuator.mesh.get_surface_count()):
		if not require(control.actuator.get_surface_override_material(surface) == null, "Local material override leaked after return"): return false
	if not require(gate.desired_open == _gate_state[0] and is_equal_approx(gate.open_fraction,float(_gate_state[1])), "Harmless calibration changed real gate state"): return false
	records.append({"id":record.id,"source_marker":record.source_marker,"actual_feet_xyz":as_array(actor.global_position),
		"actual_eye_xyz":as_array(actor.camera.global_position),"first_hit":"SourceCalibrationTarget","activations":control.activation_count-before,
		"rest_exact":true,"audio_start_requested_and_accepted":control.last_audio_started})
	return true

func occlusion_negative(control: Node3D, record: Dictionary) -> bool:
	if not await original_first_hit(control,record): return false
	var blocker := StaticBody3D.new()
	blocker.name = "QA_TemporaryFirstHitBlocker"
	var contact := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(.4,.4,.4)
	contact.shape = box
	blocker.add_child(contact)
	root.add_child(blocker)
	blocker.global_position = actor.camera.global_position.lerp(xyz(record.target_center_xyz),.5)
	if not await advance(3): return false
	var before: int = control.activation_count
	if not require(actor.target_from_view() == null, "Opaque foreground fixture did not block target"): return false
	if not await tap_e(): return false
	if not require(control.activation_count == before, "E interacted through opaque blocker"): return false
	blocker.queue_free()
	return await advance(3)

func check_pins() -> bool:
	for path in ["scripts/player.gd","scripts/fixture_switch.gd","scripts/physics_tether.gd","scripts/service_door.gd","scripts/engineering_cell_gate.gd","scripts/engineering_cell_gate_target.gd","scripts/lighting_budget.gd"]:
		if not require(FileAccess.get_sha256("res://"+path) == str(data.retained_runtime_pins[path]), "Protected controller changed: "+path): return false
	return true

func run() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	if not require(data.get("adoption_gate_accepted",false), "Draft acceptance flag still false; integration must be reviewed first"): return
	if not check_pins(): return
	main = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	if not await advance(90): return
	ship = main.get_node("World360/Astraea")
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	bank = ship.find_child("EngineeringCalibrationBank",true,false) as Node3D
	gate = ship.find_child("EngineeringCellGate",true,false) as Node3D
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	if not require(bank != null and gate != null and floors != null, "Reviewed integrated real nodes missing"): return
	if not require(bank.controls_by_id.size() == 120 and bank.find_children("SourceCalibrationTarget","Area3D",true,false).size() == 120, "120 distinct source targets required"): return
	if not require(bank.find_children("*","Light3D",true,false).is_empty() and bank.find_children("*","AudioStreamPlayer3D",true,false).size() == 4, "Calibration light/audio budget exceeded"): return
	_gate_state = [gate.desired_open,gate.open_fraction]
	var panels: Dictionary = {}
	for record in data.controls:
		var panel := str(record.bay)+"/"+str(record.panel)
		if not panels.has(panel):
			release_inputs()
			if not require(actor.held_interaction == null, "Arrival cannot transport held object"): return
			if not require(ship.arrive_at(xyz(record.proposed_approach_xyz)+Vector3.UP*.10,0), "Supported panel arrival refused"): return
			arrivals += 1
			panels[panel] = true
			if not await advance(30): return
		var control: Node3D = bank.controls_by_id[str(record.id)]
		if not await exercise_control(control,record): return
	# One representative exact first-hit occlusion test at the last real pose.
	var last: Dictionary = data.controls.back()
	if not await occlusion_negative(bank.controls_by_id[str(last.id)],last): return
	if not require(arrivals == 10 and records.size() == 120 and bank.active_controls.is_empty(), "Incomplete panel/control coverage"): return
	if not check_pins(): return
	release_inputs()
	_checkpoint = "complete focused original-player checks"
	write_receipt("PASS")
	main.queue_free()
	await process_frame
	quit(0)
