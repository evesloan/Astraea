extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var shell:=ship.find_child("NightGardenArchitecture",true,false)as Node3D
	assert(shell!=null)
	assert(shell.get_parent().get_meta("programme_key")=="D12_directory_06")
	assert(shell.get_parent().get_meta("historical_room_id")=="D12_quiet_garden5")
	for mesh in shell.find_children("*","MeshInstance3D",true,false):
		for corner in range(8):
			var p:Vector3=mesh.global_transform*mesh.get_aabb().get_endpoint(corner)
			assert(p.x>=51.99 and p.x<=98.01 and p.z>=-34.01 and p.z<=34.01,"Night garden remains inside its recorded programme")
			assert(p.y>=77.75 and p.y<=83.39,"Opaque roof stays below occupied D13")
	var routes:=[ [Vector3(50,78.1,0),Vector3(59.5,78.1,0)], [Vector3(80.5,78.1,0),Vector3(90,78.1,0)], [Vector3(54.5,78.1,-31),Vector3(54.5,78.1,31)], [Vector3(54.5,78.1,20),Vector3(66,78.1,20)], [Vector3(54.5,78.1,-15),Vector3(75,78.1,-15)] ]
	for route in routes:
		for step in range(81):assert(ship.arrive_at(route[0].lerp(route[1],step/80.0),0),"Cross-route, viewing spine and court approaches stay usable: %s"%str(route[0].lerp(route[1],step/80.0)))
	for i in range(48):
		var a:=shell.find_child("DATUM_walk_loop_%03d"%i,true,false)as Node3D
		# These markers come from the same authored geometry as the stone loop.
		var b:=shell.find_child("DATUM_walk_loop_%03d"%(i+1),true,false)as Node3D
		for j in range(5):assert(ship.arrive_at(a.global_position.lerp(b.global_position,j/4.0)+Vector3.UP*.1,0),"Follow the actual curved walking loop: %d"%i)
	var state:=ship.get_world_3d().direct_space_state
	for court in range(4):
		for group in [["plant",7],["underplant",16],["flower",8]]:
			for i in range(group[1]):
				var datum:=shell.find_child("DATUM_%s_%d_%d"%[group[0],court,i],true,false)as Node3D
				var hit:=state.intersect_ray(PhysicsRayQueryParameters3D.create(datum.global_position+Vector3.UP*.05,datum.global_position+Vector3.DOWN*.10))
				assert(not hit.is_empty() and absf(hit.position.y-datum.global_position.y)<.015,"Every plant meets its soil surface")
	for i in range(6):
		var datum:=shell.find_child("DATUM_light_"+str(i),true,false)as Node3D
		assert(state.intersect_ray(PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.DOWN*.1)).is_empty(),"Night garden fixture emits outside its lens")
	for i in range(2):
		var datum:=shell.find_child("DATUM_uplight_"+str(i),true,false)as Node3D
		assert(state.intersect_ray(PhysicsRayQueryParameters3D.create(datum.global_position,datum.global_position+Vector3.UP*.1)).is_empty(),"Planter light exits upward outside its lens")
	for p in [Vector3(55.7,78.1,-10),Vector3(55.7,78.1,10),Vector3(90,78.1,0)]:assert(ship.arrive_at(p,0),"Conversation group approach stays clear")
	print("NIGHT GARDEN PASS:645 route probes,124 soil contacts,8 source exits,3 conversation approaches and allocation/D13 bounds. No guests, carts, final art or target-GPU acceptance.")
	main.queue_free()
	await process_frame
	quit()
