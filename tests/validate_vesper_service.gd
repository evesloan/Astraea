extends "res://tests/validate_living_gifts.gd"
func assert_clear(world:Node3D,door:Node3D) -> void:
	for leaf in door.leaves:
		for shape in leaf.get_children():
			if not shape is CollisionShape3D:continue
			var q:=PhysicsShapeQueryParameters3D.new()
			q.shape=shape.shape
			q.transform=shape.global_transform
			q.margin=.001
			q.exclude=[leaf.get_rid()]
			for hit in world.get_world_3d().direct_space_state.intersect_shape(q,64):
				assert(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Vesper door clips fixed fitting: %s at %.3f"%[hit.collider.get_path(),door.open_fraction])
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var room:Node3D=ship.find_child("D10_VesperFinishingService_WIP",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var door:Node3D=room.get_node("VesperServiceDoor")
	assert(room.get_meta("programme_key")=="D10_directory_08" and door.persistent_id==&"D10_banquet7_service_door")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:
			if not door.is_ancestor_of(body):excluded.append(body.get_rid())
	for i in range(40):driver_pose(ship,cart,Vector3(46.2,61.03,237),TAU*i/40,excluded)
	for i in range(33):driver_pose(ship,cart,Vector3(46.2+i*.15,61.03,237),-PI/2,excluded)
	for i in range(2):
		var source:=room.get_node("VesperFinishingTaskLight_"+str(i))as Node3D
		var ray:=PhysicsRayQueryParameters3D.create(source.global_position,source.global_position+Vector3.DOWN*.06)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty())
		var counter:=room.get_node("VesperFinishingCounter_"+str(i))as Node3D
		var center:Vector3=counter.global_transform*Vector3(.6,.94,0) # Uncovered worktop; the center now holds verified plate stock.
		var top_ray:=PhysicsRayQueryParameters3D.create(center,center+Vector3.DOWN*.12)
		var top:=ship.get_world_3d().direct_space_state.intersect_ray(top_ray)
		assert(not top.is_empty() and counter.is_ancestor_of(top.collider),"Finishing surface lacks a real counter contact")
	for i in range(2):
		var stack:=room.get_node("VesperStaticPlateStack_"+str(i))as Node3D
		var omit:Array[RID]=[]
		for body in stack.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		for j in range(8):
			var p:Vector3=stack.global_position+Vector3(cos(TAU*j/8)*.16,0,sin(TAU*j/8)*.16)
			var support_ray:=PhysicsRayQueryParameters3D.create(p+Vector3.UP*.03,p-Vector3.UP*.03)
			support_ray.exclude=omit
			var support:=ship.get_world_3d().direct_space_state.intersect_ray(support_ray)
			assert(not support.is_empty() and absf(support.position.y-p.y)<.01,"Clean plate stock must be supported on its actual work surface")
	# Empty close and precise RMB/E reopen use the existing shared controller.
	door.interact(actor)
	for frame in range(100):
		await physics_frame
		assert_clear(ship,door)
	assert(door.open_fraction<.001)
	assert(ship.arrive_at(Vector3(46.2,61.1,237),-PI/2))
	for frame in range(15):await physics_frame
	assert(actor.target_from_view()==door,"Camera ray selects this actual finishing-bay door")
	var focus:=InputEventMouseButton.new()
	focus.button_index=MOUSE_BUTTON_RIGHT
	focus.pressed=true
	Input.parse_input_event(focus)
	var press:=InputEventKey.new()
	press.keycode=KEY_E
	press.physical_keycode=KEY_E
	press.pressed=true
	Input.parse_input_event(press)
	for frame in range(100):
		await physics_frame
		assert_clear(ship,door)
	assert(door.open_fraction>.999)
	press.pressed=false
	Input.parse_input_event(press)
	focus.pressed=false
	Input.parse_input_event(focus)
	# The delivery driver is in the closing sweep: maintain the fully-open state.
	assert(ship.arrive_at(Vector3(49.38,61.1,237),-PI/2))
	for frame in range(15):await physics_frame
	door.interact(actor)
	assert(door.obstructed and door.desired_open,"Occupied delivery sweep must keep both leaves open")
	for frame in range(30):await physics_frame
	assert(door.open_fraction>.999)
	actor.set_physics_process(false)
	for target in [Vector2(51,237),Vector2(51,234.8),Vector2(51.25,239.85),Vector2(51,237),Vector2(46.2,237)]:await walk(actor,target)
	assert(absf(actor.position.y-61)<.12)
	print("VESPER SERVICE PASS:",samples,"cart/load and driver poses including open leaves,200 moving-door samples,RMB/E target and occupied-sweep interlock,2 counter contacts,2 source exits and actual staff walking. Food workflows,stock interaction and full240-cover capacity remain pending.")
	main.queue_free()
	await process_frame
	quit()
