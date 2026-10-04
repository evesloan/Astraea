extends "res://tests/validate_living_gifts.gd"
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var room:Node3D=ship.find_child("D10_VesperDining_FirstGroups_WIP",true,false)
	assert(room.get_meta("programme_key")=="D10_directory_08" and room.get_meta("fitted_seats")==240)
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	for center in [Vector2(43,245),Vector2(43,231),Vector2(46.8,231),Vector2(46.8,198),Vector2(46.8,192.6)]:
		for i in range(40):driver_pose(ship,cart,Vector3(center.x,61.03,center.y),TAU*i/40,excluded)
	var route:Array[Vector2]=[Vector2(20,245),Vector2(43,245),Vector2(43,231),Vector2(46.8,231),Vector2(46.8,198),Vector2(46.8,192.6)]
	for segment in range(route.size()-1):
		var a:Vector2=route[segment]
		var b:Vector2=route[segment+1]
		var delta:Vector2=b-a
		var yaw:float=atan2(-delta.x,-delta.y)
		var count:int=ceili(delta.length()/.25)
		for i in range(count+1):
			var p:Vector2=a.lerp(b,float(i)/count)
			driver_pose(ship,cart,Vector3(p.x,61.03,p.y),yaw,excluded)
	for table in room.find_children("VesperTable_*","Node3D",false,false):
		var top_ray:=PhysicsRayQueryParameters3D.create(table.global_position+Vector3.UP*.9,table.global_position+Vector3.UP*.75)
		var top_hit:=ship.get_world_3d().direct_space_state.intersect_ray(top_ray)
		assert(not top_hit.is_empty() and "InsetStoneTop" in str(top_hit.collider.get_path()),"Recessed tabletop must remain exposed, not hidden under a wooden cap")
	var ids:Dictionary={}
	var chairs:=room.find_children("VesperChair_*","Node3D",false,false)
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
	actor.position=Vector3(20,61.1,245)
	actor.velocity=Vector3.ZERO
	for target in route:await walk(actor,target)
	assert(absf(actor.position.y-61)<.12)
	print("VESPER SUBSET PASS:",samples,"compound cart/load and driver poses,240 unique chair contacts/supports and clear side/rear standing positions and actual service/gallery walking. Occupied guest access, service simulation and final art remain pending.")
	main.queue_free()
	await process_frame
	quit()
