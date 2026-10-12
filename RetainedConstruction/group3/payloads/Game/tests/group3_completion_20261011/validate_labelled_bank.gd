extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var p:Dictionary
var walks:Array=[]
func walk(actor:CharacterBody3D,to:Vector3)->bool:
 var w:Dictionary=await walk_to(actor,to);walks.append(w);record("walk_"+str(walks.size()),w.reached and w.floor_contact);return w.reached and w.floor_contact
func op(actor:CharacterBody3D,door:Node3D,s:Dictionary,want:bool)->void:
 await aim(actor,vec(s.position)+Vector3.UP*2.69);record("normal_target_"+s.name+str(want),actor.interaction_target==door);await key_e()
 for i in range(100):await physics_frame
 record("normal_endpoint_"+s.name+str(want),door.desired_open==want and is_equal_approx(door.open_fraction,1 if want else 0))
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_completion_20261011/LABELLED_BANK.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 record("default_main_unadopted",ship.find_child("Group3LabelledCrewBank",true,false)==null)
 load("res://scripts/group3_completion_20261011/d03_precinct.gd").build(ship)
 var bank:Node3D=load("res://scripts/group3_completion_20261011/labelled_bank.gd").build(ship)
 for i in range(15):await physics_frame
 record("exact_sixteen_labels_only",p.instances.size()==16 and p.rejected_inferred_rooms==184)
 record("no_registry_or_C036_migration",bank.get_meta("registered_berths_added")==0 and not bank.get_meta("C036_migration_applied"))
 for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256(ProjectSettings.globalize_path("res://../"+str(f)))==p.source_pins[f])
 var state:=ship.get_world_3d().direct_space_state
 for s in p.rest_surfaces:
  var at:=vec(s.surface);var h:=ray(state,at+Vector3.UP*.16,at-Vector3.UP*.08)
  record("actual_rest_"+s.reference_room_id+s.place,not h.is_empty()and bank.is_ancestor_of(h.collider)and absf(h.position.y-at.y)<.003)
 for s in p.service_doors:
  var door:Node3D=bank.get_node(s.name);door.interact(actor)
 for i in range(100):
  await physics_frame
  if i%10==0:
   for s in p.service_doors:
    var d:Node3D=bank.get_node(s.name)
    for leaf in d.leaves:
     for c in leaf.get_children():
      if not c is CollisionShape3D:continue
      var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;q.exclude=[leaf.get_rid()];q.margin=.0001
      var bad:Array=[]
      for h in state.intersect_shape(q,128):
       if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:bad.append(str(h.collider.get_path()))
      record("door_sweep_"+s.name+str(i)+str(c.get_path()),bad.is_empty());if not bad.is_empty():print("BANK_MOTION_CONTACT ",s.name," ",bad)
 for s in p.service_doors:
  var d:Node3D=bank.get_node(s.name);record("all_sixteen_open_"+s.name,d.open_fraction==1)
  var at:=vec(s.position);var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.3)
  record("entry_floor_"+s.name,not h.is_empty()and absf(h.position.y-12)<.002)
  record("entry_worker_"+s.name,capsule_clear(state,at))
  d.interact(actor)
 for i in range(100):await physics_frame
 # One source fixture; all later travel uses ordinary W input and the existing player.
 actor.global_position=Vector3(87,12.03,-45);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
 ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 await walk(actor,Vector3(87,12,-52));await walk(actor,Vector3(81.2,12,-52))
 var a:Dictionary=p.service_doors.filter(func(s):return s.name=="C125EntryGate")[0];var da:Node3D=bank.get_node(a.name)
 await op(actor,da,a,true)
 if da.open_fraction==1:
  await walk(actor,Vector3(77.0,12,-52));await op(actor,da,a,false);await op(actor,da,a,true)
  await walk(actor,Vector3(81.2,12,-52));await op(actor,da,a,false)
 await walk(actor,Vector3(87,12,-52));await walk(actor,Vector3(90.8,12,-52))
 var b:Dictionary=p.service_doors.filter(func(s):return s.name=="C175EntryGate")[0];var db:Node3D=bank.get_node(b.name)
 await op(actor,db,b,true)
 if db.open_fraction==1:
  await walk(actor,Vector3(95.0,12,-52));await op(actor,db,b,false);await op(actor,db,b,true)
  await walk(actor,Vector3(90.8,12,-52));await op(actor,db,b,false)
 await walk(actor,Vector3(87,12,-52));await walk(actor,Vector3(87,12,-45))
 for s in p.service_doors:
  var d:Node3D=bank.get_node(s.name);record("all_doors_end_closed_"+s.name,d.open_fraction==0 and not d.desired_open)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"actual_rest_surfaces":p.rest_surfaces.size(),
 "labelled_source_rooms":16,"new_registered_berths":0,"C036_migration_applied":false,"walks":walks,"single_fixture_setup":true,"route_teleports":0,
 "source_model_pins":p.model_pins,"full_400_berth_species_stock_wet_systems_structure_and_final_visual_acceptance":false}
 FileAccess.open("res://artifacts/group3_completion_20261011/labelled_bank.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"checks":result.checks,"errors":errors,"walks":walks.size(),"actual_rest_surfaces":32}));quit(0 if errors.is_empty()else 1)
