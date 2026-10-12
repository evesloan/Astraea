extends "res://tests/validate_d04_port_forward_commons_service.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(12):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea")
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 var stream:Node3D=ship.get_node("ShipSystems/RemainingBatchStreaming")
 var manager:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 var library:Node3D=stream.rooms["D12_directory_02"]
 var far:=Node3D.new();ship.add_child(far);far.global_position=Vector3(500,200,500)
 stream.set_physics_process(false);stream.actor=far;stream.refresh()
 record("library_initially_cold",not library.get_meta("stream_loaded",false))
 record("cold_validated_library_arrival",ship.arrive_at(Vector3(2,78.1,-456),0.0))
 record("library_loaded_before_arrival_release",library.get_meta("stream_loaded",false))
 stream.actor=actor;stream.set_physics_process(true)
 for i in range(12):await physics_frame
 var walking:Array=[]
 for target in [Vector3(2,78,-458),Vector3(2,78,-456)]:
  var leg:Dictionary=await walk_to(actor,target);walking.append(leg);record("original_W_leg_"+str(walking.size()),leg.reached and leg.floor_contact)
 stream.set_physics_process(false);stream.actor=far
 var loose:=RigidBody3D.new();loose.freeze=true;ship.get_node("ShipSpace/PersistentActors").add_child(loose);loose.global_position=Vector3(30,79,-430)
 stream.refresh();record("loose_persistent_body_retains_library",library.get_meta("stream_loaded",false))
 loose.free();stream.refresh();record("library_releases_distant_geometry",not library.get_meta("stream_loaded",false))
 for light in budget.sources:record("live_light_"+str(light.get_instance_id()),is_instance_valid(light))
 stream.witnesses["D12_directory_02"].screen_entered.emit();await process_frame
 record("visibility_signal_restores_source",library.get_meta("stream_loaded",false))
 stream.prepare_position(Vector3(-11,61.1,-216))
 var dining:Node3D=stream.rooms["D10_directory_03"]
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_service.json"))
 var door:Node3D=dining.get_node(str(plan.root_name)+"/Group8DiningUtility_03")
 var id:=str(door.persistent_id);door.open_fraction=.37;door.desired_open=false;door._apply_pose()
 stream.refresh();record("dining_geometry_released",not dining.get_meta("stream_loaded",false))
 stream.prepare_position(Vector3(-11,61.1,-216));door=dining.get_node(str(plan.root_name)+"/Group8DiningUtility_03")
 record("stable_door_ID_and_pose_restored",str(door.persistent_id)==id and is_equal_approx(door.open_fraction,.37) and not door.desired_open)
 var ids:Dictionary={}
 for light in budget.sources:
  record("no_dead_or_duplicate_budget_source_"+str(light.get_instance_id()),is_instance_valid(light) and not ids.has(light.get_instance_id()));ids[light.get_instance_id()]=true
 record("budgets_unchanged",budget.shadow_source_budget==8 and budget.MAX_VISIBILITY_CANDIDATES==32)
 record("other_residency_present",manager.statistics().registered_rooms==819)
 stream.actor=actor;stream.set_physics_process(true);far.free()
 var result:Dictionary={"status":"PASS" if errors.is_empty() else "HOLD","checks":checks.size(),"errors":errors,"ordinary_W_legs":walking,"original_player_sha256":FileAccess.get_sha256("res://scripts/player.gd"),"scope":"Actual combined headless scene,cold Library arrival before controls,original W connector walking,loose-body retention,signal-driven restore,dining door state and light lifetime;graphical notifier occlusion/multi-deck views,GPU FPS,Windows navigation and full lift/stair crossings remain unaccepted"}
 FileAccess.open("res://artifacts/build_streaming_arrivals001.json",FileAccess.WRITE).store_string(JSON.stringify(result,"\t"));print(JSON.stringify(result));quit(0 if errors.is_empty() else 1)
