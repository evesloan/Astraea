extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(90): await physics_frame
	var world: Node3D = main.get_node("World360/Astraea")
	var player: CharacterBody3D = world.get_node("ShipSpace/PersistentActors/Player")
	assert(player.is_on_floor(), "Spawn must settle on supported floor")
	assert(absf(player.global_position.y-52.5) < 0.1, "D09 floor datum")
	assert(world.get_node("ShipSpace/All18DeckStructuralDatums_NOT_FINISHED_ARCHITECTURE").get_child_count()==18)
	var viewport: SubViewport = main.get_node("World360")
	assert(viewport.size == Vector2i(640,360))
	var bay := world.get_node("ShipSpace/Districts/D09_StarboardTerrace_AuthoredFootprint_WIP/QuietReturn")
	assert(bay.get_child_count()==2)
	assert(world.find_children("QuietBayTaskLight_*","SpotLight3D",true,false).size()==2, "Both real fixture lights must exist")
	assert(bay.get_node("MatedOverhead").position.is_equal_approx(Vector3(-3.1,0,0)))
	var env: Environment = world.get_node("WorldEnvironment").environment
	assert(env.glow_enabled and env.ssao_enabled)
	for light in world.find_children("QuietBayTaskLight_*","SpotLight3D",true,false):
		assert(light.global_position.y > 55.69 and light.global_position.y < 55.71)
	world.set_display_effects(false)
	assert(not env.glow_enabled and not env.ssao_enabled)
	world.set_display_effects(true)
	print("WORLD PASS: supported D09 spawn; 18 structural datums; 640x360 world; source cove mating; adjustable effect resources. Not full route, collision, visual or performance acceptance.")
	main.queue_free()
	await process_frame
	quit(0)
