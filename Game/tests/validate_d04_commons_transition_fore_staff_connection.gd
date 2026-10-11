extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var legs:Array=[]
func known(gate:Node3D,player:CharacterBody3D):
 var x:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();x.actor=weakref(player);x.request_id=&"fore_staff_connection_explicit_test_visit";x.court_ids.assign([gate.persistent_id]);x.active=true;x.consent_known=true;x.consent_allowed=true;gate.visit=x
func route(player:CharacterBody3D,goals:Array,label:String):
 for goal in goals:
  var row:Dictionary=await walk_to(player,vec(goal));row.label=label+"_"+str(legs.size()+1);legs.append(row);record(row.label,row.reached and row.floor_contact);print("WALK ",row.label," ",JSON.stringify(row))
func run():
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_COMMONS_TRANSITION_AND_FORE_STAFF.json"));var main=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var player:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var fore:Node3D=ship.get_node("D04PortForwardStaffCourtConnection");var space=ship.get_world_3d().direct_space_state
 record("production_fore_active",p.active and fore!=null);record("commons_candidate_absent_from_production",ship.find_child("D04CommonsShortTransitionsTestOnly",true,false)==null and not p.commons_candidate_active)
 player.global_position=Vector3(-57.0,12.03,-447);player.velocity=Vector3.ZERO;player.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 for j in range(3):
  var gate:Node3D=fore.get_node("PriorCourtGate_"+str(j));gate.interact(player);record("original_private_gate_unknown_visit_closed_"+str(j),gate.access_refused and not gate.desired_open);known(gate,player);gate.interact(player)
 var south:Node3D=fore.get_node("D04PC_CourtSouth");south.interact(player);record("fourth_private_gate_unknown_visit_closed",south.access_refused and not south.desired_open);known(south,player)
 var clean:Node3D=fore.get_node("D04PC_StaffClean");await aim(player,vec(p.fore_new_gates[1].control_at));print("STAFF_TARGET ",player.interaction_target.get_path()if player.interaction_target!=null else"null"," point=",p.fore_new_gates[1].control_at);record("normal_staff_clean_target",player.interaction_target==clean);await key_e()
 for i in range(100):await physics_frame
 record("staff_clean_original_controller_open",clean.open_fraction==1)
 await route(player,[[-53,12,-447],[-34,12,-447],[-31.75,12,-446.8],[-31.75,14.25,-455.4],[-31.75,14.25,-456.3],[-28.25,14.25,-456.3],[-28.25,16.5,-447.35]],"fore_staff_to_court")
 await aim(player,vec(p.fore_new_gates[2].control_at));record("normal_fourth_court_target",player.interaction_target==south);await key_e()
 for i in range(100):await physics_frame
 record("fourth_court_original_controller_open",south.open_fraction==1)
 await route(player,[[-28.1,16.5,-439.5],[-28.1,16.5,-424.5],[-28.1,16.5,-410.5],[-28.1,16.5,-424.5],[-28.1,16.5,-439.5],[-28.1,16.5,-443.1]],"fore_courts_out_and_back")
 south.visit.active=false;await aim(player,vec(p.fore_new_gates[2].control_at));record("inside_fourth_gate_control_target",player.interaction_target==south);await key_e()
 for i in range(100):await physics_frame
 record("revoked_visit_can_close_from_inside",not south.desired_open and south.open_fraction==0);await key_e()
 for i in range(100):await physics_frame
 record("revoked_visit_can_open_for_exit",south.open_fraction==1)
 await route(player,[[-28.25,16.5,-447.35]],"revoked_private_exit");await aim(player,vec(p.fore_new_gates[2].control_at));await key_e()
 for i in range(100):await physics_frame
 await key_e();record("revoked_visit_outside_reentry_denied",south.open_fraction==0 and not south.desired_open)
 var used:Node3D=fore.get_node("D04PC_StaffUsed");used.interact(player)
 for i in range(100):await physics_frame
 await route(player,[[-28.25,14.25,-456.3],[-31.75,14.25,-456.3],[-31.75,14.25,-455.4],[-31.75,12,-446.8],[-34,12,-447],[-53,12,-447],[-57.3,12,-447]],"fore_staff_return_shared_clean_lane")
 # Independent used-lane fixture. No continuous court-to-used/stair separation claim.
 player.global_position=Vector3(-34,12.03,-449);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 await route(player,[[-53,12,-449],[-57.3,12,-449]],"independent_used_lane_to_original_staff")
 await aim(player,vec(p.fore_new_gates[0].control_at));record("normal_staff_used_control_target",player.interaction_target==used);await key_e()
 for i in range(100):await physics_frame
 record("normal_staff_used_controller_closed",used.open_fraction==0);await key_e()
 for i in range(100):await physics_frame
 record("normal_staff_used_controller_open",used.open_fraction==1)
 for at in [[-34.4,12,-445.7],[-34.4,12,-450.25]]:record("local_staging_worker_"+str(at),capsule_clear(space,vec(at)))
 player.global_position=Vector3(-57,12.03,-459);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 await route(player,[[-57,12,-441]],"protected_original_staff_stem")
 player.global_position=Vector3(-43.8,16.53,-365.9);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for i in range(15):await physics_frame
 await route(player,[[-43.8,16.5,-331.7]],"protected_original_public_street")
 # Test-only short fittings inserted after the production and protected route checks.
 var common:Node3D=load("res://scripts/d04_commons_transition_fore_staff.gd").commons_candidate(ship)
 player.global_position=Vector3(-75,16.53,-1);player.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(player.global_position)
 for gate:Node3D in common.get_children():
  if gate.get_script()==load("res://scripts/d04_physical_service_fitting.gd"):gate.interact(player)
 for i in range(100):await physics_frame
 await route(player,[[-75,16.5,-5],[-75,16.5,-1]],"inactive_return_short_profile_test")
 player.global_position=Vector3(-71.8,16.53,-2);player.velocity=Vector3.ZERO
 for i in range(15):await physics_frame
 await route(player,[[-71.8,16.5,-5],[-71.8,16.5,-2]],"inactive_stock_short_profile_test")
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"checks_detail":checks,"controller_legs":legs,"private_court_thresholds_traversed":4,"temporary_known_private_visits_test_only":true,"production_private_consent_provider_available":false,"home_hatches_panes_tools_installed":false,"new_floor_m2":p.new_floor_m2,"commons_candidate_production_active":false,"commons_candidate_worker_traversal_test_only":true,"continuous_separated_commons_rear_route_accepted":false,"separate_upstream_clean_used_complete":false,"used_lane_walk_is_independent_fixture":true,"continuous_court_to_used_return_accepted":false,"cart_safe_vertical_accepted":false,"ordinary_game_visual_CRT_hardware_accepted":false,"model_pins":p.model_pins,"limits":p.limits};FileAccess.open("res://artifacts/d04_commons_transition_fore_staff_connection.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
