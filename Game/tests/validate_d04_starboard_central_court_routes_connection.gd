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
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_CENTRAL_COURT_ROUTES.json"));var n:Node3D=ship.find_child("D04StarboardCentralCourtRoutes",true,false)
 record("production_connected_once",n!=null and ship.find_children("D04StarboardCentralCourtRoutes","Node3D",true,false).size()==1)
 if n==null:quit(1);return
 record("sealed_geometry",p.sealed_receipt_sha256==FileAccess.get_sha256("res://artifacts/d04_starboard_central_court_routes_geometry.json"));var home=ship.find_child("D04StarboardCentralHabitatNeighborhood",true,false);record("original_twenty_homes_twentyfive_rests",home.get_meta("preserved_home_allocations")==20 and home.get_meta("preserved_reserved_rests")==25)
 actor.global_position=Vector3(52,16.53,-32);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 for goal in [Vector3(84,16.5,-32),Vector3(84,16.5,-73.2)]:
  if not await leg(actor,goal,"original atrium receiving to south staff threshold"):break
 # One original receiving seed only; both loops and public connections are walked.
 for branch in ["south","north"]:
  if not errors.is_empty():break
  var sign_value:float=-1 if branch=="south"else 1;var entry:int=10 if branch=="south"else 9
  if branch=="north":
   for goal in [Vector3(84,16.5,-32),Vector3(84,16.5,0),Vector3(84,16.5,32),Vector3(84,16.5,73.2)]:
    if not await leg(actor,goal,"unchanged public house street and commons through route"):break
  if not errors.is_empty():break
  if not await operate(actor,n,p,entry,true):break
  if not await leg(actor,Vector3(84.3,16.5,sign_value*77.35),"normal staff portal entry to source-supported cross passage"):break
  if not await operate(actor,n,p,entry,false):break
  for side in ["west","east"]:
   var lane:float=63.2 if side=="west"else 105
   if not await leg(actor,Vector3(lane,16.5,sign_value*76.6),"enclosed cross passage to outer court artery"):break
   var indices:Array=[]
   for i in range(9):
    var g:Dictionary=p.gates[i]
    if g.branch==branch and abs(float(g.lane_x)-lane)<.01:indices.append(i)
   # Move along the artery from the end towards the original receiving side.
   indices.sort_custom(func(a,b):return abs(float(p.gates[a].z))>abs(float(p.gates[b].z)))
   for i in indices:
    var g:Dictionary=p.gates[i];var gate:Node3D=n.get_node(g.name);var outside:float=g.wall_x-2.2 if side=="west"else g.wall_x+2.2
    if not await leg(actor,Vector3(lane,16.5,g.z),"continuous enclosed artery to private work threshold"):break
    if not await leg(actor,Vector3(outside,16.5,g.z),"walked control stance within original2.5m interaction range and outside unchanged sweep guard"):break
    gate.interact(actor);record("unknown_private_visit_refused_"+str(i),gate.access_refused and not gate.desired_open);known_visit(gate,actor)
    if not await operate(actor,n,p,i,true):break
    if not await leg(actor,vec(g.court_stance),"temporary known visit at full-size private court fitting"):break
    if not await operate(actor,n,p,i,false):break
    if not await operate(actor,n,p,i,true):break
    if not await leg(actor,Vector3(outside,16.5,g.z),"private court egress with original player"):break
    if not await operate(actor,n,p,i,false):break
    gate.visit.active=false;gate.visit=null
    if not await leg(actor,Vector3(lane,16.5,g.z),"return from control stance to enclosed artery"):break
   if not errors.is_empty():break
   if side=="east"and branch=="north":record("narrow_court_remains_sealed",home.find_child("SCK_D04HC2_west_PrivacyScreen",true,false)!=null and home.find_child("SCK_D04HC2_west_GlassUpper",true,false)!=null)
   if not await leg(actor,Vector3(lane,16.5,sign_value*76.6),"return along retained enclosed court artery"):break
   if not await leg(actor,Vector3(84.3,16.5,sign_value*77.35),"cross passage return to normal receiving portal"):break
  if not errors.is_empty():break
  if not await operate(actor,n,p,entry,true):break
  if not await leg(actor,Vector3(84,16.5,sign_value*73.2),"normal staff portal egress to original public receiving"):break
  if not await operate(actor,n,p,entry,false):break
 if errors.is_empty():
  for goal in [Vector3(84,16.5,32),Vector3(52,16.5,32),Vector3(84,16.5,32),Vector3(84,16.5,0),Vector3(52,16.5,0)]:
   if not await leg(actor,goal,"original receiving interfaces and commons guest arrival preserved"):break
 for spec in p.gates:
  var gate:Node3D=n.get_node(spec.name);record("all_new_gates_end_closed_"+spec.name,gate.open_fraction==0 and not gate.desired_open and gate.visit==null and String(gate.persistent_id)==spec.id)
 var commons:Node3D=ship.find_child("D04PortCentralCommonsRearRoute",true,false);record("approved_port_central_commons_connected",commons!=null)
 for spec in JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_COMMONS_RECOMPOSITION.json")).gates:
  var gate:Node3D=commons.get_node(spec.name);record("approved_commons_staff_ids_and_defaults_"+spec.name,gate.open_fraction==0 and not gate.desired_open and String(gate.persistent_id)==spec.id)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"model_pins":p.model_pins,"geometry_seal_sha256":p.sealed_receipt_sha256,"original_player_controller_legs":legs,"single_original_receiving_fixture_seed":true,"teleports_within_route":0,"known_private_visits_temporary_test_only":true,"production_private_consent_provider_available":false,"ordinary_game_visual_acceptance":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_starboard_central_court_routes_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
