extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var p:Dictionary
var walks:Array=[]
var stop_witnesses:Array=[]
var motion_samples:=0
func walk(actor:CharacterBody3D,at:Vector3)->void:
 var q:Dictionary=await walk_to(actor,at);walks.append(q);record("walk_"+str(walks.size()),q.reached and q.floor_contact)
func await_stop(lift:Node3D,index:int)->void:
 for i in range(1900):
  await physics_frame
  if lift.current_floor==index and lift.phase=="idle":break
 record("stop_"+lift.name+str(index),lift.current_floor==index and lift.phase=="idle")
 for j in range(17):record("gate_interlock_"+lift.name+str(index)+str(j),lift.landing_gates[j].cabin_present_and_stopped==(j==index)and(lift.landing_gates[j].open_fraction>.999 if j==index else lift.landing_gates[j].open_fraction<.001))
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_risers_20261011/AFT_PAIR.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 record("default_main_unadopted",ship.find_child("Group3AftRiserPair",true,false)==null)
 for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256(ProjectSettings.globalize_path("res://../"+str(f)))==p.source_pins[f])
 var fixtures:Dictionary={}
 for site in p.sites:fixtures[site.reservation_id]={"lift_persistent_id":"__validation_only_"+site.reservation_id,"lift_identity_prefix":"__validation_only_"+site.reservation_id}
 var package:Node3D=load("res://scripts/group3_remaining_risers_20261011/aft_pair.gd").build(ship,fixtures)
 for i in range(15):await physics_frame
 record("no_registered_berths_or_authoritative_map",package.get_meta("registered_berths_added")==0 and not package.get_meta("authoritative_identity_mapping"))
 record("existing_D01_shared_circuit",ship.find_child("LowerSharedAftStaffRoute",true,false)!=null)
 record("existing_D04_riser3",ship.find_child("PortCentralStaffLift",true,false)!=null)
 var state:=ship.get_world_3d().direct_space_state
 for site in p.sites:
  var sign:float=-1 if site.center_xz[0]<0 else 1
  for l in site.floor_checks:
   var at:=Vector3(sign*21,l.floor_y,490);var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.4)
   record("landing_floor_"+site.reservation_id+l.deck,not h.is_empty()and absf(h.position.y-at.y)<.002)
   record("landing_worker_"+site.reservation_id+l.deck,capsule_clear(state,at))
  var lift:Node3D=package.get_node(site.reservation_id);var prefix:String=fixtures[site.reservation_id].lift_identity_prefix
  actor.global_position=Vector3(sign*21.2,12.03,489.3 if sign<0 else 490.7);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
  ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  for i in range(20):await physics_frame
  var call:Node3D=lift.get_node("D03_"+prefix+"_lift_call");await aim(actor,call.global_position);record("normal_call_"+site.reservation_id,actor.interaction_target==call);await key_e();await await_stop(lift,2)
  await walk(actor,Vector3(sign*21,12,490));await walk(actor,Vector3(sign*25,12,490))
  var button:Node3D=lift.cabin.get_node(prefix+"_cabin_D05");await aim(actor,button.global_position);record("normal_cabin_button_"+site.reservation_id,actor.interaction_target==button);await key_e();await await_stop(lift,4)
  record("player_carried_to_D05_"+site.reservation_id,absf(actor.global_position.y-21)<.02 and actor.is_on_floor())
  await walk(actor,Vector3(sign*21,21,490));await walk(actor,Vector3(sign*21,21,486))
  for index in range(17):
   record("empty_request_"+site.reservation_id+str(index),lift.request_floor(index))
   for frame in range(1900):
    await physics_frame
    if frame%30==0:
     motion_samples+=1
     for contact in lift.cabin.get_children():
      if not contact is CollisionShape3D:continue
      var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.exclude=[lift.cabin.get_rid()];q.margin=.0001
      var bad:Array=[]
      for h in state.intersect_shape(q,128):
       if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:bad.append(str(h.collider.get_path()))
      record("actual_cabin_motion_"+str(motion_samples)+str(contact.name),bad.is_empty())
      if not bad.is_empty():print("AFT_CABIN_CONTACT ",site.reservation_id," ",contact.name," ",bad)
    if lift.current_floor==index and lift.phase=="idle":break
   await await_stop(lift,index);stop_witnesses.append({"reservation_id":site.reservation_id,"deck":lift.deck_numbers[index],"floor_y":lift.cabin.position.y,"phase":lift.phase})
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"walks":walks,"source_model_pins":p.model_pins,
 "disclosed_independent_fixture_placements":2,"route_position_velocity_writes":0,"empty_cabin_motion_samples":motion_samples,"all_stop_witnesses":stop_witnesses,
 "temporary_validation_labels_not_saved_or_registered":true,"authoritative_persistent_identity_mapping_created":false,"registered_berths_added":0,
 "D01_D04_originals_modified":false,"district_joins_species_loaded_cart_engineering_final_art_accepted":false}
 FileAccess.open("res://artifacts/group3_remaining_risers_20261011/aft_pair.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors,"walks":walks.size(),"stop_witnesses":stop_witnesses.size(),"motion_samples":motion_samples}));quit(0 if errors.is_empty()else 1)
