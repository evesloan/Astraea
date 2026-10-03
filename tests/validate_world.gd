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
	main.set_world_resolution(2)
	assert(viewport.size == Vector2i(1920,1080))
	assert(main.post_view.size == viewport.size and main.post_pass.size == Vector2(viewport.size))
	main.set_world_resolution(0)
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
	for deck_index in range(18):
		assert(world.express_arrive(deck_index), "Every express landing needs existing collision")
		for frame in range(15): await physics_frame
		assert(absf(player.position.y-world.deck_y[deck_index]) < 0.15)
		assert(player.is_on_floor())
		var budget := world.get_node("ShipSystems/LocalShadowSourceBudget")
		budget.refresh()
		var active_shadows := 0
		for source in budget.sources:
			if source.visible and source.shadow_enabled: active_shadows += 1
		assert(active_shadows<=budget.shadow_source_budget,"Local shadow budget")
		for z in [-500.0,-100.0,-72.0,72.0,100.0,500.0]:
			var origin := Vector3(0,world.deck_y[deck_index]+0.8,z)
			var query := PhysicsRayQueryParameters3D.create(origin,origin-Vector3.UP*1.5)
			assert(not world.get_world_3d().direct_space_state.intersect_ray(query).is_empty(), "Missing route datum support")
	var arc_floor_ray := PhysicsRayQueryParameters3D.create(Vector3(-30.623,27.8,-2.5),Vector3(-30.623,26.6,-2.5))
	assert(not world.get_world_3d().direct_space_state.intersect_ray(arc_floor_ray).is_empty(), "Authored curved floor must provide support")
	var arc_void_ray := PhysicsRayQueryParameters3D.create(Vector3(-28.823,27.8,-4),Vector3(-28.823,26.6,-4))
	assert(world.get_world_3d().direct_space_state.intersect_ray(arc_void_ray).is_empty(), "No generic slab may fill the new curved opening")
	# Actual body-width sweep across the two shared terrace boundaries and portal.
	var clearance := CapsuleShape3D.new()
	clearance.radius = 0.3
	clearance.height = 1.8
	for segment in [[Vector3(50,53.43,-36),Vector3(50,53.43,-32)], [Vector3(50,53.43,2),Vector3(50,53.43,6)], [Vector3(40,53.43,0),Vector3(59,53.43,0)], [Vector3(-46,0.93,0),Vector3(-65,0.93,0)]]:
		var sweep := PhysicsShapeQueryParameters3D.new()
		sweep.shape = clearance
		sweep.transform.origin = segment[0]
		sweep.motion = segment[1]-segment[0]
		sweep.exclude = [player.get_rid()]
		assert(world.get_world_3d().direct_space_state.intersect_shape(sweep).is_empty(), "Terrace route begins obstructed")
		var fractions := world.get_world_3d().direct_space_state.cast_motion(sweep)
		assert(fractions[0] > 0.999, "Temporary guards or portal must not block a shared route")
	assert(not world.express_arrive(-1) and not world.express_arrive(18))
	for arrival in [Vector3(13,44.1,218),Vector3(13,52.6,218),Vector3(13,61.1,218),Vector3(63,52.6,-20.5),Vector3(-59,0.1,0)]:
		assert(world.arrive_at(arrival,0.0),"Authored destination needs floor and body clearance")
	assert(not world.arrive_at(Vector3(30,52.6,216),0.0),"Arrival inside floor opening must be rejected")
	var cache = load("res://scripts/static_contact_cache.gd")
	assert(cache.shapes_reused > 0 and cache.contacts_created > cache.live_shape_count(),"Repeated source meshes should share immutable contact geometry")
	print("CONTACT CACHE: %d placements use %d shared shapes (%d reuses)" % [cache.contacts_created,cache.live_shape_count(),cache.shapes_reused])
	print("WORLD PASS: supported D09 spawn; 18 express arrivals and 108 structural route probes; 18 structural datums; 640x360 world; source cove mating; adjustable effect resources. Not full route, collision, visual or performance acceptance.")
	main.queue_free()
	await process_frame
	quit(0)
