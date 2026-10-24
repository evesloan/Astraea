extends SceneTree
func _initialize() -> void: call_deferred("run")
func fail(reason: String) -> void:
	push_error(reason)
	quit(1)
func run() -> void:
	var started := Time.get_ticks_usec()
	var main: String = str(ProjectSettings.get_setting("application/run/main_scene"))
	if main != "res://scenes/bootstrap_tidal_d14_landing_20261023.tscn":
		fail("Wrong selected source main"); return
	var bootstrap: Node = load(main).instantiate()
	root.add_child(bootstrap)
	await process_frame
	var launcher: Node = bootstrap.get_child(0)
	var launch: Button = launcher.get("launch_button")
	if launch == null or launch.disabled:
		fail("Main menu did not expose Enter the ship"); return
	launcher.call("_setting", "volume", 0.65)
	launcher.call("_setting", "resolution", 2)
	launcher.call("_setting", "effects", false)
	var prefs = load("res://scripts/delivery_shell_20261022/settings.gd").new()
	if prefs.read_preferences() != OK or absf(float(prefs.values.volume) - 0.65) > 0.0001:
		fail("Isolated settings did not persist"); return
	launch.pressed.emit()
	while not bool(launcher.get("ready_seen")):
		await create_timer(0.5, true).timeout
		if Time.get_ticks_usec() - started > 240000000:
			fail("Selected main did not reach actual readiness within bounded run"); return
	var presentation: Node = launcher.get("presentation")
	var world: Node = presentation.get("world_view")
	var ship: Node = world.get_node("Astraea")
	if not bool(ship.get_meta("runtime_ready", false)):
		fail("Launcher readiness lacks actual ship readiness"); return
	var addition: Node = ship.get_node_or_null("ShipSpace/Districts/TidalGardenReceivingCandidate/TidalD14Landing_r001")
	if addition == null:
		fail("Selected integrated Tidal successor absent after readiness"); return
	if not paused:
		fail("Ready menu did not retain pause until Resume"); return
	var resume: Button = launcher.get("resume_button")
	resume.pressed.emit()
	await process_frame
	if paused:
		fail("Resume did not release tree pause"); return
	var player: Node3D = ship.get_node("ShipSpace/PersistentActors/Player")
	var before_move := player.global_position
	var key := InputEventKey.new()
	key.keycode = KEY_W; key.physical_keycode = KEY_W; key.pressed = true
	Input.parse_input_event(key)
	await create_timer(2.0, true).timeout
	key = InputEventKey.new()
	key.keycode = KEY_W; key.physical_keycode = KEY_W; key.pressed = false
	Input.parse_input_event(key)
	await create_timer(1.0, true).timeout
	var after_move := player.global_position
	await RenderingServer.frame_post_draw
	var picture: Image = presentation.get("world_view").get_texture().get_image()
	if picture == null or picture.is_empty():
		fail("Rendered source viewport is empty"); return
	var capture_result := picture.save_png("/tmp/astraea-graphical-1091d34e/ACTUAL_SOURCE_VIEW.png")
	if capture_result != OK:
		fail("Cannot retain actual rendered view"); return
	launcher.call("_pause")
	if not paused:
		fail("Pause menu did not restore pause"); return
	var result := {"status":"GRAPHICAL_SOURCE_READY","source_commit":"1091d34e914ad9c36f7ff487ed72e4d959a96886","main_scene":main,"seconds_to_readiness":float(Time.get_ticks_usec()-started)/1000000.0,"actual_runtime_ready":true,"tidal_addition_installed":true,"menu_settings_resume_pause":true,"nodes":int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT)),"resources":int(Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT)),"headless_linux_editor":false,"renderer_adapter":RenderingServer.get_video_adapter_name(),"before_movement":var_to_str(before_move),"after_movement":var_to_str(after_move),"movement_distance":before_move.distance_to(after_move),"capture_size":var_to_str(picture.get_size()),"internal_resolution":"1920x1080","effects":false,"windows_release_tested":false,"walking_tested":"2second input smoke only; not repeated-route stability","rendered_visuals_tested":"capture produced; pixel review pending","performance_accepted":false}
	var f := FileAccess.open("/tmp/astraea-graphical-1091d34e/GRAPHICAL_SOURCE_READY.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(result,"  ")+"\n"); f.close()
	print("GRAPHICAL_SOURCE_READY ", JSON.stringify(result))
	quit(0)
