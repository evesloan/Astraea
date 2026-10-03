extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
	var main := (load("res://scenes/main.tscn") as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(25): await physics_frame
	var ship: Node3D = main.get_node("World360/Astraea")
	var shell := ship.find_child("CanopyTerraceAuthoredRoom",true,false) as Node3D
	assert(shell != null)
	for step in range(51):
		assert(ship.arrive_at(Vector3(lerpf(-50,-77,step/50.0),27.1,0),0),"Canopy arrival and gathering spine must remain walkable")
	for side in [-1.0,1.0]:
		var path := [Vector3(-63,27.1,0),Vector3(-63,27.1,side*10.3),Vector3(-68.5,27.1,side*10.3)]
		for leg in range(2):
			for step in range(21):
				assert(ship.arrive_at(path[leg].lerp(path[leg+1],step/20.0),0),"Quiet niches need a clear supported approach around planting")
	for mesh in shell.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var p: Vector3 = mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(p.x>=-98 and p.x<=-51.99 and absf(p.z)<34,"Architecture must remain within existing allocation")
			assert(p.y>=26.75 and p.y<35.25,"Keep D05 and occupied D07 intact")
	var state := ship.get_world_3d().direct_space_state
	for i in range(4):
		var datum := shell.find_child("DATUM_light_"+str(i),true,false) as Node3D
		assert(state.intersect_ray(PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN*.2)).is_empty(),"Pendant source must clear its lens")
	print("CANOPY PASS: 51 arrival-spine and84 quiet-niche probes, allocation and vertical fit,4 source exits. Partial room; no final art, cart, NPC or performance acceptance.")
	main.queue_free()
	await process_frame
	quit()
