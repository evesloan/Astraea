extends "res://tests/validate_d04_court_controls_staff_candidate.gd"
var p:Dictionary
var package:Node3D
var samples:=0
var actual_leaf_checks:=0
var walks:Array=[]
func moving()->void:
 samples+=1;var state:=package.get_world_3d().direct_space_state
 for s in p.door_bindings:
  var gate:Node3D=package.get_node(s.name)
  for leaf in gate.leaves:
   var c:CollisionShape3D=leaf.get_node("DimensionedLeafContact");var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;q.exclude=[leaf.get_rid()];q.margin=.0001
   var bad:Array=[]
   for hit in state.intersect_shape(q,128):
    if hit.collider is StaticBody3D and not hit.collider is AnimatableBody3D:bad.append(str(hit.collider.get_path()))
   record("actual_leaf_"+str(samples)+s.name+str(leaf.name),bad.is_empty());actual_leaf_checks+=1
   if not bad.is_empty():print("CLINICAL_LEAF_CONTACT ",s.name," ",bad)
  var a:=PhysicsShapeQueryParameters3D.new();var c:CollisionShape3D=gate.leaves[0].get_node("DimensionedLeafContact");a.shape=c.shape;a.transform=c.global_transform;a.exclude=[gate.leaves[0].get_rid()];a.margin=.0001
  var other:=false
  for h in state.intersect_shape(a,128):
   if h.collider==gate.leaves[1]:other=true
  record("opposed_leaves_do_not_interpenetrate_"+str(samples)+s.name,not other)
 for row in p.crossings:record("axes_exclusive_"+str(samples)+row.programme_key,package.get_node(row.programme_key).exclusive_state())
func settle(n:int=260)->void:
 for i in range(n):
  await physics_frame
  if i%20==0:moving()
func walk(actor:CharacterBody3D,at:Vector3)->void:
 var q:Dictionary=await walk_to(actor,at);walks.append(q);record("walk_"+str(walks.size()),q.reached and q.floor_contact)
func button(actor:CharacterBody3D,name:String,mode:String)->void:
 var n:Node3D=package.get_node(name);await aim(actor,n.global_position);record("normal_button_target_"+name+str(samples),actor.interaction_target==n);await key_e();await settle()
 record("normal_selected_mode_"+name+mode+str(samples),n.supervisor.selected_axis==mode and not n.supervisor.switching)
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CLINICAL.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player")
 record("main_unadopted",ship.find_child("Group3CompleteClinical",true,false)==null)
 for f in p.source_pins:record("source_pin_"+str(f),FileAccess.get_sha256(ProjectSettings.globalize_path("res://../"+str(f)))==p.source_pins[f])
 var old:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_port2_clinical_20261011/PHYSICAL.json"));var old_ids:Dictionary={}
 for key in old.supplied_identity_map_required:old_ids[key]="__validation_only_full_port2_"+key
 var prior:Node3D=load("res://scripts/group3_port2_clinical_20261011/physical_package.gd").build(ship,old_ids)
 load("res://scripts/group3_fore_starboard_clinical_20261011/physical_package.gd").build(ship)
 var ids:Dictionary={}
 for d in p.door_bindings:ids[d.name]="__validation_only_full_"+d.name
 for row in p.crossings:
  for d in row.dispatch_buttons:ids[d.name]="__validation_only_full_"+d.name
 package=load("res://scripts/group3_clinical_full_20261011/physical_package.gd").build(ship,ids)
 for i in range(20):await physics_frame
 record("bounded_port2_selection_replaced_once",prior.get_node_or_null("AST-MED-G3-006")==null)
 record("no_authoritative_keys_or_berths",p.authoritative_identity_map==null and p.authoritative_operation_IDs==null and package.get_meta("registered_berths_added")==0)
 # Empty-fixture initialization through the existing managers; not evidence of
 # normal input. The separate button trial below supplies that evidence.
 record("prior_port2_fixture_clean",prior.get_node("ClinicalCrossing").request_axis("clean"))
 for row in p.crossings:
  var manager:Node3D=package.get_node(row.programme_key);record("unvalidated_return_rejected_"+row.programme_key,not manager.request_axis("sealed_return"));record("fixture_initial_clean_"+row.programme_key,manager.request_axis("clean"))
 await settle()
 var state:=ship.get_world_3d().direct_space_state;var probes:=0;var held_probes:=0
 for route in p.routes:
  var path:Array=route.proposed_centerline_xz
  for j in range(path.size()-1):
   var a:=Vector3(path[j][0],21,path[j][1]);var b:=Vector3(path[j+1][0],21,path[j+1][1]);var count:=int(ceil(a.distance_to(b)/.5))
   for i in range(count+1):
    var at:=a.lerp(b,float(i)/count);var hold:=false
    for h in p.held_support_spans:
     var r:Array=h.bounds_xz
     if at.x>=r[0]-.31 and at.x<=r[2]+.31 and at.z>=r[1]-.31 and at.z<=r[3]+.31:hold=true
    if hold:held_probes+=1;continue
    # Return longitudinal routes use the outer half of their original3.6m
    # width at controlled-crossing pockets; centerline cannot cross a jamb.
    if str(route.id).begins_with("soiled_return"):
     for c in p.crossings:
      var r:Array=c.source_outer_bounds_xz
      if at.z>=r[1]-1 and at.z<=r[3]+1 and absf(at.x-(r[0]if at.x<0 else r[2]))<.01:at.x+=-1.0 if at.x<0 else 1.0
    var floor:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.4);record("route_floor_"+str(probes),not floor.is_empty()and absf(floor.position.y-21)<.002)
    record("route_worker_"+str(probes),capsule_clear(state,at));probes+=1
 # One original supported actor setup; no writes along the route afterward.
 actor.global_position=Vector3(57,21.03,-472);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(actor.global_position)
 for i in range(20):await physics_frame
 await walk(actor,Vector3(57,21,-407.3));await button(actor,"D05_directory_02_clean_dispatch","closed");await button(actor,"D05_directory_02_clean_dispatch","clean")
 await walk(actor,Vector3(57,21,-402));var trial:Node3D=package.get_node("D05_directory_02");record("occupied_crossing_switch_rejected",not trial.request_axis("closed")and trial.selected_axis=="clean")
 await walk(actor,Vector3(57,21,-394));await walk(actor,Vector3(57,21,-178));await walk(actor,Vector3(57,21,-70));await walk(actor,Vector3(102,21,-70));await walk(actor,Vector3(102,21,38));await walk(actor,Vector3(102,21,70));await walk(actor,Vector3(57,21,70));await walk(actor,Vector3(57,21,254));await walk(actor,Vector3(57,21,470))
 # Empty-buffer sealed mode trial uses a disclosed synthetic load predicate.
 for row in p.crossings:
  var manager:Node3D=package.get_node(row.programme_key)
  if not row.sealed_return_available:record("support_hold_return_denied",not manager.request_axis("sealed_return"));continue
  manager.sealed_load_ready=func()->bool:return true
  record("synthetic_sealed_request_"+row.programme_key,manager.request_axis("sealed_return"))
 await settle(400)
 for row in p.crossings:
  var manager:Node3D=package.get_node(row.programme_key)
  record("sealed_endpoint_or_held_clean_"+row.programme_key,manager.selected_axis==("sealed_return"if row.sealed_return_available else"clean")and not manager.switching)
  record("final_close_request_"+row.programme_key,manager.request_axis("closed"))
 await settle(400)
 for d in p.door_bindings:record("final_gate_closed_"+d.name,package.get_node(d.name).open_fraction==0 and not package.get_node(d.name).desired_open)
 record("original_fore_port_stop_binding_retained",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 record("original_D04_port_riser3_retained",ship.find_child("PortCentralStaffLift",true,false)!=null)
 physical_key(false)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks.size(),"errors":errors,"walks":walks,"route_worker_floor_probes":probes,"held_support_probes_omitted":held_probes,"actual_leaf_motion_checks":actual_leaf_checks,"motion_samples":samples,"crossings":10,"sliding_gates":40,"fixture_actor_setup_placements":1,"route_position_velocity_writes":0,"fixture_initial_clean_mode_requests_disclosed":true,"normal_RMB_E_dispatch_trial":true,"synthetic_sealed_load_only":true,"temporary_validation_labels_not_saved_or_registered":true,"source_model_pins":p.model_pins,"whole_starboard_return_medical_receiver_stock_sterility_species_loaded_cart_primary_structure_graphical_or_final_acceptance":false}
 FileAccess.open("res://artifacts/group3_clinical_full_20261011/full.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "))
 print(JSON.stringify({"status":result.status,"checks":checks.size(),"errors":errors,"walks":walks.size(),"probes":probes,"held_probes":held_probes,"actual_leaf_checks":actual_leaf_checks}));quit(0 if errors.is_empty()else 1)
