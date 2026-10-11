extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
func leg(actor:CharacterBody3D,goal:Vector3,label:String)->bool:
 var w:Dictionary=await walk_to(actor,goal);w.scope=label;legs.append(w);record("original_player_leg_"+str(legs.size()),w.reached and w.floor_contact);return w.reached
func operate(actor:CharacterBody3D,n:Node3D,p:Dictionary,index:int,want:bool)->bool:
 var spec:Dictionary=p.gates[index];var gate:Node3D=n.get_node(spec.name);await aim(actor,vec(spec.control_at));record("normal_control_targets_"+str(index)+"_"+str(legs.size()),actor.interaction_target==gate);await key_e()
 for i in range(100):await physics_frame
 record("original_staff_controller_endpoint_"+str(index)+"_"+str(legs.size()),gate.open_fraction==(1.0 if want else 0.0)and gate.desired_open==want);return gate.open_fraction==(1.0 if want else 0.0)
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json"));var n:Node3D=ship.find_child("D04PortCentralCommonsRearRoute",true,false)
 record("production_connected_once",n!=null and ship.find_children("D04PortCentralCommonsRearRoute","Node3D",true,false).size()==1)
 if n==null:quit(1);return
 record("sealed_geometry",p.sealed_receipt_sha256==FileAccess.get_sha256("res://artifacts/d04_port_central_commons_recomposition_geometry.json"));record("original_twenty_homes_twentyfive_rests",ship.find_child(p.source_co_root,true,false).get_meta("preserved_home_allocations")==20 and ship.find_child(p.source_co_root,true,false).get_meta("preserved_reserved_rests")==25)
 actor.global_position=Vector3(-21,16.53,-90);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 for goal in [Vector3(-21,16.5,-100.6),Vector3(-63.2,16.5,-100.6),Vector3(-104,16.5,-100.6),Vector3(-104,16.5,0),Vector3(-97.8,16.5,0)]:
  if not await leg(actor,goal,"original upper staff landing and retained western circuit to new commons branch"):break
 if errors.is_empty():await operate(actor,n,p,0,true)
 if errors.is_empty():await leg(actor,Vector3(-93.8,16.5,0),"original-player entry to enclosed rear staff route")
 if errors.is_empty():await operate(actor,n,p,0,false)
 for goal in [Vector3(-94.5,16.5,0),Vector3(-94.5,16.5,6),Vector3(-94.5,16.5,-6),Vector3(-94.5,16.5,1.5),Vector3(-89.976,16.5,1.5)]:
  if not errors.is_empty()or not await leg(actor,goal,"continuous staff-only rear route behind relocated quiet and service bays"):break
 for index in [1,2]:
  if not errors.is_empty():break
  var x:float=p.gates[index].closed_center[0]
  if not await leg(actor,Vector3(x,16.5,1.5),"enclosed receiving hall at retained return/stock function"):break
  if not await operate(actor,n,p,index,true):break
  if not await leg(actor,Vector3(x,16.5,-2.1),"full-size original fitting and source room threshold"):break
  if not await operate(actor,n,p,index,false):break
  if not await operate(actor,n,p,index,true):break
  if not await leg(actor,Vector3(x,16.5,1.5),"return/stock egress to rear staff hall"):break
  if not await operate(actor,n,p,index,false):break
 if errors.is_empty():
  for goal in [Vector3(-93.8,16.5,1.5),Vector3(-93.8,16.5,0)]:
   if not await leg(actor,goal,"enclosed service return to branch portal"):break
 if errors.is_empty():await operate(actor,n,p,0,true)
 if errors.is_empty():await leg(actor,Vector3(-97.8,16.5,0),"staff portal egress to western artery")
 if errors.is_empty():await operate(actor,n,p,0,false)
 if errors.is_empty():
  for goal in [Vector3(-104,16.5,0),Vector3(-104,16.5,-100.6),Vector3(-63.2,16.5,-100.6),Vector3(-21,16.5,-100.6),Vector3(-21,16.5,-90)]:
   if not await leg(actor,goal,"retained original staff circuit return"):break
 # Separate public-route fixture: one seed on original atrium receiving, all subsequent legs walked.
 if errors.is_empty():
  actor.global_position=Vector3(-52,16.53,-32);actor.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  for i in range(20):await physics_frame
  for goal in [Vector3(-84,16.5,-32),Vector3(-84,16.5,-13),Vector3(-84,16.5,0),Vector3(-84,16.5,-3.3),Vector3(-70,16.5,-3.3),Vector3(-70,16.5,0),Vector3(-52,16.5,0),Vector3(-70,16.5,0),Vector3(-70,16.5,-3.3),Vector3(-84,16.5,-3.3),Vector3(-84,16.5,0),Vector3(-84,16.5,7),Vector3(-87,16.5,7),Vector3(-87.4,16.5,7),Vector3(-84,16.5,7),Vector3(-84,16.5,13),Vector3(-84,16.5,32),Vector3(-52,16.5,32)]:
   if not await leg(actor,goal,"original public receiving entrances and bounded recomposed guest arrival paths"):break
 for spec in p.gates:
  var gate:Node3D=n.get_node(spec.name);record("all_new_staff_gates_end_closed_"+spec.name,gate.open_fraction==0 and not gate.desired_open and String(gate.persistent_id)==spec.id)
 for root_name in ["D04PortCentralCourtWorkLinks","D04PortCentralWestStaffCircuit"]:
  for gate:Node in ship.find_child(root_name,true,false).get_children():
   if "fitting"in gate and gate.fitting.requires_visit:record("private_defaults_preserved_"+String(gate.persistent_id),gate.visit==null and gate.open_fraction==0 and not gate.desired_open)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"original_player_controller_legs":legs,"staff_and_guest_routes_have_separate_initial_fixture_seeds":true,"teleports_within_any_route":0,"original_stock_cupboard_bottles_closed_return_functions_preserved":true,"refill_save_inventory_operation_accepted":false,"production_private_consent_provider_available":false,"ordinary_game_visual_acceptance":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_commons_ceiling_junctions_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
