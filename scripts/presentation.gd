extends Node
var world_view: SubViewport
var display: TextureRect
var post_view: SubViewport
var post_pass: TextureRect
var effects := true
var directory: PanelContainer
var directory_open := false

func _ready() -> void:
	Engine.max_fps = 60
	process_mode = Node.PROCESS_MODE_ALWAYS
	world_view = SubViewport.new()
	world_view.name = "World360"
	world_view.process_mode = Node.PROCESS_MODE_PAUSABLE
	world_view.size = Vector2i(640, 360)
	world_view.own_world_3d = true
	world_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(world_view)
	world_view.add_child(load("res://scenes/ship.tscn").instantiate())
	post_view = SubViewport.new()
	post_view.name = "WorldDisplayEffects360"
	post_view.size = world_view.size
	post_view.disable_3d = true
	post_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(post_view)
	post_pass = TextureRect.new()
	post_pass.name = "SingleRetroPass"
	post_pass.size = Vector2(world_view.size)
	post_pass.texture = world_view.get_texture()
	post_pass.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	post_pass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	post_view.add_child(post_pass)
	display = TextureRect.new()
	display.name = "NearestWorldPresentation"
	display.texture = post_view.get_texture()
	display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	display.stretch_mode = TextureRect.STRETCH_SCALE
	display.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load("res://shaders/retro.gdshader")
	post_pass.material = mat
	add_child(display)
	get_viewport().size_changed.connect(_resize)
	_resize()
	var hud := Label.new()
	hud.name = "NativeResolutionStatus"
	hud.text = "ASTRAEA / D09 TERRACE — PRODUCTION WIP\nWASD · Mouse · RMB focus · Esc release · M express directory · F4 effects\nInitial authored components; full ship and gameplay incomplete"
	hud.position = Vector2(18, 18)
	hud.add_theme_font_size_override("font_size", 16)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(hud)
	_build_directory()
	if "--capture-validation" in OS.get_cmdline_user_args():
		await get_tree().create_timer(2.0).timeout
		await _capture()
		if "--capture-d06" in OS.get_cmdline_user_args():
			var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
			actor.spawn_position = Vector3(-51,27.1,4)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = 0.0
			actor.pitch = -0.22
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			await _capture("d06_")
		if "--capture-aquatic" in OS.get_cmdline_user_args():
			var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
			actor.spawn_position = Vector3(13,44.1,218)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = -PI/2
			actor.pitch = 0.18
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			await _capture("aquatic_")
			actor.spawn_position = Vector3(47,44.1,216)
			actor.position = actor.spawn_position
			actor.pitch = 0.0
			actor.camera.rotation.x = 0.0
			await get_tree().create_timer(1.0).timeout
			await _capture("wet_retreat_")
		get_tree().quit()

func _resize() -> void:
	var screen := Vector2(get_viewport().size)
	var scale_factor := minf(screen.x / 640.0, screen.y / 360.0)
	if scale_factor >= 1.0:
		scale_factor = maxf(1.0, floorf(scale_factor))
	display.size = Vector2(640,360) * scale_factor
	display.position = (screen - display.size) * 0.5

func _unhandled_input(event: InputEvent) -> void:
	if directory_open and event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		_toggle_directory()
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_M:
		_toggle_directory()
	if event is InputEventKey and event.pressed and event.keycode == KEY_F12:
		_capture()
	if event is InputEventKey and event.pressed and event.keycode == KEY_F4:
		effects = not effects
		post_pass.material.set_shader_parameter("effects_enabled", effects)
		world_view.get_node("Astraea").set_display_effects(effects)

func _input(event: InputEvent) -> void:
	if is_instance_valid(world_view) and not directory_open: world_view.push_input(event)

func _capture(prefix: String = "") -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://artifacts")
	world_view.get_texture().get_image().save_png("res://artifacts/"+prefix+"world_capture.png")
	post_view.get_texture().get_image().save_png("res://artifacts/"+prefix+"processed_world_capture.png")
	get_viewport().get_texture().get_image().save_png("res://artifacts/"+prefix+"presentation_capture.png")

func _build_directory() -> void:
	directory = PanelContainer.new()
	directory.name = "ExpressDirectory"
	directory.position = Vector2(80,90)
	directory.custom_minimum_size = Vector2(920,530)
	add_child(directory)
	var column := VBoxContainer.new()
	directory.add_child(column)
	var title := Label.new()
	title.text = "EXPRESS DECK DIRECTORY — structural destinations, interiors unfinished"
	column.add_child(title)
	var grid := GridContainer.new()
	grid.columns = 2
	column.add_child(grid)
	var contract: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/design_contract.json"))
	for index in range(contract.deck_datums.size()):
		var button := Button.new()
		var datum: Dictionary = contract.deck_datums[index]
		button.text = datum.deck_id + "  " + datum.historical_program_label
		button.custom_minimum_size = Vector2(450,46)
		grid.add_child(button)
		button.pressed.connect(_travel.bind(index))
	var close := Button.new()
	close.text = "Close directory"
	close.pressed.connect(_toggle_directory)
	column.add_child(close)
	directory.hide()

func _toggle_directory() -> void:
	directory_open = not directory_open
	directory.visible = directory_open
	get_tree().paused = directory_open
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if directory_open else Input.MOUSE_MODE_CAPTURED

func _travel(index: int) -> void:
	var world = world_view.get_node("Astraea")
	if world.express_arrive(index):
		get_node("NativeResolutionStatus").text = "ASTRAEA / D%02d / +%.1f m — STRUCTURE ONLY\nWASD · Mouse · RMB focus · M directory · F4 effects\nInteriors, transport, population and final architecture unfinished" % [index+1,world.deck_y[index]]
		_toggle_directory()
