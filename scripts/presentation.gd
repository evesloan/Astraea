extends Node
var world_view: SubViewport
var display: TextureRect
var post_view: SubViewport
var post_pass: TextureRect
var effects := true
var directory: PanelContainer
var directory_open := false
var reticle: Node2D
var interaction_hint: Label
var resolution_index := 0
var capture_records: Array = []
const RESOLUTIONS := [Vector2i(640,360),Vector2i(960,540),Vector2i(1920,1080)]

func _ready() -> void:
	Engine.max_fps = 60
	process_mode = Node.PROCESS_MODE_ALWAYS
	world_view = SubViewport.new()
	world_view.name = "World360"
	world_view.process_mode = Node.PROCESS_MODE_PAUSABLE
	world_view.size = Vector2i(640, 360)
	world_view.own_world_3d = true
	world_view.positional_shadow_atlas_16_bits = false
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
	reticle = Node2D.new()
	reticle.set_script(load("res://scripts/focus_reticle.gd"))
	post_view.add_child(reticle)
	reticle.hide()
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
	interaction_hint = Label.new()
	interaction_hint.position = Vector2(18,76)
	interaction_hint.add_theme_font_size_override("font_size",16)
	add_child(interaction_hint)
	_build_directory()
	if "--capture-validation" in OS.get_cmdline_user_args():
		await get_tree().create_timer(2.0).timeout
		await _capture()
		if "--capture-d06" in OS.get_cmdline_user_args():
			var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
			actor.spawn_position = Vector3(-31.623,27.1,4)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = 0.0
			actor.pitch = -0.22
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D06 CURVED GALLERY — unfinished architecture"
			await _capture("d06_")
			actor.spawn_position = Vector3(5,52.6,-59)
			actor.position = actor.spawn_position
			actor.rotation.y = PI
			actor.pitch = 0.08
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / GRAND ATRIUM — restored floor contours, finish incomplete"
			await _capture("atrium_")
			actor.spawn_position = Vector3(0,6.1,-51)
			actor.position = actor.spawn_position
			actor.rotation.y = PI
			actor.pitch = 0.12
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D02 BOTANICAL COURT — first architectural composition"
			await _capture("garden_")
			actor.spawn_position = Vector3(-9,6.1,-35)
			actor.position = actor.spawn_position
			actor.pitch = 0.20
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(0.5).timeout
			await _capture("garden_near_")
			set_world_resolution(2)
			effects = false
			post_pass.material.set_shader_parameter("enabled",effects)
			world_view.get_node("Astraea").set_display_effects(false)
			await get_tree().create_timer(0.5).timeout
			await _capture("garden_clear_")
			set_world_resolution(0)
			effects = true
			post_pass.material.set_shader_parameter("enabled",effects)
			world_view.get_node("Astraea").set_display_effects(true)
		if "--capture-aquatic" in OS.get_cmdline_user_args():
			var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
			actor.spawn_position = Vector3(13,44.1,218)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = -PI/2
			actor.pitch = 0.18
			actor.camera.rotation.x = actor.pitch
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D08–D10 AQUATIC SECTION — unfinished architecture"
			await _capture("aquatic_")
			actor.spawn_position = Vector3(47,44.1,216)
			actor.position = actor.spawn_position
			actor.pitch = 0.0
			actor.camera.rotation.x = 0.0
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D08 WET RETREAT — component integration"
			await _capture("wet_retreat_")
		if "--capture-staff" in OS.get_cmdline_user_args():
			var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
			actor.spawn_position = Vector3(-59,0.1,0)
			actor.position = actor.spawn_position
			actor.velocity = Vector3.ZERO
			actor.rotation.y = PI/2
			actor.pitch = 0.0
			actor.camera.rotation.x = 0.0
			await get_tree().create_timer(1.0).timeout
			get_node("NativeResolutionStatus").text = "ASTRAEA / D01 SYNTHESIS SERVICE BAY — partial installation"
			await _capture("staff_")
			var door = world_view.get_node("Astraea").find_child("SynthesisServiceDoor",true,false)
			await get_tree().physics_frame
			door.interact(actor)
			await get_tree().create_timer(1.4).timeout
			var focus := InputEventMouseButton.new()
			focus.button_index = MOUSE_BUTTON_RIGHT
			focus.pressed = true
			Input.parse_input_event(focus)
			await get_tree().create_timer(0.5).timeout
			await _capture("staff_focus_")
			focus.pressed = false
			Input.parse_input_event(focus)
			await get_tree().physics_frame
			door.interact(actor)
			await get_tree().create_timer(1.4).timeout
			set_world_resolution(2)
			effects = false
			post_pass.material.set_shader_parameter("effects_enabled",false)
			world_view.get_node("Astraea").set_display_effects(false)
			await get_tree().create_timer(0.25).timeout
			await _capture("staff_clear_")
		get_tree().quit()

func _resize() -> void:
	var screen := Vector2(get_viewport().size)
	var logical := Vector2(world_view.size)
	var scale_factor := minf(screen.x / logical.x, screen.y / logical.y)
	if scale_factor >= 1.0:
		scale_factor = maxf(1.0, floorf(scale_factor))
	display.size = logical * scale_factor
	display.position = (screen - display.size) * 0.5

func _unhandled_input(event: InputEvent) -> void:
	if directory_open and event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		_toggle_directory()
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_M:
		_toggle_directory()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F3:
		set_world_resolution((resolution_index+1)%RESOLUTIONS.size())
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F11:
		get_window().mode = Window.MODE_WINDOWED if get_window().mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN
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
	var actor = world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
	capture_records.append({"prefix":prefix,"world_resolution":[world_view.size.x,world_view.size.y],"effects_enabled":effects,"camera_position":[actor.camera.global_position.x,actor.camera.global_position.y,actor.camera.global_position.z],"camera_rotation":[actor.camera.global_rotation.x,actor.camera.global_rotation.y,actor.camera.global_rotation.z],"fov":actor.camera.fov,"adapter":RenderingServer.get_video_adapter_name(),"scope":"In-engine review, not target-platform performance acceptance"})
	var record := FileAccess.open("res://artifacts/capture_settings.json",FileAccess.WRITE)
	record.store_string(JSON.stringify(capture_records,"  "))
	record.close()

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
	var places := GridContainer.new()
	places.columns = 2
	column.add_child(places)
	for target in [{"name":"D02 Botanical garden — unfinished", "position":Vector3(0,6.1,-51),"facing":PI}, {"name":"D09 Grand Atrium — unfinished", "position":Vector3(5,52.6,-59),"facing":PI}, {"name":"D01 Synthesis service bay — partial", "position":Vector3(-59,0.1,0)}, {"name":"D08 Gentle Waters — unfinished", "position":Vector3(13,44.1,218)}, {"name":"D09 Living Gifts — unfinished", "position":Vector3(13,52.6,218)}, {"name":"D10 Vesper — unfinished", "position":Vector3(13,61.1,218)}, {"name":"D09 Conversation salon — partial", "position":Vector3(63,52.6,-20.5)}]:
		var button := Button.new()
		button.text = target.name
		button.custom_minimum_size = Vector2(450,36)
		places.add_child(button)
		button.pressed.connect(_visit.bind(target.name,target.position,target.get("facing",PI/2 if target.position.x < 0 else -PI/2)))
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

func _visit(label: String, arrival: Vector3, facing: float) -> void:
	var world = world_view.get_node("Astraea")
	if world.arrive_at(arrival,facing):
		get_node("NativeResolutionStatus").text = "ASTRAEA / "+label+"\nWASD · Mouse · RMB focus · M directory · F4 effects\nProduction architecture in progress"
		_toggle_directory()

func _process(_delta: float) -> void:
	if not is_instance_valid(reticle): return
	reticle.visible = Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) and not directory_open
	var actor = world_view.get_node_or_null("Astraea/ShipSpace/PersistentActors/Player")
	if actor != null and reticle.visible and is_instance_valid(actor.interaction_target):
		interaction_hint.text = actor.interaction_target.get_interaction_label()
	else: interaction_hint.text = ""

func set_world_resolution(index: int) -> void:
	assert(index >= 0 and index < RESOLUTIONS.size())
	resolution_index = index
	world_view.size = RESOLUTIONS[index]
	post_view.size = world_view.size
	post_pass.size = Vector2(world_view.size)
	reticle.queue_redraw()
	_resize()
