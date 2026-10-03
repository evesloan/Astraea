extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(25): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var bay := ship.find_child("AuthoredGardenOverlook",true,false) as Node3D
	var state := ship.get_world_3d().direct_space_state
	assert(bay != null)
	# Arrival and through route stay on the existing terrace and outside the planter/seat contacts.
	for i in range(31):
		var point := Vector3(-37,27.1,lerpf(-35,-19,float(i)/30.0))
		assert(ship.arrive_at(point,0),"Garden edge route must remain clear")
	for point in [Vector3(-39,27.1,-27),Vector3(-40,27.1,-25),Vector3(-34,27.1,-19)]:
		assert(ship.arrive_at(point,0),"Overlook stopping/arrival position must remain usable")
	for mesh in bay.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var world_point: Vector3 = mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(world_point.y >= 26.99 and world_point.y < 35.26,"Overlook must fit D06 without intruding on D07")
	for i in range(2):
		var datum := bay.find_child("DATUM_light_"+str(i),true,false) as Node3D
		var ray := PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN*.2)
		assert(state.intersect_ray(ray).is_empty(),"Overlook source must exit its actual lens")
		var soil := bay.find_child("DATUM_plant_"+str(i),true,false) as Node3D
		ray = PhysicsRayQueryParameters3D.create(soil.global_position+Vector3.UP*.01,soil.global_position-Vector3.UP*.03)
		var hit := state.intersect_ray(ray)
		assert(not hit.is_empty() and absf(hit.position.y-soil.global_position.y)<.02,"Planting datum requires a containing soil surface")
	print("OVERLOOK PASS: 31 through-route probes,3 arrivals,actual optical/soil contacts and D06/D07 height fit. Not final architecture, seating AI, cart or structural-load approval.")
	main.queue_free()
	await process_frame
	quit()
