extends "res://tests/validate_living_gifts.gd"
var measured_walk_frames := 0
var measured_walk_distance := 0.0
var measured_max_step := 0.0
var measured_support_hits := 0
var measured_compiled_support_hits := 0
var measured_missing_support := 0
var measured_support_owners:Dictionary={}
var measured_support_exceptions:Array=[]
var measured_phase := "door_scenarios"
var measured_phases:Dictionary={}
var measured_floors:Node
func record_walk_step(actor:CharacterBody3D,before:Vector3)->void:
	var distance:=before.distance_to(actor.position)
	measured_walk_frames+=1;measured_walk_distance+=distance;measured_max_step=maxf(measured_max_step,distance)
	if not measured_phases.has(measured_phase):measured_phases[measured_phase]={"frames":0,"distance_m":0.0}
	measured_phases[measured_phase].frames+=1;measured_phases[measured_phase].distance_m+=distance
	var query:=PhysicsRayQueryParameters3D.create(actor.global_position+Vector3.UP*.12,actor.global_position-Vector3.UP*.25)
	query.exclude=[actor.get_rid()]
	var hit:=actor.get_world_3d().direct_space_state.intersect_ray(query)
	if hit.is_empty():
		measured_missing_support+=1
		if measured_support_exceptions.size()<20:measured_support_exceptions.append({"frame":measured_walk_frames,"position":[actor.position.x,actor.position.y,actor.position.z]})
	else:
		measured_support_hits+=1
		if measured_floors.is_ancestor_of(hit.collider):measured_compiled_support_hits+=1
		var owner:Node=hit.collider
		while owner!=null and not owner.has_meta("region_id"):owner=owner.get_parent()
		var key:=str(owner.get_meta("region_id")) if owner!=null else str(hit.collider.get_path())
		measured_support_owners[key]=int(measured_support_owners.get(key,0))+1
	if measured_walk_frames%300==0:write_walk_receipt("running")
func write_walk_receipt(status:String)->void:
	var f:=FileAccess.open("res://artifacts/crown_connected_access002.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"status":status,"walk_frames":measured_walk_frames,"actual_walk_distance_m":measured_walk_distance,"max_single_move_m":measured_max_step,"support_ray_hits":measured_support_hits,"compiled_floor_support_hits":measured_compiled_support_hits,"missing_support_rays":measured_missing_support,"support_owners":measured_support_owners,"support_exceptions":measured_support_exceptions,"phases":measured_phases,"scope":"Movement samples only; original seeded individual-door placements and one circuit-start placement excluded. No relocation between connected circuit legs. Not normal-spawn traversal or full27source paths."},"  "))
	f.close()
func furnished_entry_return(actor:CharacterBody3D,programme:String)->void:
	const PLAN := "res://data/architecture/crown_batch/CONNECTED_ENTRY_ROUTES.json"
	assert(FileAccess.get_sha256(PLAN)=="2135395d1828da3217016a94cf2767c1fe4618127b9e48c88066ec3ada2b943a","Exact reviewed furnished-route successor required")
	var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(PLAN))
	assert(FileAccess.get_sha256("res://"+str(plan.source_manifest))==str(plan.source_manifest_sha256))
	var manifest:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://"+str(plan.source_manifest)))
	var selected:Array=plan.routes.filter(func(r:Dictionary)->bool:return str(r.programme_key)==programme)
	var sources:Array=manifest.sections.filter(func(r:Dictionary)->bool:return str(r.programme_key)==programme)
	assert(selected.size()==1 and sources.size()==1)
	var route:Dictionary=selected[0];var section:Dictionary=sources[0]
	assert(route.replacement_required and route.source_path_xz==section.source_paths_xz[str(route.source_path_key)])
	assert(FileAccess.get_sha256("res://assets/models/"+str(route.model_file))==str(route.model_sha256))
	var forward:Array=[route.spine_approach_xz];forward.append_array(route.source_path_xz)
	var expected:Array=forward.duplicate(true)
	for i in range(forward.size()-2,-1,-1):expected.append(forward[i])
	assert(expected==route.applied_path_xz,"Only exact source entry and reversed return plus spine connector")
	var points:Array=[]
	for point in route.applied_path_xz:points.append(Vector2(point[0],point[1]))
	measured_phase=programme+"_source_entry_return"
	await walk_route(actor,points)
	assert(absf(actor.position.y-106.5)<.12,"Furnished entry return remains at original floor datum")
	print("CROWN FURNISHED ENTRY PASS:",programme)
	measured_phase="connected_circuit"

func walk(actor:CharacterBody3D,destination:Vector2) -> void:
	var reached:=false
	for frame in range(700):
		var delta:=Vector3(destination.x-actor.position.x,0,destination.y-actor.position.z)
		if delta.length()<.09:
			reached=true
			break
		var movement:=delta.normalized()*3.1
		actor.velocity.x=movement.x
		actor.velocity.z=movement.z
		actor.velocity.y=-.1 if actor.is_on_floor()else actor.velocity.y-9.8/60
		var before := actor.position
		actor.move_and_slide()
		record_walk_step(actor,before)
		await physics_frame
	if not reached:
		for i in range(actor.get_slide_collision_count()):print("WALK BLOCK:",actor.get_slide_collision(i).get_collider().get_path())
	if not reached: write_walk_receipt("walk_stalled")
	assert(reached,"Florist walk stalled at %s toward %s"%[actor.position,destination])

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
	measured_floors=ship.find_child("CompiledStructuralFloors_NotFinishedRooms",true,false)
	assert(measured_floors!=null)
	var crown:Node3D=ship.find_child("CentralCommandCrown_WIP",true,false)
	var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/CENTRAL_CROWN_RUNTIME.json"))
	assert(crown!=null and data.programmes.size()==6 and data.doors.size()==12)
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
	measured_phase="connected_circuit"
	actor.position=Vector3(5.5,106.6,-82);actor.velocity=Vector3.ZERO
	for entry in data.doors:
		var door:Node3D=crown.get_node("CrownDoor_"+str(entry.name));door.interact(actor)
	for frame in range(110):await physics_frame
	await walk_route(actor,[Vector2(5.5,-77),Vector2(45,-77),Vector2(45,63),Vector2(0,63),Vector2(0,-77),Vector2(-8,-77),Vector2(-8,-71)])
	for z in [-52.0,-4.0,40.0]:
		if z == -4.0: await furnished_entry_return(actor,"D18_directory_05")
		else: await walk_route(actor,[Vector2(-8,z),Vector2(-23,z),Vector2(-8,z)])
	await walk_route(actor,[Vector2(-8,16),Vector2(0,16),Vector2(0,30),Vector2(8,30)])
	for z in [-52.0,0.0,46.0]:
		if z == 0.0: await furnished_entry_return(actor,"D18_directory_04")
		else: await walk_route(actor,[Vector2(8,z),Vector2(23,z),Vector2(8,z)])
	await walk_route(actor,[Vector2(8,30),Vector2(0,30),Vector2(0,108),Vector2(5.5,108),Vector2(5.5,137),Vector2(0,137)])
	assert(absf(actor.position.y-106.5)<.12,"Destination circuit must reach the existing aft crown link at the same datum")
	assert(ship.express_arrive(17),"Temporary D18 directory arrival remains safe on the new fore cross-street")
	write_walk_receipt("pass")
	print("CROWN ACCESS PASS: twelve precisely targeted RMB/E doors with full opening/closing collision sweeps and capsule entry/return; continuous walk visits all six programme shells, revised fore street and both existing core approaches. Equipment, role-based access, species fit and final appearance remain unfinished.")
	main.queue_free();await process_frame;quit()
