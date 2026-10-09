extends SceneTree

# Review candidate architecture inside the unmodified default ship. Camera
# placement is for visual inspection, not evidence of ordinary-input traversal.
func _initialize() -> void:
	root.size = Vector2i(1280, 720)
	call_deferred("run")

func run() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	var ship := main.get_node("World360/Astraea") as Node3D
	for frame in range(12): await physics_frame
	load("res://scripts/tidal_garden_receiving.gd").build(ship)
	var camera := Camera3D.new()
	ship.add_child(camera)
	camera.fov = 72.0
	camera.make_current()
	var views := [
		["01_d13_arrival", Vector3(-7,85.65,-370), Vector3(-82,86,-370)],
		["02_d13_watercourt", Vector3(-90,85.65,-350), Vector3(-86,88,-425)],
		["03_d14_landing", Vector3(-76,90.15,-370), Vector3(-92,89,-403)],
		["04_d16_overlook", Vector3(-76,99.15,-370), Vector3(-87,87,-425)]
	]
	DirAccess.make_dir_recursive_absolute("res://artifacts/tidal_visual_candidate")
	for view in views:
		camera.position = view[1]
		camera.look_at(ship.to_global(view[2]))
		for frame in range(8): await process_frame
		await RenderingServer.frame_post_draw
		var error := root.get_texture().get_image().save_png("res://artifacts/tidal_visual_candidate/" + str(view[0]) + ".png")
		assert(error == OK)
		print("TIDAL_CAPTURE_SAVED ", view[0])
	print("TIDAL_CAPTURE_COMPLETE")
	quit()
