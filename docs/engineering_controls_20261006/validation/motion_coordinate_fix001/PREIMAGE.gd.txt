extends SceneTree
# RUNTIME V3 SCRATCH DRAFT, UNRUN. One supported diagnostic start only.
# All ten panels and all 120 controls are reached with the original physical
# player and ordinary W input in the real main-scene World360. No fly camera.
const CONTRACT := "res://data/architecture/ENGINEERING_CALIBRATION_DRAFT.json"
const ROUTE := "res://data/architecture/ENGINEERING_CONTROLS_WALK_ROUTE_V3.json"
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
var route: Dictionary
var route_records: Array = []
var motion_samples: Dictionary = {}
var system_states: Array = []
var audio_evidence: Dictionary = {}
var negative_cases: Array = []
var motion_sample_count := 0
var source_materials: Dictionary = {}
var first_hit_evidence: Dictionary = {}
var observed_audio_starts: Array = []
var observed_audio_count := 0

func _initialize() -> void:
	_started = Time.get_ticks_msec()
	call_deferred("run")

func _process(_delta: float) -> bool:
	if not failed and Time.get_ticks_msec() - _started > 1200000: require(false, "1200-second test watchdog")
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
		"diagnostic_arrivals":arrivals,"ordinary_walk_frames":walked_frames,"records":records,
		"contract_sha256":FileAccess.get_sha256(CONTRACT),"route_sha256":FileAccess.get_sha256(ROUTE),
		"connected_route":route_records,"motion_samples":motion_samples,"negative_cases":negative_cases,"audio_scheduling":audio_evidence,"observed_audio_starts":observed_audio_starts,
		"scope":"Focused full-main-scene 120-control first-hit/capsule/reach, connected walking, bounded local feedback/rest, listener topology/scheduling and real door/transport preservation. Human listening, rendered visual acceptance and aggregate checks remain separate.",
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
		if not require(frames <= 40000, "Derived 40000-frame test allowance exceeded"): return false
		if is_instance_valid(bank):
			if not active_motion_proof() or not collect_audio_start_evidence(): return false
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
		if delta.length() < .06 and speed < .06:
			key(KEY_W,false)
			route_records.append({"target_xyz":as_array(point),"actual_xyz":as_array(actor.global_position),"frames":walked_frames})
			return support_and_capsule(owner)
		if delta.length() > .045: actor.rotation.y = atan2(-delta.x,-delta.y)
		key(KEY_W,delta.length() > speed*speed/32.0+.012)
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
	if not require(not hit.is_empty() and hit.collider == control.target_area, "First collider must be this precise Area, never an ancestor proxy"): return false
	var distance: float = start.distance_to(hit.position)
	if not require(distance <= 2.5001, "Original first hit exceeded 2.5 m"): return false
	first_hit_evidence[str(record.id)] = {"collider_path":str(hit.collider.get_path()),"distance_m":distance,"eye_xyz":as_array(start),"position_xyz":as_array(hit.position)}
	return true

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
	if not protected_systems_unchanged(): return false
	# A second complete original-input cycle tests repeatability, including every
	# physical toggle, without changing the source's momentary-return semantics.
	if not await original_first_hit(control,record): return false
	if not await tap_e(): return false
	if not require(control.activation_count == before+2, "Second independent cycle failed"): return false
	if not await advance(65): return false
	if not require(control.actuator.transform == home and not control.busy, "Second cycle drifted from exact rest"): return false
	for surface in range(control.actuator.mesh.get_surface_count()):
		if not require(control.actuator.get_surface_override_material(surface) == null, "Second cycle failed to restore NULL override"): return false
	if not protected_systems_unchanged(): return false
	if not await seam_negative_cases(record): return false
	records.append({"id":record.id,"source_marker":record.source_marker,"actual_feet_xyz":as_array(actor.global_position),
		"actual_eye_xyz":as_array(actor.camera.global_position),"first_hit":"SourceCalibrationTarget","activations":control.activation_count-before,
		"rest_exact":true,"first_hit_record":first_hit_evidence[str(record.id)],"audio_start_requested_and_accepted":control.last_audio_started})
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
	ship.add_child(blocker)
	if not require(blocker.get_world_3d() == actor.get_world_3d() and blocker.get_viewport() == actor.get_viewport(), "Occluder fixture is in the wrong world"): return false
	blocker.global_position = actor.camera.global_position.lerp(xyz(record.target_center_xyz),.5)
	if not await advance(3): return false
	var before: int = control.activation_count
	if not require(actor.target_from_view() == null, "Opaque foreground fixture did not block target"): return false
	if not await tap_e(): return false
	if not require(control.activation_count == before, "E interacted through opaque blocker"): return false
	negative_cases.append({"case":"opaque_same_world_blocker","id":record.id,"activated":false})
	blocker.queue_free()
	return await advance(3)

func check_pins() -> bool:
	for path in ["scripts/player.gd","scripts/fixture_switch.gd","scripts/physics_tether.gd","scripts/service_door.gd","scripts/engineering_cell_gate.gd","scripts/engineering_cell_gate_target.gd","scripts/lighting_budget.gd"]:
		if not require(FileAccess.get_sha256("res://"+path) == str(data.retained_runtime_pins[path]), "Protected controller changed: "+path): return false
	return true

func run() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	route = JSON.parse_string(FileAccess.get_file_as_string(ROUTE))
	if not require(data.get("adoption_gate_accepted",false), "Draft acceptance flag still false; integration must be reviewed first"): return
	if not check_pins() or not contract_negative_cases(): return
	main = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	if not await advance(180): return
	ship = main.get_node("World360/Astraea")
	actor = ship.get_node("ShipSpace/PersistentActors/Player")
	bank = ship.find_child("EngineeringCalibrationBank",true,false) as Node3D
	gate = ship.find_child("EngineeringCellGate",true,false) as Node3D
	floors = ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false) as Node3D
	if not require(bank != null and gate != null and floors != null, "Reviewed integrated real nodes missing"): return
	if not identity_and_listener_census(): return
	_gate_state = [gate.desired_open,gate.open_fraction]
	cache_real_system_states()
	if not await audio_and_slot_bounds(): return
	release_inputs()
	if not require(actor.held_interaction == null and arrivals == 0, "Only one empty-hand diagnostic arrival permitted"): return
	if not require(ship.arrive_at(xyz(route.initial_supported_arrival_xyz)+Vector3.UP*.10,0), "Supported staff starting arrival refused"): return
	arrivals += 1
	if not await advance(30): return
	for segment in route.segments:
		_checkpoint = "connected walk to " + str(segment.panel)
		for waypoint in segment.waypoints_xyz:
			if not await walk_to(xyz(waypoint),str(route.floor_owner)): return
		for record in data.controls:
			if str(record.panel) != str(segment.panel): continue
			var control: Node3D = bank.controls_by_id[str(record.id)]
			if not await exercise_control(control,record): return
			if str(record.id) == "ENG2_CONTROL_C1L_01":
				if not await range_negative(control,record): return
				if not await original_input_four_control_cap(): return
	# Scope is last in the connected walk, independent of source array ordering.
	var last: Dictionary = {}
	for row in data.controls:
		if str(row.id) == "ENG2_WORKBAY_SCOPE_12": last = row
	if not require(not last.is_empty(), "Final connected-route target missing"): return
	if not await occlusion_negative(bank.controls_by_id[str(last.id)],last): return
	if not await interrupted_pulse_restore(): return
	if not require(arrivals == 1 and records.size() == 120 and bank.active_controls.is_empty(), "Incomplete connected coverage or extra arrival"): return
	if not require(motion_samples.size() == 120 and negative_cases.size() >= 20, "Incomplete motion/negative evidence"): return
	if not protected_systems_unchanged() or not check_pins(): return
	release_inputs()
	_checkpoint = "complete focused connected main-world checks"
	write_receipt("PASS")
	print("PASS: engineering_controls; all120 original-input connected-route checks completed. Native listening remains separate.")
	main.queue_free()
	await process_frame
	quit(0)

func transform_from_rows(rows: Array) -> Transform3D:
	return Transform3D(Basis(
		Vector3(float(rows[0][0]),float(rows[1][0]),float(rows[2][0])),
		Vector3(float(rows[0][1]),float(rows[1][1]),float(rows[2][1])),
		Vector3(float(rows[0][2]),float(rows[1][2]),float(rows[2][2]))),
		Vector3(float(rows[0][3]),float(rows[1][3]),float(rows[2][3])))

func identity_and_listener_census() -> bool:
	if not require(Engine.physics_ticks_per_second == 60, "Run using existing 60 Hz physics setting; do not change player or physics rate"): return false
	if not require(bank.controls_by_id.size() == 120 and bank.find_children("SourceCalibrationTarget","Area3D",true,false).size() == 120, "120 distinct Areas required"): return false
	if not require(bank.find_children("*","Light3D",true,false).is_empty(), "Calibration added a dynamic light"): return false
	if not require(bank.original_actor == actor and bank.listener_ready and bank.listener_bind_attempts == 1, "Original player was not bound exactly once after construction"): return false
	var audio: Node3D = bank.audio_owner
	if not require(audio.available and audio.listener_ready and audio.listener_contract_holds(), "Listener topology or imported source audio unavailable"): return false
	if not require(main.world_view == actor.camera.get_viewport() and main.world_view.audio_listener_enable_3d, "Original camera is outside listener-enabled World360"): return false
	if not require(not main.post_view.audio_listener_enable_3d and main.world_view.get_camera_3d() == actor.camera, "Wrong post viewport/camera owns listening"): return false
	if not require(audio.listener_camera == actor.camera and audio._voices.size() == 4, "Four cached voices and original listener required"): return false
	for voice in audio._voices:
		if not require(voice.get_viewport() == actor.camera.get_viewport() and voice.get_world_3d() == actor.camera.get_world_3d(), "Voice/camera worlds differ"): return false
		if not require(voice.max_polyphony == 1 and not voice.autoplay and voice.volume_db <= -12.0 and voice.max_distance <= 6.0, "Spatial voice bounds changed"): return false
	var counts := {"CONTROL":0,"WORKBAY":0}
	var space := actor.get_world_3d().direct_space_state
	for record in data.controls:
		var control: Node3D = bank.controls_by_id[str(record.id)]
		if not require(str(control.persistent_id) == str(record.id) and str(control.source_marker) == str(record.source_marker), "Stable source identity changed"): return false
		if not require(str(control.actuator.name) == str(record.actuator_mesh_name), "Wrong ACT mesh bound"): return false
		if not require(control.actuator.get_node_or_null("StaticContact") == null, "Actuator body contact was added"): return false
		if not require(control._home_source.is_equal_approx(transform_from_rows(record.runtime_mesh_original_transform_rows)), "Imported original ACT transform differs"): return false
		if not require(control.global_position.distance_to(control.visual.to_global(xyz(record.target_center_xyz))) < .001, "Source target moved"): return false
		var area: Area3D = control.target_area
		if not require(area.collision_layer == 2 and area.collision_mask == 0 and not area.monitoring and not area.monitorable, "Target collision contract changed"): return false
		var shape: CollisionShape3D = area.get_node("PreciseSourceTarget")
		if not require(shape.shape is SphereShape3D and is_equal_approx(shape.shape.radius,.018), "Target precision widened"): return false
		var query := PhysicsShapeQueryParameters3D.new()
		query.shape = shape.shape
		query.transform = shape.global_transform
		query.collision_mask = 2
		query.collide_with_areas = true
		query.collide_with_bodies = false
		query.exclude = [area.get_rid()]
		if not require(space.intersect_shape(query,128).is_empty(), "Actual source target overlaps another interaction Area"): return false
		var originals: Array = []
		for surface in range(control.actuator.mesh.get_surface_count()):
			if not require(control.actuator.get_surface_override_material(surface) == null, "Initial ACT override must be NULL"): return false
			var material := control.actuator.get_active_material(surface) as StandardMaterial3D
			if not require(material != null, "Expected source StandardMaterial3D missing"): return false
			originals.append({"material":material,"emission_enabled":material.emission_enabled,"emission":material.emission,"energy":material.emission_energy_multiplier})
		source_materials[str(record.id)] = originals
		counts[str(record.bay)] += 1
	return require(counts == {"CONTROL":72,"WORKBAY":48}, "Wrong source bay counts")

func active_motion_proof() -> bool:
	if not require(bank.active_controls.size() <= 4, "More than four local effects active"): return false
	for reference in bank.active_controls.values():
		var control: Node3D = reference.get_ref()
		if not require(is_instance_valid(control) and control.busy, "Active slot has no running source control"): return false
		var record: Dictionary = control.record
		var value: float = control.last_motion_displacement
		if not require(value >= float(record.travel_limits[0])-.000001 and value <= float(record.travel_limits[1])+.000001, "Actuator exceeded authored travel"): return false
		var delta := Transform3D.IDENTITY
		var axis := xyz(record.travel_axis_xyz)
		if str(record.travel_type) == "rotation":
			var rotation := Basis(axis,deg_to_rad(value))
			var pivot := xyz(record.pivot_xyz)
			delta = Transform3D(rotation,pivot-rotation*pivot)
		else: delta.origin = axis*value
		var expected: Transform3D = control.visual.global_transform*delta*transform_from_rows(record.runtime_mesh_original_transform_rows)
		var actual: Transform3D = control.actuator.global_transform
		if not require(actual.origin.distance_to(expected.origin) < .0002 and actual.basis.is_equal_approx(expected.basis), "Complete ACT pose differs from source-pivot formula"): return false
		var identity := str(record.id)
		if not motion_samples.has(identity): motion_samples[identity] = {"count":0,"minimum":value,"maximum":value}
		motion_samples[identity].count += 1
		motion_samples[identity].minimum = minf(float(motion_samples[identity].minimum),value)
		motion_samples[identity].maximum = maxf(float(motion_samples[identity].maximum),value)
		motion_sample_count += 1
		for surface in range(control.actuator.mesh.get_surface_count()):
			var original: Dictionary = source_materials[identity][surface]
			var material: StandardMaterial3D = original.material
			if not require(material.emission_enabled == original.emission_enabled and material.emission == original.emission and is_equal_approx(material.emission_energy_multiplier,float(original.energy)), "Shared source material changed"): return false
			var override: Material = control.actuator.get_surface_override_material(surface)
			if surface == control._pulse_surface:
				if not require(override is StandardMaterial3D and override != material and override.resource_local_to_scene and override.emission_energy_multiplier <= .220001, "Pulse material is shared or unbounded"): return false
			elif not require(override == null, "Unexpected actuator surface override"): return false
	return true

func inherits_script(node: Node, wanted: String) -> bool:
	var script: Script = node.get_script()
	while script != null:
		if script.resource_path == wanted: return true
		script = script.get_base_script()
	return false

func cache_real_system_states() -> void:
	# One test-only startup census; subsequent checks use this cached roster.
	for node in ship.find_children("*","Node",true,false):
		var fields: Array[String] = []
		if inherits_script(node,"res://scripts/service_door.gd"):
			fields = ["desired_open","open_fraction"]
		elif inherits_script(node,"res://scripts/commons_lift.gd"):
			fields = ["current_floor","destination_floor","queued_floor","phase","travel_velocity"]
		elif inherits_script(node,"res://scripts/lift_gate.gd"):
			fields = ["requested_open","open_fraction","cabin_present_and_stopped"]
		if fields.is_empty(): continue
		var values: Dictionary = {}
		for field in fields: values[field] = node.get(field)
		if fields.has("current_floor"):
			var cabin := node.get("cabin") as Node3D
			values["__cabin_pose"] = cabin.global_transform
		system_states.append({"node":node,"path":str(node.get_path()),"values":values})

func protected_systems_unchanged() -> bool:
	if not require(not system_states.is_empty(), "No real door/transport state was captured"): return false
	for row in system_states:
		var node: Node = row.node
		if not require(is_instance_valid(node), "Real door/transport node disappeared"): return false
		for field in row.values:
			var actual: Variant = node.get("cabin").global_transform if field == "__cabin_pose" else node.get(field)
			if not require(actual == row.values[field], "Unrelated real door/transport state changed: " + str(row.path) + "/" + field): return false
	return true

func contract_negative_cases() -> bool:
	var builder := load("res://scripts/engineering_calibration_builder.gd")
	if not require(builder.validate_precise_target_data(data).is_empty(), "Final source data preflight rejected"): return false
	for name in ["overlap","wide_target","live_effect","cake"]:
		var altered: Dictionary = data.duplicate(true)
		match name:
			"overlap": altered.controls[1].target_center_xyz = altered.controls[0].target_center_xyz.duplicate()
			"wide_target": altered.controls[0].target_radius_m = .045
			"live_effect": altered.controls[0].runtime_profile = "open_airlock"
			"cake": altered.cake.enabled = true
		if not require(not builder.validate_precise_target_data(altered).is_empty(), "Unsafe/ambiguous mutation was accepted: " + name): return false
		negative_cases.append({"case":"data_reject_"+name,"rejected_before_instantiation":true})
	return true

func seam_negative_cases(record: Dictionary) -> bool:
	for pair in data.source_target_box_overlap_pairs:
		if str(pair[0]) != str(record.id): continue
		var a: Node3D = bank.controls_by_id[str(pair[0])]
		var b: Node3D = bank.controls_by_id[str(pair[1])]
		if not aim(a.global_position.lerp(b.global_position,.5)): return false
		focus(true)
		if not await advance(3): return false
		if not require(actor.target_from_view() == null, "Old overlapping-box seam still selects a neighbor"): return false
		var before_a: int = a.activation_count
		var before_b: int = b.activation_count
		if not await tap_e(): return false
		if not require(a.activation_count == before_a and b.activation_count == before_b, "Neighbor seam activated a control"): return false
		negative_cases.append({"case":"neighbor_seam","a":pair[0],"b":pair[1],"activated":false})
	return true

func range_negative(control: Node3D, record: Dictionary) -> bool:
	var away := xyz(record.proposed_approach_xyz)+xyz(record.target_normal_xyz)*1.8
	if not await walk_to(away,str(record.floor_owner)): return false
	if not aim(xyz(record.target_center_xyz)): return false
	focus(true)
	if not await advance(3): return false
	if not require(actor.camera.global_position.distance_to(control.global_position) > 2.5+.018 and actor.target_from_view() == null, "Beyond-reach target was selected"): return false
	var before: int = control.activation_count
	if not await tap_e(): return false
	if not require(control.activation_count == before, "Beyond-reach E activated control"): return false
	negative_cases.append({"case":"original_2_5m_range","id":record.id,"activated":false})
	return await walk_to(xyz(record.proposed_approach_xyz),str(record.floor_owner))

func audio_and_slot_bounds() -> bool:
	var audio: Node3D = bank.audio_owner
	var candidates: Array = bank.controls_by_id.values()
	for index in range(4):
		if not require(bank.try_begin_control(candidates[index]), "Four control slots not available"): return false
	if not require(not bank.try_begin_control(candidates[4]) and not bank.try_begin_control(candidates[0]), "Fifth/duplicate control slot accepted"): return false
	for index in range(4): bank.end_control(candidates[index])
	negative_cases.append({"case":"four_control_slot_cap","fifth_rejected":true})
	audio.stop_all()
	var spacing := ceili(.08*float(Engine.physics_ticks_per_second))
	if not await advance(spacing+2): return false
	var first_record: int = audio.start_history.size()
	var point: Vector3 = candidates[0].global_position
	for index in range(4):
		if index > 0:
			if not await advance(spacing): return false
		if not require(audio.play_cue("soft_hum",point), "Four finite audio leases could not be started"): return false
		if not require(not audio.play_cue("mechanical_click",point), "Same-frame audio start bypassed 80 ms spacing"): return false
	if not await advance(spacing): return false
	if not require(audio.active_lease_count() == 4 and not audio.play_cue("soft_hum",point), "Fifth finite voice was not rejected"): return false
	var starts: Array = audio.start_history.slice(first_record)
	if not require(starts.size() == 4, "Incorrect scheduling start count"): return false
	var voice_ids: Dictionary = {}
	var start_frames: Array = []
	var measured_intervals: Array = []
	for index in range(starts.size()):
		start_frames.append(int(starts[index].frame))
		voice_ids[int(starts[index].voice)] = true
		if index > 0:
			var interval := float(starts[index].frame-starts[index-1].frame)/float(starts[index].physics_hz)
			measured_intervals.append(interval)
			if not require(interval >= .08, "Global audio starts were closer than 80 ms"): return false
	if not require(voice_ids.size() == 4 and audio._voices.size() == 4, "Audio reused an occupied voice or expanded pool"): return false
	audio_evidence = {"four_distinct_slots":true,"fifth_rejected":true,"required_start_spacing_s":.08,"observed_start_frames":start_frames,"measured_intervals_s":measured_intervals,"physics_hz":Engine.physics_ticks_per_second,
		"listener_viewport":str(actor.camera.get_viewport().get_path()),"same_world_verified":true,"human_listening_accepted":false,
		"mode_note":"Finite leases and starts verified; headless scheduler evidence is not proof of audibility."}
	negative_cases.append({"case":"four_audio_voice_cap_and_80ms","rejected":true})
	audio.stop_all()
	if not require(audio.active_lease_count() == 0, "Audio stop leaked a finite lease"): return false
	return true

func interrupted_pulse_restore() -> bool:
	# Stay in the connected SCOPE service strip; walk to a real pulse control.
	var record: Dictionary = {}
	for row in data.controls:
		if str(row.id) == "ENG2_WORKBAY_SCOPE_03": record = row
	var control: Node3D = bank.controls_by_id[str(record.id)]
	if not await walk_to(xyz(record.proposed_approach_xyz),str(record.floor_owner)): return false
	if not await original_first_hit(control,record): return false
	var home: Transform3D = control.actuator.transform
	if not await tap_e(): return false
	if not require(control.busy and control.actuator.get_surface_override_material(control._pulse_surface) != null, "Pulse did not create its private temporary override"): return false
	key(KEY_ESCAPE,true)
	if not await advance(2): return false
	key(KEY_ESCAPE,false)
	if not require(not actor.gameplay_input_enabled, "Original Escape path did not disable controls"): return false
	bank.cancel_all()
	if not await advance(2): return false
	if not require(control.actuator.transform == home and control.actuator.get_surface_override_material(control._pulse_surface) == null and not control.busy, "Cancellation failed exact pose/NULL override restoration"): return false
	if not require(bank.active_controls.is_empty() and bank.audio_owner.active_lease_count() == 0, "Cancellation leaked active slots/voices"): return false
	negative_cases.append({"case":"escape_cancel_null_material_restore","restored":true})
	focus(false)
	focus(true)
	if not await advance(2): return false
	return require(actor.gameplay_input_enabled and bank.audio_owner.listener_contract_holds(), "Original input/listener did not recover")

func collect_audio_start_evidence() -> bool:
	var audio: Node3D = bank.audio_owner
	var new_count: int = audio.started_count - observed_audio_count
	if new_count <= 0: return true
	var history: Array = audio.start_history
	if not require(new_count <= history.size(), "Bounded audio history lost unobserved starts"): return false
	for index in range(history.size()-new_count,history.size()):
		var item: Dictionary = history[index]
		if not observed_audio_starts.is_empty():
			var previous: Dictionary = observed_audio_starts.back()
			var interval := float(int(item.frame)-int(previous.frame))/float(item.physics_hz)
			if not require(interval >= .08, "Actual emitted start spacing violated 80 ms"): return false
		observed_audio_starts.append({"frame":item.frame,"voice":item.voice,"cue":item.cue,"physics_hz":item.physics_hz,"lease_end_frame":item.lease_end_frame})
	observed_audio_count = audio.started_count
	return require(audio.active_lease_count() <= 4, "Actual audio voice/lease cap exceeded")

func original_input_four_control_cap() -> bool:
	var rows: Array = []
	for item in data.controls:
		if str(item.panel) == "C1L" and int(str(item.id).get_slice("_",3)) <= 5: rows.append(item)
	# IDs have four underscore-separated components: ENG2, CONTROL, C1L, NN.
	if not require(rows.size() == 5, "Five source controls missing for actual-input cap test"): return false
	for index in range(rows.size()):
		var row: Dictionary = rows[index]
		var control: Node3D = bank.controls_by_id[str(row.id)]
		if not await original_first_hit(control,row): return false
		var before: int = control.activation_count
		if not await tap_e(): return false
		if index < 4:
			if not require(control.activation_count == before+1 and control.busy, "Original RMB/E did not occupy one of four slots"): return false
		else:
			if not require(control.activation_count == before and not control.busy, "Fifth original-input effect bypassed four-control cap"): return false
	if not require(bank.active_controls.size() <= 4, "Actual-input burst exceeded cap"): return false
	if not await advance(65): return false
	for row in rows:
		var control: Node3D = bank.controls_by_id[str(row.id)]
		if not require(not control.busy and control.actuator.transform == control._home_local, "Burst failed exact source rest restoration"): return false
		for surface in range(control.actuator.mesh.get_surface_count()):
			if not require(control.actuator.get_surface_override_material(surface) == null, "Burst leaked NULL material override"): return false
	negative_cases.append({"case":"original_RMB_E_four_control_cap","fifth_rejected":true,"all_restored":true})
	return protected_systems_unchanged()
