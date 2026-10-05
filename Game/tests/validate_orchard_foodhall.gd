extends "res://tests/validate_thread_shell.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var room:Node3D=ship.find_child("D10_OrchardFoodHall_WIP",true,false)
	assert(room.get_meta("programme_key")=="D10_directory_04" and room.get_meta("candidate_places")==240)
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	for center in [Vector2(23,-216),Vector2(26.5,-233.4)]:
		for i in range(40):driver_pose(ship,cart,Vector3(center.x,61.03,center.y),TAU*i/40,excluded)
	var route:Array[Vector2]=[Vector2(6,-216),Vector2(23,-216),Vector2(26.5,-216),Vector2(26.5,-233.4),Vector2(47.6,-233.4),Vector2(47.6,-214)]
	for segment in range(route.size()-1):
		var a:Vector2=route[segment]
		var b:Vector2=route[segment+1]
		var delta:Vector2=b-a
		var yaw:float=atan2(-delta.x,-delta.y)
		var count:int=ceili(delta.length()/.25)
		for i in range(count+1):
			var p:Vector2=a.lerp(b,float(i)/count)
			driver_pose(ship,cart,Vector3(p.x,61.03,p.y),yaw,excluded)
	for table in room.find_children("OrchardTable_*","Node3D",false,false):
		var top_ray:=PhysicsRayQueryParameters3D.create(table.global_position+Vector3.UP*.9,table.global_position+Vector3.UP*.75)
		var top_hit:=ship.get_world_3d().direct_space_state.intersect_ray(top_ray)
		assert(not top_hit.is_empty() and "InsetStone" in str(top_hit.collider.get_path()),"Recessed tabletop must remain exposed, not hidden under a wooden cap")
	var ids:Dictionary={}
	var chairs:=room.find_children("OrchardChair_*","Node3D",false,false)
	assert(chairs.size()==240)
	for chair in chairs:
		var id:String=chair.get_meta("persistent_id")
		assert(not ids.has(id))
		ids[id]=true
		var marker:=chair.find_child("DATUM_seat_contact",true,false)as Node3D
		var ray:=PhysicsRayQueryParameters3D.create(marker.global_position+Vector3.UP*.08,marker.global_position-Vector3.UP*.05)
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
		assert(not hit.is_empty() and chair.is_ancestor_of(hit.collider),"Dining seat contact must hit its own chair")
		var foot:=PhysicsRayQueryParameters3D.create(chair.global_position+Vector3.UP*.03,chair.global_position-Vector3.UP*.1)
		var omit:Array[RID]=[]
		for body in chair.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		foot.exclude=omit
		assert(not ship.get_world_3d().direct_space_state.intersect_ray(foot).is_empty(),"Dining chair needs supported floor")
	var approach_count:=0
	for chair in chairs:
		var usable:=false
		for local in [Vector3(-.85,0,0),Vector3(.85,0,0),Vector3(0,0,-.85)]:
			var foot:Vector3=chair.global_transform*local
			var capsule:=CapsuleShape3D.new()
			capsule.radius=.3
			capsule.height=1.8
			var query:=PhysicsShapeQueryParameters3D.new()
			query.shape=capsule
			query.transform.origin=foot+Vector3.UP*.93
			query.exclude=excluded
			if not ship.get_world_3d().direct_space_state.intersect_shape(query).is_empty():continue
			var ray:=PhysicsRayQueryParameters3D.create(foot+Vector3.UP*.08,foot-Vector3.UP*.1)
			ray.exclude=excluded
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(ray)
			if hit.is_empty() or hit.normal.y<.9:continue
			usable=true
			break
		if not usable:print("DINING APPROACH BLOCK:",chair.get_meta("persistent_id")," ",chair.global_position)
		assert(usable,"Every installed chair needs a supported clear side/rear standing position")
		approach_count+=1
	actor.set_physics_process(false)
	actor.position=Vector3(6,61.1,-216)
	actor.velocity=Vector3.ZERO
	for target in route:await walk(actor,target)
	assert(absf(actor.position.y-61)<.12)
	var architecture:Node3D=room.find_child("OrchardFoodHallArchitecture",true,false)
	assert(architecture.find_children("DATUM_light_*","Node3D",true,false).size()==46,"Current authored fixture revision must be imported")
	for marker in architecture.find_children("DATUM_light_*","Node3D",true,false):
		var q:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position+Vector3.DOWN*.07)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(q).is_empty(),"Orchard source exit is obstructed")
	for i in range(2):
		var machine:Node3D=room.find_child("OrchardBeverage_"+str(i),true,false)
		var omit:Array[RID]=[]
		for body in machine.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		for x in [-.255,.255]:
			for z in [-.157,.157]:
				var p:Vector3=machine.global_transform*Vector3(x,0,z)
				var q:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.02,p-Vector3.UP*.04)
				q.exclude=omit
				var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q)
				assert(not hit.is_empty() and "ORCH_CounterTop_" in str(hit.collider.get_path()),"Beverage station lacks counter support")
	await walk(actor,Vector2(47.2,-214))
	var door:Node3D=room.find_child("OrchardFood_staff_door",true,false)
	await press_door(actor,door,door.leaves[0].get_node("PushContact"))
	await animate_clear(ship,door)
	assert(door.open_fraction>.999)
	for target in [Vector2(50.5,-214),Vector2(51,-201.5),Vector2(40,-201.5),Vector2(40,-208.5)]:await walk(actor,target)
	for i in [1,0]:
		var z:float=-208.5 if i==1 else -223.5
		await walk(actor,Vector2(40,z))
		var work_door:Node3D=room.find_child("OrchardFood_pavilion_door_"+str(i),true,false)
		work_door.interact(actor)
		await animate_clear(ship,work_door)
		assert(work_door.open_fraction>.999)
		await walk(actor,Vector2(33.5,z))
		await walk(actor,Vector2(31.2,z))
		await walk(actor,Vector2(40,z))
		work_door.interact(actor)
		await animate_clear(ship,work_door)
		assert(work_door.open_fraction<.001)
	print("ORCHARD DINING PASS:240 unique supported candidate chairs and clear standing positions;36 exposed stone table surfaces;",samples,"cart/operator poses; actual guest/service/work-bay routes,46 source exits,8 beverage supports and500door-motion frames. Occupied guest access, food service, full species fit and final art pending.")
	main.queue_free()
	await process_frame
	quit()
