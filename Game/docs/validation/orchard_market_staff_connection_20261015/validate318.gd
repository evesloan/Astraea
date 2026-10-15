extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
const D="/workspace/astraea-integration-cutoff-20261013/orchard_market_staff_connection_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/PORT_FORE404_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
var legs:Array=[]
var operations:Array=[]
func leg(actor:CharacterBody3D,goal:Vector3)->bool:
 var r:Dictionary=await walk_to(actor,goal);legs.append(r);return r.reached and r.floor_contact
func operate(actor:CharacterBody3D,door:Node3D,want:bool)->bool:
 var at:Vector3=door.to_global(Vector3(0,1.35,0));var delta:Vector3=at-actor.camera.global_position;actor.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());await aim(actor,at);var focused:bool=actor.interaction_target==door
 if focused:await key_e()
 await frames(100);var passed:bool=focused and door.desired_open==want and is_equal_approx(door.open_fraction,1. if want else 0.);operations.append({"existing_door_id":str(door.persistent_id),"normal_RMB_focus":focused,"normal_E":focused,"wanted_open":want,"actual_fraction":door.open_fraction,"obstructed":door.obstructed,"player_at":str(actor.global_position),"passed":passed});return passed
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var owner:Node3D=ship.get_node("ShipSpace/Districts/GrandPoolOrchardSection_WIP");var door:Node3D=owner.get_node("GrandPoolDoor_service_52_5");assert(str(door.persistent_id)=="grand_pool_service_52_5_door_001"and door.global_position.distance_to(Vector3(-53.86,52.5,-463))<.001);var door_states:Dictionary={}
 for d:Node3D in owner.find_children("GrandPoolDoor_*","Node3D",true,false):door_states[d]={"id":str(d.persistent_id),"pose":d.global_transform,"open":d.desired_open}
 var lift:Node3D=ship.find_child("ForwardStaffLift",true,false);var initial_stops:Array=lift.floor_heights.duplicate();var initial_ids:Array=lift.stop_ids.duplicate();actor.global_position=Vector3(-62,52.53,-404);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(actor.global_position);await frames(20);var ok:bool=not door.desired_open and door.open_fraction==0.
 for at:Vector3 in[Vector3(-62,52.5,-403.2),Vector3(-60,52.5,-403.2),Vector3(-57.3,52.5,-403.2),Vector3(-54.5,52.5,-403.2),Vector3(-52.5,52.5,-403.2),Vector3(-51.5,52.5,-400.9),Vector3(-45.9,52.5,-400.9),Vector3(-45.9,52.5,-410),Vector3(-45.9,52.5,-420),Vector3(-45.9,52.5,-430),Vector3(-45.9,52.5,-440),Vector3(-45.9,52.5,-450),Vector3(-45.9,52.5,-458.6),Vector3(-51.5,52.5,-458.6),Vector3(-51.5,52.5,-463)]:
  if not ok:break
  if not await leg(actor,at):ok=false;break
 if ok:ok=await operate(actor,door,true)
 if ok:ok=await leg(actor,Vector3(-55.9,52.5,-463))
 if ok:ok=await operate(actor,door,false)
 for at:Vector3 in[Vector3(-57,52.5,-463),Vector3(-57,52.5,-473),Vector3(-57,52.5,-483),Vector3(-57,52.5,-493),Vector3(-57,52.5,-500),Vector3(-47,52.5,-500),Vector3(-37,52.5,-500),Vector3(-27,52.5,-500),Vector3(-21,52.5,-500),Vector3(-21,52.5,-490),Vector3(-21,52.5,-500),Vector3(-31,52.5,-500),Vector3(-41,52.5,-500),Vector3(-51,52.5,-500),Vector3(-57,52.5,-500),Vector3(-57,52.5,-490),Vector3(-57,52.5,-480),Vector3(-57,52.5,-470),Vector3(-57,52.5,-463),Vector3(-55.9,52.5,-463)]:
  if not ok:break
  if not await leg(actor,at):ok=false;break
 if ok:ok=await operate(actor,door,true)
 if ok:ok=await leg(actor,Vector3(-51.5,52.5,-463))
 if ok:ok=await operate(actor,door,false)
 for at:Vector3 in[Vector3(-51.5,52.5,-458.6),Vector3(-45.9,52.5,-458.6),Vector3(-45.9,52.5,-450),Vector3(-45.9,52.5,-440),Vector3(-45.9,52.5,-430),Vector3(-45.9,52.5,-420),Vector3(-45.9,52.5,-410),Vector3(-45.9,52.5,-400.9),Vector3(-51.5,52.5,-400.9),Vector3(-52.5,52.5,-403.2),Vector3(-54.5,52.5,-403.2),Vector3(-57.3,52.5,-403.2),Vector3(-60,52.5,-403.2),Vector3(-62,52.5,-403.2),Vector3(-62,52.5,-404)]:
  if not ok:break
  if not await leg(actor,at):ok=false;break
 physical_key(false);var identities_preserved:=true
 for d in door_states:
  if not is_instance_valid(d)or str(d.persistent_id)!=door_states[d].id or not d.global_transform.is_equal_approx(door_states[d].pose)or d.desired_open!=door_states[d].open:identities_preserved=false
 var joins=ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks").get_meta("unresolved_address_joins");ok=ok and legs.size()==52 and operations.size()==4 and operations.all(func(a):return a.passed)and identities_preserved and initial_stops==lift.floor_heights and initial_ids==lift.stop_ids and joins==84
 FileAccess.open(D+"MARKET_STAFF_CONNECTION318.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","protected_base":"babcc79ff2baaa1908547180cd657e835955800a","production_changed":false,"original_controller_legs":legs,"normal_existing_door_RMB_E_operations":operations,"teleports_within_continuous_route":0,"original_door_states_ids_and_poses_preserved":identities_preserved,"original_door_count":door_states.size(),"existing_staff_lift_id":str(lift.persistent_id),"original_lift_stops_and_ids_preserved":initial_stops==lift.floor_heights and initial_ids==lift.stop_ids,"all84addressjoins_still_unresolved":joins,"starboard_receiver_admitted":false,"scope":"Unladen fore404 to actualMarketdryloop,originalscreenedvestibule/servicedoor andretainedD09staffspine/liftlanding,then continuousreturn;no fullnetwork,cart,stock,roles,species,saveorfinalartacceptance"},"  "));print("PASS_MARKET_ORIGINAL_STAFF_CONNECTION"if ok else"FAIL_MARKET_ORIGINAL_STAFF_CONNECTION");quit(0 if ok else 1)
