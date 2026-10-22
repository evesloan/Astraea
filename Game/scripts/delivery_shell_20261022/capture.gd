extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	root.size = Vector2i(1280, 720)
	var shell = load("res://scenes/launcher_delivery_20261022.tscn").instantiate()
	shell.preferences.path = "user://absent_menu_capture_preferences.cfg"
	root.add_child(shell)
	shell.settings_panel.show()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	assert(shell.presentation == null)
	var image := root.get_texture().get_image()
	assert(image.save_png("res://docs/validation/delivery_shell_20261022/MENU_SETTINGS_UNFINISHED.png") == OK)
	quit()
