extends Node
# The retained ship/presentation is created once, on request. No readiness bypass.
const MAIN := "res://scenes/main_quiet_court_balance_20261022.tscn"
var preferences = preload("res://scripts/delivery_shell_20261022/settings.gd").new()
var presentation: Node
var overlay: CanvasLayer
var panel: PanelContainer
var rows: VBoxContainer
var status: Label
var launch_button: Button
var resume_button: Button
var settings_panel: VBoxContainer
var ready_seen := false
var launching := false

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var result: Error = preferences.read_preferences()
	preferences.apply_global(get_window())
	_build_menu()
	if result not in [OK, ERR_FILE_NOT_FOUND]: status.text = "Preferences could not be read; defaults are active."
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _button(label: String, action: Callable, parent: Node = rows) -> Button:
	var button := Button.new()
	button.text = label
	button.custom_minimum_size.y = 42
	button.pressed.connect(action)
	parent.add_child(button)
	return button

func _build_menu() -> void:
	overlay = CanvasLayer.new()
	overlay.layer = 100
	add_child(overlay)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.add_child(center)
	panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(520, 0)
	center.add_child(panel)
	var margin := MarginContainer.new()
	for side in ["left", "top", "right", "bottom"]: margin.add_theme_constant_override("margin_" + side, 24)
	panel.add_child(margin)
	rows = VBoxContainer.new()
	rows.add_theme_constant_override("separation", 12)
	margin.add_child(rows)
	var title := Label.new()
	title.text = "THE ASTRAEA"
	title.add_theme_font_size_override("font_size", 34)
	rows.add_child(title)
	status = Label.new()
	status.text = "Construction preview · ship and final acceptance unfinished"
	status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	status.custom_minimum_size.x = 470
	rows.add_child(status)
	launch_button = _button("Enter the ship", _launch)
	resume_button = _button("Resume", _resume)
	resume_button.hide()
	_button("Settings", func(): settings_panel.visible = not settings_panel.visible)
	settings_panel = VBoxContainer.new()
	rows.add_child(settings_panel)
	_build_settings()
	settings_panel.hide()
	_button("Quit", func(): get_tree().quit())
	var help := Label.new()
	help.text = "WASD · Mouse · RMB focus · E interact\nM directory · F10 pause menu · Esc release pointer"
	rows.add_child(help)
	launch_button.grab_focus()

func _build_settings() -> void:
	var resolution := OptionButton.new()
	for label in ["Render resolution: 640 × 360", "Render resolution: 960 × 540", "Render resolution: 1920 × 1080"]: resolution.add_item(label)
	resolution.select(preferences.values.resolution)
	resolution.item_selected.connect(func(index): _setting("resolution", index))
	settings_panel.add_child(resolution)
	for key in ["effects", "fullscreen"]:
		var toggle := CheckButton.new()
		toggle.text = "Retro display effects" if key == "effects" else "Fullscreen"
		toggle.button_pressed = preferences.values[key]
		toggle.toggled.connect(func(value): _setting(key, value))
		settings_panel.add_child(toggle)
	var volume_label := Label.new()
	volume_label.text = "Master volume"
	settings_panel.add_child(volume_label)
	var volume := HSlider.new()
	volume.min_value = 0.0
	volume.max_value = 1.0
	volume.step = 0.05
	volume.value = preferences.values.volume
	volume.value_changed.connect(func(value): _setting("volume", float(value)))
	settings_panel.add_child(volume)
	var fps := OptionButton.new()
	for value in [30, 60, 120]: fps.add_item("Frame limit: %d" % value)
	fps.select([30, 60, 120].find(preferences.values.fps))
	fps.item_selected.connect(func(index): _setting("fps", [30, 60, 120][index]))
	settings_panel.add_child(fps)

func _setting(key: String, value: Variant) -> void:
	preferences.values[key] = value
	preferences.apply_global(get_window())
	if ready_seen: preferences.apply_presentation(presentation)
	if preferences.save_preferences() != OK:
		status.text = "Settings applied, but could not be saved. Check the user-data folder."

func _launch() -> void:
	if launching or is_instance_valid(presentation): return
	launching = true
	launch_button.disabled = true
	status.text = "Constructing the ship… movement unlocks only after ship readiness."
	await get_tree().process_frame
	var packed := load(MAIN) as PackedScene
	if packed == null:
		status.text = "The retained ship scene could not be loaded."
		launching = false
		launch_button.disabled = false
		return
	presentation = packed.instantiate()
	add_child(presentation)
	presentation.set_process_input(false)
	presentation.set_process_unhandled_input(false)
	preferences.apply_global(get_window())
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _process(_delta: float) -> void:
	if not is_instance_valid(presentation) or ready_seen: return
	var ship: Node = presentation.world_view.get_node_or_null("Astraea")
	if ship == null or not ship.get_meta("runtime_ready", false): return
	ready_seen = true
	preferences.apply_presentation(presentation)
	preferences.apply_global(get_window())
	launch_button.hide()
	resume_button.show()
	status.text = "Ship construction ready · gameplay and final visual acceptance remain unfinished"
	_pause()

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and ready_seen and not panel.visible:
		if event.keycode == KEY_F3:
			_setting("resolution", (preferences.values.resolution + 1) % 3)
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_F4:
			_setting("effects", not preferences.values.effects)
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_F11:
			_setting("fullscreen", not preferences.values.fullscreen)
			get_viewport().set_input_as_handled()
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F10 and ready_seen:
		if presentation.directory_open: return
		get_viewport().set_input_as_handled()
		if panel.visible: _resume()
		else: _pause()

func _pause() -> void:
	if not ready_seen: return
	# Rebuild from live preferences so hotkey changes are represented accurately.
	for child in settings_panel.get_children():
		settings_panel.remove_child(child)
		child.queue_free()
	_build_settings()
	presentation.set_process_input(false)
	presentation.set_process_unhandled_input(false)
	presentation.world_view.get_node("Astraea/ShipSpace/PersistentActors/Player").set_controls_enabled(false)
	get_tree().paused = true
	panel.show()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	resume_button.grab_focus()

func _resume() -> void:
	if not ready_seen: return
	panel.hide()
	get_tree().paused = false
	presentation.set_process_input(true)
	presentation.set_process_unhandled_input(true)
	presentation.world_view.get_node("Astraea/ShipSpace/PersistentActors/Player").set_controls_enabled(true)
