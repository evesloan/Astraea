extends "/workspace/astraea-integration-cutoff-20261013/validate_ready_dry_thermal_integrated.gd"
func target_door(actor:CharacterBody3D,door:Node3D,inside:bool)->void:
	var contact:CollisionShape3D=door.leaves[0].get_node("LeafContact")
	await aim(actor,contact.to_global(Vector3(0,0,-.04 if inside else .04)))
	record("source_contact_normal_target_"+str(inside),actor.interaction_target==door)
	if actor.interaction_target!=door:
		var q:=PhysicsRayQueryParameters3D.create(actor.camera.global_position,actor.camera.global_position-actor.camera.global_basis.z*2.5);q.exclude=[actor.get_rid()]
		var hit:=actor.get_world_3d().direct_space_state.intersect_ray(q)
		print("DRY_ACTUAL_TARGET ",str(hit.collider.get_path()) if not hit.is_empty() else "missing"," actor ",actor.global_position," target ",contact.global_position)
func operate_source(actor:CharacterBody3D,door:Node3D,want:bool,inside:bool)->bool:
	await target_door(actor,door,inside);await key_e()
	for i in range(90):await physics_frame
	var ok:bool=door.desired_open==want and (door.open_fraction>.999 if want else door.open_fraction<.001)
	record("normal_source_E_"+str(want)+str(inside),ok)
	return ok
func run()->void:
	var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
	for i in range(20):await physics_frame
	var ship:Node3D=main.get_node("World360/Astraea")
	var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
	var original_actor_id:=actor.get_instance_id()
	var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
	var upper:Node3D=ship.get_node("ShipSpace/Districts/D15_D17_StarAtlasUpper_WIP")
	var kit:Node3D=upper.get_node("VIPDryClub_Source");var door:Node3D=kit.get_node("DiningEntry")
	record("actual_original_upper_receiver",upper.get_meta("source_part_count")==514 and kit.get_meta("construction_installed",false))
	actor.global_position=Vector3(-65.5,102.03,0);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position)
	for i in range(20):await physics_frame
	var ok:=true
	for goal in [Vector3(-79,102,-2.5),Vector3(-86.25,102,-2.5),Vector3(-90.9,102,1)]:
		if not await visit(actor,goal,"owner measured original public arrival"):ok=false;break
	if ok and not await operate_source(actor,door,true,false):ok=false
	if ok and not await visit(actor,Vector3(-90.9,102,3.8),"actual opened dining entry"):ok=false
	if ok:
		var witness_actor:=CharacterBody3D.new();var col:=CollisionShape3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;col.shape=shape;col.position=Vector3.UP*.9;witness_actor.add_child(col);ship.get_node("ShipSpace/PersistentActors").add_child(witness_actor);witness_actor.global_position=door.global_position+Vector3.UP*.02
		for i in range(3):await physics_frame
		await target_door(actor,door,true);await key_e()
		for i in range(5):await physics_frame
		record("occupied_actual_character_refuses_close",door.desired_open and door.open_fraction>.999 and door.obstructed)
		witness_actor.queue_free()
		for i in range(3):await physics_frame
	if ok and not await operate_source(actor,door,false,true):ok=false
	if ok and not await operate_source(actor,door,true,true):ok=false
	if ok and not await visit(actor,Vector3(-90.9,102,1),"normal dry entry egress"):ok=false
	if ok and not await operate_source(actor,door,false,false):ok=false
	for goal in [Vector3(-86.25,102,-2.5),Vector3(-79,102,-2.5),Vector3(-65.5,102,0)]:
		if not ok:break
		if not await visit(actor,goal,"original supported public return"):ok=false
	physical_key(false)
	record("complete_normal_public_round_trip",ok and legs.size()==8 and not door.desired_open and door.open_fraction<.001)
	record("original_player_unchanged",actor.get_instance_id()==original_actor_id)
	var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks,"errors":errors,"legs":legs,"normal_RMB_E_operations":4,"occupied_character_guard":1,"teleports_inside_routes":0,"original_fixture_start":1,"full_build_or_visual_acceptance":false,"scope":"Changed dry-club public entry only;thermal route checks retained from prior passing affected subset"}
	FileAccess.open("/workspace/astraea-integration-cutoff-20261013/DRY_CLUB_CONNECTED_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
	print("DRY_CLUB_CONNECTED ",JSON.stringify({"status":result.status,"legs":legs.size(),"errors":errors}));quit(0 if errors.is_empty() else 1)
