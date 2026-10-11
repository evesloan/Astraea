extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
func leg(actor:CharacterBody3D,goal:Vector3,label:String)->bool:
 var w:Dictionary=await walk_to(actor,goal);w.scope=label;legs.append(w);record("original_player_leg_"+str(legs.size()),w.reached and w.floor_contact);return w.reached
func operate(actor:CharacterBody3D,n:Node3D,p:Dictionary,index:int,want:bool)->bool:
 var spec:Dictionary=p.gates[index];var gate:Node3D=n.get_node(spec.name);await aim(actor,vec(spec.control_at));record("normal_control_targets_"+str(index)+"_"+str(legs.size()),actor.interaction_target==gate);await key_e()
 for i in range(100):await physics_frame
 print("NORMAL_OPERATION ",index," ",want," fraction=",gate.open_fraction," desired=",gate.desired_open," obstruction=",gate.obstructed," refused=",gate.access_refused," actor=",actor.global_position)
 record("original_controller_endpoint_"+str(index)+"_"+str(legs.size()),gate.open_fraction==(1.0 if want else 0.0)and gate.desired_open==want);return gate.open_fraction==(1.0 if want else 0.0)
func known_visit(gate:Node3D,actor:CharacterBody3D):
 var v:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();v.actor=weakref(actor);v.request_id=&"temporary_known_connection_visit";v.court_ids.assign([gate.persistent_id]);v.consent_known=true;v.consent_allowed=true;v.active=true;gate.visit=v
func courts(actor:CharacterBody3D,n:Node3D,p:Dictionary,branch:String,lane:float,end_z:float)->bool:
 var indices:Array=[]
 for i in range(9):
  var g:Dictionary=p.gates[i]
  if g.branch==branch and abs(float(g.lane_x)-lane)<.01:indices.append(i)
 indices.sort_custom(func(a,b):return abs(float(p.gates[a].z)-end_z)<abs(float(p.gates[b].z)-end_z))
 for i in indices:
  var g:Dictionary=p.gates[i];var gate:Node3D=n.get_node(g.name);var outside:float=g.wall_x-2.2 if lane<-40 else g.wall_x+2.2
  if not await leg(actor,Vector3(lane,16.5,g.z),"continuous enclosed court artery"):return false
  if not await leg(actor,Vector3(outside,16.5,g.z),"normal control stance outside original sweep guard"):return false
  gate.interact(actor);record("unknown_visit_refused_"+str(i),gate.access_refused and not gate.desired_open);known_visit(gate,actor)
  if not await operate(actor,n,p,i,true):return false
  if not await leg(actor,vec(g.court_stance),"temporary known private work visit"):return false
  if not await operate(actor,n,p,i,false):return false
  if not await operate(actor,n,p,i,true):return false
  if not await leg(actor,Vector3(outside,16.5,g.z),"original-player private court egress"):return false
  if not await operate(actor,n,p,i,false):return false
  gate.visit.active=false;gate.visit=null
  if not await leg(actor,Vector3(lane,16.5,g.z),"return to enclosed artery"):return false
 return errors.is_empty()
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_AFT_COURT_ROUTES.json"));var n:Node3D=ship.find_child("D04PortAftCourtRoutes",true,false)
 record("production_connected_once",n!=null and ship.find_children("D04PortAftCourtRoutes","Node3D",true,false).size()==1)
 if n==null:quit(1);return
 record("sealed_geometry",p.sealed_receipt_sha256==FileAccess.get_sha256("res://artifacts/d04_port_aft_court_routes_geometry.json"));var home=ship.find_child("D04PortAftHabitatNeighborhood",true,false);record("original_twenty_homes_twentyfive_rests",home.get_meta("preserved_home_allocations")==20 and home.get_meta("preserved_reserved_rests")==25)
 actor.global_position=Vector3(-8,16.53,405.2);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 for goal in [Vector3(-44,16.5,405.2),Vector3(-44,16.5,443.2)]:
  if not await leg(actor,goal,"original receiving street to south portal"):break
 if errors.is_empty() and await operate(actor,n,p,11,true):
  await leg(actor,Vector3(-44.3,16.5,447.35),"normal south staff entry");await operate(actor,n,p,11,false)
  for lane in [-65.0,-23.2]:
   if not errors.is_empty():break
   await leg(actor,Vector3(lane,16.5,446.6),"enclosed south cross passage");await courts(actor,n,p,"south",lane,445.4);await leg(actor,Vector3(lane,16.5,446.6),"south artery return");await leg(actor,Vector3(-44.3,16.5,447.35),"source receiving portal return")
  if errors.is_empty():await operate(actor,n,p,11,true);await leg(actor,Vector3(-44,16.5,443.2),"south public egress");await operate(actor,n,p,11,false)
 # Walk the actual broad north arrival; no reflected cross passage through its retained service room.
 if errors.is_empty():
  for goal in [Vector3(-44,16.5,405.2),Vector3(-44,16.5,369),Vector3(-44,16.5,340),Vector3(-44,16.5,310),Vector3(-44,16.5,288.7),Vector3(-23.2,16.5,288.7)]:
   if not await leg(actor,goal,"retained public receiving and wide north platform"):break
 if errors.is_empty() and await operate(actor,n,p,10,true):
  await leg(actor,Vector3(-23.0,16.5,292.65),"distinct north east arrival-edge staff entry");await operate(actor,n,p,10,false);await leg(actor,Vector3(-23.2,16.5,295),"north east corridor");await courts(actor,n,p,"north",-23.2,290.8);await leg(actor,Vector3(-22.65,16.5,292.85),"north east artery return and outside unchanged conservative guard")
  if errors.is_empty():await operate(actor,n,p,10,true);await leg(actor,Vector3(-23.2,16.5,288.7),"return to unchanged public platform");await operate(actor,n,p,10,false)
 if errors.is_empty():
  for goal in [Vector3(-44,16.5,288.7),Vector3(-44,16.5,287.4),Vector3(-49.3,16.5,287.4),Vector3(-55.7,16.5,287.4),Vector3(-55.7,16.5,291.4),Vector3(-56.8,16.5,291.4)]:
   if not await leg(actor,goal,"actual existing service access retains stocks and closed returns"):break
 if errors.is_empty() and await operate(actor,n,p,9,true):
  await leg(actor,Vector3(-60.85,16.5,291.5),"distinct north west service wall entry");await operate(actor,n,p,9,false);await leg(actor,Vector3(-65,16.5,291.4),"new west connector");await courts(actor,n,p,"north",-65,291.4);await leg(actor,Vector3(-65,16.5,291.4),"west artery return");await leg(actor,Vector3(-61.15,16.5,291.5),"west staff control stance outside unchanged guard")
  if errors.is_empty():await operate(actor,n,p,9,true);await leg(actor,Vector3(-56.8,16.5,291.4),"original service bay egress");await operate(actor,n,p,9,false)
 if errors.is_empty():
  for goal in [Vector3(-55.7,16.5,291.4),Vector3(-55.7,16.5,287.4),Vector3(-44,16.5,287.4),Vector3(-44,16.5,310),Vector3(-44,16.5,340),Vector3(-44,16.5,369.9),Vector3(-65,16.5,369.9),Vector3(-69,16.5,369.9),Vector3(-65,16.5,369.9),Vector3(-44,16.5,369.9),Vector3(-44,16.5,405.2),Vector3(-8,16.5,405.2)]:
   if not await leg(actor,goal,"retained public interfaces and commons guest arrival"):break
 record("narrow_west_court_retained_sealed",home.find_child("PASH_D04SFH_D04HC2_west_PrivacyScreen",true,false)!=null and home.find_child("PASH_D04SFH_D04HC2_west_GlassUpper",true,false)!=null)
 for spec in p.gates:
  var gate:Node3D=n.get_node(spec.name);record("gates_end_closed_"+spec.name,gate.open_fraction==0 and not gate.desired_open and gate.visit==null and String(gate.persistent_id)==spec.id)
 record("recent_commons_ceiling_correction_active",ship.find_child("D04CommonsCeilingJunctions",true,false)!=null)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"original_player_controller_legs":legs,"single_original_receiving_fixture_seed":true,"teleports_within_route":0,"known_private_visits_temporary_test_only":true,"production_private_consent_provider_available":false,"ordinary_game_visual_acceptance":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_port_aft_court_routes_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
