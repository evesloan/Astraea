extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var p:Dictionary
var walks:Array=[]
var samples:=0
var stop_witnesses:Array=[]
var package:Node3D
func walk(actor:CharacterBody3D,at:Vector3)->void:
 var q:Dictionary=await walk_to(actor,at);walks.append(q);record("walk_"+str(walks.size()),q.reached and q.floor_contact)
func moving_doors()->void:
 samples+=1;var state:=package.get_world_3d().direct_space_state
 for s in p.door_bindings:
  var door:Node3D=package.get_node(s.name)
  for leaf in door.leaves:
   for c in leaf.get_children():
    if not c is CollisionShape3D:continue
    var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;q.exclude=[leaf.get_rid()];q.margin=.0001
    var bad:Array=[]
    for h in state.intersect_shape(q,128):
     if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:bad.append(str(h.collider.get_path()))
    record("moving_leaf_"+str(samples)+s.name+str(c.name),bad.is_empty())
    if not bad.is_empty():print("FORE_LEAF_CONTACT ",s.name," ",bad)
 record("shared_buffer_axes_exclusive_"+str(samples),package.get_node("ForeSharedTransfer").exclusive_state())
func operation(actor:CharacterBody3D,name:String,want:bool)->void:
 var s:Dictionary=p.door_bindings.filter(func(q):return q.name==name)[0];var door:Node3D=package.get_node(name)
 await aim(actor,vec(s.position)+Vector3.UP*2.69);record("normal_door_target_"+name+str(want)+str(samples),actor.interaction_target==door);await key_e()
 for i in range(100):
  await physics_frame
  if i%10==0:moving_doors()
 record("door_endpoint_"+name+str(want)+str(samples),door.open_fraction==(1 if want else 0)and door.desired_open==want)
func dispatch(actor:CharacterBody3D,name:String,axis:String)->void:
 var button:Node3D=package.get_node(name);await aim(actor,button.global_position);record("normal_dispatch_"+name+axis+str(samples),actor.interaction_target==button);await key_e()
 for i in range(200):
  await physics_frame
  if i%10==0:moving_doors()
 var manager:Node3D=package.get_node("ForeSharedTransfer");record("selected_dispatch_"+axis+str(samples),not manager.switching and manager.selected_axis==axis)
func wait_stop(lift:Node3D,index:int)->void:
 for i in range(1900):
  await physics_frame
  if lift.current_floor==index and lift.phase=="idle":break
 record("stop_"+str(index),lift.current_floor==index and lift.phase=="idle")
 for j in range(17):record("landing_interlock_"+str(index)+"_"+str(j),lift.landing_gates[j].cabin_present_and_stopped==(index==j)and(lift.landing_gates[j].open_fraction>.999 if index==j else lift.landing_gates[j].open_fraction<.001))
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_fore_starboard_clinical_20261011/FORE.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var cart:Node3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart");var cart_id:=cart.get_instance_id()
 record("default_main_unadopted",ship.find_child("Group3ForeStarboardClinical",true,false)==null)
 for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256(ProjectSettings.globalize_path("res://../"+str(f)))==p.source_pins[f])
 var ids:Dictionary={"lift_persistent_id":"__validation_only_fore_starboard_lift","lift_identity_prefix":"__validation_only_fore_starboard"}
 for q in p.door_bindings:ids[q.name]="__validation_only_fore_"+q.name
 for q in p.dispatch_buttons:ids[q.name]="__validation_only_fore_"+q.name
 package=load("res://scripts/group3_fore_starboard_clinical_20261011/physical_package.gd").build(ship,ids)
 for i in range(15):await physics_frame
 record("existing_cart_not_duplicated_or_replaced",cart.get_instance_id()==cart_id and not p.duplicate_physics_cart_created and not p.original_custodial_cart_identity_or_position_changed)
 record("no_authoritative_identity_or_berth_mapping",p.authoritative_identity_map==null and package.get_meta("registered_berths_added")==0)
 var state:=ship.get_world_3d().direct_space_state
 for l in p.floor_checks:
  var at:=Vector3(21,l.floor_y,-490);var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.4);record("landing_floor_"+l.deck,not h.is_empty()and absf(h.position.y-at.y)<.002);record("landing_worker_"+l.deck,capsule_clear(state,at))
 var manager:Node3D=package.get_node("ForeSharedTransfer");record("unvalidated_sealed_return_rejected",not manager.request_axis("sealed_return"))
 # One supported fixture; every later movement uses the original player and W.
 actor.global_position=Vector3(57,12.03,-477);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 await walk(actor,Vector3(57,12,-499));await walk(actor,Vector3(57,12,-500));await walk(actor,Vector3(21,12,-500));await walk(actor,Vector3(21,12,-498.5));await operation(actor,"crew_arrival",true)
 await walk(actor,Vector3(21,12,-494.3));await operation(actor,"crew_arrival",false);await walk(actor,Vector3(21.2,12,-489.3))
 var lift:Node3D=package.get_node("ForeStarboardLift");var call:Node3D=lift.get_node("D03___validation_only_fore_starboard_lift_call")
 await aim(actor,call.global_position);record("normal_lift_call",actor.interaction_target==call);await key_e();await wait_stop(lift,2)
 await walk(actor,Vector3(21,12,-490));await walk(actor,Vector3(25,12,-490))
 var button:Node3D=lift.cabin.get_node("__validation_only_fore_starboard_cabin_D05");await aim(actor,button.global_position);record("normal_lift_D05_button",actor.interaction_target==button);await key_e();await wait_stop(lift,4)
 record("player_physically_carried_D05",actor.is_on_floor()and absf(actor.global_position.y-21)<.02)
 await walk(actor,Vector3(21,21,-490));await walk(actor,Vector3(21,21,-494.35));await dispatch(actor,"clean_dispatch","clean")
 await walk(actor,Vector3(21,21,-500));record("occupied_shared_buffer_switch_rejected",not manager.request_axis("closed")and manager.selected_axis=="clean")
 await walk(actor,Vector3(27,21,-500));await walk(actor,Vector3(33,21,-500));await operation(actor,"clean_linen_supply_entry",true)
 await walk(actor,Vector3(33,21,-496.4));await operation(actor,"clean_linen_supply_entry",false);await operation(actor,"clean_linen_supply_entry",true)
 await walk(actor,Vector3(33,21,-500));await operation(actor,"clean_linen_supply_entry",false)
 await walk(actor,Vector3(43,21,-500));await operation(actor,"maintenance_and_custodial_cart_entry",true);await walk(actor,Vector3(43,21,-496.4));await operation(actor,"maintenance_and_custodial_cart_entry",false);await operation(actor,"maintenance_and_custodial_cart_entry",true)
 await walk(actor,Vector3(43,21,-500));await operation(actor,"maintenance_and_custodial_cart_entry",false)
 await walk(actor,Vector3(57,21,-500));await walk(actor,Vector3(57,21,-472));await walk(actor,Vector3(57,21,-500));await walk(actor,Vector3(27,21,-500));await walk(actor,Vector3(21,21,-500));await walk(actor,Vector3(21,21,-494.35));await dispatch(actor,"clean_dispatch","closed")
 # Candidate dispatch predicate only; real stock/sealing is deliberately unaccepted.
 manager.sealed_load_ready=func()->bool:return true
 await dispatch(actor,"return_dispatch","sealed_return");await walk(actor,Vector3(21,21,-504));await walk(actor,Vector3(27,21,-504));await walk(actor,Vector3(43,21,-504));await operation(actor,"used_linen_and_closed_waste_entry",true)
 await walk(actor,Vector3(43,21,-507.6));await operation(actor,"used_linen_and_closed_waste_entry",false);await operation(actor,"used_linen_and_closed_waste_entry",true);await walk(actor,Vector3(43,21,-504));await operation(actor,"used_linen_and_closed_waste_entry",false)
 await walk(actor,Vector3(61,21,-504));await walk(actor,Vector3(61,21,-472));await walk(actor,Vector3(61,21,-504));await walk(actor,Vector3(27,21,-504));await walk(actor,Vector3(21,21,-504));await walk(actor,Vector3(21,21,-494.35));await dispatch(actor,"return_dispatch","closed")
 for q in p.door_bindings:record("final_door_closed_"+q.name,package.get_node(q.name).open_fraction==0 and not package.get_node(q.name).desired_open)
 record("existing_forward_stop_keys_retained",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 record("existing_D04_riser3_retained",ship.find_child("PortCentralStaffLift",true,false)!=null)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"walks":walks,"actual_door_motion_samples":samples,"source_model_pins":p.model_pins,
 "fixture_placements":1,"route_position_velocity_writes":0,"original_cart_not_duplicated":true,"normal_lift_doors_and_dispatch_RMB_E":true,
 "temporary_validation_labels_not_saved_or_registered":true,"synthetic_sealed_load_predicate_only":true,"authoritative_persistent_identity_map_created":false,"new_registered_berths":0,
 "full_medical_stock_species_loaded_cart_primary_structure_graphical_or_final_acceptance":false}
 FileAccess.open("res://artifacts/group3_fore_starboard_clinical_20261011/fore.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors,"walks":walks.size(),"door_motion_samples":samples}));quit(0 if errors.is_empty()else 1)
