extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var p:Dictionary
var walks:Array=[]
var supervisor:Node3D
var package:Node3D
var empty_lift_stop_witnesses:Array=[]
var cabin_motion_samples:=0
func walk(actor:CharacterBody3D,at:Vector3)->bool:
 var q:Dictionary=await walk_to(actor,at);walks.append(q);record("walk_"+str(walks.size()),q.reached and q.floor_contact);return q.reached and q.floor_contact
func wait_lift(lift:Node3D,index:int)->void:
 for i in range(1900):
  await physics_frame
  if lift.current_floor==index and lift.phase=="idle":break
 record("lift_idle_at_"+str(index),lift.current_floor==index and lift.phase=="idle")
 for j in range(lift.landing_gates.size()):
  record("lift_gate_interlock_"+str(index)+"_"+str(j),lift.landing_gates[j].cabin_present_and_stopped==(j==index)and(lift.landing_gates[j].open_fraction>.999 if j==index else lift.landing_gates[j].open_fraction<.001))
func motion_witnesses(i:int)->void:
 record("axes_exclusive_"+str(i),supervisor.exclusive_state())
 var state:=package.get_world_3d().direct_space_state
 for s in p.door_bindings:
  var d:Node3D=package.get_node(s.name)
  for leaf in d.leaves:
   for c in leaf.get_children():
    if not c is CollisionShape3D:continue
    var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;q.exclude=[leaf.get_rid()];q.margin=.0001
    var bad:Array=[]
    for h in state.intersect_shape(q,128):
     if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:bad.append(str(h.collider.get_path()))
    record("actual_crossing_leaf_clear_"+str(i)+"_"+s.name+"_"+str(c.get_path()),bad.is_empty())
    if not bad.is_empty():print("CROSSING_MOTION_CONTACT ",s.name," ",bad)
func gate_request(actor:CharacterBody3D,s:Dictionary,axis:String)->void:
 var door:Node3D=package.get_node(s.name)
 await aim(actor,vec(s.position)+Vector3.UP*2.69);record("normal_target_"+s.name+axis,actor.interaction_target==door);await key_e()
 for i in range(200):
  await physics_frame
  if i%10==0:motion_witnesses(i)
 record("axis_selected_"+s.name+axis,not supervisor.switching and supervisor.selected_axis==axis)
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_port2_clinical_20261011/PHYSICAL.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 record("default_main_unadopted",ship.find_child("Group3Port2ClinicalPhysical",true,false)==null)
 for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256(ProjectSettings.globalize_path("res://../"+str(f)))==p.source_pins[f])
 # Temporary fixture labels exercise the existing APIs; these are never saved,
 # registered, or proposed as authoritative reservation/person/berth identities.
 var fixture:Dictionary={"lift_persistent_id":"__validation_only_port2_lift","lift_identity_prefix":"__validation_only_port2"}
 for key in ["clean_north","clean_south","sealed_load_east","sealed_load_west"]:fixture[key]="__validation_only_port2_"+key
 package=load("res://scripts/group3_port2_clinical_20261011/physical_package.gd").build(ship,fixture);supervisor=package.get_node("ClinicalCrossing")
 for i in range(15):await physics_frame
 record("no_authoritative_identity_or_berth_mapping",not package.get_meta("authoritative_identity_mapping")and package.get_meta("registered_berths_added")==0 and p.authoritative_identity_map==null)
 record("existing_D04_riser3_preserved",ship.find_child("PortCentralStaffLift",true,false)!=null)
 record("existing_forward_stop_list_preserved",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 var state:=ship.get_world_3d().direct_space_state
 for landing in p.floor_checks:
  var at:=Vector3(-21,landing.floor_y,-283);var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.4)
  record("actual_landing_floor_"+landing.deck,not h.is_empty()and absf(h.position.y-at.y)<.002)
  record("actual_landing_worker_"+landing.deck,capsule_clear(state,at))
 var lift:Node3D=package.get_node("Port2Lift");record("all_seventeen_source_stops",lift.floor_heights==p.controller_binding.floor_heights and lift.deck_numbers.size()==17)
 record("unsealed_return_rejected",not supervisor.request_axis("sealed_return")and supervisor.selected_axis=="closed")
 actor.global_position=Vector3(-21.2,12.03,-283.7);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 var call:Node3D=lift.get_node("D03___validation_only_port2_lift_call")
 await aim(actor,call.global_position);record("normal_call_target",actor.interaction_target==call);await key_e();await wait_lift(lift,2)
 await walk(actor,Vector3(-21,12,-283));await walk(actor,Vector3(-25,12,-283))
 var button:Node3D=lift.cabin.get_node("__validation_only_port2_cabin_D05")
 await aim(actor,button.global_position);record("normal_cabin_D05_target",actor.interaction_target==button);await key_e();await wait_lift(lift,4)
 record("player_physically_carried_to_D05",absf(actor.global_position.y-21)<.02 and actor.is_on_floor())
 await walk(actor,Vector3(-21,21,-283));await walk(actor,Vector3(-21,21,-288));await walk(actor,Vector3(-21,21,-293));await walk(actor,Vector3(-57,21,-293))
 var south:Dictionary=p.door_bindings.filter(func(s):return s.name=="clean_south")[0]
 await gate_request(actor,south,"clean")
 await walk(actor,Vector3(-57,21,-297))
 supervisor.sealed_load_ready=func()->bool:return true
 record("occupied_buffer_switch_rejected",not supervisor.request_axis("sealed_return")and supervisor.selected_axis=="clean")
 await walk(actor,Vector3(-57,21,-301.1));await walk(actor,Vector3(-57,21,-297));await walk(actor,Vector3(-57,21,-293));await gate_request(actor,south,"closed")
 await walk(actor,Vector3(-21,21,-293));await walk(actor,Vector3(-21,21,-297));await walk(actor,Vector3(-52.5,21,-297))
 var east:Dictionary=p.door_bindings.filter(func(s):return s.name=="sealed_load_east")[0]
 await gate_request(actor,east,"sealed_return");await walk(actor,Vector3(-61,21,-297));await walk(actor,Vector3(-61,21,-305));await walk(actor,Vector3(-61,21,-297))
 record("close_after_return_axis",supervisor.request_axis("closed"))
 for i in range(200):
  await physics_frame
  if i%10==0:motion_witnesses(i)
 for s in p.door_bindings:record("crossing_end_closed_"+s.name,package.get_node(s.name).open_fraction==0 and not package.get_node(s.name).desired_open)
 # Exercise every authored stop with the existing lift API and its physical
 # cabin/gates. Player stays outside; this is an empty-cabin sweep, not seventeen
 # normal player arrivals or loaded-cart/species boarding acceptance.
 for index in range(17):
  record("existing_empty_lift_request_"+str(index),lift.request_floor(index))
  for frame in range(1900):
   await physics_frame
   if frame%30==0:
    cabin_motion_samples+=1
    for contact in lift.cabin.get_children():
     if not contact is CollisionShape3D:continue
     var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.exclude=[lift.cabin.get_rid()];q.margin=.0001
     var bad:Array=[]
     for h in state.intersect_shape(q,128):
      if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:bad.append(str(h.collider.get_path()))
     record("empty_cabin_motion_"+str(cabin_motion_samples)+"_"+str(contact.name),bad.is_empty())
     if not bad.is_empty():print("CABIN_STATIC_CONTACT ",contact.name," ",bad)
   if lift.current_floor==index and lift.phase=="idle":break
  await wait_lift(lift,index);empty_lift_stop_witnesses.append({"deck":lift.deck_numbers[index],"y":lift.cabin.position.y,"phase":lift.phase})
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"walks":walks,
 "seventeen_landing_source_floors":17,"existing_controllers_used":true,"normal_lift_and_crossing_RMB_E_inputs":true,
 "fixture_setup_placements":1,"route_position_velocity_writes":0,"new_registered_berths":0,"persistent_identity_map_created":false,
 "validation_fixture_labels_only_not_saved_or_registered":true,"sealed_load_predicate_is_synthetic_test_fixture":true,
 "empty_cabin_stop_witnesses":empty_lift_stop_witnesses,"empty_cabin_motion_samples":cabin_motion_samples,
 "clinical_sterility_inventory_original_identity_species_loaded_cart_engineering_final_art_accepted":false,"source_model_pins":p.model_pins}
 FileAccess.open("res://artifacts/group3_port2_clinical_20261011/physical.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors,"walks":walks.size()}));quit(0 if errors.is_empty()else 1)
