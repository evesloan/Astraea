extends "res://tests/group8/validate_dining_service.gd"
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for f in range(90):await physics_frame
	ship=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");actor.set_physics_process(false)
	var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_fixture_adaptation.json"));var number:=int(OS.get_environment("G8_FIXTURE_ROOM"));verify(number in[6,10],"One fixture room case required")
	var key:="D10_directory_%02d"%number;var record:Dictionary={}
	for row in definition.rooms:
		if str(row.programme_key)==key:record=row
	actor.position=Vector3(54.5,61.06,0)if number==6 else Vector3(11,61.06,432);actor.velocity=Vector3.ZERO
	for f in range(20):actor.velocity.y=-.1;actor.move_and_slide();await physics_frame
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var room:Node3D
	for entry in residency.entries:
		if str(entry.room.get_meta("programme_key",""))==key:room=entry.room
	verify(room!=null and room.is_inside_tree(),"Exact cached received dining room not attached")
	var poses:Dictionary={}
	for n:Node3D in room.find_children("*","Node3D",true,false):poses[n.get_instance_id()]={"node":n,"pose":n.global_transform}
	var n:Node3D=load("res://scripts/group8/dining_fixture_adaptation.gd").build(ship,room);var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for f in range(8):await physics_frame
	for row in record.lights:
		var light:SpotLight3D=n.get_node(str(row.name));verify(light.global_position.distance_to(Vector3(row.at[0],row.at[1],row.at[2]))<.0001,"Retained fixture intent displaced")
		verify(budget.sources.has(light)and budget.requested_shadow[light.get_instance_id()],"Existing budget missing modeled dining source")
		var ray:=PhysicsRayQueryParameters3D.create(light.global_position,light.global_position+Vector3.DOWN*.05)
		verify(ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Actual retained dining housing exit blocked")
		ray.to=light.global_position+Vector3.DOWN*float(row.range);verify(not ship.get_world_3d().direct_space_state.intersect_ray(ray).is_empty(),"Housed source lacks actual receiver in range")
	var admitted:Dictionary={}
	var waypoints:Array=[Vector3(63,61,0),Vector3(80,61,0),Vector3(83,61,0)]if number==6 else[Vector3(19,61,432),Vector3(33,61,432),Vector3(43,61,432)]
	for target:Vector3 in waypoints:
		await go(actor,target);budget.refresh();var visible:Array=[]
		for row in record.lights:
			var light:SpotLight3D=n.get_node(str(row.name))
			if light.visible and light.shadow_enabled:visible.append(str(row.name))
		verify(not visible.is_empty(),"Reached dining work/arrival stance has no admitted housed task source");admitted[str(target)]=visible
	for row in poses.values():verify(row.node.global_transform.is_equal_approx(row.pose),"Original dining furniture/architecture pose changed")
	verify(n.get_meta("new_capacity")==0 and n.get_meta("new_physical_fixtures")==0,"New fixture or capacity count fabricated")
	var report:={"status":"PASS","programme_key":key,"checks":checks,"original_node_poses":poses.size(),"existing_physical_housings_adapted":record.lights.size(),"retained_places":record.retained_capacity,"actual_source_admission_at_reached_stances":admitted,"walk_legs":walk_legs,"walk_frames":walk_frames,"walk_distance_m":walk_distance,"maximum_step_m":max_step,"setup_placements":1,"subsequent_teleports":0,"new_native_geometry":0,"food_species_cart_hull_engineering_final_art_acceptance":false}
	FileAccess.open("res://data/architecture/group8/DINING_FIXTURE_%02d_VALIDATION.json"%number,FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n");print("GROUP8 DINING FIXTURE PASS: ",JSON.stringify(report))
	main.queue_free();for f in range(4):await process_frame
	quit(0)
