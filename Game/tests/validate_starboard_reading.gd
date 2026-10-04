extends "res://tests/validate_living_gifts.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(50):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var edge:Node3D=ship.find_child("D15ResidentialReadingEdge",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	assert(edge!=null)
	for part in edge.find_children("*","MeshInstance3D",true,false):
		var bounds:AABB=part.global_transform*part.get_aabb()
		assert(bounds.end.y<97.26 and bounds.position.y>=92.999,"Reading edge must remain inside D15")
	for i in range(2):
		var source:Node3D=edge.find_child("DATUM_light_"+str(i),true,false)
		var surface:Node3D=edge.find_child("DATUM_work_surface_"+str(i),true,false)
		var query:=PhysicsRayQueryParameters3D.create(source.global_position,surface.global_position+Vector3.DOWN*.03)
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
		assert(not hit.is_empty() and "READ_Desk_" in str(hit.collider.get_path()),"Reading task source must reach its own desk")
		var chair:Node3D=ship.find_child("D15ReadingChair_"+str(i),true,false)
		var omit:Array[RID]=[]
		for body in chair.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		for x in [-.40,.40]:
			for z in [-.28,.28]:
				var p:Vector3=chair.global_transform*Vector3(x,0,z)
				query=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.04,p-Vector3.UP*.04)
				query.exclude=omit
				hit=ship.get_world_3d().direct_space_state.intersect_ray(query)
				assert(not hit.is_empty() and abs(hit.position.y-93)<.015,"Reading chair needs four supported foot samples")
	for i in range(5):
		var marker:Node3D=edge.find_child("DATUM_shelf_"+str(i),true,false)
		for x in [-.23,0.0,.23]:
			for z in [-.09,.09]:
				var p:Vector3=marker.global_position+Vector3(x,0,z)
				var query:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.02,p-Vector3.UP*.02)
				var hit:=ship.get_world_3d().direct_space_state.intersect_ray(query)
				assert(not hit.is_empty() and "READ_Shelf_" in str(hit.collider.get_path()),"Book group base must rest on its shelf")
	actor.set_physics_process(false)
	actor.position=Vector3(78,93.1,-9.5)
	actor.velocity=Vector3.ZERO
	for i in range(2):
		var approach:Node3D=edge.find_child("DATUM_approach_"+str(i),true,false)
		var chair_anchor:Node3D=edge.find_child("DATUM_chair_"+str(i),true,false)
		await walk(actor,Vector2(approach.global_position.x,-9.5))
		await walk(actor,Vector2(approach.global_position.x,approach.global_position.z))
		await walk(actor,Vector2(approach.global_position.x+.92,approach.global_position.z))
		await walk(actor,Vector2(chair_anchor.global_position.x+.92,chair_anchor.global_position.z))
		await walk(actor,Vector2(approach.global_position.x+.92,-9.5))
	await walk(actor,Vector2(79.895,-9.5))
	await walk(actor,Vector2(79.895,-11.8))
	await walk(actor,Vector2(79.895,-9.5))
	assert(abs(actor.position.y-93)<.12)
	print("STARBOARD READING PASS: actual two chair-side approaches and shared shelf browsing; eight chair feet,30 book supports and both task-light receiver paths. Seated use, species fit, book interaction and final art pending.")
	main.queue_free()
	await process_frame
	quit()
