extends RefCounted
# Preferences only: never saves or fabricates ship readiness/game state.
const DEFAULTS := {"resolution": 0, "effects": true, "fullscreen": false, "volume": 0.8, "fps": 60}
var values: Dictionary = DEFAULTS.duplicate()
var path := "user://astraea_preferences_v1.cfg"

func read_preferences() -> Error:
	var cfg := ConfigFile.new()
	var result := cfg.load(path)
	if result != OK:
		return result
	for key in DEFAULTS:
		var value = cfg.get_value("presentation", key, DEFAULTS[key])
		if typeof(value) == typeof(DEFAULTS[key]):
			values[key] = value
	values.resolution = clampi(values.resolution, 0, 2)
	values.volume = clampf(values.volume, 0.0, 1.0) if is_finite(values.volume) else DEFAULTS.volume
	if values.fps not in [30, 60, 120]: values.fps = 60
	return OK

func save_preferences() -> Error:
	var cfg := ConfigFile.new()
	for key in DEFAULTS: cfg.set_value("presentation", key, values[key])
	return cfg.save(path)

func apply_global(window: Window) -> void:
	window.mode = Window.MODE_FULLSCREEN if values.fullscreen else Window.MODE_WINDOWED
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(values.volume, 0.0001)))
	AudioServer.set_bus_mute(0, values.volume == 0.0)
	Engine.max_fps = values.fps

func apply_presentation(presentation: Node) -> void:
	presentation.set_world_resolution(values.resolution)
	presentation.effects = values.effects
	presentation.post_pass.material.set_shader_parameter("effects_enabled", values.effects)
	presentation.world_view.get_node("Astraea").set_display_effects(values.effects)
