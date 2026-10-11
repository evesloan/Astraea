extends "res://tests/validate_d04_commons_receiving_routes.gd"
var legs:Array=[]
func walk_leg(actor:CharacterBody3D,target:Vector3,label:String)->bool:
 var w:Dictionary=await walk_to(actor,target);w.scope=label;legs.append(w);record("walking_leg_"+str(legs.size()),w.reached and w.floor_contact);return w.reached
func ride(actor:CharacterBody3D,lift:Node3D,stop:int)->Dictionary:
 var start:=actor.global_position;var parent:=actor.get_parent();var floor_frames:=0;var moving_frames:=0;record("lift_request_"+str(stop),lift.request_floor(stop))
 for i in range(1800):
  await physics_frame
  if lift.phase=="moving":
   moving_frames+=1
   if actor.is_on_floor():floor_frames+=1
  if lift.current_floor==stop and lift.phase=="idle":break
 var target:float=lift.floor_heights[stop]
 var result:Dictionary={"stop":stop,"start":str(start),"final":str(actor.global_position),"reached":lift.current_floor==stop and lift.phase=="idle" and absf(actor.global_position.y-target)<.12,"floor_contact":actor.is_on_floor(),"moving_frames":moving_frames,"moving_floor_contact_frames":floor_frames,"actor_parent_unchanged":actor.get_parent()==parent,"existing_lift_controller":true,"actor_manually_relocated_during_ride":false}
 record("actual_unloaded_ride_"+str(stop),result.reached and result.floor_contact and result.actor_parent_unchanged and moving_frames>0);return result
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_STAFF_RISER.json"));var n:Node3D=ship.find_child("D04PortCentralStaffCatchment",true,false)
 record("connected_once",n!=null and ship.find_children("D04PortCentralStaffCatchment","Node3D",true,false).size()==1)
 if n==null:quit(1);return
 record("geometry_seal",FileAccess.get_sha256("res://artifacts/d04_port_central_staff_riser_geometry.json")==p.sealed_receipt_sha256)
 var lift:Node3D=n.get_node("PortCentralStaffLift");record("actual_two_stop_lift",lift.deck_numbers==[1,4]and lift.floor_heights==[0.0,16.5]);record("old_forward_lift_still_blank_D04_D07",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 for name in ["D04PortAftHabitatNeighborhood","D04StarboardAftHabitatNeighborhood","D04PortCentralHabitatNeighborhood","D04StarboardCentralHabitatNeighborhood"]:
  var house:Node3D=ship.find_child(name,true,false);record("retained_house_"+name,house!=null)
  if house!=null:record("retained_capacity_"+name,house.get_meta("preserved_home_allocations")==20 and house.get_meta("preserved_reserved_rests")==25)
 for name in ["D04PortForwardFifthHomeCandidates","D04StarboardSouthHomeCandidates"]:
  var house:Node3D=ship.find_child(name,true,false);record("retained_forward_house_"+name,house!=null)
  if house!=null:record("retained_forward_capacity_"+name,house.get_meta("total_house_reservation_count")==20 and house.get_meta("capacity_preserved")==25)
 for item in p.service_doors:n.get_node(item.name).interact(null)
 for i in range(100):await physics_frame
 actor.global_position=Vector3(-57,.03,-105);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 for target in [Vector3(-57,0,-97.8),Vector3(-51,0,-97.8),Vector3(-21,0,-97.8),Vector3(-21,0,-90),Vector3(-25,0,-90)]:
  if not await walk_leg(actor,target,"D01 original stem to clean branch and physical boarding"):break
 var rides:Array=[]
 if errors.is_empty():rides.append(await ride(actor,lift,1))
 if errors.is_empty():
  for target in [Vector3(-21,16.5,-90),Vector3(-21,16.5,-97.8),Vector3(-60.4,16.5,-97.8),Vector3(-60.4,16.5,-40.2),Vector3(-60.4,16.5,-97.8),Vector3(-21,16.5,-97.8),Vector3(-21,16.5,-100.6),Vector3(-63.2,16.5,-100.6),Vector3(-63.2,16.5,-40.2),Vector3(-63.2,16.5,-100.6),Vector3(-21,16.5,-100.6),Vector3(-21,16.5,-90),Vector3(-25,16.5,-90)]:
   if not await walk_leg(actor,target,"D04 shared landing to separate clean/used receiving and back"):break
 if errors.is_empty():rides.append(await ride(actor,lift,0))
 if errors.is_empty():
  for target in [Vector3(-21,0,-90),Vector3(-21,0,-100.6),Vector3(-51,0,-100.6),Vector3(-57,0,-100.6),Vector3(-57,0,-105)]:
   if not await walk_leg(actor,target,"D01 used branch return into original staff stem"):break
 physical_key(false)
 var result:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"controller_legs":legs,"actual_unloaded_lift_rides":rides,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"scope":"Original D01 staff stem through real service doors, two-stop lift boarding/ride/exit, both D04 separated receiving lanes, return through used D01 branch; existing controllers","cart_tool_gameplay_tests_performed":false,"limits":p.limits}
 FileAccess.open("res://artifacts/d04_port_central_staff_riser_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
