extends "res://tests/validate_d04_commons_receiving_routes.gd"
var legs:Array=[]
func leg(actor:CharacterBody3D,goal:Vector3,label:String)->bool:
 var w:Dictionary=await walk_to(actor,goal);w.scope=label;legs.append(w);record("original_controller_leg_"+str(legs.size()),w.reached and w.floor_contact);return w.reached
func visit_court(actor:CharacterBody3D,p:Dictionary,n:Node3D,index:int,lane_x:float)->bool:
 var g:Dictionary=p.gates[index];var gate:Node3D=n.get_node(g.name)
 if not await leg(actor,Vector3(lane_x,16.5,g.z),"screened staff perimeter to private work threshold"):return false
 gate.interact(actor);record("private_request_without_provider_refused_"+str(index),gate.access_refused and not gate.desired_open and gate.open_fraction==0)
 var visit:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();visit.actor=weakref(actor);visit.request_id=StringName("scoped_route_temporary_visit_"+str(index));visit.court_ids.assign([gate.persistent_id]);visit.consent_known=true;visit.consent_allowed=true;visit.active=true;gate.visit=visit;gate.interact(actor)
 for i in range(100):await physics_frame
 record("original_fitting_controller_opens_"+str(index),gate.open_fraction==1)
 if not await leg(actor,vec(g.court_stance),"private work stance; narrowcourt uses recessed edge stance only"):return false
 visit.active=false;record("original_egress_after_temporary_visit_revoked_"+str(index),gate.egress_allowed(actor))
 if not await leg(actor,Vector3(lane_x,16.5,g.z),"private court egress to screened staff perimeter"):return false
 gate.interact(actor)
 for i in range(100):await physics_frame
 record("private_gate_closes_"+str(index),gate.open_fraction==0 and not gate.desired_open);return true
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT.json"));var n:Node3D=ship.find_child("D04PortCentralWestStaffCircuit",true,false)
 record("connected_exactly_once",n!=null and ship.find_children("D04PortCentralWestStaffCircuit","Node3D",true,false).size()==1)
 if n==null:quit(1);return
 record("geometry_seal",p.sealed_receipt_sha256==FileAccess.get_sha256("res://artifacts/d04_port_central_west_staff_circuit_geometry.json"));record("retained_port_central_capacity",ship.find_child("D04PortCentralHabitatNeighborhood",true,false).get_meta("preserved_home_allocations")==20 and ship.find_child("D04PortCentralHabitatNeighborhood",true,false).get_meta("preserved_reserved_rests")==25)
 actor.global_position=Vector3(-21,16.53,-90);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 for goal in [Vector3(-21,16.5,-100.6),Vector3(-63.2,16.5,-100.6),Vector3(-104,16.5,-100.6)]:
  if not await leg(actor,goal,"retained upper landing/used lane through exact staff-wall aperture"):break
 var visited:Array=[]
 for index in [2,1,0,3,4]:
  if not errors.is_empty():break
  if await visit_court(actor,p,n,index,-104):visited.append(p.gates[index].id)
 if errors.is_empty():
  for goal in [Vector3(-104,16.5,78),Vector3(-63.2,16.5,78)]:
   if not await leg(actor,goal,"southern perimeter bypass beyond retained public street/court ends"):break
 for index in [6,5]:
  if not errors.is_empty():break
  if await visit_court(actor,p,n,index,-63.2):visited.append(p.gates[index].id)
 record("all_seven_remaining_work_thresholds_traversed",visited.size()==7)
 if errors.is_empty():
  for goal in [Vector3(-63.2,16.5,78),Vector3(-104,16.5,78),Vector3(-104,16.5,-100.6),Vector3(-63.2,16.5,-100.6),Vector3(-21,16.5,-100.6),Vector3(-21,16.5,-90)]:
   if not await leg(actor,goal,"connected staff circuit return to original upper landing"):break
 # Public-route checks are separate initial seeds, never service crossings.
 for z in [-32,0,32]:
  var west:float=-80 if z!=0 else -62
  actor.global_position=Vector3(-52,16.53,z);actor.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  for i in range(20):await physics_frame
  for goal in [Vector3(west,16.5,z),Vector3(-52,16.5,z)]:
   if not await leg(actor,goal,"retained public receiving branch unchanged"):break
 physical_key(false)
 var result:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"controller_legs":legs,"private_court_thresholds_traversed":visited,"temporary_private_visits_for_route_test_only":true,"production_private_consent_provider_available":false,"loaded_cart_or_unrelated_gameplay_tests":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_port_central_west_staff_circuit_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
