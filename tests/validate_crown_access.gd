extends "res://tests/validate_living_gifts.gd"
func key(code:Key,pressed:bool)->void:
	var event:=InputEventKey.new();event.keycode=code;event.physical_keycode=code;event.pressed=pressed
	Input.parse_input_event(event);Input.flush_buffered_events()
func focus(pressed:bool)->void:
	var event:=InputEventMouseButton.new();event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=pressed
	Input.parse_input_event(event);Input.flush_buffered_events()
func assert_door_clear(ship:Node3D,door:Node3D)->void:
	for leaf in door.leaves:
		for contact in leaf.get_children():
			if not contact is CollisionShape3D:continue
			var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.margin=.001;q.exclude=[leaf.get_rid()]
			for hit in ship.get_world_3d().direct_space_state.intersect_shape(q,64):
				assert(not(hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D),"Crown door moving leaf clips %s: %s"%[door.name,hit.collider.get_path()])
func walk_route(actor:CharacterBody3D,points:Array)->void:
	for target:Vector2 in points:
		var start:=Vector2(actor.position.x,actor.position.z)
		var n:=maxi(1,ceili(start.distance_to(target)/24.0))
		for i in range(1,n+1):await walk(actor,start.lerp(target,float(i)/n))
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var crown:Node3D=ship.find_child("CentralCommandCrown_WIP",true,false)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CENTRAL_CROWN_RUNTIME.json"))
	assert(crown!=null and data.programmes.size()==6 and data.doors.size()==10)
	var identities:Dictionary={}
	for entry in data.doors:
		var door:Node3D=crown.get_node("CrownDoor_"+str(entry.name))
		assert(not identities.has(door.persistent_id));identities[door.persistent_id]=true
		var front:Vector3=door.global_basis.z
		actor.set_physics_process(true);actor.global_position=door.global_position+front*2.2+Vector3.UP*.1;actor.velocity=Vector3.ZERO
		for frame in range(20):await physics_frame
		var aim:Vector3=door.global_position+Vector3.UP*1.3-actor.camera.global_position
		actor.rotation.y=atan2(-aim.x,-aim.z);actor.pitch=atan2(aim.y,Vector2(aim.x,aim.z).length());actor.camera.rotation.x=actor.pitch
		assert(actor.target_from_view()==door,"Crown door is a precise physical interaction target: "+str(door.name))
		key(KEY_E,true)
		for frame in range(3):await physics_frame
		assert(not door.desired_open,"Unfocused E cannot operate crown doors")
		key(KEY_E,false);focus(true);key(KEY_E,true)
		for frame in range(3):await physics_frame
		assert(door.desired_open,"Focused E must open the selected crown door")
		key(KEY_E,false);focus(false)
		for frame in range(100):await physics_frame;assert_door_clear(ship,door)
		assert(door.open_fraction>.999)
		actor.set_physics_process(false)
		var inside:Vector3=door.global_position-front*2.2
		await walk_route(actor,[Vector2(inside.x,inside.z)])
		assert(absf(actor.position.y-106.5)<.12)
		var outside:Vector3=door.global_position+front*2.2
		await walk_route(actor,[Vector2(outside.x,outside.z)])
		door.interact(actor)
		for frame in range(100):await physics_frame;assert_door_clear(ship,door)
		assert(door.open_fraction<.001)
		print("CROWN DOOR PASS:",door.name)
	# Open through the existing controller, then walk one continuous destination circuit.
	actor.position=Vector3(5.5,106.6,-82);actor.velocity=Vector3.ZERO
	for entry in data.doors:
		var door:Node3D=crown.get_node("CrownDoor_"+str(entry.name));door.interact(actor)
	for frame in range(110):await physics_frame
	await walk_route(actor,[Vector2(5.5,-77),Vector2(45,-77),Vector2(45,72),Vector2(0,72),Vector2(0,-77),Vector2(-8,-77),Vector2(-8,-71)])
	for z in [-52.0,-4.0,40.0]:
		await walk_route(actor,[Vector2(-8,z),Vector2(-23,z),Vector2(-8,z)])
	await walk_route(actor,[Vector2(-8,16),Vector2(0,16),Vector2(0,30),Vector2(8,30)])
	for z in [-52.0,0.0,46.0]:
		await walk_route(actor,[Vector2(8,z),Vector2(23,z),Vector2(8,z)])
	await walk_route(actor,[Vector2(8,30),Vector2(0,30),Vector2(0,108),Vector2(5.5,108),Vector2(5.5,137),Vector2(0,137)])
	assert(absf(actor.position.y-106.5)<.12,"Destination circuit must reach the existing aft crown link at the same datum")
	assert(ship.express_arrive(17),"Temporary D18 directory arrival remains safe on the new fore cross-street")
	print("CROWN ACCESS PASS: ten precisely targeted RMB/E doors with full opening/closing collision sweeps and capsule entry/return; continuous walk visits all six programme shells, revised fore street and both existing core approaches. Equipment, role-based access, species fit and final appearance remain unfinished.")
	main.queue_free();await process_frame;quit()
