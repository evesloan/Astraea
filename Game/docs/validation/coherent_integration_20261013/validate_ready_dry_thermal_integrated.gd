extends "res://tests/group6_completion/validate_water_care.gd"
func _initialize()->void:
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip",true))
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip",true))
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip",true))
	super._initialize()
func visit(actor:CharacterBody3D,goal:Vector3,label:String)->bool:
	var result:Dictionary=await walk_to(actor,goal);result.scope=label;legs.append(result)
	record("combined_leg_"+str(legs.size()),result.reached and result.floor_contact)
	return result.reached and result.floor_contact
func dry_operate(actor:CharacterBody3D,door:Node3D,want:bool,inside:bool)->bool:
	await aim(actor,door.to_global(Vector3(-.3,1.3,-.04 if inside else .04)))
	record("dry_normal_RMB_target_"+str(want)+str(inside),actor.interaction_target==door)
	await key_e()
	for i in range(90):await physics_frame
	var ok:bool=door.desired_open==want and (door.open_fraction>.999 if want else door.open_fraction<.001)
	record("dry_normal_E_state_"+str(want)+str(inside),ok)
	return ok
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var actor_id:=actor.get_instance_id()
	var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var source_count:int=budget.sources.size()
	var room:Node3D
	var mineral:Node3D
	for entry in residency.entries:
		if entry.room.name=="D08_directory_02":room=entry.room
		if entry.room.name=="D08_directory_03":mineral=entry.room
	assert(room!=null and mineral!=null,"Both original rooms must remain in the actual residency registry")
	var chamber:Node3D=room.get_node("Group6TidalNorthRoom")
	record("both_recovery_rooms_and_r008_installed",room.has_node("Group6ThermalRecovery") and mineral.has_node("Group6ThermalRecovery") and chamber!=null)
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group6_completion/TIDAL_NORTH_ROOM_CONTRACT.json"))
	record("exact_r008_roles",chamber.find_children("*","MeshInstance3D",true,false).size()==spec.new_meshes.size())
	var new_sources:Array=[]
	for addition:Node3D in [room.get_node("Group6ThermalRecovery"),mineral.get_node("Group6ThermalRecovery"),chamber]:
		for light:Light3D in addition.find_children("*","Light3D",true,false):
			new_sources.append(light);record("registered_once_"+str(light.name),budget.sources.count(light)==1)
	record("thirty_four_sources_no_duplicates",new_sources.size()==34 and budget.sources.size()==source_count)
	for name in spec.original_runtime_exclusions:
		var mesh:MeshInstance3D=room.find_child(str(name),true,false)
		record("old_successor_contact_removed_"+str(name),not mesh.visible and mesh.get_node_or_null("StaticContact")==null)
	actor.global_position=Vector3(38.5,44.93,-430.15);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position)
	for i in range(20):await physics_frame
	record("original_wet_landing_support",actor.is_on_floor() and absf(actor.global_position.y-44.9)<.01)
	var witness:=MotionWitness.new();witness.process_physics_priority=1000;ship.add_child(witness);witness.reset(actor)
	var goals:Array=[Vector3(42.5,44.9,-430.15),Vector3(42.05,44.9,-423),Vector3(42.05,44.9,-417.5),Vector3(43.65,44.9,-417.5),Vector3(43.65,44,-406.7),Vector3(45,44,-406.7),Vector3(45,44,-412),Vector3(46,44,-412),Vector3(45,44,-412),Vector3(45,44,-432),Vector3(46,44,-432),Vector3(45,44,-432),Vector3(45,44,-406.7),Vector3(43.65,44,-406.7),Vector3(43.65,44.9,-417.5),Vector3(42.05,44.9,-417.5),Vector3(42.05,44.9,-430.15),Vector3(38.5,44.9,-430.15),Vector3(34,44.9,-430.2),Vector3(34,44.3,-424.4),Vector3(34,44.9,-430.2),Vector3(38.5,44.9,-430.15)]
	var ok:=errors.is_empty()
	for goal in goals:
		if not ok:break
		if not await visit(actor,goal,"owner R008 continuous wet gallery/ramp/dry/return route on actual combined floors"):ok=false
		budget.refresh();var active:=0;var owned_active:=0
		for light:Light3D in budget.sources:
			if is_instance_valid(light) and light.is_inside_tree() and light.visible and light.shadow_enabled:
				active+=1
				if new_sources.has(light):owned_active+=1
		record("unchanged_eight_source_cap_"+str(legs.size()),active>0 and active<=8 and budget.shadow_source_budget==8)
		record("new_thermal_source_admitted_"+str(legs.size()),owned_active>0)
		if not errors.is_empty():ok=false
	witness.active=false;physical_key(false)
	record("tidal_route_completed",ok and legs.size()==22)
	record("bounded_continuous_actor_motion",witness.maximum_step<.12 and witness.minimum_y>43.95 and witness.samples>100)
	var reflection:ReflectionProbe=chamber.get_node("TidalActualRoomReflection")
	record("reflection_after_admitted_real_sources",reflection.visible and reflection.get_meta("captured_after_shared_budget",false))
	var upper:Node3D=ship.get_node("ShipSpace/Districts/D15_D17_StarAtlasUpper_WIP")
	var dry:Node3D=upper.get_node("VIPDryClub_Source")
	record("dry_bound_to_actual_existing_parent",dry.get_meta("construction_installed",false) and dry.get_meta("existing_parent_programme")=="D17_directory_03" and upper.get_meta("source_part_count")==514)
	record("dry_no_programme_capacity_or_booking_credit",not dry.get_meta("food_service_membership_booking_and_capacity_accepted",true))
	var dry_lights:Array=dry.find_children("*","OmniLight3D",true,false)
	record("dry_three_source_lights_registered_once",dry_lights.size()==3)
	for light:Light3D in dry_lights:record("dry_registration_"+str(light.get_instance_id()),budget.sources.count(light)==1)
	if ok:
		actor.global_position=Vector3(-65.5,102.03,0);actor.velocity=Vector3.ZERO;residency.prepare_position(actor.global_position)
		for i in range(20):await physics_frame
		for goal in [Vector3(-79,102,-2.5),Vector3(-86.25,102,-2.5),Vector3(-90.9,102,1)]:
			if not await visit(actor,goal,"measured inclusive Star Atlas dry public arrival on existing floor"):ok=false;break
	record("actual_dry_public_arrival",ok and legs.size()==25)
	var door:Node3D=dry.get_node("DiningEntry")
	if ok and not await dry_operate(actor,door,true,false):ok=false
	if ok and not await visit(actor,Vector3(-90.9,102,3.8),"ordinary opened source dry dining threshold"):ok=false
	if ok:
		var witness_actor:=CharacterBody3D.new();var col:=CollisionShape3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;col.shape=shape;col.position=Vector3.UP*.9;witness_actor.add_child(col);ship.get_node("ShipSpace/PersistentActors").add_child(witness_actor);witness_actor.global_position=door.global_position+Vector3.UP*.02
		for i in range(3):await physics_frame
		await aim(actor,door.to_global(Vector3(-.3,1.3,-.04)));await key_e()
		for i in range(5):await physics_frame
		record("dry_actual_character_refuses_close",door.desired_open and door.open_fraction>.999 and door.obstructed)
		witness_actor.queue_free()
		for i in range(3):await physics_frame
	if ok and not await dry_operate(actor,door,false,true):ok=false
	if ok and not await dry_operate(actor,door,true,true):ok=false
	if ok and not await visit(actor,Vector3(-90.9,102,1),"ordinary source dry dining egress"):ok=false
	if ok and not await dry_operate(actor,door,false,false):ok=false
	record("dry_source_door_ends_closed",ok and not door.desired_open and door.open_fraction<.001)
	record("original_player_identity_preserved",actor.get_instance_id()==actor_id)
	record("living_service_still_disabled",not ship.get_meta("group5_living_service_candidate_installed",true))
	physical_key(false)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"new_thermal_sources":new_sources.size(),"tidal_walk_legs":mini(legs.size(),22),"dry_arrival_legs":maxi(legs.size()-22,0),"controller_changed":false,"relocations_inside_routes":0,"explicit_between_district_fixture_starts":2,"full_build_visual_cart_species_gameplay_acceptance":false}
	FileAccess.open("/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("READY_DRY_THERMAL_INTEGRATED ",JSON.stringify({"status":result.status,"checks":checks.size(),"legs":legs.size(),"errors":errors}))
	quit(0 if errors.is_empty() else 1)
