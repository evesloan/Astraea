extends "res://tests/group3_fore_starboard_clinical_20261011/validate_fore.gd"
var motion_samples:=0
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_fore_starboard_clinical_20261011/FORE.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 var ids:Dictionary={"lift_persistent_id":"__validation_only_fore_starboard_lift","lift_identity_prefix":"__validation_only_fore_starboard"}
 for q in p.door_bindings:ids[q.name]="__validation_only_fore_"+q.name
 for q in p.dispatch_buttons:ids[q.name]="__validation_only_fore_"+q.name
 package=load("res://scripts/group3_fore_starboard_clinical_20261011/physical_package.gd").build(ship,ids)
 for i in range(15):await physics_frame
 var state:=ship.get_world_3d().direct_space_state
 for a in [[29.95,21,-497.15],[32.5,21,-496.9],[35.6,21,-495.7],[40.05,21,-495.95],[45.5,21,-494.1],[40.7,21,-507.55],[42.55,21,-507.2],[45.45,21,-507.2]]:
  var at:=vec(a);var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.4)
  record("operator_floor_"+str(a),not h.is_empty()and absf(h.position.y-at.y)<.002);record("operator_clear_"+str(a),capsule_clear(state,at))
 # Supported setup outside transfer and lift swing: no transported person,
 # load, or registered identity is introduced for the empty-cabin test.
 actor.global_position=Vector3(21,12.03,-494.35);actor.velocity=Vector3.ZERO;ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 var lift:Node3D=package.get_node("ForeStarboardLift")
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
     if not bad.is_empty():print("FORE_CABIN_CONTACT ",contact.name," ",bad)
   if lift.current_floor==index and lift.phase=="idle":break
  await wait_stop(lift,index);stop_witnesses.append({"deck":lift.deck_numbers[index],"floor_y":lift.cabin.position.y,"phase":lift.phase})
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"empty_cabin_motion_samples":motion_samples,"stop_witnesses":stop_witnesses,"source_model_pins":p.model_pins,"disclosed_setup_placements":1,"route_position_velocity_writes":0,"temporary_validation_labels_not_saved_or_registered":true,"full_medical_stock_species_loaded_cart_engineering_graphical_or_final_acceptance":false}
 FileAccess.open("res://artifacts/group3_fore_starboard_clinical_20261011/fore_stops.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors,"empty_cabin_motion_samples":motion_samples,"stop_witnesses":stop_witnesses.size()}));quit(0 if errors.is_empty()else 1)
