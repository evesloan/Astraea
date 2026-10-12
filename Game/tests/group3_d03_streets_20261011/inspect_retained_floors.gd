extends "res://tests/group3_fore_starboard_clinical_20261011/validate_fore.gd"
var probe_count:=0
var setups:=0
var held_error_keys:Array=[]
var preserved_block_witnesses:Array=[]
func moving_doors()->void:
 samples+=1;var state:=package.get_world_3d().direct_space_state
 for s in p.door_bindings:
  var door:Node3D=package.get_node(s.name)
  for leaf in door.leaves:
   for c in leaf.get_children():
    if not c is CollisionShape3D:continue
    var q:=PhysicsShapeQueryParameters3D.new();q.shape=c.shape;q.transform=c.global_transform;q.exclude=[leaf.get_rid()];q.margin=.0001;var bad:Array=[]
    for h in state.intersect_shape(q,128):
     if h.collider is StaticBody3D and not h.collider is AnimatableBody3D:bad.append(str(h.collider.get_path()))
    record("continuation_leaf_"+str(samples)+str(c.name),bad.is_empty())
    if not bad.is_empty():print("CONTINUATION_LEAF_CONTACT ",bad)
func line_probe(state:PhysicsDirectSpaceState3D,a:Vector3,b:Vector3,label:String)->void:
 var count:int=ceili(a.distance_to(b)/2)
 for j in range(count+1):
  var at:=a.lerp(b,float(j)/maxi(count,1));var h:=ray(state,at+Vector3.UP*.1,at-Vector3.UP*.3);var clear:=capsule_clear(state,at);var worker_key:="worker_"+label+str(j)
  probe_count+=1;record("floor_"+label+str(j),not h.is_empty()and absf(h.position.y-12)<.002);record(worker_key,clear)
  if not clear:
   var query:=PhysicsShapeQueryParameters3D.new();var shape:=CapsuleShape3D.new();shape.radius=.3;shape.height=1.8;shape.margin=.001;query.shape=shape;query.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var names:Array=[]
   for hit in state.intersect_shape(query,128):names.append(str(hit.collider.get_path()))
   for delta in [Vector3(.3,0,0),Vector3(0,0,.3)]:
    var hit:=ray(state,at+Vector3.UP-delta,at+Vector3.UP+delta)
    if not hit.is_empty():names.append(str(hit.collider.get_path()))
   var permitted:Array=["D04SC_LowerServiceWall_1","D04SC_LowerServiceWall_7","SAC_LowerScreen_3","SAC_LowerScreen_5","PACO_D04SC_LowerServiceWall_1","PACO_D04SC_LowerServiceWall_7"];var original_block:=not names.is_empty()
   for name in names:
    var matched:=false
    for target in permitted:if str(name).contains("/Districts/")and str(name).contains("/"+str(target)+"/"):matched=true
    original_block=original_block and matched
   if original_block:held_error_keys.append(worker_key);preserved_block_witnesses.append({"position":[at.x,at.y,at.z],"colliders":names,"worker_clearance_criterion":false})
   record("protected_block_owner_"+worker_key,original_block);print("STREET_WORKER_CONTACT ",label," ",at," ",names)
func setup(actor:CharacterBody3D,at:Vector3)->void:
 setups+=1;actor.global_position=at+Vector3.UP*.03;actor.velocity=Vector3.ZERO;actor.set_controls_enabled(true)
 for i in range(20):await physics_frame
func run()->void:
 p=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_streets_20261011/STREETS.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(60):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var cart:Node3D=ship.get_node("ShipSpace/PersistentActors/CustodialCart");var cart_id:=cart.get_instance_id()
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency");residency.enabled=false;residency.set_physics_process(false)
 for entry in residency.entries:
  var room:Node3D=entry.room
  if str(room.get_meta("programme_key",""))not in["D03_directory_02","D03_directory_04","D03_directory_09"]:continue
  if not entry.attached:entry.parent.add_child(room);entry.attached=true
  load("res://scripts/deferred_home_visual.gd").ensure(room)
 load("res://scripts/group3_completion_20261011/d03_precinct.gd").build(ship)
 load("res://scripts/group3_completion_20261011/labelled_bank.gd").build(ship)
 load("res://scripts/group3_fore_starboard_clinical_20261011/physical_package.gd").build(ship)
 load("res://scripts/group3_d03_services_20261011/physical_package.gd").build(ship)
 var port2:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_port2_clinical_20261011/PHYSICAL.json"));var p2ids:Dictionary={}
 for key in port2.supplied_identity_map_required:p2ids[key]="__validation_only_streets_port2_"+key
 load("res://scripts/group3_port2_clinical_20261011/physical_package.gd").build(ship,p2ids)
 var connection:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_port2_20261011/CONNECTION.json"));var cids:Dictionary={}
 for q in connection.door_bindings:cids[q.name]="__validation_only_streets_connection_"+q.name
 load("res://scripts/group3_d03_port2_20261011/physical_package.gd").build(ship,cids,true)
 for i in range(15):await physics_frame
 var owners:Array=[];var triangles:Array=[]
 for body in ship.find_children("*","StaticBody3D",true,false):
  if body is AnimatableBody3D:continue
  for c in body.find_children("*","CollisionShape3D",false,false):
   var faces:PackedVector3Array=[]
   if c.shape is ConcavePolygonShape3D:faces=c.shape.get_faces()
   elif c.shape is BoxShape3D:
    var h:Vector3=c.shape.size/2;faces=PackedVector3Array([Vector3(-h.x,h.y,-h.z),Vector3(-h.x,h.y,h.z),Vector3(h.x,h.y,h.z),Vector3(-h.x,h.y,-h.z),Vector3(h.x,h.y,h.z),Vector3(h.x,h.y,-h.z)])
   else:continue
   var selected:Array=[]
   for i in range(0,faces.size(),3):
    var a:Vector3=c.global_transform*faces[i];var b:Vector3=c.global_transform*faces[i+1];var d:Vector3=c.global_transform*faces[i+2]
    if maxf(absf(a.y-12),maxf(absf(b.y-12),absf(d.y-12)))>.00001:continue
    if (b-a).cross(d-a).y<=.0000000001:continue
    var lo:=Vector3(minf(a.x,minf(b.x,d.x)),12,minf(a.z,minf(b.z,d.z)));var hi:=Vector3(maxf(a.x,maxf(b.x,d.x)),12,maxf(a.z,maxf(b.z,d.z)))
    if lo.x>106 or hi.x < -106 or lo.z>440 or hi.z < -510:continue
    var tri:Array=[[a.x,a.z],[b.x,b.z],[d.x,d.z]];selected.append(tri);triangles.append(tri)
   if not selected.is_empty():owners.append({"collider":str(body.get_path()),"triangles":selected})
 var result={"status":"EXACT_RETAINED_PHYSICAL_D03_FLOOR_SURVEY","parent_handoff_commit":"229e94a67997b910160836366e3e12348544fbc0","engine":Engine.get_version_info(),"new_remaining_street_package_present":false,"previous_group3_modules_staged":true,"source_pins":p.source_pins,"owners":owners,"triangles":triangles,"no_original_geometry_or_registered_ids_modified":true}
 FileAccess.open("res://artifacts/group3_d03_streets_20261011/retained_physical_floor_survey.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"floor_owners":owners.size(),"triangles":triangles.size()}));quit()
