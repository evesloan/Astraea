extends "res://tests/validate_d04_port_forward_commons_service.gd"
const D="/workspace/astraea-integration-cutoff-20261013/dining_public_core_20261015/"
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",D+"CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var package:Node3D=load("res://scripts/dining_public_core_20261015/package.gd").build(ship);await frames(4)
 var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var stream:Node=ship.get_node("ShipSystems/RemainingBatchStreaming");var space:=ship.get_world_3d().direct_space_state;var routes:Array=[];var stances:Array=[]
 for side in[-1.,1.]:
  var start:=Vector3(0,61,-432);player.global_position=start+Vector3.UP*.03;player.velocity=Vector3.ZERO;player.set_controls_enabled(true);stream.prepare_position(Vector3(side*15,61,-432));await frames(20)
  var legs:Array=[]
  for goal:Vector3 in[Vector3(side*6,61,-432),Vector3(side*8.5,61,-432),Vector3(side*15,61,-432)]:
   var leg:Dictionary=await walk_to(player,goal);legs.append(leg)
   if not leg.reached or not leg.floor_contact:break
  routes.append({"side":side,"legs":legs,"complete":legs.size()==3 and legs.all(func(a):return a.reached and a.floor_contact)})
  for z in[-433.5,-432.,-430.5]:
   for x in[side*7.6,side*7.9,side*8.3]:
    var at:=Vector3(x,61,z);stances.append({"at":str(at),"capsule_clear":capsule_clear(space,at),"floor":not ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty()})
 # Lantern already has a4m native connector to the axial route;verify its actual receiving path too.
 player.global_position=Vector3(0,61.03,-216);player.velocity=Vector3.ZERO;stream.prepare_position(Vector3(-15,61,-216));await frames(20)
 var lantern_legs:Array=[]
 for goal:Vector3 in[Vector3(-3,61,-216),Vector3(-6,61,-216),Vector3(-8.5,61,-216),Vector3(-15,61,-216)]:
  var leg:Dictionary=await walk_to(player,goal);lantern_legs.append(leg)
  if not leg.reached or not leg.floor_contact:break
 routes.append({"programme_key":"D10_directory_03","legs":lantern_legs,"complete":lantern_legs.size()==4 and lantern_legs.all(func(a):return a.reached and a.floor_contact)})
 for x in[-7.9,-6.,-4.1,0.]:
  for z in[-217.5,-216.,-214.5]:
   var at:=Vector3(x,61,z);stances.append({"at":str(at),"capsule_clear":capsule_clear(space,at),"floor":not ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty()})
 var contracts:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group8/dining_service.json"));var original_places:=0
 for key in contracts.programme_keys:
  var row:Dictionary=contracts.retained_contracts[str(key)];assert(FileAccess.get_sha256("res://assets/models/"+str(row.runtime_file))==str(row.runtime_sha256));original_places+=int(row.old_counts.registered_occupancy)
 assert(original_places==720)
 var ok:bool=routes.all(func(a):return a.complete)and stances.all(func(a):return a.capsule_clear and a.floor)
 FileAccess.open(D+"CANDIDATE_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if ok else"FAIL","routes":routes,"stances":stances,"wall_successors":package.get_meta("exact_selected_wall_preimages"),"original_player_controller":true,"retained_source_places":original_places,"food_service_pressure_capacity_admitted":false},"  "));print("PASS_DINING_PUBLIC_CORE"if ok else"FAIL_DINING_PUBLIC_CORE");quit(0 if ok else 1)
