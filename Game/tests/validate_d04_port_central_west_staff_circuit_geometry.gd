extends SceneTree
var checks:=0
var errors:Array=[]
func ck(ok:bool,label:String)->void:
 checks+=1
 if not ok:errors.append(label);print("FAIL ",label)
func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func rids(n:Node)->Array[RID]:
 var out:Array[RID]=[]
 if n is CollisionObject3D:out.append(n.get_rid())
 for c in n.get_children():out.append_array(rids(c))
 return out
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_WEST_STAFF_CIRCUIT.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var d:Node3D=ship.get_node("ShipSpace/Districts");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var retained:Dictionary={};var removed:Array=[]
 for pre in p.runtime_preimages:removed.append(pre.name)
 for owner_name in ["D04PortCentralHabitatNeighborhood","D04PortCentralStaffCatchment","D04PortCentralCourtWorkLinks"]:
  for mesh:MeshInstance3D in d.get_node(owner_name).find_children("*","MeshInstance3D",true,false):
   if not str(mesh.name)in removed:retained[str(mesh.get_path())]={"node":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var n:Node3D=d.get_node_or_null("D04PortCentralWestStaffCircuit")
 if n==null:n=load("res://scripts/d04_port_central_west_staff_circuit.gd").build(ship,true)
 for i in range(120):await physics_frame
 for key in retained:
  var row:Dictionary=retained[key];ck(is_instance_valid(row.node),"retained source mesh "+key)
  if is_instance_valid(row.node):ck(row.node.mesh.get_faces()==row.faces and row.node.global_transform==row.pose,"exact source geometry/pose "+key)
 var parts:Array=p.parts.duplicate();parts.append_array(p.copied_gate_parts)
 for part in parts:
  var mesh:MeshInstance3D=n.find_child(str(part.name).replace(".","_"),true,false);ck(mesh!=null,"owned part "+part.name)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for at in part.verts:lo=lo.min(v(at));hi=hi.max(v(at))
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(lo)<.001 and a.end.distance_to(hi)<.001,"actual native bounds "+part.name)
 var space:=ship.get_world_3d().direct_space_state;var exclude:=rids(n);var bearing_count:=0;var samples:=0;var pose_samples:=0;var query_rows:Array=[]
 for s in p.support_preimages:
  for c in s.corners:
   var at:=v(c.point);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.05);ray.exclude=exclude;ray.hit_back_faces=true;var h:=space.intersect_ray(ray);ck(not h.is_empty(),"source hull bearing present")
   if not h.is_empty():ck(h.position.distance_to(at)<.001 and str(h.collider.get_path())==c.owner,"exact source hull bearing identity/datum");bearing_count+=1
  var half:float=s.half-.04;var box:=BoxShape3D.new();box.size=Vector3(half*2,16.13-s.column_bottom-.01,half*2);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(s.x,(16.13+s.column_bottom+.01)/2,s.z));q.exclude=exclude;ck(space.intersect_shape(q,64).is_empty(),"new column retains actual source occupied volumes")
 var route:Array=[]
 for z in range(-98,78,2):route.append(Vector3(-104,16.5,z))
 for x in range(-102,-65,2):route.append(Vector3(x,16.5,-100.6))
 for z in range(44,78,2):route.append(Vector3(-63.2,16.5,z))
 for x in range(-102,-63,2):route.append(Vector3(x,16.5,78))
 route.append_array([Vector3(-104,16.5,-100.6),Vector3(-65.2,16.5,-100.6)])
 for at in route:
  var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.4);ray.exclude=exclude;ck(space.intersect_ray(ray).is_empty(),"missing-only new floor, source floors retained once")
  var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits:=space.intersect_shape(q,64);ck(hits.is_empty(),"enclosed staff circuit worker clearance "+str(at));samples+=1
  var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.08));ck(not h.is_empty()and abs(h.position.y-16.5)<.001,"actual staff circuit floor support")
 for g in p.gates:
  var lane_x:float=-104 if g.private_side_normal[0]>0 else -63.2
  var gate:Node3D=n.get_node(g.name);ck(gate.open_fraction==0 and not gate.desired_open,"private gate default closed "+g.name);gate.interact(actor);ck(gate.access_refused and not gate.desired_open,"no production private consent invented "+g.name)
  var visit:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();visit.actor=weakref(actor);visit.request_id=&"geometry_temporary_known_consent";visit.court_ids.assign([gate.persistent_id]);visit.consent_known=true;visit.consent_allowed=true;visit.active=true;gate.visit=visit;gate.interact(actor)
  for i in range(100):
   await physics_frame
   if i%5==0:
    pose_samples+=1
    for contact:CollisionShape3D in gate.leaves[0].find_children("*","CollisionShape3D",true,false):
     var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.exclude=[gate.leaves[0].get_rid()];var hits:=space.intersect_shape(q,64);ck(hits.is_empty(),"real moving leaf native contact clear "+g.name+" frame="+str(i));query_rows.append({"gate":g.name,"frame":i,"blockers":hits.map(func(h):return str(h.collider.get_path()))})
  ck(gate.open_fraction==1.0,"original controller fully opens "+g.name)
  for x in [lane_x,(g.pivot[0]+lane_x)/2,g.pivot[0],g.wall_x,g.court_stance[0]]:
   var at:=Vector3(x,16.5,g.z);var capsule:=CapsuleShape3D.new();capsule.height=1.8;capsule.radius=.3;capsule.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits:=space.intersect_shape(q,64);ck(hits.is_empty(),"court worker clear "+str(at));query_rows.append({"at":str(at),"blockers":hits.map(func(h):return str(h.collider.get_path()))});samples+=1
   var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.08);var h:=space.intersect_ray(ray);ck(not h.is_empty()and abs(h.position.y-16.5)<.001,"court worker supported "+str(at))
 for z in [-32,0,32]:
  for x in [-80,-75,-70,-65,-60,-55,-52]:
   if z==0 and x<-63:continue
   var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.height=2.4;capsule.radius=.5;capsule.margin=.001;q.shape=capsule;q.transform=Transform3D(Basis.IDENTITY,Vector3(x,17.74,z));ck(space.intersect_shape(q).is_empty(),"protected public branch clear "+str(Vector2(x,z)));var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,16.55,z),Vector3(x,16.42,z)));ck(not h.is_empty()and abs(h.position.y-16.5)<.001,"protected public branch original supported floor")
 var oldp:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_COURT_WORK_LINKS.json"))
 for g in oldp.gates:
  var gate:Node3D=d.get_node("D04PortCentralCourtWorkLinks").get_node(g.name);ck(String(gate.persistent_id)==g.id and gate.open_fraction==0 and gate.visit==null,"original northern private gate identity/closed/consent remains intact")
 ck(d.get_node("D04PortCentralHabitatNeighborhood").get_meta("preserved_home_allocations")==20 and d.get_node("D04PortCentralHabitatNeighborhood").get_meta("preserved_reserved_rests")==25,"original capacity20/25")
 var result:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"model_pins":p.model_pins,"retained_source_meshes_exact":retained.size(),"source_hull_bearing_corners":bearing_count,"worker_capsule_samples":samples,"actual_controller_moving_pose_samples":pose_samples,"new_missing_only_floor_m2":p.new_floor_m2,"rows":query_rows,"temporary_private_visit_test_only":true,"production_private_consent_provider_available":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_port_central_west_staff_circuit_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
