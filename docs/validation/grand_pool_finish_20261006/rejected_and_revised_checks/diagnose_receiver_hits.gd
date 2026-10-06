extends SceneTree
func _initialize() -> void: call_deferred("run")
func xyz(p: Array) -> Vector3: return Vector3(p[0],p[1],p[2])
func run() -> void:
	var main: Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for f in range(50):await physics_frame
	var ship: Node3D=main.get_node("World360/Astraea")
	var actor: CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var space := ship.get_world_3d().direct_space_state
	var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GRAND_POOL_FINISH_RUNTIME.json"))
	for row in data.fixtures:
		var light:=ship.find_child("GrandPoolFinishSource_"+str(row.name),true,false)as SpotLight3D
		var start:=light.global_position;var target:=xyz(row.receiver_xyz);var direction:=(target-start).normalized()
		for retreat in [0.0,.0001,.001,.005,.02]:
			var query:=PhysicsRayQueryParameters3D.create(start,target-direction*retreat,1);query.exclude=[actor.get_rid()]
			var hit:=space.intersect_ray(query)
			if hit.is_empty():print("RECEIVER_DIAGNOSTIC ",row.name," retreat ",retreat," CLEAR")
			else:print("RECEIVER_DIAGNOSTIC ",row.name," retreat ",retreat," HIT ",hit.collider.get_parent().get_path()," at ",hit.position," target_gap ",hit.position.distance_to(target)," travel ",hit.position.distance_to(start)," total ",start.distance_to(target))
	main.queue_free();await process_frame;quit(0)
