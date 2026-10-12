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
 # Conservative complete-source fixture: install original medical receiving
 # models and retain them for this geometry/operation run. No source is altered.
 var stream:Node3D=ship.get_node("ShipSystems/RemainingBatchStreaming");stream.set_physics_process(false);var loaded_original_programmes:Array=[]
 for item in stream.entries:
  if not str(item.key).begins_with("D05_directory_"):continue
  var room:Node3D=stream.rooms[str(item.key)]
  if not room.get_meta("stream_loaded",false):load("res://scripts/remaining_batch_receiving.gd").install(ship,item,room)
  loaded_original_programmes.append(str(item.key))
 for i in range(5):await physics_frame
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
 var state:=ship.get_world_3d().direct_space_state;var rows:Array=[]
 for z in [-455.0,-454.0,-452.0,-451.0,-434.0,-433.0,-431.0,-430.0]:
  for x in [-61.0,-61.4,-61.8,-62.0,-62.4]:
   var at:=Vector3(x,21,z);var q:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;q.shape=shape;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925)
   var bad:Array=[]
   for h in state.intersect_shape(q,128):bad.append(str(h.collider.get_path()))
   for delta in [Vector3(.3,0,0),Vector3(0,0,.3)]:
    var h:=ray(state,at+Vector3.UP-delta,at+Vector3.UP+delta)
    if not h.is_empty()and str(h.collider.get_path())not in bad:bad.append(str(h.collider.get_path()))
   rows.append({"position":[x,21,z],"contacts":bad})
 var result={"status":"ACTUAL_ALL_D05_SOURCE_RETURN_STANCE_DIAGNOSTIC","rows":rows,"originals_or_registry_modified":false,"original_D05_sources_loaded":loaded_original_programmes}
 FileAccess.open("res://artifacts/group3_clinical_full_20261011/return_stance.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"rows":rows.size(),"blocked":rows.filter(func(r):return not r.contacts.is_empty()).size()}));quit()
