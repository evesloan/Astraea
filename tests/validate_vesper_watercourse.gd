extends "res://tests/validate_living_gifts.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var feature:Node3D=ship.find_child("VesperWatercourse_WIP",true,false)
	assert(feature.get_meta("programme_key")=="D10_directory_08")
	var space:=ship.get_world_3d().direct_space_state
	var own:Array[RID]=[]
	for body in feature.find_children("*","StaticBody3D",true,false):own.append(body.get_rid())
	for i in range(5):
		var marker:=feature.find_child("DATUM_supported_base_"+str(i),true,false)as Node3D
		for j in range(16):
			var p:Vector3=marker.global_position+Vector3(cos(TAU*j/16)*.28,0,sin(TAU*j/16)*.28)
			var ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.04,p-Vector3.UP*.1)
			ray.exclude=own
			var hit:=space.intersect_ray(ray)
			assert(not hit.is_empty() and absf(hit.position.y-61)<.015,"Watercourse support leaves the original D10 slab")
	var crossing:=feature.find_child("DATUM_spillway_guard_crossing",true,false)as Node3D
	var underside:=crossing.global_position.y-.06
	var guard_ray:=PhysicsRayQueryParameters3D.create(Vector3(crossing.global_position.x,underside-.005,215),Vector3(crossing.global_position.x,62,215))
	guard_ray.exclude=own
	var guard_hit:=space.intersect_ray(guard_ray)
	assert(not guard_hit.is_empty() and "AquaticAuthoredBalconyEdges" in str(guard_hit.collider.get_path()),"Original guard remains under the spillway")
	assert(underside-guard_hit.position.y>.035,"Spillway underside must clear the unchanged rail")
	var stream_shape:=BoxShape3D.new()
	var drops:Array[float]=[]
	for i in range(61):drops.append(18.5*i/60.0)
	for i in range(51):drops.append(i*.01)
	for drop in drops:
		var t:float=drop/18.5
		stream_shape.size=Vector3(.04,.04,.65+.15*t)
		var q:=PhysicsShapeQueryParameters3D.new()
		q.shape=stream_shape
		q.transform=Transform3D(Basis.IDENTITY,Vector3(25+.12*sin(minf(drop/.12,1)*PI/2),62.36-drop,215))
		var hits:=space.intersect_shape(q)
		for hit in hits:print("FALL INTERSECTION:",t," ",hit.collider.get_path())
		assert(hits.is_empty(),"Water curtain must pass through real openings without clipping architecture or return spine")
	var receiver:=feature.find_child("DATUM_receiver_floor",true,false)as Node3D
	var receiver_ray:=PhysicsRayQueryParameters3D.create(receiver.global_position+Vector3.UP*.04,receiver.global_position-Vector3.UP*.1)
	receiver_ray.exclude=own
	var receiver_hit:=space.intersect_ray(receiver_ray)
	assert(not receiver_hit.is_empty() and absf(receiver_hit.position.y-42.8)<.015,"Receiver uses the retained basin bottom")
	for i in range(3):
		var source:=feature.find_child("WatercourseSource_"+str(i),true,false)as Node3D
		var exit_ray:=PhysicsRayQueryParameters3D.create(source.global_position,source.global_position+(Vector3.DOWN if i<2 else Vector3.UP)*.04)
		assert(space.intersect_ray(exit_ray).is_empty(),"Watercourse fixture exit is obstructed")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	for i in range(61):
		for yaw in [0.0,PI]:driver_pose(ship,cart,Vector3(18,61.03,202+i*.3),yaw,excluded)
	actor.set_physics_process(false)
	actor.position=Vector3(18,61.1,202)
	actor.velocity=Vector3.ZERO
	for target in [Vector2(18,220),Vector2(20.5,220),Vector2(22,223),Vector2(22,234),Vector2(20,245)]:await walk(actor,target)
	assert(absf(actor.position.y-61)<.12)
	print("VESPER WATERCOURSE PASS:80 upper support probes,112 curtain-clearance samples, original guard and basin retained,3 clear fixture exits,",samples,"cart/driver poses and actual west passage. Flow is visual animation; pumping, splash/acoustic simulation and swimming remain unimplemented.")
	main.queue_free()
	await process_frame
	quit()
