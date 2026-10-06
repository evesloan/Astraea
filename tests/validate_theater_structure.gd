extends SceneTree
# UNRUN integration draft. No engine was started to author these checks.
# A focused pass is NOT bridge adoption, operational door/lift, or full-suite proof.
var probe = preload("res://tests/theater_stage_probe.gd").new()
var started := 0
func _initialize() -> void:
	started = Time.get_ticks_msec()
	call_deferred("run")
func _process(_delta: float) -> bool:
	if Time.get_ticks_msec()-started > 240000:
		push_error("Theater structure 240-second watchdog")
		quit(1)
	return false
func run() -> void:
	var main: Node = (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(150): await physics_frame
	probe.configure(main.get_node("World360/Astraea"))
	load("res://tests/secondary_engineering_additive_guard.gd").validate(JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json")))
	probe.actor.set_physics_process(false)
	probe.check_import_and_scene_census()
	probe.check_instances()
	probe.check_floor_owners()
	probe.check_motion_poses_and_barriers()
	for frame in range(120): await physics_frame
	probe.check_motion_poses_and_barriers()
	print("THEATER STRUCTURE PASS: actual imported four-file census; unique 2200 chair/2494 authored placements; strict native visual readback (retained proof on dummy renderer), current exact source contacts, 17 bounded owners, eight asset-owned upper surfaces, ",probe.floor_samples," source-floor probes, preserved open voids, fixed D11 open leaves, all other exits/landing gates closed, visual-only cabin. Bridge underside census, continuous traversal, appearance and aggregate acceptance remain separate.")
	main.queue_free()
	await process_frame
	quit(0)
