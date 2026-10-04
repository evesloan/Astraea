extends SceneTree
func _initialize() -> void:call_deferred("run")
func walk(actor:CharacterBody3D,destination:Vector2) -> void:
	var reached:=false
	for frame in range(900):
		var delta:=Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
		if delta.length()<.09:
			reached=true
			break
		var motion:=delta.normalized()*3.1
		actor.velocity.x=motion.x
		actor.velocity.z=motion.z
		actor.velocity.y=-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60
		actor.move_and_slide()
		await physics_frame
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("STAR ATLAS BLOCKER ",actor.get_slide_collision(i).get_collider().get_path())
	assert(reached,"Star Atlas route stalled at %s toward %s"%[actor.position,destination])
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(30):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var district:=ship.find_child("D12_D14_StarAtlas_WIP",true,false)
	assert(district!=null and district.get_meta("historical_library_id")=="D12_stargazing4")
	var architecture:=district.get_node("StarAtlasAuthoredArchitecture")
	for i in range(10):
		var marker:=architecture.find_child("DATUM_light_"+str(i),true,false)as Node3D
		var ray:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position-Vector3.UP*.12)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Library fixture exit must be outside its source")
	var roof:=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-84,92.70,1),Vector3(-84,93.10,1)))
	assert(not roof.is_empty() and absf(roof.position.y-92.76)<.015,"Protected D15 cover remains opaque")
	var pan:=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(-66.5,77.4,-10.2),Vector3(-66.5,77.81,-10.2)))
	assert(not pan.is_empty() and absf(pan.position.y-77.76)<.015,"Lift pit remains sealed within D12 slab, above performers' commons")
	var lift=district.get_node("StarAtlasPassengerLift")
	assert(lift.floor_heights==[78.0,84.0,88.5])
	for deck in [12,13,14]:assert(lift.find_child("star_atlas_cabin_D"+str(deck),true,false)!=null)
	var collection:=district.get_node("NorthCollectionStudy_WIP")
	var batch:MultiMeshInstance3D=collection.get_node("LocalCollectionStock")
	assert(batch.multimesh.instance_count>40,"Collection stock must be present")
	for index in range(batch.multimesh.instance_count):
		var base:Vector3=batch.global_transform*batch.multimesh.get_instance_transform(index).origin
		var support:=ship.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(base+Vector3.UP*.02,base-Vector3.UP*.03))
		assert(not support.is_empty() and absf(support.position.y-base.y)<.012,"Each book group must rest on a real shelf")
	actor.set_physics_process(false)
	actor.position=Vector3(-50,78.1,0)
	actor.velocity=Vector3.ZERO
	var route:Array[Vector2]=[Vector2(-60,0),Vector2(-77,-8),Vector2(-87,-15),Vector2(-94.5,-15),Vector2(-94.5,-9.4),Vector2(-94.5,-.5),Vector2(-91,-.5),Vector2(-91,-9.5),Vector2(-85,-11.5),Vector2(-79,-11.5),Vector2(-72.2,-6),Vector2(-63,0),Vector2(-72.2,0),Vector2(-72.2,12.5),Vector2(-69,12.5),Vector2(-69,5),Vector2(-65.5,5),Vector2(-65.5,12.5),Vector2(-83,12.5),Vector2(-72.2,12.5),Vector2(-72.2,0),Vector2(-63,0),Vector2(-72.2,0),Vector2(-72.2,-10.2),Vector2(-70,-10.2)]
	for i in range(route.size()):
		await walk(actor,route[i])
		if i==7:assert(absf(actor.position.y-84)<.12,"First library stair reaches D13")
		if i==17:assert(absf(actor.position.y-88.5)<.12,"Second library stair reaches D14")
	assert(absf(actor.position.y-88.5)<.12)
	route.reverse()
	for p in route:await walk(actor,p)
	await walk(actor,Vector2(-50,0))
	assert(absf(actor.position.y-78)<.12,"Both actual stairs return to the lower library")
	for point in [Vector2(-60,0),Vector2(-77,-8),Vector2(-87,-15),Vector2(-89.5,-21.5),Vector2(-87,-25.3),Vector2(-83,-25.3),Vector2(-79,-24),Vector2(-79,-18),Vector2(-87,-15)]:await walk(actor,point)
	print("STAR ATLAS PASS: actual bidirectional three-level walking circuit, ten light exits, protected D15 cap, sealed D12 lift pan, three distinct controls, supported local book stock and first collection study approaches. Loaded lift, detailed guards, wider furnishing and final art require separate checks.")
	main.queue_free()
	await process_frame
	quit()
