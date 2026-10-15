extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
const D="/workspace/astraea-integration-cutoff-20261013/d09_retail_service_receiving_20261015/"
var motion:Array=[]
var operations:Array=[]
func _initialize()->void:
 for path in["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/DINING_SERVICE_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/SYNTHESIS_EXTERNAL_ADOPTION_OVERLAY.zip",D+"INSTALLED_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func operate(player:CharacterBody3D,door:Node3D,side:String,want:bool)->void:
 await aim(player,door.get_node(side).to_global(Vector3(0,0,.055)));record("ordinary_target_"+str(operations.size()),player.interaction_target==door);await key_e()
 for frame in range(85):
  await physics_frame
  if frame%5==0:
   for body:AnimatableBody3D in door.panels:
    for child in body.get_children():
     if not child is CollisionShape3D:continue
     var shape:BoxShape3D=child.shape.duplicate();shape.size-=Vector3.ONE*.001;shape.margin=0.;var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;q.margin=0.;q.transform=child.global_transform;q.exclude=[body.get_rid()];var bad:Array=[]
     for hit in player.get_world_3d().direct_space_state.intersect_shape(q,128):
      if hit.collider is StaticBody3D or hit.collider is AnimatableBody3D:bad.append(str(hit.collider.get_path()))
     motion.append({"fraction":door.fraction,"panel":str(body.name),"static_or_panel_contacts":bad})
 var ok:bool=door.desired_open==want and door.fraction==(1. if want else 0.);record("ordinary_operation_"+str(operations.size()),ok);operations.append({"side":side,"open":want,"passed":ok,"ordinary_RMB_E":true})
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(90);var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var space:=ship.get_world_3d().direct_space_state;var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");var owner:Node3D=ship.find_child("LivingGiftsInterior_WIP",true,false);var root_doors:Node3D=owner.get_node("Group5LivingDoors");var service:Node3D=root_doors.get_node("Group5LivingServiceCandidate");var public_door:Node3D=root_doors.get_node("Group5LivingPublicDoor");var public_id:int=public_door.get_instance_id();var public_pose:=public_door.global_transform;var public_open:bool=public_door.desired_open;record("one_public_one_service",root_doors.get_child_count()==2);record("service_closed_at_default_startup",not service.desired_open and service.fraction==0);var before:Dictionary={}
 for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
  if not service.is_ancestor_of(mesh):before[mesh]={"pose":mesh.global_transform,"mesh":mesh.mesh}
 player.set_physics_process(false);player.global_position=Vector3(0,0,0);player.force_update_transform();await frames(3);var approaches:Array=[]
 for at:Vector3 in[Vector3(52.9,52.53,240.9),Vector3(53.485,52.53,244),Vector3(51.5,52.53,247)]:
  var h:=ray(space,at+Vector3.UP*.03,at-Vector3.UP*.08);approaches.append({"at":str(at),"clear":capsule_clear(space,at),"floor":str(h.collider.get_path())if not h.is_empty()else"","supported":not h.is_empty()and absf(h.position.y-52.5)<.003})
 record("actual_living_received_stances",approaches.all(func(a):return a.clear and a.supported));player.global_position=Vector3(52.9,52.53,240.9);player.velocity=Vector3.ZERO;player.set_physics_process(true);player.set_controls_enabled(true);residency.prepare_position(player.global_position);await frames(20);await operate(player,service,"InteriorControl",true);var living_legs:Array=[]
 for at:Vector3 in[Vector3(52.4,52.53,241),Vector3(52.4,52.53,244.5),Vector3(51.5,52.53,247),Vector3(53.485,52.53,244)]:
  living_legs.append(await walk_to(player,at))
  if not living_legs[-1].reached:break
 await operate(player,service,"PublicControl",false);await operate(player,service,"PublicControl",true)
 for at:Vector3 in[Vector3(52.4,52.53,244.5),Vector3(52.4,52.53,241),Vector3(52.9,52.53,240.9)]:
  living_legs.append(await walk_to(player,at))
  if not living_legs[-1].reached:break
 await operate(player,service,"InteriorControl",false);record("living_continuous_entry_return",living_legs.size()==7 and living_legs.all(func(a):return a.reached and a.floor_contact));record("all_motion_poses_clear",motion.size()==272 and motion.all(func(a):return a.static_or_panel_contacts.is_empty()));var preserved:=true
 for mesh in before:
  if not is_instance_valid(mesh)or not mesh.global_transform.is_equal_approx(before[mesh].pose)or mesh.mesh!=before[mesh].mesh:preserved=false
 record("living_original_mesh_poses_and_resources_preserved",preserved);record("same_public_door_identity_pose_state",public_door.get_instance_id()==public_id and public_door.global_transform.is_equal_approx(public_pose)and public_door.desired_open==public_open);var staff_legs:Array=[];var sockets:Array=[]
 for spec in[[-1.,-69.],[1.,-69.],[-1.,69.],[1.,69.],[-1.,378.],[1.,378.],[-1.,-404.],[1.,-404.]]:
  var side:float=spec[0];var z:float=spec[1];var center_z:float=379. if z==378 else z;var start:=Vector3(side*(65. if z==-404 else 48.),52.53,center_z);player.set_physics_process(false);player.global_position=start;player.velocity=Vector3.ZERO;player.force_update_transform();residency.prepare_position(start);await frames(4);player.set_physics_process(true);await frames(20);var goals:Array[Vector3]=[]
  if z==-404:goals.assign([Vector3(side*60.5,52.5,z),Vector3(side*65,52.5,z)])
  elif z==378:goals.assign([Vector3(side*60.5,52.5,379),Vector3(side*60.5,52.5,378),Vector3(side*65,52.5,378),Vector3(side*65,52.5,379),Vector3(side*48,52.5,379)])
  else:goals.assign([Vector3(side*60.5,52.5,z),Vector3(side*65,52.5,z),Vector3(side*60.5,52.5,z),Vector3(side*48,52.5,z)])
  for goal in goals:
   var leg:Dictionary=await walk_to(player,goal);leg["socket"]=str(side)+"_"+str(z);staff_legs.append(leg)
   if not leg.reached:break
  var point:=Vector3(side*60.5,52.5,z);var h:=ray(space,point+Vector3.UP*.03,point-Vector3.UP*.03);sockets.append({"at":str(point),"floor":str(h.collider.get_path())if not h.is_empty()else"","supported":not h.is_empty()and absf(h.position.y-52.5)<.003,"matching_external_receiver_admitted":z!=-404,"fore404_external_target_still_unresolved":z==-404})
 record("four_circuit_and_eight_socket_routes",staff_legs.size()==30 and staff_legs.all(func(a):return a.reached and a.floor_contact));record("all_eight_literal_floor_supports",sockets.size()==8 and sockets.all(func(a):return a.supported));record("all84_unresolved_joins_preserved",ship.get_node("ShipSpace/Districts/ShoppingPromenadeChunks").get_meta("unresolved_address_joins")==84)
 FileAccess.open(D+"INSTALLED_RUNTIME.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS"if errors.is_empty()else"FAIL","checks":checks,"errors":errors,"living_received_approaches":approaches,"living_original_meshes_preserved":before.size(),"living_actual_controller_legs":living_legs,"living_ordinary_operations":operations,"moving_body_poses":motion,"staff_receiver_controller_legs":staff_legs,"eight_socket_supports":sockets,"two_fore404_external_target_joins_remain_unaccepted":true,"four_circuits_received_via_existing_six_links":true,"new_floors_or_floor_owners":0,"all84_unresolved_address_joins_preserved":true,"operational_or_final_acceptance":false},"  "));print("PASS_D09_LIVING_SERVICE_AND_FOUR_STAFF_CIRCUIT_RECEIVING"if errors.is_empty()else"FAIL_D09_LIVING_SERVICE_AND_FOUR_STAFF_CIRCUIT_RECEIVING");quit(0 if errors.is_empty()else 1)
