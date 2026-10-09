extends SceneTree

# Bounded source-context visual QA only. This does not replace default-ship
# graphical acceptance; the full graphical run terminated before capture.
func _initialize() -> void:
	root.size = Vector2i(1280,720)
	call_deferred("run")

func run() -> void:
	var world := SubViewport.new()
	world.size = Vector2i(640,360)
	world.own_world_3d = true
	world.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(world)
	var ship := Node3D.new()
	ship.name = "TidalSourceContext_QA_ONLY"
	world.add_child(ship)
	var space := Node3D.new()
	space.name = "ShipSpace"
	ship.add_child(space)
	var districts := Node3D.new()
	districts.name = "Districts"
	space.add_child(districts)
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(.025,.034,.046)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(.75,.81,.86)
	environment.ambient_light_energy = .2
	var setting := WorldEnvironment.new()
	setting.environment = environment
	ship.add_child(setting)
	var lift: Node3D = load("res://scripts/tidal_lift_candidate.gd").build(ship)
	load("res://scripts/tidal_room_candidates.gd").build(ship)
	for frame in range(120): await physics_frame
	var horizon: Node3D = load("res://assets/models/SOL_D12_directory_01_entry001.glb").instantiate()
	districts.add_child(horizon)
	var display := TextureRect.new()
	display.texture = world.get_texture()
	display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	display.size = Vector2(1280,720)
	display.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	root.add_child(display)
	var camera := Camera3D.new()
	ship.add_child(camera)
	camera.fov = 72
	camera.make_current()
	var views := [
		["01_d13_lift_approach",Vector3(-74.5,85.65,-373.5),Vector3(-74.5,85.3,-379.5)],
		["02_d13_lift_cabin",Vector3(-74.5,85.65,-380.4),Vector3(-74.5,85.3,-375)],
		["03_d14_closed_landing",Vector3(-74.5,90.15,-373.5),Vector3(-74.5,89.8,-379.5)]
	]
	DirAccess.make_dir_recursive_absolute("res://artifacts/tidal_lift_context_visual")
	for view in views:
		camera.position = view[1]
		camera.look_at(view[2])
		for frame in range(4): await process_frame
		await RenderingServer.frame_post_draw
		assert(world.get_texture().get_image().save_png("res://artifacts/tidal_lift_context_visual/"+str(view[0])+".png") == OK)
		print("TIDAL_LIFT_CONTEXT_CAPTURE ",view[0])
	print("TIDAL_LIFT_CONTEXT_COMPLETE")
	quit()
