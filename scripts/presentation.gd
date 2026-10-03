extends Node
var world_view: SubViewport
var display: TextureRect
var effects := true

func _ready() -> void:
	Engine.max_fps = 60
	world_view = SubViewport.new()
	world_view.name = "World360"
	world_view.size = Vector2i(640, 360)
	world_view.own_world_3d = true
	world_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(world_view)
	world_view.add_child(load("res://scenes/ship.tscn").instantiate())
	display = TextureRect.new()
	display.name = "NearestWorldPresentation"
	display.texture = world_view.get_texture()
	display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	display.stretch_mode = TextureRect.STRETCH_SCALE
	display.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load("res://shaders/retro.gdshader")
	display.material = mat
	add_child(display)
	get_viewport().size_changed.connect(_resize)
	_resize()
	var hud := Label.new()
	hud.name = "NativeResolutionStatus"
	hud.text = "ASTRAEA / D09 TERRACE — PRODUCTION WIP\nWASD · Mouse · RMB focus · Esc release · F4 effects\nInitial authored components; full ship and gameplay incomplete"
	hud.position = Vector2(18, 18)
	hud.add_theme_font_size_override("font_size", 16)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(hud)

func _resize() -> void:
	var screen := Vector2(get_viewport().size)
	var scale_factor := minf(screen.x / 640.0, screen.y / 360.0)
	if scale_factor >= 1.0:
		scale_factor = maxf(1.0, floorf(scale_factor))
	display.size = Vector2(640,360) * scale_factor
	display.position = (screen - display.size) * 0.5

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode == KEY_F12:
		_capture()
	if event is InputEventKey and event.pressed and event.keycode == KEY_F4:
		effects = not effects
		display.material.set_shader_parameter("effects_enabled", effects)
		world_view.get_node("Astraea").set_display_effects(effects)

func _input(event: InputEvent) -> void:
	if is_instance_valid(world_view): world_view.push_input(event)

func _capture() -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://artifacts")
	world_view.get_texture().get_image().save_png("res://artifacts/world_capture.png")
	get_viewport().get_texture().get_image().save_png("res://artifacts/presentation_capture.png")
