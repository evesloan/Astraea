extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var p:Dictionary
var walks:Array=[]
var scenario_placements:=0
func source_pins()->void:
 for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256(ProjectSettings.globalize_path("res://../"+str(f)))==p.source_pins[f])
func step(actor:CharacterBody3D,to:Vector3)->bool:
 var w:Dictionary=await walk_to(actor,to);walks.append(w)
 record("walk_"+str(walks.size()),w.reached and w.floor_contact);return w.reached and w.floor_contact
func operation(actor:CharacterBody3D,door:Node3D,spec:Dictionary,want:bool)->void:
 await aim(actor,vec(spec.position)+Vector3.UP*2.69)
 record("normal_target_"+spec.name+str(want),actor.interaction_target==door)
 await key_e()
 for i in range(100):
  await physics_frame
  if i%10==0:
   for leaf in door.leaves:
    for c in leaf.get_children():
     if not c is CollisionShape3D:continue
     var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;q.exclude=[leaf.get_rid()];q.margin=.0001
     var conflicts:Array=[]
     for h in door.get_world_3d().direct_space_state.intersect_shape(q,128):
      if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:conflicts.append(str(h.collider.get_path()))
     record("actual_leaf_clear_"+spec.name+str(want)+str(i)+str(c.get_path()),conflicts.is_empty())
     if not conflicts.is_empty():print("MOVING_CONTACT ",spec.name," ",conflicts)
 record("endpoint_"+spec.name+str(want),door.desired_open==want and is_equal_approx(door.open_fraction,1.0 if want else 0.0)and not door.obstructed)
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_completion_20261011/D03_PRECINCT.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 source_pins();record("default_main_unmodified_and_unadopted",ship.find_child("Group3D03ReceivingPrecincts",true,false)==null)
 var precinct:Node3D=load("res://scripts/group3_completion_20261011/d03_precinct.gd").build(ship)
 for i in range(15):await physics_frame
 record("no_new_registered_berths",precinct.get_meta("registered_berths_added")==0)
 record("existing_forward_lift_unchanged",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 record("existing_D01_shared_route_unchanged",ship.find_child("LowerSharedAftStaffRoute",true,false)!=null)
 var state:=ship.get_world_3d().direct_space_state
 for side in [-1,1]:
  for z in range(-39,40,3):
   var at:=Vector3(-102 if side==-1 else 103,12,z);var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.3)
   record("source_floor_"+str(at),not h.is_empty()and absf(h.position.y-12)<.002)
   record("source_worker_"+str(at),capsule_clear(state,at))
 for j in range(p.service_doors.size()):
  var spec:Dictionary=p.service_doors[j];var door:Node3D=precinct.get_node(spec.name)
  var x:float=103 if j==1 else -102 if j==0 else 57
  var z:float=float(spec.position[2]);var first:=Vector3(x,12.03,z-6)
  # Separate independent precincts each start at one supported original-controller fixture.
  # These three setup placements are disclosed; no position/velocity writes within a route.
  actor.global_position=first;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);scenario_placements+=1
  ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
  for i in range(20):await physics_frame
  if not await step(actor,Vector3(x,12,z)):continue
  var outside:=Vector3(float(spec.position[0])+(2.2 if j>0 else -2.2),12,z)
  if j==2:outside.x=56.4
  if not await step(actor,outside):continue
  await operation(actor,door,spec,true)
  if door.open_fraction<.999:continue
  var inside:=Vector3(float(spec.position[0])-(2.0 if j>0 else -2.0),12,z)
  if not await step(actor,inside):continue
  await operation(actor,door,spec,false)
  await operation(actor,door,spec,true)
  if await step(actor,outside):await operation(actor,door,spec,false)
  await step(actor,Vector3(x,12,z));await step(actor,first-Vector3.UP*.03)
 for spec in p.service_doors:
  var door:Node3D=precinct.get_node(spec.name);record("door_end_closed_"+spec.name,not door.desired_open and door.open_fraction==0)
 physical_key(false)
 var focus:=InputEventMouseButton.new();focus.button_index=MOUSE_BUTTON_RIGHT;focus.pressed=false;Input.parse_input_event(focus)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"walks":walks,
 "independent_precinct_setup_placements":scenario_placements,"route_position_velocity_writes":0,
 "original_player_service_door_and_light_controllers":true,"shared_root_not_edited":true,
 "source_model_pins":p.model_pins,"normal_RMB_E_operation":true,"new_floor_m2":p.new_floor_m2,
 "full_G3_or_400_berth_acceptance":false,"loaded_cart_species_sterile_operations_structural_capacity_final_art_accepted":false}
 FileAccess.open("res://artifacts/group3_completion_20261011/d03_precinct.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors,"walks":walks.size()}));quit(0 if errors.is_empty()else 1)
