extends SceneTree
# Bounded actual-main-scene receiving target candidate. Not an ordinary-arrival tour.
# Two explicit production arrival calls establish the independently source-checked stances.
var main: Node
var ship: Node3D
var actor: CharacterBody3D
var failed := false
func _initialize() -> void: call_deferred("run")
func require(ok: bool, message: String) -> bool:
	if ok: return true
	failed = true
	push_error("SPORTS CARE INFORMATION: " + message)
	quit(1)
	return false
func xyz(a: Array) -> Vector3: return Vector3(float(a[0]), float(a[1]), float(a[2]))
func key(pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = KEY_E
	event.physical_keycode = KEY_E
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()
func focus(pressed: bool) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_RIGHT
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()
func tick(count: int) -> void:
	for i in range(count): await physics_frame
func run() -> void:
	main = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	await tick(120)
	ship = main.get_node("World360/Astraea") as Node3D
	actor = ship.get_node("ShipSpace/PersistentActors/Player") as CharacterBody3D
	if not require(actor.get_script() == load("res://scripts/player.gd"), "Original controller required"): return
	var room := ship.find_child("WholeRetainedSportsCare", true, false)
	if not require(room != null, "Whole receiving section required"): return
	var info: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/packages/sports_care/INFORMATION_TARGETS.json"))
	for spec in info.candidates:
		focus(false)
		key(false)
		var feet := xyz(spec.approach_feet_world_m)
		if not require(ship.arrive_at(feet + Vector3.UP * .1, 0), "Verified target approach refused"): return
		await tick(30)
		if not require(actor.global_position.distance_to(feet) < .15, "Target stance did not settle"): return
		var target := room.get_node(str(spec.id))
		var delta := xyz(spec.focus_world_m) - actor.camera.global_position
		actor.rotation.y = atan2(-delta.x, -delta.z)
		actor.pitch = atan2(delta.y, Vector2(delta.x, delta.z).length())
		actor.camera.rotation.x = actor.pitch
		await tick(2)
		if not require(actor.target_from_view() == target, "Original player ray did not select authored plaque"): return
		key(true)
		await tick(2)
		key(false)
		if not require(not target.expanded, "E without RMB must not open information"): return
		focus(true)
		await tick(18)
		if not require(actor.interaction_target == target and actor.camera.fov < 65.0, "Original RMB focus failed"): return
		for cycle in range(2):
			key(true)
			await tick(2)
			key(false)
			await tick(2)
			if not require(target.expanded and "Close" in target.get_interaction_label(), "Information did not open"): return
			key(true)
			await tick(2)
			key(false)
			await tick(2)
			if not require(not target.expanded, "Information did not close"): return
		focus(false)
		await tick(18)
		if not require(actor.interaction_target == null and actor.camera.fov > 69.0, "RMB release did not clear focus"): return
	print("SPORTS CARE INFORMATION PASS: two fitted targets, original RMB/E, two read-close cycles; staff authority and gameplay remain unimplemented")
	main.queue_free()
	await process_frame
	quit(0)
