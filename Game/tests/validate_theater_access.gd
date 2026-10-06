extends SceneTree
# One supported initial arrival, then ordinary physical W movement throughout.
# No assignment to the player transform/velocity or repeated arrivals in travel.
const MAX_FRAMES := 10000
var probe = preload("res://tests/theater_stage_probe.gd").new()
var frames := 0
var support_samples := 0
var peak_speed := 0.0
var walked_metres := 0.0
var started := 0
var last_position := Vector3.ZERO
func _initialize() -> void:
	started = Time.get_ticks_msec()
	call_deferred("run")
func _process(_delta: float) -> bool:
	if Time.get_ticks_msec()-started > 240000:
		key(false)
		push_error("Theater access 240-second watchdog")
		quit(1)
	return false
func key(pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = KEY_W
	event.physical_keycode = KEY_W
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()
func inspect() -> void:
	frames += 1
	assert(frames < MAX_FRAMES)
	var actor: CharacterBody3D = probe.actor
	assert(actor.global_position.is_finite() and absf(actor.global_position.y-69.5) < .14)
	var travelled := Vector2(actor.global_position.x-last_position.x,actor.global_position.z-last_position.z).length()
	assert(travelled < .08, "Discontinuous actor position is not walking")
	walked_metres += travelled
	last_position = actor.global_position
	peak_speed = maxf(peak_speed,Vector2(actor.velocity.x,actor.velocity.z).length())
	probe.floor_at(actor.global_position)
	support_samples += 1
	for identity in probe.held_poses:
		var node: Node3D = probe.motion.find_child(str(probe.data.motion_node_names[identity]),true,false)
		probe.assert_transform(node.global_transform,probe.held_poses[identity],"Moving locked mechanism")
func walk_to(target: Vector3) -> void:
	var actor: CharacterBody3D = probe.actor
	var initial := Vector2(target.x-actor.global_position.x,target.z-actor.global_position.z).length()
	var frame_budget := ceili(initial/3.1*60)+360
	var reached := false
	for frame in range(frame_budget):
		var delta := Vector3(target.x-actor.global_position.x,0,target.z-actor.global_position.z)
		var speed := Vector2(actor.velocity.x,actor.velocity.z).length()
		if delta.length() < .075 and speed < .08:
			reached = true
			break
		actor.rotation.y = atan2(-delta.x,-delta.z)
		# Brake using the unchanged normal player's 16m/s² acceleration. This
		# changes only keyboard intent, never its movement speed or tolerances.
		key(delta.length() > .06 + speed*speed/32.0)
		await physics_frame
		inspect()
	key(false)
	assert(reached,"Ordinary W walking stalled at %s toward %s" % [actor.global_position,target])
	probe.check_lights("walk waypoint " + str(target))
func run() -> void:
	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150): await physics_frame
	probe.configure(main.get_node("World360/Astraea"))
	probe.check_motion_poses_and_barriers()
	var actor: CharacterBody3D = probe.actor
	assert(probe.ship.arrive_at(Vector3(-2,69.6,-126),PI/2),"Supported fore-spine starting point required")
	actor.set_controls_enabled(true)
	for frame in range(30): await physics_frame
	last_position = actor.global_position
	probe.floor_at(actor.global_position,"D11_fore_route")
	probe.check_lights("D11 fore spine")
	var points: Array = probe.fixture.walking_waypoints_xz
	for index in range(1,points.size()):
		var p: Array = points[index]
		await walk_to(Vector3(p[0],69.5,p[1]))
	for index in range(points.size()-2,-1,-1):
		var p: Array = points[index]
		await walk_to(Vector3(p[0],69.5,p[1]))
	assert(peak_speed > 3.05 and peak_speed <= 3.101,"Exercise unchanged ordinary 3.1m/s walking")
	assert(walked_metres > 225 and support_samples > 4000)
	assert(Vector2(actor.global_position.x+2,actor.global_position.z+126).length() < .075)
	probe.check_motion_poses_and_barriers()
	probe.check_lights("returned D11 spine")
	print("THEATER ACCESS PASS: one initial arrival, continuous ordinary 3.1m/s fore-spine/30m-bridge/D11-held-open-door/south-bypass/foyer round trip; ",walked_metres,"m, ",frames," movement frames, ",support_samples," exact owner supports; actual selected lights <=8 with unchanged MAX_VISIBILITY_CANDIDATES=32. No operational-door/lift, underside-census, visual or full-suite acceptance claimed.")
	main.queue_free()
	await process_frame
	quit(0)
