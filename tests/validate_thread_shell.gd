extends "res://tests/validate_living_gifts.gd"
func animate_clear(ship:Node3D,door:Node3D) -> void:
	for frame in range(100):
		await physics_frame
		for leaf in door.leaves:
			for collider in leaf.get_children():
				if not collider is CollisionShape3D:continue
				var q:=PhysicsShapeQueryParameters3D.new()
				q.shape=collider.shape
				q.transform=collider.global_transform
				q.margin=.001
				q.exclude=[leaf.get_rid()]
				for hit in ship.get_world_3d().direct_space_state.intersect_shape(q,64):
					assert(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Tailor door clips fixed geometry: %s fraction %.3f / %s"%[door.name,door.open_fraction,hit.collider.get_path()])
func press_door(actor:CharacterBody3D,door:Node3D,marker:Node3D) -> void:
	actor.set_physics_process(true)
	actor.velocity=Vector3.ZERO
	actor.camera.look_at(marker.global_position,Vector3.UP)
	assert(actor.target_from_view()==door,"Tailor call plate must be precisely selectable")
	var focus:=InputEventMouseButton.new()
	focus.button_index=MOUSE_BUTTON_RIGHT
	focus.pressed=true
	Input.parse_input_event(focus.duplicate())
	var event:=InputEventKey.new()
	event.keycode=KEY_E
	event.physical_keycode=KEY_E
	event.pressed=true
	Input.parse_input_event(event.duplicate())
	Input.flush_buffered_events()
	for frame in range(3):await physics_frame
	event.pressed=false
	Input.parse_input_event(event.duplicate())
	focus.pressed=false
	Input.parse_input_event(focus.duplicate())
	Input.flush_buffered_events()
	actor.set_physics_process(false)
func run() -> void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate()
	root.add_child(main)
	for frame in range(60):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var shop:Node3D=ship.find_child("D09_ThreadAndShell_WIP",true,false)
	assert(shop.get_meta("programme_key")=="D09_directory_04" and shop.get_meta("historical_room_id")=="D09_tailor3")
	var architecture:Node3D=shop.find_child("ThreadShellArchitecture",true,false)
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var cart:RigidBody3D=ship.find_child("CustodialCart",true,false)
	for marker in architecture.find_children("DATUM_light_*","Node3D",true,false):
		var q:=PhysicsRayQueryParameters3D.create(marker.global_position,marker.global_position+Vector3.DOWN*.07)
		assert(ship.get_world_3d().direct_space_state.intersect_ray(q).is_empty(),"Tailor fixture exit blocked: "+str(marker.name))
	for i in range(10):
		var stock:Node3D=shop.find_child("ThreadShellTextile_"+str(i),true,false)
		var marker:Node3D=stock.find_child("DATUM_hanging_contact",true,false)
		var q:=PhysicsRayQueryParameters3D.create(marker.global_position+Vector3.UP*.02,marker.global_position-Vector3.UP*.02)
		var omit:Array[RID]=[]
		for body in stock.find_children("*","StaticBody3D",true,false):omit.append(body.get_rid())
		q.exclude=omit
		var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q)
		assert(not hit.is_empty() and "TAIL_DisplayRail_" in str(hit.collider.get_path()),"Textile sample %s needs support from actual rail at %s; hit %s"%[i,marker.global_position,hit])
	actor.set_physics_process(false)
	actor.position=Vector3(0,52.6,-216)
	actor.velocity=Vector3.ZERO
	for target in [Vector2(6,-216),Vector2(17,-216),Vector2(24,-220)]:await walk(actor,target)
	for i in range(2):
		var z:float=-225.5 if i==0 else -209.5
		var door:Node3D=shop.find_child("D09_tailor3_fitting_%02d_Door"%(i+1),true,false)
		assert(door.open_fraction<.001 and is_equal_approx(door.leaf_width,1.18))
		for dz in [-.8,0.0,.8]:
			var q:=PhysicsRayQueryParameters3D.create(Vector3(27,53.6,z+dz),Vector3(34,53.6,z+dz))
			var hit:=ship.get_world_3d().direct_space_state.intersect_ray(q)
			assert(not hit.is_empty() and str(door.name) in str(hit.collider.get_path()),"Closed fitting door must screen its occupied bay")
		await walk(actor,Vector2(24,z))
		await walk(actor,Vector2(27,z))
		var plate:=door.find_child("DATUM_call_button",true,false)as Node3D
		await walk(actor,Vector2(27,plate.global_position.z))
		await press_door(actor,door,plate)
		await animate_clear(ship,door)
		assert(door.open_fraction>.999)
		await walk(actor,Vector2(27,z))
		await walk(actor,Vector2(30.5,z))
		await walk(actor,Vector2(34.8,z))
		await walk(actor,Vector2(30.5,z))
		var inside:=door.find_child("DATUM_call_button_inside",true,false)as Node3D
		await walk(actor,Vector2(30.5,inside.global_position.z))
		await press_door(actor,door,inside)
		await animate_clear(ship,door)
		assert(door.open_fraction<.001)
		await press_door(actor,door,inside)
		await animate_clear(ship,door)
		await walk(actor,Vector2(30.5,z))
		await walk(actor,Vector2(27,z))
		await walk(actor,Vector2(24,z))
	await walk(actor,Vector2(24,-215.5))
	await walk(actor,Vector2(28,-215.5))
	await walk(actor,Vector2(35,-215.5))
	var service:Node3D=shop.find_child("ThreadShell_service_door",true,false)
	service.interact(actor)
	await animate_clear(ship,service)
	await walk(actor,Vector2(40,-215.5))
	await walk(actor,Vector2(40,-194.5))
	await walk(actor,Vector2(8,-194.5))
	var exit_door:Node3D=shop.find_child("ThreadShell_staff_entry_door",true,false)
	exit_door.interact(actor)
	await animate_clear(ship,exit_door)
	await walk(actor,Vector2(0,-194.5))
	assert(abs(actor.position.y-52.5)<.12)
	var excluded:Array[RID]=[]
	for body in ship.find_children("*","CollisionObject3D",true,false):
		if not body is StaticBody3D or body is AnimatableBody3D:excluded.append(body.get_rid())
	for i in range(117):driver_pose(ship,cart,Vector3(6,52.53,-230+i*.25),0,excluded)
	for i in range(40):driver_pose(ship,cart,Vector3(6,52.53,-216),TAU*i/40,excluded)
	print("THREAD SHELL PASS: actual promenade/shop/two private fitting bays/staff return walk; wide-door outside/inside RMB/E, closed privacy rays and800motion frames;9 fixture exits,10 hanger supports and",samples,"cart/operator poses. Sales, guest use, full species fit, physical shop cart-driving and final art pending.")
	main.queue_free()
	await process_frame
	quit()
