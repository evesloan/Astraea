extends SceneTree

# Bounded source-context visual QA only. This does not replace default-ship
# graphical acceptance; the full graphical run terminated before capture.
func _initialize() -> void:
	OS.set_environment("ASTRAEA_TIDAL_CANDIDATE_ISOLATION", "1")
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
	load("res://scripts/tidal_garden_receiving.gd").build(ship)
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
		["01_d13_arrival",Vector3(-7,85.65,-370),Vector3(-82,86,-370)],
		["02_d13_watercourt",Vector3(-90,85.65,-350),Vector3(-86,88,-425)],
		["03_d14_landing",Vector3(-76,90.15,-370),Vector3(-92,89,-403)],
		["04_d16_overlook",Vector3(-76,99.15,-370),Vector3(-87,87,-425)]
	]
	DirAccess.make_dir_recursive_absolute("res://artifacts/tidal_source_context_visual")
	for view in views:
		camera.position = view[1]
		camera.look_at(view[2])
		for frame in range(4): await process_frame
		await RenderingServer.frame_post_draw
		assert(root.get_texture().get_image().save_png("res://artifacts/tidal_source_context_visual/"+str(view[0])+".png") == OK)
		print("TIDAL_SOURCE_CONTEXT_CAPTURE ",view[0])
	print("TIDAL_SOURCE_CONTEXT_COMPLETE")
	quit()
