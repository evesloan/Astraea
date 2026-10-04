extends "res://tests/validate_living_gifts.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var architecture:Node3D=ship.find_child("VesperMezzanineArchitecture",true,false)
	assert(architecture!=null)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	actor.set_physics_process(false)
	actor.position=Vector3(9.8,61.1,204.9)
	actor.velocity=Vector3.ZERO
	for target in [Vector2(17.6,204.9),Vector2(17.6,196),Vector2(18.25,192)]:await walk(actor,target)
	assert(absf(actor.position.y-64.5)<.12,"Upper stair must reach the authored mezzanine")
	for target in [Vector2(17.6,196),Vector2(17.6,204.9),Vector2(9.8,204.9)]:await walk(actor,target)
	assert(absf(actor.position.y-61)<.12,"Return stair must reach original D10")
	actor.position=Vector3(18,61.1,208)
	actor.velocity=Vector3.ZERO
	await walk(actor,Vector2(18,200.8))
	assert(absf(actor.position.y-61)<.12,"Lower passage must remain usable beneath upper corridor")
	var lift:Node3D=ship.find_child("VesperDiningLift",true,false)
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var excluded:Array[RID]=[cart.get_rid(),actor.get_rid()]
	for product in cart.products:excluded.append(product.get_rid())
	for stop in [0,1]:
		actor.position=Vector3(9.8,61.1,208)
		actor.velocity=Vector3.ZERO
		lift.request_floor(stop)
		for frame in range(800):
			await physics_frame
			if lift.phase=="idle" and lift.current_floor==stop:break
		assert(lift.phase=="idle" and lift.current_floor==stop)
		var y:float=lift.floor_heights[stop]
		for index in range(40):driver_pose(ship,cart,Vector3(18.25,y+.03,192),TAU*index/40,excluded)
		for index in range(47):driver_pose(ship,cart,Vector3(18.25+.1*index,y+.03,192),-PI/2,excluded)
		actor.position=Vector3(18.25,y+.1,192)
		actor.velocity=Vector3.ZERO
		await walk(actor,Vector2(22.6,192))
		await walk(actor,Vector2(18.25,192))
		assert(absf(actor.position.y-y)<.12)
	for target in [Vector2(18.25,196),Vector2(25.6,196),Vector2(25.6,186.8),Vector2(48.2,186.8),Vector2(48.2,192.6),Vector2(25.6,192.6),Vector2(25.6,196),Vector2(18.25,196)]:await walk(actor,target)
	assert(absf(actor.position.y-64.5)<.12,"Upper dining circuit must retain its floor")
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D10_vesper_mezzanine.json"))
	var boundary:Array=definition.rail_boundary
	var guard_samples:=0
	for edge in range(boundary.size()):
		var a:=Vector2(boundary[edge][0],boundary[edge][1])
		var b:=Vector2(boundary[(edge+1)%boundary.size()][0],boundary[(edge+1)%boundary.size()][1])
		var normal:=Vector2(-(b-a).y,(b-a).x).normalized()
		for t in [.25,.5,.75]:
			var point:Vector2=a.lerp(b,t)
			if absf(point.x-16.51)<.02 and point.y>203.58 and point.y<206.42:continue
			if absf(point.x-20.21)<.02 and point.y>190.8 and point.y<193.2:continue
			var start:=Vector3(point.x+normal.x*.35,65.1,point.y+normal.y*.35)
			var end:=Vector3(point.x-normal.x*.35,65.1,point.y-normal.y*.35)
			var ray:=PhysicsRayQueryParameters3D.create(start,end)
			ray.hit_back_faces=true
			ray.exclude=[lift.cabin.get_rid()]
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
			assert(not hit.is_empty() and ("MEZ_GuardGlass" in str(hit.collider.get_path()) or "MEZ_LiftShaft" in str(hit.collider.get_path()) or "LandingGate_D10M/AST-DOR-003/LIFT_fixed" in str(hit.collider.get_path())),"Missing upper edge protection near %s; first contact %s"%[point,"none" if hit.is_empty() else hit.collider.get_path()])
			guard_samples+=1
	print("UPPER GUARD CONTACTS:",guard_samples)
	for i in range(8):
		var light:Node3D=ship.find_child("VesperMezzanineTaskLight_"+str(i),true,false)
		var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.05)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"New fixture must emit outside its housing")
	print("VESPER MEZZANINE PASS: actual stair up/return, lower passage walking and eight fixture exits. Both-stop player boarding/exit and 174 compound cart/driver staging-entry poses pass. Upper pedestrian circuit and fixed perimeter containment also checked. Driven cart boarding, occupied seat access and visual acceptance remain pending.")
	main.queue_free()
	await process_frame
	quit()
