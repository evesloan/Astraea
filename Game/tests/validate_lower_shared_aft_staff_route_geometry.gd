extends SceneTree
var errors:Array=[]
var checks:int=0
func record(label:String,okay:bool)->void:
 checks+=1
 if not okay:errors.append(label)
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func mesh_snapshot(ship:Node3D)->Dictionary:
 var result:Dictionary={}
 for m:MeshInstance3D in ship.get_node("ShipSpace/Districts").find_children("*","MeshInstance3D",true,false):
  if m.mesh==null:continue
  var ctx:=HashingContext.new();ctx.start(HashingContext.HASH_SHA256);ctx.update(m.mesh.get_faces().to_byte_array());ctx.update(var_to_bytes(m.global_transform));result[str(m.get_path())]=ctx.finish().hex_encode()
 return result
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/LOWER_SHARED_AFT_STAFF_ROUTE.json"))
 record("inactive_before_independent_geometry_retention",not p.active)
 var before:=mesh_snapshot(ship);var old_hits:Array=[]
 #Only strict interiors are queried;2mm inset excludes intended source contacts and physics margins.
 for part in p.parts:
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for v in part.verts:lo=lo.min(vec(v));hi=hi.max(vec(v))
  var points:=PackedVector3Array()
  for v in part.verts:points.append(vec(v).clamp(lo+Vector3.ONE*.002,hi-Vector3.ONE*.002))
  var shape:=ConvexPolygonShape3D.new();shape.points=points;shape.margin=.001
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=shape;var hits:=space.intersect_shape(q,64)
  record("no_original_volume_penetration_"+part.name,hits.is_empty())
  if not hits.is_empty():old_hits.append({"part":part.name,"bounds":[str(lo),str(hi)],"owners":hits.map(func(v):return str(v.collider.get_path()))})
 var n:Node3D=load("res://scripts/lower_shared_aft_staff_route.gd").build(ship,true)
 for i in range(120):await physics_frame
 var after:=mesh_snapshot(ship)
 for path in before:record("original_mesh_transform_faces_exact_"+path,after.has(path)and after[path]==before[path])
 var roof_meshes:Array=[]
 for part in p.parts:
  var mesh:MeshInstance3D=n.find_child(part.name,true,false);record("authored_source_present_"+part.name,mesh!=null)
  if mesh==null:continue
  var expected:=AABB();var first:=true
  for v in part.verts:
   if first:expected=AABB(vec(v),Vector3.ZERO);first=false
   else:expected=expected.expand(vec(v))
  var a:AABB=mesh.global_transform*mesh.get_aabb();record("actual_native_bounds_"+part.name,a.position.distance_to(expected.position)<.0001 and a.end.distance_to(expected.end)<.0001)
  if part.category=="roof":roof_meshes.append(mesh)
 for junction in p.wall_ceiling_junctions:
  var wall:MeshInstance3D=n.find_child(junction.wall,true,false);var a:AABB=wall.global_transform*wall.get_aabb();var meets:=false
  for roof:MeshInstance3D in roof_meshes:
   var b:AABB=roof.global_transform*roof.get_aabb()
   if abs(a.end.y-b.position.y)<.0001 and minf(a.end.x,b.end.x)-maxf(a.position.x,b.position.x)>0 and minf(a.end.z,b.end.z)-maxf(a.position.z,b.position.z)>0:meets=true
  record("actual_wall_meets_local_roof_"+junction.wall,meets)
 var exclusion:Array[RID]=[]
 for body:CollisionObject3D in n.find_children("*","CollisionObject3D",true,false):exclusion.append(body.get_rid())
 var bearings:int=0
 for foot in p.support_preimages:
  for witness in foot.corners:
   var at:=vec(witness.at);var q:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.005,at-Vector3.UP*.1);q.exclude=exclusion;q.hit_back_faces=true;var h:=space.intersect_ray(q)
   record("original_hull_foot_contact_"+str(bearings),not h.is_empty()and str(h.collider.get_path())==witness.owner and h.position.distance_to(at)<.0001);bearings+=1
 var floor_contacts:int=0
 for contact in p.source_contact_faces:
  for dz in [-1.3,0,1.3]:
   for dx in [-.015,.015]:
    var at:=vec(contact.at)+Vector3(dx,.05,dz);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at,at-Vector3.UP*.3));record("source_floor_edge_joint_"+str(floor_contacts),not h.is_empty()and absf(h.position.y)<.0001 and ("LowerSharedAftStaffRoute"in str(h.collider.get_path())if dx<0 else contact.original_floor in str(h.collider.get_path())));floor_contacts+=1
 var frame_contacts:int=0;var pose_samples:int=0
 for spec in p.service_doors:
  var door:Node3D=n.get_node(spec.name);var low:=Vector3(INF,INF,INF);var high:=-low
  for mesh:MeshInstance3D in door.find_children("*","MeshInstance3D",true,false):
   var a:AABB=mesh.global_transform*mesh.get_aabb();low=low.min(a.position);high=high.max(a.end)
  record("original_frame_actual_height_"+spec.name,absf(high.y-2.82)<.0001);record("original_frame_actual_width_"+spec.name,absf(high.z-low.z-2.76)<.0001)
  for part in p.parts:
   if not part.name.begins_with("LSA_Entry"):continue
   var m:MeshInstance3D=n.find_child(part.name,true,false);var a:AABB=m.global_transform*m.get_aabb()
   if not a.position.x<high.x or not a.end.x>low.x:continue
   if "Header"in part.name:record("source_frame_header_sealed_"+spec.name,absf(a.position.y-high.y)<.0001);frame_contacts+=1
   elif absf(a.end.z-low.z)<.0001 or absf(a.position.z-high.z)<.0001:record("source_frame_jamb_sealed_"+spec.name,true);frame_contacts+=1
  door.interact(null)
  for i in range(100):
   await physics_frame
   if i%5==0:
    pose_samples+=1;record("source_door_opening_pose_"+spec.name+str(i),door.open_fraction>=0 and door.open_fraction<=1 and not door.obstructed)
  record("source_door_open_endpoint_"+spec.name,door.open_fraction==1)
  door.interact(null)
  for i in range(100):
   await physics_frame
   if i%5==0:pose_samples+=1;record("source_door_closing_pose_"+spec.name+str(i),door.open_fraction>=0 and door.open_fraction<=1 and not door.obstructed)
  record("source_door_end_closed_"+spec.name,door.open_fraction==0 and not door.desired_open)
 var route_checks:int=0
 for point in p.route_samples:
  var at:=vec(point);var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);record("worker_capsule_clear_"+str(route_checks),space.intersect_shape(q,64).is_empty());var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.4));record("walk_floor_present_"+str(route_checks),not h.is_empty()and absf(h.position.y)<.0001);route_checks+=1
 record("old_forward_lift_stops_preserved",ship.find_child("ForwardStaffLift",true,false).deck_numbers==[1,2,3,8,9,13,14,15,16,17])
 record("port_central_lift_preserved",ship.find_child("PortCentralStaffLift",true,false).deck_numbers==[1,4])
 record("all_six_source_frame_joints",frame_contacts==6)
 var result={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"original_volume_penetrations":old_hits,"original_meshes_exact":before.size(),"wall_ceiling_joints":p.wall_ceiling_junctions.size(),"actual_door_frame_joints":frame_contacts,"hull_contact_corners":bearings,"original_floor_edge_contacts":floor_contacts,"source_controller_pose_samples":pose_samples,"worker_capsule_samples":route_checks,"model_pins":p.model_pins,"limits":p.limits}
 FileAccess.open("res://artifacts/lower_shared_aft_staff_route_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors,"penetrations":old_hits}));quit(0 if errors.is_empty()else 1)
