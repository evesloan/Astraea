extends "res://tests/validate_crown_access.gd"
func run()->void:
	var main:Node=(load("res://scenes/main.tscn")as PackedScene).instantiate();root.add_child(main)
	for frame in range(90):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var central:Node3D=ship.find_child("CentralCommandCrown_WIP",true,false)
	var aft:Node3D=ship.find_child("AftCommandCrown_WIP",true,false)
	assert(central!=null and aft!=null)
	var old_data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CENTRAL_CROWN_RUNTIME.json"))
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_COMMAND_RUNTIME.json"))
	assert(data.programmes.size()==2 and data.doors.size()==4)
	var doors:Array[Node3D]=[]
	for entry in old_data.doors:
		if float(entry.position[2])>58:doors.append(central.get_node("CrownDoor_"+str(entry.name)))
	for entry in data.doors:doors.append(aft.get_node("AftCommandDoor_"+str(entry.name)))
	assert(doors.size()==6,"Two former endcaps plus four aft doors")
	var identities:Dictionary={}
	for door in doors:
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
		print("AFT COMMAND DOOR PASS:",door.name)
	actor.set_physics_process(false);actor.position=Vector3(0,106.6,63);actor.velocity=Vector3.ZERO
	for door in doors:door.interact(actor)
	for frame in range(110):await physics_frame
	# The replacement public street is walked end-to-end before using either controlled branch.
	await walk_route(actor,[Vector2(45,63),Vector2(-45,63),Vector2(-7.5,63),Vector2(-7.5,57),Vector2(-7.5,63),Vector2(-7.5,82),Vector2(-23,82),Vector2(-7.5,82),Vector2(-7.5,63),Vector2(7.5,63),Vector2(7.5,57),Vector2(7.5,63),Vector2(7.5,82),Vector2(23,82),Vector2(7.5,82),Vector2(7.5,63),Vector2(0,63),Vector2(0,108),Vector2(5.5,108),Vector2(5.5,137),Vector2(0,137)])
	assert(absf(actor.position.y-106.5)<.12,"Aft room circuit reaches existing crown lift link on real floor")
	print("AFT COMMAND ACCESS PASS: six precisely focused doors, full moving-leaf sweeps and entry/return; continuous public cross-street, both former endcaps, both new rooms and existing aft lift approach. Equipment, staff permissions and final art remain unfinished.")
	main.queue_free();await process_frame;quit()
