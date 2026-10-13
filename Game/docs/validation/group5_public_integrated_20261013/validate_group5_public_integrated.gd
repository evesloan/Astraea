extends "/workspace/astraea-integration-cutoff-20261013/validate_group5_living_gifts_doors_source.gd"
func _initialize()->void:
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip",true))
	assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip",true))
	super._initialize()
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var owner:Node3D=ship.find_child("LivingGiftsInterior_WIP",true,false)
	var spec:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/LIVING_GIFTS_DOORS.json"))
	var builder=load("res://scripts/group5_living_gifts_doors.gd")
	var doors:Array=builder.build(ship)
	record("startup_public_attached",ship.get_meta("group5_living_doors_attached",false))
	record("default_public_only",doors.size()==1 and not ship.get_meta("group5_living_service_candidate_installed",true))
	record("repeat_source_build_same_nodes",builder.build(ship)==doors)
	var pub:Node3D=doors[0]
	record("closed_public_default",pub.fraction==0 and not pub.desired_open)
	actor.set_controls_enabled(true);actor.global_position=Vector3(52,52.53,216);actor.velocity=Vector3.ZERO
	ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
	for i in range(15):await physics_frame
	var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
	var ray:=PhysicsRayQueryParameters3D.create(Vector3(13,45.65,218),Vector3(46.88,56.45,236))
	record("protected_aquatic_upper_frame_sightline",space.intersect_ray(ray).is_empty())
	for want in [true,false]:
		pub.interact(actor)
		for frame in range(85):
			await physics_frame
			if frame%5==0:motion_contacts(ship,doors)
		record("public_motion_end_"+str(want),pub.fraction==(1.0 if want else 0.0))
	var ok:=errors.is_empty()
	for at in [Vector3(52,52.53,225),Vector3(46.7,52.53,227.5),Vector3(44.5,52.53,232),Vector3(44.5,52.53,236),vec(spec.doors[0].public_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"original aquatic arrival to public threshold"):ok=false
	if ok and not await operate(actor,pub,"PublicControl",true):ok=false
	for at in [Vector3(44.5,52.53,236),Vector3(48.2,52.53,236),Vector3(50.8,52.53,235.7),vec(spec.doors[0].interior_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"opened public threshold and original nursery turn"):ok=false
	if ok:await guarded_attempt(ship,actor,pub)
	if ok and not await operate(actor,pub,"InteriorControl",false):ok=false
	if ok and not await operate(actor,pub,"InteriorControl",true):ok=false
	for at in [Vector3(50.8,52.53,235.7),Vector3(48.2,52.53,236),Vector3(44.5,52.53,236),vec(spec.doors[0].public_stance_world_xyz)]:
		if not ok:break
		if not await leg(actor,at,"continuous public threshold egress"):ok=false
	if ok and not await operate(actor,pub,"PublicControl",false):ok=false
	for at in [Vector3(44.5,52.53,236),Vector3(44.5,52.53,232),Vector3(46.7,52.53,227.5),Vector3(52,52.53,225),Vector3(52,52.53,216)]:
		if not ok:break
		if not await leg(actor,at,"original protected public return"):ok=false
	physical_key(false)
	record("public_route_complete",ok and legs.size()==18 and operations.size()==4 and guards==1)
	record("public_ends_closed",pub.fraction==0 and not pub.desired_open)
	record("service_remains_absent",owner.get_node("Group5LivingDoors").get_child_count()==1 and not ship.get_meta("group5_living_service_candidate_installed",true))
	var out:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"public_walk_legs":legs,"normal_RMB_E_operations":operations,"occupied_actual_character_guards":guards,"motion_samples":motion_samples,"teleports_inside_walking_routes":0,"service_enabled":false,"full_group_or_visual_or_build_acceptance":false}
	FileAccess.open("/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_INTEGRATED_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(out,"  "))
	print("GROUP5_PUBLIC_INTEGRATED ",JSON.stringify({"status":out.status,"checks":checks.size(),"legs":legs.size(),"operations":operations.size(),"guards":guards,"poses":motion_samples,"errors":errors}))
	quit(0 if errors.is_empty() else 1)
