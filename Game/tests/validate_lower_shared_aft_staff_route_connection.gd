extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
func leg(actor:CharacterBody3D,goal:Vector3,label:String)->bool:
 var w:Dictionary=await walk_to(actor,goal);w.scope=label;legs.append(w);record("original_player_leg_"+str(legs.size()),w.reached and w.floor_contact);return w.reached
func operate(actor:CharacterBody3D,door:Node3D,spec:Dictionary,want:bool)->bool:
 await aim(actor,vec(spec.at)+Vector3(0,2.69,0));record("normal_header_interaction_target_"+str(legs.size()),actor.interaction_target==door);await key_e()
 for i in range(100):await physics_frame
 record("normal_source_door_endpoint_"+str(legs.size()),door.open_fraction==(1.0 if want else 0.0)and door.desired_open==want and not door.obstructed);return door.open_fraction==(1.0 if want else 0.0)
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/LOWER_SHARED_AFT_STAFF_ROUTE.json"));var n:Node3D=ship.find_child("LowerSharedAftStaffRoute",true,false)
 record("connected_once",n!=null and ship.find_children("LowerSharedAftStaffRoute","Node3D",true,false).size()==1)
 if n==null:quit(1);return
 record("geometry_sealed",FileAccess.get_sha256("res://artifacts/lower_shared_aft_staff_route_geometry.json")==p.sealed_receipt_sha256)
 var entry:Node3D=n.get_node(p.service_doors[0].name);var aft:Node3D=n.get_node(p.service_doors[1].name)
 #One original supported fixture seed;all subsequent route movement uses the real controller.
 actor.global_position=Vector3(-46,.03,60);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 await leg(actor,Vector3(-46,0,76),"original central service spine to shared aft apron")
 if errors.is_empty()and await operate(actor,entry,p.service_doors[0],true):
  await leg(actor,Vector3(-50,0,76),"actual north source-floor junction");await operate(actor,entry,p.service_doors[0],false)
 if errors.is_empty():
  for goal in [Vector3(-56.5,0,76),Vector3(-56.5,0,110),Vector3(-56.5,0,145),Vector3(-56.5,0,180),Vector3(-56.5,0,215),Vector3(-56.5,0,250),Vector3(-56.5,0,285),Vector3(-56.5,0,300),Vector3(-35,0,300),Vector3(-6.1,0,300)]:
   if not await leg(actor,goal,"continuous enclosed shared lower staff route"):break
 if errors.is_empty()and await operate(actor,aft,p.service_doors[1],true):
  await leg(actor,Vector3(-2.1,0,300),"actual aft source-floor junction");await operate(actor,aft,p.service_doors[1],false);await leg(actor,Vector3(0,0,300),"original shared aft main spine");await leg(actor,Vector3(-2.1,0,300),"source main-spine return")
 if errors.is_empty()and await operate(actor,aft,p.service_doors[1],true):
  await leg(actor,Vector3(-6.1,0,300),"normal aft staff threshold return");await operate(actor,aft,p.service_doors[1],false)
 if errors.is_empty():
  for goal in [Vector3(-35,0,300),Vector3(-56.5,0,300),Vector3(-56.5,0,285),Vector3(-56.5,0,250),Vector3(-56.5,0,215),Vector3(-56.5,0,180),Vector3(-56.5,0,145),Vector3(-56.5,0,110),Vector3(-56.5,0,76),Vector3(-50,0,76)]:
   if not await leg(actor,goal,"continuous shared lower service return"):break
 if errors.is_empty()and await operate(actor,entry,p.service_doors[0],true):
  await leg(actor,Vector3(-46,0,76),"normal original apron egress");await operate(actor,entry,p.service_doors[0],false);await leg(actor,Vector3(-46,0,60),"original central service stem return")
 for spec in p.service_doors:
  var door:Node3D=n.get_node(spec.name);record("new_staff_doors_end_closed_"+spec.name,door.open_fraction==0 and not door.desired_open and String(door.persistent_id)==spec.id)
 record("old_forward_lift_stops_preserved",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17]);record("central_two_stop_lift_preserved",ship.find_child("PortCentralStaffLift",true,false).deck_numbers==[1,4])
 record("recent_commons_ceiling_package_preserved",ship.find_child("D04CommonsCeilingJunctions",true,false)!=null);record("latest_port_aft_court_package_preserved",ship.find_child("D04PortAftCourtRoutes",true,false)!=null)
 record("explicit_shared_upstream_downstream",n.get_meta("shared_upstream_and_downstream")and not n.get_meta("full_clean_used_network_accepted"))
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"original_player_controller_legs":legs,"single_original_supported_fixture_seed":true,"route_teleports":0,"normal_RMB_E_and_original_door_controllers":true,"new_doors_end_closed":entry.open_fraction==0 and aft.open_fraction==0,"loaded_cart_or_tool_experiments":false,"full_clean_used_segregation_accepted":false,"limits":p.limits};FileAccess.open("res://artifacts/lower_shared_aft_staff_route_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
