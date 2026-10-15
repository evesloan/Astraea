extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
const D="/workspace/astraea-integration-cutoff-20261013/arrivals_staff_network_journey_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/D09_RETAIL_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/AQUATIC_EXTERNAL_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_STAFF_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/THREAD_SUCCESSOR_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ARRIVALS_UPPER_STAFF_ADOPTION_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
var route_legs:Array=[]
var operations:Array=[]
func leg(player:CharacterBody3D,at:Vector3)->bool:
 var r:Dictionary=await walk_to(player,at);route_legs.append(r);return r.reached and r.floor_contact
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var lift:Node3D=ship.find_child("ForwardStaffLift",true,false);var initial_stops:Array=lift.floor_heights.duplicate();var initial_ids:Array=lift.stop_ids.duplicate();assert(lift.operation_ready and str(lift.persistent_id)=="forward_staff_lift_001");player.global_position=Vector3(-50,.03,-442);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position);ship.get_node("ShipSystems/RemainingBatchStreaming").prepare_position(player.global_position);await frames(20);var ok:=true
 for at:Vector3 in[Vector3(-54.6,0,-442),Vector3(-57,0,-442),Vector3(-57,0,-450),Vector3(-57,0,-460),Vector3(-57,0,-470),Vector3(-57,0,-480),Vector3(-57,0,-490),Vector3(-57,0,-500),Vector3(-47,0,-500),Vector3(-37,0,-500),Vector3(-27,0,-500),Vector3(-21,0,-500),Vector3(-21,0,-490),Vector3(-25.35,0,-490),Vector3(-25.35,0,-491.25)]:
  if not await leg(player,at):ok=false;break
 var travel_frames:=0;var moving_frames:=0;var player_platform_continuity:=true;var gates_interlocked:=true;var bounded_motion:=true;var arrived:=false
 if ok:
  var button:Node3D=lift.find_child("forward_staff_cabin_D02",true,false);assert(button!=null);var delta:Vector3=button.global_position-player.camera.global_position;player.pitch=atan2(delta.y,Vector2(delta.x,delta.z).length());await aim(player,button.global_position);var focused:bool=player.interaction_target==button;operations.append({"button":str(button.persistent_id),"normal_RMB_focus":focused})
  if focused:await key_e()
  else:ok=false
  var previous_velocity:float=lift.travel_velocity
  if ok:
   for i in range(1500):
    await physics_frame;travel_frames+=1;player_platform_continuity=player_platform_continuity and absf(player.global_position.y-lift.cabin.global_position.y)<.18 and player.get_parent().name=="PersistentActors";bounded_motion=bounded_motion and absf(lift.travel_velocity)<=lift.maximum_speed+.001 and absf(lift.travel_velocity-previous_velocity)<.025
    if lift.phase=="moving":
     moving_frames+=1;gates_interlocked=gates_interlocked and lift.cabin_gate.open_fraction<.001
     for gate in lift.landing_gates:gates_interlocked=gates_interlocked and gate.open_fraction<.001
    previous_velocity=lift.travel_velocity
    if lift.current_floor==1 and lift.phase=="idle"and lift.cabin_gate.open_fraction>.999:arrived=true;break
   ok=ok and arrived and player_platform_continuity and gates_interlocked and bounded_motion
 if ok:
  for at:Vector3 in[Vector3(-25.35,6,-490),Vector3(-21,6,-490),Vector3(-21,6,-500),Vector3(-31,6,-500),Vector3(-41,6,-500),Vector3(-51,6,-500),Vector3(-57,6,-500),Vector3(-57,6,-490),Vector3(-57,6,-480),Vector3(-57,6,-470),Vector3(-57,6,-460),Vector3(-57,6,-450),Vector3(-57,6,-442),Vector3(-54.6,6,-442),Vector3(-50,6,-442)]:
   if not await leg(player,at):ok=false;break
 physical_key(false);ok=ok and initial_stops==lift.floor_heights and initial_ids==lift.stop_ids and route_legs.size()==30
 FileAccess.open(D+"ARRIVALS_ORIGINAL_STAFF_LIFT_JOURNEY310.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","production_changed":false,"initial_player_placement_only":true,"teleports_within_continuous_route":0,"original_controller_legs":route_legs,"normal_original_cabin_panel_operations":operations,"existing_lift_id":str(lift.persistent_id),"unchanged_stop_heights":initial_stops,"unchanged_stop_ids":initial_ids,"moving_frames":moving_frames,"travel_frames":travel_frames,"reached_D02":arrived,"original_player_platform_continuity":player_platform_continuity,"all_original_gates_closed_during_travel":gates_interlocked,"bounded_original_velocity_and_acceleration":bounded_motion,"scope":"Unladen operator D01 Arrivals receiver through existing staff-spine dogleg and original ten-stop lift to D02 screened receiver;not fullten-stop,cart,species,role/stock/save orfinalacceptance"},"  "));print("PASS_ARRIVALS_COUPLED_ORIGINAL_STAFF_LIFT_JOURNEY"if ok else"FAIL_ARRIVALS_COUPLED_ORIGINAL_STAFF_LIFT_JOURNEY");quit(0 if ok else 1)
