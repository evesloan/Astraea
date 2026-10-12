extends "res://tests/group6_completion/validate_cascade_proposal.gd"
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var actor_id:=actor.get_instance_id()
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var annex:Node3D=ship.get_node("ShipSpace/Districts/AquaticRiverSlideAnnex_WIP")
	var addition:Node3D=load("res://scripts/group6_completion/completion.gd").build(annex,ship)
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	for light:Light3D in addition.find_children("*","Light3D",true,false):budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.visible=false;light.shadow_enabled=false
	actor.set_physics_process(false)
	await optical_checks(ship,annex,addition,actor,budget)
	actor.set_physics_process(true)
	var proposal:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://docs/group6_completion/interfaces/SHARED_ROUTE_PROPOSALS002.json"));var evidence:Array=[]
	for route in proposal.routes:
		var points:Array=route.points_xyz;actor.global_position=vec(points[0])+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position)
		for i in range(20):await physics_frame
		record(str(route.id)+"_supported_initial_fixture",actor.is_on_floor() and absf(actor.position.y-44)<.01)
		var witness:=MotionWitness.new();witness.process_physics_priority=1000;root.add_child(witness);witness.reset(actor)
		var route_legs:Array=[]
		for goal in points.slice(1):
			residency.prepare_position(vec(goal));var w:Dictionary=await walk_to(actor,vec(goal));legs.append(w);route_legs.append(w);record(str(route.id)+"_leg_"+str(route_legs.size()),w.reached and w.floor_contact)
			if not errors.is_empty():break
		if errors.is_empty():
			var reverse:Array=points.duplicate();reverse.reverse()
			for goal in reverse.slice(1):
				residency.prepare_position(vec(goal));var w:Dictionary=await walk_to(actor,vec(goal));legs.append(w);route_legs.append(w);record(str(route.id)+"_return_"+str(route_legs.size()),w.reached and w.floor_contact)
				if not errors.is_empty():break
		witness.active=false;record(str(route.id)+"_continuous_original_movement",witness.maximum_step<.12 and witness.minimum_y>43.9)
		evidence.append({"id":route.id,"legs":route_legs,"physics_samples":witness.samples,"maximum_frame_motion_m":witness.maximum_step,"minimum_y":witness.minimum_y});witness.queue_free()
		if not errors.is_empty():break
	physical_key(false);record("same_original_persistent_player",actor.get_instance_id()==actor_id);record("both_routes_and_returns_exercised",legs.size()==26)
	var cascade:Node3D=load("res://scripts/group6_completion/cascade_proposal.gd").build(annex);record("cascade_proposal_build_succeeded",cascade!=null)
	if errors.is_empty() and cascade!=null:
		for light:Light3D in cascade.find_children("*","Light3D",true,false):budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true;light.visible=false;light.shadow_enabled=false
		for goal in [Vector3(18.8,44,210),Vector3(18.8,44,215.2),Vector3(21.5,44,215.2)]:
			residency.prepare_position(goal);var w:Dictionary=await walk_to(actor,goal);legs.append(w);record("cascade_link_from_returned_route_"+str(legs.size()),w.reached and w.floor_contact)
			if not errors.is_empty():break
		if errors.is_empty():await cascade_checks(ship,cascade,actor,ship.find_child("VesperWatercourse_WIP",true,false))
	record("full_route_and_mechanical_case_coverage",legs.size()==31)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"routes":evidence,"optical_evidence":optical_evidence,"cascade_evidence":cascade_evidence,"independent_supported_fixtures":2,"traversal_position_or_velocity_writes":0,"scope":"Baseline actual-main plus r018 source, outside Universal Changing portal to annex seam and existing cascade shoulder/console proposals, 19-fitted optics and original mechanical-input controls. Original player/input/contact. No room admission, permissions, interior changing/restaurant operation or shared-root/floor mutation. Current integration-owner main reconciliation remains separate."}
	FileAccess.open("res://docs/group6_completion/SHARED_ROUTE001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print("GROUP6 SHARED ROUTE ",result.status," ",errors," LEGS ",legs.size());quit(0 if errors.is_empty() else 1)
