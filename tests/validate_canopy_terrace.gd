extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(25): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var shell := ship.find_child("CanopyTerraceAuthoredRoom",true,false) as Node3D
	assert(shell != null)
	for lane in [-1.2,0.0,1.2]:
		for step in range(71):
			assert(ship.arrive_at(Vector3(lerpf(-42,-77,step/70.0),27.1,lane),0),"Canopy arrival and gathering spine must remain walkable")
	for side in [-1.0,1.0]:
		var path := [Vector3(-63,27.1,0),Vector3(-63,27.1,side*10.3),Vector3(-68.5,27.1,side*10.3)]
		for leg in range(2):
			for step in range(21):
				assert(ship.arrive_at(path[leg].lerp(path[leg+1],step/20.0),0),"Quiet niches need a clear supported approach around planting")
	for side in [-1.0,1.0]:
		for step in range(13):
			assert(ship.arrive_at(Vector3(-76.7,27.1,side*lerpf(0,2.0,step/12.0)),0),"Rear benches need a usable side approach")
	for mesh in shell.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var p: Vector3 = mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(p.x>=-98 and p.x<=-51.99 and absf(p.z)<34,"Architecture must remain within existing allocation")
			assert(p.y>=26.75 and p.y<35.25,"Keep D05 and occupied D07 intact")
	var state := ship.get_world_3d().direct_space_state
	for i in range(4):
		var datum := shell.find_child("DATUM_light_"+str(i),true,false) as Node3D
		assert(state.intersect_ray(PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN*.2)).is_empty(),"Pendant source must clear its lens")
	var portico := ship.find_child("CanopyArrivalPortico",true,false) as Node3D
	assert(portico != null)
	for mesh in portico.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var p: Vector3 = mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(p.x>=-52.2 and p.x<-45.4 and absf(p.z)<4.7 and p.y>=26.99 and p.y<32.2,"Portico stays in the verified forecourt above existing floor")
	for i in range(2):
		var datum := portico.find_child("DATUM_light_"+str(i),true,false) as Node3D
		assert(state.intersect_ray(PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN*.2)).is_empty(),"Portico source must clear its real lens")
	print("CANOPY PASS: 213 three-lane arrival-spine,84 quiet-niche and26 rear-seat probes, allocation and vertical fit,4 source exits. Partial room; no final art, cart, NPC or performance acceptance.")
	main.queue_free()
	await process_frame
	quit()
