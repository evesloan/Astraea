extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
func route(player:CharacterBody3D,goals:Array,label:String):
 for goal in goals:
  var row:Dictionary=await walk_to(player,vec(goal));row.label=label+"_"+str(legs.size()+1);legs.append(row);record(row.label,row.reached and row.floor_contact);print("WALK ",row.label," ",JSON.stringify(row))
  if not row.reached:break
func known(gate:Node3D,player:CharacterBody3D):
 var x:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();x.actor=weakref(player);x.request_id=&"starboard_branch_explicit_test_visit";x.court_ids.assign([gate.persistent_id]);x.active=true;x.consent_known=true;x.consent_allowed=true;gate.visit=x
func open_normal(player:CharacterBody3D,gate:Node3D,label:String):
 await aim(player,vec(gate.fitting.control_at));record(label+"_normal_target",player.interaction_target==gate);await key_e()
 for i in range(100):await physics_frame
 record(label+"_normal_controller_open",gate.open_fraction==1)
func court_visit(player:CharacterBody3D,gate:Node3D,label:String):
 var g:Dictionary=gate.fitting;var outside:Array=[64.7 if g.branch=="south"else 64.1,16.5,g.z]
 await route(player,[outside],label+"_staff_stance");await aim(player,vec(g.control_at));record(label+"_normal_private_target",player.interaction_target==gate);await key_e();record(label+"_unknown_private_closed",gate.access_refused and not gate.desired_open)
 known(gate,player);await key_e()
 for i in range(100):await physics_frame
 record(label+"_known_test_visit_opens",gate.open_fraction==1);await route(player,[g.court_stance],label+"_court_enter")
 gate.visit.active=false;await aim(player,vec(g.control_at));record(label+"_inside_control_target",player.interaction_target==gate);await key_e()
 for i in range(100):await physics_frame
 record(label+"_revoked_inside_closes",gate.open_fraction==0);await key_e()
 for i in range(100):await physics_frame
 record(label+"_revoked_inside_exit_opens",gate.open_fraction==1);await route(player,[outside],label+"_revoked_private_exit")
 await aim(player,vec(g.control_at));await key_e()
 for i in range(100):await physics_frame
 await key_e();record(label+"_revoked_outside_reentry_denied",gate.open_fraction==0 and not gate.desired_open)
 await route(player,[[g.lane_x,16.5,g.z]],label+"_return_to_lane")
func run():
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_WORK_BRANCHES.json"));var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var n:Node3D=ship.get_node("ShipSpace/Districts/D04StarboardForwardWorkBranches");var commons:Node3D=ship.find_child("D04StarboardFullCommons",true,false)
 record("production_connected_once",p.active and ship.find_children("D04StarboardForwardWorkBranches","Node3D",true,false).size()==1);record("original20homes25rests",commons.get_meta("preserved_home_allocations")==20 and commons.get_meta("preserved_reserved_rests")==25);record("port_central_commons_candidate_inactive",not JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json")).commons_candidate_active)
 player.global_position=Vector3(58,12.03,-381.2);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(20):await physics_frame
 await route(player,[[61.6,12,-381.2],[61.6,12,-371.3],[64.45,12,-371.3],[64.45,14.25,-381.3],[67.95,14.25,-381.3],[67.95,16.5,-372.3],[67.95,16.5,-364],[71,16.5,-364],[71,16.5,-377],[72,16.5,-382]],"existing_shared_approach_stair_commons")
 await open_normal(player,n.get_node(p.gates[4].name),"south_staff_portal")
 await route(player,[[72,16.5,-386.4],[65.2,16.5,-386.4],[65.2,16.5,-413.5]],"south_receiving_branch")
 await court_visit(player,n.get_node(p.gates[0].name),"south_first_court")
 await route(player,[[65.2,16.5,-443.7]],"south_short_court_approach")
 await court_visit(player,n.get_node(p.gates[1].name),"south_short_court")
 await route(player,[[65.2,16.5,-386.4],[72,16.5,-386.4],[72,16.5,-380],[71,16.5,-377],[71,16.5,-364],[64.5,16.5,-364],[64.5,16.5,-357.2]],"south_return_shared_commons_north_approach")
 await open_normal(player,n.get_node(p.gates[5].name),"north_staff_portal")
 await route(player,[[64.5,16.5,-354.6],[64.5,16.5,-327.2]],"north_receiving_branch")
 await court_visit(player,n.get_node(p.gates[2].name),"north_first_court")
 await route(player,[[64.5,16.5,-312.1]],"north_second_court_approach")
 await court_visit(player,n.get_node(p.gates[3].name),"north_second_court")
 await route(player,[[64.5,16.5,-354.6],[64.5,16.5,-364],[71,16.5,-364],[71,16.5,-361],[71,16.5,-364],[75.9,16.5,-364],[75.9,16.5,-361]],"north_return_original_stock_closed_returns")
 # Independent representative original public route; no new endpoint connection claim.
 player.global_position=Vector3(60,16.53,-369.5);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(20):await physics_frame
 await route(player,[[70,16.5,-369.5],[70,16.5,-364.8],[78.4,16.5,-364.8],[78.4,16.5,-360.3],[81.25,16.5,-360.3]],"retained_public_activity_quiet")
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"checks_detail":checks,"controller_legs":legs,"private_court_thresholds_traversed":4,"temporary_known_private_visits_test_only":true,"production_private_consent_provider_available":false,"all_four_revoked_egress_and_outside_reentry_denial_tested":true,"shared_original_lower_approach_stair_commons":true,"continuous_clean_used_segregation_accepted":false,"closed_staging_dock_is_static_source_geometry":true,"cart_safe_vertical_accepted":false,"ordinary_game_visual_CRT_hardware_accepted":false,"model_pins":p.model_pins,"limits":p.limits};FileAccess.open("res://artifacts/d04_starboard_forward_work_branches_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
