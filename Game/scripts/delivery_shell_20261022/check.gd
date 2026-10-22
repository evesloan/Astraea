extends SceneTree
var checks := 0
var failures: Array[String] = []

class Actor extends Node:
	var enabled := false
	func set_controls_enabled(value: bool) -> void: enabled = value
class Ship extends Node:
	var effects := true
	func set_display_effects(value: bool) -> void: effects = value
class Presentation extends Node:
	var world_view := SubViewport.new()
	var post_pass := TextureRect.new()
	var effects := true
	var resolution := 0
	var directory_open := false
	func set_world_resolution(index: int) -> void: resolution = index
	func _init() -> void:
		add_child(world_view)
		add_child(post_pass)
		post_pass.material = ShaderMaterial.new()
		post_pass.material.shader = load("res://shaders/retro.gdshader")
		var ship := Ship.new()
		ship.name = "Astraea"
		world_view.add_child(ship)
		var space := Node.new()
		space.name = "ShipSpace"
		ship.add_child(space)
		var actors := Node.new()
		actors.name = "PersistentActors"
		space.add_child(actors)
		var actor := Actor.new()
		actor.name = "Player"
		actors.add_child(actor)

func require(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures.append(label)

func _initialize() -> void: call_deferred("run")

func run() -> void:
	var prefs = load("res://scripts/delivery_shell_20261022/settings.gd").new()
	prefs.path = "user://delivery_check_%d.cfg" % Time.get_ticks_usec()
	require(prefs.read_preferences() == ERR_FILE_NOT_FOUND, "missing preferences safe defaults")
	prefs.values = {"resolution": 2, "effects": false, "fullscreen": false, "volume": 0.35, "fps": 30}
	require(prefs.save_preferences() == OK, "save preferences")
	var reread = load("res://scripts/delivery_shell_20261022/settings.gd").new()
	reread.path = prefs.path
	require(reread.read_preferences() == OK and reread.values == prefs.values, "persistent round trip")
	var cfg := ConfigFile.new()
	cfg.set_value("presentation", "resolution", 99)
	cfg.set_value("presentation", "fps", 900)
	cfg.set_value("presentation", "volume", -2.0)
	cfg.set_value("presentation", "effects", "not a bool")
	cfg.save(prefs.path)
	var invalid = load("res://scripts/delivery_shell_20261022/settings.gd").new()
	invalid.path = prefs.path
	invalid.read_preferences()
	require(invalid.values.resolution == 2 and invalid.values.fps == 60 and invalid.values.volume == 0.0 and invalid.values.effects, "malformed values bounded")
	var shell = load("res://scripts/delivery_shell_20261022/launcher.gd").new()
	shell.preferences.path = "user://absent_delivery_%d.cfg" % Time.get_ticks_usec()
	root.add_child(shell)
	require(shell.presentation == null and shell.launch_button.text == "Enter the ship", "menu does not construct ship")
	shell._resume()
	require(not paused and shell.panel.visible, "resume cannot bypass readiness")
	var stub := Presentation.new()
	shell.add_child(stub)
	shell.presentation = stub
	shell._process(0.0)
	require(not shell.ready_seen and not paused, "unready ship remains constructing")
	stub.world_view.get_node("Astraea").set_meta("runtime_ready", true)
	shell._process(0.0)
	var actor: Node = stub.world_view.get_node("Astraea/ShipSpace/PersistentActors/Player")
	require(shell.ready_seen and paused and not actor.enabled, "ready transition opens paused menu")
	shell._setting("resolution", 1)
	shell._setting("effects", false)
	require(stub.resolution == 1 and not stub.effects and not stub.world_view.get_node("Astraea").effects, "reuse presentation settings")
	shell._resume()
	require(not paused and actor.enabled and not shell.panel.visible, "resume restores controls")
	shell._pause()
	require(paused and not actor.enabled and shell.panel.visible, "pause suspends controls")
	var event := InputEventKey.new()
	event.keycode = KEY_F10
	event.pressed = true
	stub.directory_open = true
	shell._input(event)
	require(paused, "directory ownership preserved")
	stub.directory_open = false
	shell._input(event)
	require(not paused and actor.enabled, "F10 resumes")
	event.keycode = KEY_F3
	shell._input(event)
	require(stub.resolution == 2 and shell.preferences.values.resolution == 2, "resolution hotkey uses persistent setting")
	event.keycode = KEY_F4
	shell._input(event)
	require(stub.effects and shell.preferences.values.effects, "effects hotkey uses persistent setting")
	var absent := FileAccess.open(prefs.path, FileAccess.WRITE)
	absent.store_string("[invalid")
	absent.close()
	require(invalid.read_preferences() != OK, "corrupt settings reported")
	DirAccess.remove_absolute(prefs.path)
	DirAccess.remove_absolute(shell.preferences.path)
	shell.free()
	var receipt := {"checks": checks, "failures": failures, "scope": "Launcher/preferences and simulated readiness interface only; no ship instantiation or playable acceptance"}
	FileAccess.open("res://docs/validation/delivery_shell_20261022/CHECK.json", FileAccess.WRITE).store_string(JSON.stringify(receipt, "\t"))
	print(JSON.stringify(receipt))
	quit(0 if failures.is_empty() else 1)
