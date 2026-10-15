extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/"
var count:=0
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"FITTED_CANDIDATE_OVERLAY_r008.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var group:Node3D=load("res://scripts/fitted_wet_pavilions_20261015/package.gd").build(ship);await frames(4)
 var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space:=ship.get_world_3d().direct_space_state;var suites:Array=[]
 var routes:Array=[{"name":"Tidal public-to-ramp","start":Vector3(-96.1,102,-370),"goals":[Vector3(-96.1,102,-357.2),Vector3(-95.4,102,-357.2),Vector3(-94.5,102.04167,-357.2),Vector3(-77.4,103.46667,-357.2),Vector3(-73.8,103.5,-357.2),Vector3(-73.8,103.5,-360.8)]},{"name":"Quiet public-to-L-ramp","start":Vector3(63.5,102,-370),"goals":[Vector3(63.5,102,-382.7),Vector3(64.7,102.01667,-382.7),Vector3(77.2,103.05833,-382.7),Vector3(78.4,103.08333,-382.7),Vector3(78.4,103.08333,-381.6),Vector3(78.4,103.5,-376.1),Vector3(77.4,103.5,-376.1),Vector3(77.35,103.5,-375.6)]}]
 for route in routes:
  player.global_position=route.start+Vector3.UP*.03;player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position);await frames(20)
  var legs:Array=[]
  for goal:Vector3 in route.goals:
   var leg:Dictionary=await walk_to(player,goal);legs.append(leg)
   if not leg.reached or not leg.floor_contact:break
  suites.append({"name":route.name,"legs":legs,"complete":legs.size()==route.goals.size()and legs.all(func(a):return a.reached and a.floor_contact)})
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(2)
 var stances:Array=[]
 for point:Vector3 in[Vector3(-73.9,103.5,-360.8),Vector3(77.35,103.5,-375.6),Vector3(-91.7,102,-374.5),Vector3(-88.3,102,-374.5),Vector3(66.55,102,-363.1),Vector3(71.05,102,-363.1)]:stances.append({"at":str(point),"capsule_clear":capsule_clear(space,point)})
 var ok:bool=suites.all(func(a):return a.complete)and stances.all(func(a):return a.capsule_clear)
 FileAccess.open(D+"FITTED_ACTUAL_ROUTES_r008.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","routes":suites,"stances":stances,"original_player_controller":true,"new_capacity_or_water_operation_admitted":false},"  "));print("PASS_FITTED_R008_ROUTE_INVENTORY"if ok else"FAIL_FITTED_R008_ROUTE_INVENTORY");quit(0 if ok else 1)
