extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_AFT_COMMONS_ENCLOSURE.json"));var n:Node3D=ship.find_child("D04StarboardAftCommonsEnclosure",true,false)
 record("production_connected_once",p.active and n!=null and ship.find_children("D04StarboardAftCommonsEnclosure","Node3D",true,false).size()==1)
 record("sealed_geometry",p.sealed_receipt_sha256==FileAccess.get_sha256("res://artifacts/d04_starboard_aft_commons_enclosure_geometry.json"))
 var home:Node3D=ship.find_child(p.source_root,true,false);record("original_twenty_homes_twentyfive_rests",home.get_meta("preserved_home_allocations")==20 and home.get_meta("preserved_reserved_rests")==25)
 if n==null:quit(1);return
 # One fixture on original public receiving; no position/velocity writes after seed.
 actor.global_position=Vector3(44,16.53,369.9);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 var route:Array=[Vector3(65,16.5,369.9),Vector3(74,16.5,369.9),Vector3(81,16.5,369.9),Vector3(81,16.5,364.5),Vector3(81,16.5,361.8),Vector3(81,16.5,364.5),Vector3(81,16.5,369.9),Vector3(74,16.5,369.9),Vector3(65,16.5,369.9),Vector3(64.45,16.5,369.9),Vector3(64.45,16.5,364),Vector3(64.45,16.5,361.2),Vector3(64.45,16.5,364),Vector3(64.45,16.5,369.9),Vector3(68.4,16.5,369.9),Vector3(68.4,16.5,364),Vector3(68.4,16.5,361.2),Vector3(68.4,16.5,364),Vector3(68.4,16.5,369.9),Vector3(65,16.5,369.9),Vector3(44,16.5,369.9)]
 for goal in route:
  var w:Dictionary=await walk_to(actor,goal);w.scope="retained original commons arrival,quiet portal,returns and stock doorway access";legs.append(w);record("original_player_leg_"+str(legs.size()),w.reached and w.floor_contact)
  if not errors.is_empty():break
 for root_name in ["D04StarboardAftCourtRoutes","D04PortAftCourtRoutes","D04PortCentralCommonsRearRoute"]:
  var gates:Node3D=ship.find_child(root_name,true,false)
  record("previous_route_retained_"+root_name,gates!=null)
  for gate:Node in gates.get_children():
   if "fitting"in gate:record("previous_gates_closed_and_no_visit_"+str(gate.name),gate.open_fraction==0 and not gate.desired_open and gate.visit==null)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"original_player_controller_legs":legs,"single_original_receiving_fixture_seed":true,"route_teleports":0,"source_stock_return_furniture_preserved":true,"loaded_cart_species_permissions_stock_operations_accepted":false,"ordinary_game_visual_acceptance":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_starboard_aft_commons_enclosure_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors,"legs":legs.size()}));quit(0 if errors.is_empty()else 1)
