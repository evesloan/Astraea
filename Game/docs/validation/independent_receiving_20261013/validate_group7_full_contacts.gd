extends "res://tests/validate_d04_port_forward_commons_service.gd"
var nchecks:=0
var legs:Array=[]
var operations:=0
var failures:Array=[]
var support_results:Array=[]
var transit_conflicts:Array=[]
const OUT="/workspace/astraea-integration-cutoff-20261013/G7_FULL_CURRENT_CONTACT_RUNTIME.json"
func _initialize()->void:
 OS.set_environment("ASTRAEA_GROUP7_ENABLE","1")
 for p in ["/workspace/astraea-synthesis-adoption-20261012/SYNTHESIS_ACTUAL_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/GROUP5_PUBLIC_VALIDATION_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/READY_DRY_THERMAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/ENVELOPE_MEDICAL_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip","/workspace/astraea-integration-cutoff-20261013/G7_FULL_SELECTION_CANDIDATE_OVERLAY.zip"]:assert(ProjectSettings.load_resource_pack(p,true))
 call_deferred("run")
func result()->void:
 FileAccess.open(OUT,FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_FULL_SOURCE_SELECTION_CURRENT_CONTACTS"if failures.is_empty()else"HOLD","checks":nchecks,"failures":failures,"support_results":support_results,"strict_transit_conflicts":transit_conflicts,"models":88,"sources":39,"doors":8,"additional_contact_cells":19,"ordinary_door_operations":operations,"changed_area_legs":legs,"original_floor_owners":303,"source_models_and_old_envelope_definitions_unchanged":true,"production_selection_changed":false,"species_capacity_whole_engineering_final_art_accepted":false},"  "))
func require(ok:bool,label:String)->bool:
 nchecks+=1
 if not ok:failures.append(label);result();push_error(label);quit(1)
 return ok
func frames(n:int)->void:
 for i in range(n):await physics_frame
func mouse(on:bool)->void:
 var e:=InputEventMouseButton.new();e.button_index=MOUSE_BUTTON_RIGHT;e.pressed=on;Input.parse_input_event(e)
func press(actor:CharacterBody3D,door:Node3D)->bool:
 var contact:CollisionShape3D=door.leaves[0].get_node("LeafContact");actor.camera.look_at(contact.global_position,Vector3.UP);mouse(true);await frames(3)
 if not require(actor.target_from_view()==door,"Exact current leaf target "+str(door.persistent_id)):return false
 var e:=InputEventKey.new();e.keycode=KEY_E;e.physical_keycode=KEY_E;e.pressed=true;Input.parse_input_event(e);await frames(3);e.pressed=false;Input.parse_input_event(e);mouse(false);operations+=1;return true
func audit_receivers(ship:Node3D,g:Node3D,actor:CharacterBody3D,old:Dictionary,p:Dictionary)->void:
 var space:PhysicsDirectSpaceState3D=ship.get_world_3d().direct_space_state
 var exclusion:Array[RID]=[]
 for row in p.models:
  if row in old.models:continue
  for body:CollisionObject3D in g.get_node(str(row.cell)).find_children("*","CollisionObject3D",true,false):exclusion.append(body.get_rid())
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/g7_contact_metadata/docs/PLAN.json"))
 var edge:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-protected-integration-20261012/RetainedConstruction/group7/payloads/external_packages/group7_completion_20261011/continuation_r006/docs/BOTANICAL_PLAN.json"))
 var witnesses:Array=[]
 for court in plan.botanical_pockets:
  var at:Vector3=Vector3(court.origin[0],court.origin[1],court.origin[2])
  for dx in [-.8,0.,.8]:
   for dz in [-1.0,0.,1.0]:witnesses.append({"id":str(court.id),"at":at+Vector3(dx,0,dz)})
 for terrace in edge.terraces:
  for island in terrace.islands:
   for dx in [-.8,0.,.8]:
    for dz in [-float(island.length_m)*.25,0.,float(island.length_m)*.25]:witnesses.append({"id":str(island.id),"at":Vector3(island.center[0],island.center[1],island.center[2])+Vector3(dx,0,dz)})
 for row in witnesses:
  var at:Vector3=row.at;var query:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.03,at-Vector3.UP*.03);query.exclude=exclusion
  var hit:Dictionary=space.intersect_ray(query);var ok:bool=not hit.is_empty()and absf(hit.position.y-at.y)<.002;nchecks+=1
  if not ok:failures.append("Existing floor receiver "+row.id+" at "+str(at))
  support_results.append({"id":row.id,"at":str(at),"supported":ok,"actual":str(hit.get("position",Vector3.INF)),"source":str(hit.collider.get_path())if not hit.is_empty()else "none"})
 var reservation:=CylinderShape3D.new();reservation.radius=2;reservation.height=4;var points:Array=edge.protected_transit_contract.points_xz
 for y in [27.,52.5,78.,97.5]:
  for i in range(points.size()-1):
   var query:=PhysicsShapeQueryParameters3D.new();query.shape=reservation;query.transform.origin=Vector3(points[i][0],y+2.05,points[i][1]);query.motion=Vector3(points[i+1][0]-points[i][0],0,points[i+1][1]-points[i][1]);query.exclude=[actor.get_rid()]
   var hits:Array=space.intersect_shape(query,32);var fraction:float=space.cast_motion(query)[0];nchecks+=2
   if not hits.is_empty()or fraction<=.999:
    var colliders:Array=[]
    for hit in hits:colliders.append(str(hit.collider.get_path()))
    transit_conflicts.append({"floor_y":y,"segment":i,"start":str(query.transform.origin),"initial_colliders":colliders,"motion_fraction":fraction});failures.append("Unchanged four-metre transit reservation Y"+str(y)+" segment"+str(i))
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main);await frames(40)
 var ship:Node3D=main.get_node("World360/Astraea");var g:Node3D=ship.get_node("ShipSpace/Districts/Group7CompletionCandidate");var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/GROUP7_COMPLETION.json"));var old:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/G7_envelope.json"))
 if not require(p.models.size()==88 and p.lights.size()==39 and p.doors.size()==8,"Exact owner full-source selection"):return
 for row in p.models:
  var cell:Node3D=g.get_node(str(row.cell))
  if not require(cell.transform.is_equal_approx(Transform3D.IDENTITY)and FileAccess.get_sha256("res://assets/models/"+str(row.file))==str(row.sha256),"Exact zero-origin source "+str(row.cell)):return
  if row in old.models:continue
  for mesh:MeshInstance3D in cell.find_children("*","MeshInstance3D",true,false):
   var category:String=str(mesh.get_meta("extras",{}).get("contact_category",""))
   if not require(mesh.has_node("StaticContact")==category.begins_with("solid_"),"Exact new member contact category "+str(mesh.name)):return
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 for row in p.lights:
  var light:Light3D=g.get_node(str(row.id))
  if not require(budget.sources.count(light)==1 and budget.requested_shadow[light.get_instance_id()],"One shared source registration "+str(row.id)):return
 for row in p.doors:
  var door:Node3D=g.get_node(str(row.id))
  if not require(str(door.persistent_id)==str(row.id)and not door.desired_open and door.open_fraction==0,"Closed original door identity "+str(row.id)):return
 var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 audit_receivers(ship,g,actor,old,p)
 if not failures.is_empty():result();print("G7_FULL_RECEIVING_HOLD ",JSON.stringify(failures));quit(1);return
 for row in p.doors:
  if row in old.doors:continue
  var at:Vector3=Vector3(row.normal_review_stance[0],row.normal_review_stance[1],row.normal_review_stance[2]);actor.global_position=at+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true);residency.prepare_position(actor.global_position);await frames(25)
  if not require(actor.is_on_floor()and absf(actor.global_position.y-at.y)<.12,"Existing floor supports tool-door stance "+str(row.id)):return
  var leg:Dictionary=await walk_to(actor,at+Vector3(.7,0,0));legs.append(leg)
  if not require(leg.reached and leg.floor_contact,"Existing supported forecourt leg "+str(row.id)):return
  leg=await walk_to(actor,at);legs.append(leg)
  if not require(leg.reached and leg.floor_contact,"Return to exact source door stance "+str(row.id)):return
  var door:Node3D=g.get_node(str(row.id))
  if not await press(actor,door):return
  await frames(100)
  if not require(door.open_fraction>.999 and door.desired_open,"Original tool door opens "+str(row.id)):return
  if not await press(actor,door):return
  await frames(100)
  if not require(door.open_fraction<.001 and not door.desired_open,"Original tool door closes "+str(row.id)):return
 if not require(ship.get_node("ShipSpace/CompiledStructuralFloors_NotFinishedRooms").get_child_count()==303,"All original compiled floor owners preserved"):return
 result();print("G7_FULL_CONTACT_PASS checks=",nchecks," legs=",legs.size()," operations=",operations);quit(0)
