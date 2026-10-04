extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var player:Node3D=ship.get_node("ShipSpace/PersistentActors/Player")
	player.position=Vector3(89,84.1,8)
	var budget=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	budget.refresh()
	for light in budget.sources:
		if light.visible and light.shadow_enabled:
			var query:=PhysicsRayQueryParameters3D.create(light.global_position,player.global_position+Vector3.UP*1.6)
			query.exclude=[player.get_rid()]
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
			print("ACTIVE_SOURCE ",light.name," at ",light.global_position," first_blocker ",hit.collider.get_path()if not hit.is_empty()else"none")
	var total_us:=0
	var worst_us:=0
	for sample in range(30):
		var start:=Time.get_ticks_usec()
		budget.refresh()
		var elapsed:=Time.get_ticks_usec()-start
		total_us+=elapsed
		worst_us=maxi(worst_us,elapsed)
	print("BUDGET_CPU_US mean=",total_us/30.0," worst=",worst_us," cloud only; not target frame time")
	main.queue_free()
	await process_frame
	quit()
