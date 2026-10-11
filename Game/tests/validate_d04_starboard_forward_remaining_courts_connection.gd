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
 var g:Dictionary=gate.fitting;var outside:Array=[23.2 if g.branch=="south"else 24.0,16.5,g.z]
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
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_REMAINING_COURTS.json"));var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var districts:Node3D=ship.get_node("ShipSpace/Districts");var n:Node3D=districts.get_node("D04StarboardForwardRemainingCourts");var east:Node3D=districts.get_node("D04StarboardForwardWorkBranches");var commons:Node3D=ship.find_child("D04StarboardFullCommons",true,false)
 record("production_connected_once",p.active and ship.find_children("D04StarboardForwardRemainingCourts","Node3D",true,false).size()==1);record("original20homes25rests",commons.get_meta("preserved_home_allocations")==20 and commons.get_meta("preserved_reserved_rests")==25);record("port_central_commons_candidate_inactive",not JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json")).commons_candidate_active)
 player.global_position=Vector3(58,12.03,-381.2);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(20):await physics_frame
 await route(player,[[61.6,12,-381.2],[61.6,12,-371.3],[64.45,12,-371.3],[64.45,14.25,-381.3],[67.95,14.25,-381.3],[67.95,16.5,-372.3],[67.95,16.5,-369.5],[60,16.5,-369.5],[43.8,16.5,-369.5],[43.8,16.5,-405.2],[23.2,16.5,-405.2]],"retained_shared_stair_commons_public_cross_passage")
 await open_normal(player,n.get_node(p.gates[5].name),"west_south_staff_portal")
 await route(player,[[23.2,16.5,-413.5]],"west_south_first_approach");await court_visit(player,n.get_node(p.gates[0].name),"west_south_first_court")
 await route(player,[[23.2,16.5,-427.7]],"west_south_second_approach");await court_visit(player,n.get_node(p.gates[1].name),"west_south_second_court")
 await route(player,[[23.2,16.5,-443.7]],"west_south_short_approach");await court_visit(player,n.get_node(p.gates[2].name),"west_south_short_court")
 await route(player,[[23.2,16.5,-405.2],[43.8,16.5,-405.2],[43.8,16.5,-334.5],[43.8,16.5,-288.7],[23.2,16.5,-288.7]],"shared_public_spine_and_original_north_cross_passage")
 await open_normal(player,n.get_node(p.gates[6].name),"west_north_staff_portal")
 await route(player,[[23.2,16.5,-312.1]],"west_north_first_approach");await court_visit(player,n.get_node(p.gates[4].name),"west_north_first_court")
 await route(player,[[23.2,16.5,-327.2]],"west_north_second_approach");await court_visit(player,n.get_node(p.gates[3].name),"west_north_second_court")
 await route(player,[[23.2,16.5,-288.7],[43.8,16.5,-288.7],[43.8,16.5,-334.5],[43.8,16.5,-369.5],[60,16.5,-369.5],[71,16.5,-369.5],[71,16.5,-377],[72,16.5,-382]],"west_return_original_shared_commons")
 var ep:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_STARBOARD_FORWARD_WORK_BRANCHES.json"));await open_normal(player,east.get_node(ep.gates[4].name),"retained_east_south_staff_portal")
 await route(player,[[72,16.5,-386.4],[65.2,16.5,-386.4],[65.2,16.5,-427.7],p.narrow_court_exterior_stance,[65.2,16.5,-427.7]],"sealed_narrow_east_exterior_stance_out_and_back")
 for suffix in ["_Floor","_Roof","_PrivacyScreen","_GlassUpper"]:record("narrow_source_preserved_"+suffix,districts.get_node("D04StarboardSouthHomeCandidates").find_child(p.narrow_court_unchanged_source_prefix+suffix,true,false)!=null)
 for g in ep.gates.slice(0,4):
  var old_gate:Node3D=east.get_node(g.name);old_gate.interact(player);record("retained_east_private_unknown_visit_refused_"+g.name,old_gate.access_refused and not old_gate.desired_open and old_gate.open_fraction==0 and old_gate.visit==null)
 await route(player,[[65.2,16.5,-386.4],[72,16.5,-386.4],[72,16.5,-380],[71,16.5,-377],[71,16.5,-364],[71,16.5,-361],[71,16.5,-364],[75.9,16.5,-364],[75.9,16.5,-361]],"original_stock_closed_returns")
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"checks_detail":checks,"controller_legs":legs,"private_court_thresholds_traversed":5,"all_six_remaining_court_approaches_addressed":true,"narrow_court_sealed_exterior_stance_only":true,"narrow_court_entry_or_reach_accepted":false,"temporary_known_private_visits_test_only":true,"production_private_consent_provider_available":false,"all_five_revoked_egress_and_outside_reentry_denial_tested":true,"shared_original_stair_commons_lower_approach_and_public_passages":true,"continuous_clean_used_segregation_accepted":false,"cart_safe_vertical_accepted":false,"ordinary_game_visual_CRT_hardware_accepted":false,"model_pins":p.model_pins,"limits":p.limits};FileAccess.open("res://artifacts/d04_starboard_forward_remaining_courts_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
