extends "res://tests/group3_fore_starboard_clinical_20261011/validate_fore.gd"
var motion_samples:=0
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
    record("private_leaf_"+str(samples)+s.name+str(c.name),bad.is_empty())
    if not bad.is_empty():print("PRIVATE_LEAF_CONTACT ",s.name," ",bad)
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_starboard3_private_20261011/PRIVATE.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 record("default_main_unadopted",ship.find_child("Group3Starboard3Private",true,false)==null)
 for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256(ProjectSettings.globalize_path("res://../"+str(f)))==p.source_pins[f])
 var ids:Dictionary={"lift_persistent_id":"__validation_only_starboard3_lift","lift_identity_prefix":"__validation_only_starboard3"}
 for q in p.door_bindings:ids[q.name]="__validation_only_starboard3_"+q.name
 package=load("res://scripts/group3_starboard3_private_20261011/physical_package.gd").build(ship,ids)
 for i in range(15):await physics_frame
 record("no_authoritative_identity_or_berth_mapping",p.authoritative_identity_map==null and package.get_meta("registered_berths_added")==0)
 var state:=ship.get_world_3d().direct_space_state
 for l in p.floor_checks:
  for z in [-86.0,-82.3,-80.1,-79.5]:
   var at:=Vector3(21,l.floor_y,z);var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.4);record("arrival_floor_"+l.deck+str(z),not h.is_empty()and absf(h.position.y-at.y)<.002)
   if z!=-80.1:record("arrival_worker_"+l.deck+str(z),capsule_clear(state,at))
 # One supported fixture on retained fore apron; all later walking is original W.
 actor.global_position=Vector3(21,12.03,-78.5);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 var d03:Node3D=package.get_node("private_arrival_D03");await operation(actor,"private_arrival_D03",false);record("unknown_external_permission_denied",d03.authorization_denied and not d03.desired_open)
 d03.can_enter=func(_actor:CharacterBody3D)->bool:return true
 await operation(actor,"private_arrival_D03",true);await walk(actor,Vector3(21,12,-82.3));await operation(actor,"private_arrival_D03",false);await walk(actor,Vector3(21.2,12,-85.3))
 var lift:Node3D=package.get_node("Starboard3Lift");var call:Node3D=lift.get_node("D03___validation_only_starboard3_lift_call")
 await aim(actor,call.global_position);record("normal_lift_call",actor.interaction_target==call);await key_e();await wait_stop(lift,2)
 await walk(actor,Vector3(21,12,-86));await walk(actor,Vector3(25,12,-86))
 var button:Node3D=lift.cabin.get_node("__validation_only_starboard3_cabin_D05");await aim(actor,button.global_position);record("normal_D05_cabin_button",actor.interaction_target==button);await key_e();await wait_stop(lift,4)
 record("player_carried_D05",actor.is_on_floor()and absf(actor.global_position.y-21)<.02)
 await walk(actor,Vector3(21,21,-86));await walk(actor,Vector3(21,21,-82.3));await operation(actor,"private_arrival_D05",true)
 await walk(actor,Vector3(21,21,-78.5));await operation(actor,"private_arrival_D05",false);await operation(actor,"private_arrival_D05",false)
 record("inside_egress_then_unknown_external_reentry_denied",package.get_node("private_arrival_D05").authorization_denied and not package.get_node("private_arrival_D05").desired_open)
 for index in range(17):
  record("empty_request_"+str(index),lift.request_floor(index))
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
     if not bad.is_empty():print("PRIVATE_CABIN_CONTACT ",contact.name," ",bad)
   if lift.current_floor==index and lift.phase=="idle":break
  await wait_stop(lift,index);stop_witnesses.append({"deck":lift.deck_numbers[index],"floor_y":lift.cabin.position.y,"phase":lift.phase})
 record("original_D04_port_riser3_retained",ship.find_child("PortCentralStaffLift",true,false)!=null)
 record("original_fore_port_stop_binding_retained",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 for q in p.door_bindings:record("final_private_gate_closed_"+q.deck,package.get_node(q.name).open_fraction==0 and not package.get_node(q.name).desired_open)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"walks":walks,"empty_cabin_motion_samples":motion_samples,"stop_witnesses":stop_witnesses,"actual_door_motion_samples":samples,"source_model_pins":p.model_pins,"disclosed_setup_placements":1,"route_position_velocity_writes":0,"temporary_validation_labels_and_synthetic_permission_not_saved_or_registered":true,"inside_egress_and_unknown_external_entry_covered":true,"full_identity_district_species_loaded_cart_egress_engineering_graphical_or_final_acceptance":false}
 FileAccess.open("res://artifacts/group3_starboard3_private_20261011/private.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors,"walks":walks.size(),"motion_samples":motion_samples,"door_samples":samples,"stop_witnesses":stop_witnesses.size()}));quit(0 if errors.is_empty()else 1)
