extends "res://tests/validate_d04_commons_receiving_routes.gd"
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_AFT_CORE_THRESHOLD.json"));var n:Node3D=ship.find_child("D04PortAftCoreThreshold",true,false);var legs:Array=[]
 record("threshold_connected_once",n!=null and ship.find_children("D04PortAftCoreThreshold","Node3D",true,false).size()==1)
 if n==null:quit(1);return
 record("geometry_seal",FileAccess.get_sha256("res://artifacts/d04_port_aft_core_threshold_geometry.json")==p.sealed_receipt_sha256)
 var core:Node3D=ship.get_node("ShipSpace/Districts/"+p.core_root);record("only_placed_core_derivative",core.get_node("PrimaryCoreEnclosure").get_meta("catalogue_file")==p.core_derivative_file)
 var datum:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/AFT_MIDSHIP_PUBLIC_CORE.json"));var lift:Node3D=core.get_node("AftMidshipPublicLift");record("persistent_core_and_lift_identity",core.get_meta("persistent_id")=="aft_midship_public_core_001"and str(lift.persistent_id)=="aft_midship_public_core_lift_001");record("17_original_lift_stops_heights",lift.deck_numbers==datum.deck_numbers.map(func(v):return int(v)) and lift.floor_heights==datum.floor_y.map(func(v):return float(v)))
 for i in range(datum.stairs.size()):
  var stairs:Node3D=core.get_node("PrimarySwitchback_D%02d"%(i+1));record("original_stair_"+str(i),stairs.position.distance_to(vec(datum.stairs[i].origin))<.0001 and stairs.get_meta("catalogue_file")==datum.stairs[i].file)
 var neighborhood:Node3D=ship.find_child("D04PortAftHabitatNeighborhood",true,false)
 for pre in p.original_runtime_guards:record("exact_stub_guard_opened_"+pre.name,neighborhood.find_child(pre.name,true,false)==null)
 record("original_port_aft_capacity",neighborhood.get_meta("preserved_home_allocations")==20 and neighborhood.get_meta("preserved_reserved_rests")==25)
 var routes:Array=[{"label":"port_northern_receiving_into_original_core_bypass","start":Vector3(-44,16.53,288.7),"goals":[Vector3(-30,16.5,288.7),Vector3(-15,16.5,288.7),Vector3(-9,16.5,288.7),Vector3(-7,16.5,288.7),Vector3(-5.4,16.5,288.7),Vector3(-5.4,16.5,280),Vector3(-5.4,16.5,270)]},{"label":"original_core_return_through_new_threshold","start":Vector3(-5.4,16.53,270),"goals":[Vector3(-5.4,16.5,288.7),Vector3(-7,16.5,288.7),Vector3(-9,16.5,288.7),Vector3(-15,16.5,288.7),Vector3(-30,16.5,288.7),Vector3(-44,16.5,288.7)]}]
 for route in routes:
  actor.global_position=route.start;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  for i in range(20):await physics_frame
  for target in route.goals:
   var w:Dictionary=await walk_to(actor,target);w.scope=route.label;legs.append(w);record("existing_controller_leg_"+str(legs.size()),w.reached and w.floor_contact)
   if not w.reached:break
 record("staff_lift_D04_D07_remain_blank",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 var result={"status":"PASS"if errors.is_empty()else"FAIL","checks":checks.size(),"errors":errors,"controller_legs":legs,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"scope":"Port-aft northern D04 receiving through new lateral threshold into original aft-midship public bypass and back; original stairs/identities/heights preserved, no lift/cart/tool experiments","dedicated_staff_links_vertical_service_engineering_final_accepted":false};FileAccess.open("res://artifacts/d04_port_aft_core_threshold_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
