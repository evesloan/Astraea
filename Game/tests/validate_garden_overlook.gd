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
	# A legible approach from the preserved port portal must reach the bay without
	# crossing its planted crescent; also keep the outer service-side passage open.
	var approach := [Vector3(-52,27.1,0),Vector3(-42,27.1,-12),Vector3(-37,27.1,-19)]
	for leg in range(approach.size()-1):
		for step in range(21):
			assert(ship.arrive_at(approach[leg].lerp(approach[leg+1],step/20.0),0),"Port arrival to overlook must stay supported and unobstructed")
	for step in range(21):
		assert(ship.arrive_at(Vector3(-50,27.1,lerpf(-39,-10,step/20.0)),0),"Rear gallery passage must remain clear")
	for segment in range(7):
		for item in range(2):
			var soil := bay.find_child("DATUM_backplant_%d_%d" % [segment,item],true,false) as Node3D
			assert(soil != null)
			var contact := state.intersect_ray(PhysicsRayQueryParameters3D.create(soil.global_position+Vector3.UP*.02,soil.global_position-Vector3.UP*.04))
			assert(not contact.is_empty() and absf(contact.position.y-soil.global_position.y)<.025,"Rear plants need containing soil contacts")
	for mesh in bay.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var world_point: Vector3 = mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(world_point.x > -48 and world_point.x < -28,"Bay remains inside existing terrace footprint")
			assert(world_point.y >= 26.99 and world_point.y < 35.26,"Overlook must fit D06 without intruding on D07")
	for i in range(2):
		var datum := bay.find_child("DATUM_light_"+str(i),true,false) as Node3D
		var ray := PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN*.2)
		assert(state.intersect_ray(ray).is_empty(),"Overlook source must exit its actual lens")
		var soil := bay.find_child("DATUM_plant_"+str(i),true,false) as Node3D
		ray = PhysicsRayQueryParameters3D.create(soil.global_position+Vector3.UP*.01,soil.global_position-Vector3.UP*.03)
		var hit := state.intersect_ray(ray)
		assert(not hit.is_empty() and absf(hit.position.y-soil.global_position.y)<.02,"Planting datum requires a containing soil surface")
	print("OVERLOOK PASS: 31 through-route probes,63 portal/rear-route probes,3 arrivals,14 rear soil contacts,actual optical/soil contacts and D06/D07 height fit. Not final architecture, seating AI, cart or structural-load approval.")
	main.queue_free()
	await process_frame
	quit()
