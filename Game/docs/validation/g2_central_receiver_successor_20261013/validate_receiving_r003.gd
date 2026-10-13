extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var failures:Array=[]
var legs:Array=[]
var confirmed_bearings:=0
const OUT="/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/RECEIVING_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for path in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(path,true))
 call_deferred("run")
func frames(n:int)->void:
 for i in range(n):await physics_frame
func receipt()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_CURRENT_CENTRAL_ADJUNCT_CARE_RECEIVING"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"original_controller_legs":legs,"completion_adjuncts_selected":1,"completion_luxury_homes_selected":0,"care_kits_selected":1,"source_floor_m2":80,"missing_connector_m2":39.654,"actual_positive_bearing_contacts":confirmed_bearings,"all_original_D16_D17_profilewalls_and_contacts_retained":true,"primary_wall_cuts":0,"bounded_guard_successor_parts":3,"guard_crossing_width_m":1.8,"new_compiler_owners":0,"operating_private_admission_or_service":false,"beam_primary_structure_capacity_and_lower_section_accepted":false,"clinical_streaming_and_support_holds_unchanged":true,"capacity_credit":0,"full_build_accepted":false},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);receipt();push_error(label);quit(1)
 return ok
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(30)
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget");var space:=ship.get_world_3d().direct_space_state
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/group2_central_receiving_20261013/RECEIVING.json"));var old:Node3D=ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms/D17_starboard_house_extension");var originals:Array=[]
 for mesh:MeshInstance3D in old.find_children("*","MeshInstance3D",true,false):originals.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"bounds":mesh.get_aabb()})
 var shapes:Array=[]
 for c:CollisionShape3D in old.find_children("*","CollisionShape3D",true,false):shapes.append({"node":c,"shape":c.shape,"pose":c.global_transform})
 if not require(not originals.is_empty()and not shapes.is_empty(),"ActualoriginalD17receiver captured"):return
 for path in p.model_pins:
  if not require(FileAccess.get_sha256("res://"+str(path))==str(p.model_pins[path]),"Exactsource modelpin "+str(path)):return
 var wall_arch:Node3D=ship.find_child("StarboardHouseUpperArchitecture",true,false);var wall_pre:Array=[]
 for mesh:MeshInstance3D in wall_arch.find_children("*","MeshInstance3D",true,false):
  if str(mesh.name).begins_with("HC_ProfileWall_D16")or str(mesh.name).begins_with("HC_ProfileWall_D17"):wall_pre.append({"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform,"bounds":mesh.get_aabb(),"contacts":mesh.find_children("*","CollisionShape3D",true,false)})
 if not require(not wall_pre.is_empty(),"ActualretainedD16D17 profilewalls captured"):return
 var bearings:=0
 for part in p.parts:
  var a:Array=part.bounds_xyz;var shape:=BoxShape3D.new();shape.size=Vector3(a[1]-a[0],a[3]-a[2],a[5]-a[4]);var q:=PhysicsShapeQueryParameters3D.new();shape.margin=.001;q.shape=shape;q.margin=.0001;q.transform=Transform3D(Basis.IDENTITY,Vector3((a[0]+a[1])/2.,(a[2]+a[3])/2.,(a[4]+a[5])/2.));var hits:Array=space.intersect_shape(q,128)
  for hit in hits:
   var declared_fascia:bool=str(hit.collider.get_path()).ends_with("AST-COM-003/HC_Fascia_D17_0_4_0/StaticContact");var declared_guard:=false
   for row in p.guard_successor.rows:
    if str(hit.collider.get_path()).ends_with("AST-COM-003/"+str(row.name)+"/StaticContact")and part.kind in ["guard_post","guard_rail"]:declared_guard=true
   if not require(old.is_ancestor_of(hit.collider)or declared_fascia or declared_guard,"No undeclaredframe/floor/guard preimage "+str(part.name)+" "+str(hit.collider.get_path())):return
  if part.kind=="frame_bearing_on_original_D17":
   if not require(not hits.is_empty(),"Actualpositive retainedslab bearing "+str(part.name)):return
   bearings+=1;confirmed_bearings+=1
 if not require(bearings==14,"All14lappedbearings meetactualoriginalD17slab"):return
 var witnesses:Array=[]
 for x in [79.1,81.,84.,87.,88.9]:
  for z in [-23.9,-22.,-20.,-18.,-16.1]:witnesses.append(Vector3(x,102.+((z+14.37)/.3)*.025 if x<60.9 and z>=-14.37 else 102.,z))
 for x in [59.2,60.,64.,68.,72.,76.,80.9]:
  for z in [-15.9,-15.1,-14.3]:witnesses.append(Vector3(x,102.+((z+14.37)/.3)*.025 if x<60.9 and z>=-14.37 else 102.,z))
 witnesses.append(Vector3(60,102.0225,-14.1))
 for at:Vector3 in witnesses:
  if not require(ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02).is_empty(),"Exactnewfloor receiving preimage "+str(at)):return
 var saved_guards:Array=[]
 for row in p.guard_successor.rows:
  var mesh:MeshInstance3D=wall_arch.find_child(str(row.name),true,false);saved_guards.append({"node":mesh,"parent":mesh.get_parent(),"body":mesh.get_node("StaticContact"),"shape_node":mesh.get_node("StaticContact/SharedShape"),"material_override":mesh.material_override,"transform":mesh.global_transform})
 var fascia:MeshInstance3D=wall_arch.find_child("HC_Fascia_D17_0_4_0",true,false);var fascia_mesh:Mesh=fascia.mesh;var fascia_shape:Shape3D=fascia.get_node("StaticContact/SharedShape").shape
 var addition:Node3D=load("res://scripts/group2_central_receiving_20261013/package.gd").build(ship);await frames(4)
 for row in originals:
  var mesh:MeshInstance3D=row.node
  if not require(is_instance_valid(mesh)and mesh.mesh==row.mesh and mesh.global_transform==row.pose and mesh.get_aabb()==row.bounds,"OriginalD17floor mesh exact"):return
 for row in shapes:
  var c:CollisionShape3D=row.node
  if not require(is_instance_valid(c)and c.shape==row.shape and c.global_transform==row.pose,"OriginalD17floor contact exact"):return
 for at:Vector3 in witnesses:
  var h:=ray(space,at+Vector3.UP*.02,at-Vector3.UP*.02)
  if not require(not h.is_empty()and addition.get_node("ReceivingFrame").is_ancestor_of(h.collider)and absf(h.position.y-at.y)<.002,"Newdeclaredfloororconnection support "+str(at)):return
 for row in wall_pre:
  var mesh:MeshInstance3D=row.node
  if not require(is_instance_valid(mesh)and mesh.mesh==row.mesh and mesh.global_transform==row.pose and mesh.get_aabb()==row.bounds,"Exact originalprofilewall retained "+str(mesh.name)):return
  for shape in row.contacts:
   if not require(is_instance_valid(shape)and mesh.is_ancestor_of(shape),"Originalprofilewall contact retained"):return
 for row in saved_guards:
  if not require(row.node.get_parent()==row.parent and row.node.get_node("StaticContact")==row.body and row.node.get_node("StaticContact/SharedShape")==row.shape_node and row.node.material_override==row.material_override and row.node.global_transform==row.transform,"Originalguard node/body/material/pose identity retained"):return
 if not require(fascia.mesh==fascia_mesh and fascia.get_node("StaticContact/SharedShape").shape==fascia_shape,"Originalfascia mesh/contact unchanged"):return
 for x in [58.5,60.,61.5]:
  var hit:Dictionary=ray(space,Vector3(x,102.7,-14.2),Vector3(x,102.7,-13.8))
  if not require(hit.is_empty()if x==60. else not hit.is_empty(),"Boundedguard crossing withflanking protection "+str(x)):return
 var section:Node3D=addition.get_node("StarboardCentralSourceAdjunct");var counter:MeshInstance3D=section.get_node("RetainedSource").find_child("CareStoneSurface",true,false);var cb:AABB=counter.global_transform*counter.get_aabb()
 if not require(cb.position.distance_to(Vector3(80.44999694824219,102.83999633789062,-23.549999237060547))<.001 and cb.end.distance_to(Vector3(81.44999694824219,102.9000015258789,-21.700000762939453))<.001,"Actualimmutablecarecounter sourcepreimage"):return
 if not require(addition.find_children("*","OmniLight3D",true,false).size()==2,"Exactlytwo retainedsourcefixtures"):return
 for l:Light3D in addition.find_children("*","Light3D",true,false):
  if not require(budget.sources.count(l)==1,"Single originalfixture registration"):return
 var clinical:Node3D=ship.get_node("ShipSpace/Group3CompleteClinical")
 if not require(clinical.find_children("*","OmniLight3D",true,false).size()==193 and not clinical.get_meta("clinical_operational_acceptance")and not clinical.get_meta("operating_gates_or_dispatch_admitted"),"Clinical physicalfixtures andholds retained"):return
 actor.global_position=Vector3(60,102.03,-12);actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);await frames(25)
 if not require(actor.is_on_floor(),"OriginalD17receiver supportedstart"):return
 for goal:Vector3 in [Vector3(60,102,-15.1),Vector3(80,102,-15.1),Vector3(80,102,-17),Vector3(82.8,102,-17),Vector3(82.8,102,-20.8),Vector3(80.94999694824219,102,-21.000000762939454),Vector3(82.8,102,-20.8),Vector3(82.8,102,-17),Vector3(80,102,-17),Vector3(80,102,-15.1),Vector3(60,102,-15.1),Vector3(60,102,-12)]:
  var leg:Dictionary=await walk_to(actor,goal);legs.append(leg)
  if not require(leg.reached and leg.floor_contact,"Originalcontroller adjunct/connection/care route"):return
 if not require(not addition.get_meta("operating_private_admission_or_service")and not addition.get_meta("primary_structure_capacity_or_lower_section_accepted")and not section.get_meta("capacity_migrated"),"No operational/engineering/capacity acceptance"):return
 receipt();print("CENTRAL_ADJUNCT_CARE_CURRENT_RECEIVING_PASS nchecks=",nchecks);quit(0)
