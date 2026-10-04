extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(25): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var shell := ship.find_child("AuthoredTwinSuite",true,false) as Node3D
	assert(shell != null)
	for mesh in shell.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var p: Vector3 = mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(p.x>=69.04 and p.x<=81.96 and p.z>=-45.61 and p.z<=-38.39,"Suite respects its recovered allocation")
			assert(p.y>=83.77 and p.y<88.26,"Keep room below future D14 slab and above D12 headroom")
	var path := [Vector3(52,84.1,-42),Vector3(52,84.1,-28),Vector3(84,84.1,-28),Vector3(84,84.1,-42),Vector3(70,84.1,-42)]
	for leg in range(path.size()-1):
		for step in range(41):
			assert(ship.arrive_at(path[leg].lerp(path[leg+1],step/40.0),0),"Actual atrium-to-street-to-room route stays supported and clear")
	for pos in [Vector3(79.1,84.1,-41.35),Vector3(79.1,84.1,-40.1),Vector3(64,84.1,-42)]:
		assert(ship.arrive_at(pos,0),"Bath threshold or view terrace must remain approachable")
	var beds := shell.get_parent().find_children("HistoricalBedAnchor_*","Node3D",true,false)
	assert(beds.size()==2)
	for bed in beds:
		assert(absf(bed.global_position.x-71.7)<.002 and absf(bed.global_position.y-84)<.002)
		assert(minf(absf(bed.global_position.z+43.65),absf(bed.global_position.z+40.35))<.002,"Keep explicit historical bed anchor locations")
	var state := ship.get_world_3d().direct_space_state
	for i in range(3):
		var datum := shell.find_child("DATUM_light_"+str(i),true,false) as Node3D
		assert(state.intersect_ray(PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN*.1)).is_empty(),"Suite source exits its lens")
	var arrival := ship.find_child("QuietResidentialArrival",true,false) as Node3D
	assert(arrival != null)
	for mesh in arrival.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var p: Vector3 = mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(p.x>=81.94 and p.x<=86.06 and p.z>=-45.61 and p.z<=-38.39,"Arrival stays inside existing street")
			assert(p.y>=84 and p.y<88.26,"Arrival stays below occupied D14")
	for x in [83.0,84.0,85.0]:
		for step in range(29):
			assert(ship.arrive_at(Vector3(x,84.1,-45.5+step*.25),0),"Three-lane arrival clearance")
	for i in range(3):
		var datum := arrival.find_child("DATUM_arrival_light_"+str(i),true,false) as Node3D
		assert(state.intersect_ray(PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN*.1)).is_empty(),"Arrival source exits its lens")
	print("RESIDENTIAL PASS: allocation and D14 clearance,164 connected route and87 arrival probes,2 historical bed anchors and6 source exits. Plumbing, saving, NPC use and final art incomplete.")
	main.queue_free()
	await process_frame
	quit()
