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
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/D04_PORT_CENTRAL_COURT_WORK_LINKS.json"));var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var d:Node3D=ship.get_node("ShipSpace/Districts");var actor:CharacterBody3D=ship.get_node("ShipSpace/PersistentActors/Player");var retained:Dictionary={};var removed:Array=[]
 for pre in p.runtime_preimages:removed.append(pre.name)
 for owner_name in ["D04PortCentralHabitatNeighborhood","D04PortCentralStaffCatchment"]:
  var owner:Node3D=d.get_node(owner_name)
  for mesh:MeshInstance3D in owner.find_children("*","MeshInstance3D",true,false):
   if not str(mesh.name)in removed:retained[str(mesh.get_path())]={"node":mesh,"faces":mesh.mesh.get_faces(),"pose":mesh.global_transform}
 var n:Node3D=d.get_node_or_null("D04PortCentralCourtWorkLinks")
 if n==null:n=load("res://scripts/d04_port_central_court_work_links.gd").build(ship,true)
 for i in range(120):await physics_frame
 for key in retained:
  var q:Dictionary=retained[key];ck(is_instance_valid(q.node),"retained source mesh "+key)
  if is_instance_valid(q.node):ck(q.node.mesh.get_faces()==q.faces and q.node.global_transform==q.pose,"exact source geometry/pose "+key)
 var parts:Array=p.parts.duplicate();parts.append_array(p.copied_gate_parts)
 for part in parts:
  var mesh:MeshInstance3D=n.find_child(str(part.name).replace(".","_"),true,false);ck(mesh!=null,"owned part "+part.name)
  if mesh==null:continue
  var lo:=Vector3(INF,INF,INF);var hi:=-lo
  for at in part.verts:lo=lo.min(v(at));hi=hi.max(v(at))
  var a:AABB=mesh.global_transform*mesh.get_aabb();ck(a.position.distance_to(lo)<.001 and a.end.distance_to(hi)<.001,"actual native bounds "+part.name)
 var space:=ship.get_world_3d().direct_space_state;var exclude:=rids(n);var bearing_count:=0;var samples:=0;var pose_samples:=0;var query_rows:Array=[]
 for g in p.gates:
  var gate:Node3D=n.get_node(g.name);ck(gate.open_fraction==0 and not gate.desired_open,"private gate default closed "+g.name);gate.interact(actor);ck(gate.access_refused and not gate.desired_open,"no production private consent invented "+g.name)
  for x in [-65.75,-65.55,-64.45,-64.25]:
   for z in [g.z-.69,g.z-.61,g.z+.61,g.z+.69]:
    var q:=PhysicsRayQueryParameters3D.create(Vector3(x,16.15,z),Vector3(x,16.35,z));q.exclude=exclude;q.hit_back_faces=true;var h:=space.intersect_ray(q);ck(not h.is_empty(),"retained underside bearing "+str(Vector2(x,z)))
    if not h.is_empty():ck(abs(h.position.y-16.26)<.001,"retained slab underside datum");bearing_count+=1
  for x in [-65.2,-64.8]:
   for z in [g.z-.5,g.z,g.z+.5]:
    var q:=PhysicsRayQueryParameters3D.create(Vector3(x,16.55,z),Vector3(x,16.15,z));q.exclude=exclude;ck(space.intersect_ray(q).is_empty(),"new gap floor retains original floors once")
  var visit:RefCounted=load("res://scripts/d04_court_service_visit.gd").new();visit.actor=weakref(actor);visit.request_id=&"geometry_temporary_known_consent";visit.court_ids.assign([gate.persistent_id]);visit.consent_known=true;visit.consent_allowed=true;visit.active=true;gate.visit=visit;gate.interact(actor)
  for i in range(100):
   await physics_frame
   if i%5==0:
    pose_samples+=1
    for contact:CollisionShape3D in gate.leaves[0].find_children("*","CollisionShape3D",true,false):
     var q:=PhysicsShapeQueryParameters3D.new();q.shape=contact.shape;q.transform=contact.global_transform;q.exclude=[gate.leaves[0].get_rid()];var hits:=space.intersect_shape(q,64);ck(hits.is_empty(),"real moving leaf native contact clear "+g.name+" frame="+str(i));query_rows.append({"gate":g.name,"frame":i,"blockers":hits.map(func(h):return str(h.collider.get_path()))})
  ck(gate.open_fraction==1.0,"original controller fully opens "+g.name)
  for x in [-63.2,-64,-64.8,-65.2,-65.8,-66.5,-67]:
   var at:=Vector3(x,16.5,g.z);var capsule:=CapsuleShape3D.new();capsule.height=1.8;capsule.radius=.3;capsule.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=capsule;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits:=space.intersect_shape(q,64);ck(hits.is_empty(),"court worker clear "+str(at));query_rows.append({"at":str(at),"blockers":hits.map(func(h):return str(h.collider.get_path()))});samples+=1
   var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.08);var h:=space.intersect_ray(ray);ck(not h.is_empty()and abs(h.position.y-16.5)<.001,"court worker supported "+str(at))
 for x in [-80,-75,-70,-65,-60,-55,-52]:
  var q:=PhysicsShapeQueryParameters3D.new();var capsule:=CapsuleShape3D.new();capsule.height=2.4;capsule.radius=.5;capsule.margin=.001;q.shape=capsule;q.transform=Transform3D(Basis.IDENTITY,Vector3(x,17.74,-32));ck(space.intersect_shape(q).is_empty(),"protected north public branch clear "+str(x));var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(x,16.55,-32),Vector3(x,16.42,-32)));ck(not h.is_empty()and abs(h.position.y-16.5)<.001,"protected public branch original supported floor")
 ck(d.get_node("D04PortCentralHabitatNeighborhood").get_meta("preserved_home_allocations")==20 and d.get_node("D04PortCentralHabitatNeighborhood").get_meta("preserved_reserved_rests")==25,"original capacity20/25")
 var result:Dictionary={"status":"PASS"if errors.is_empty()else"HOLD","checks":checks,"errors":errors,"model_pins":p.model_pins,"retained_source_meshes_exact":retained.size(),"source_slab_underside_bearings":bearing_count,"worker_capsule_samples":samples,"actual_controller_moving_pose_samples":pose_samples,"new_gap_floor_m2":p.new_floor_m2,"rows":query_rows,"temporary_private_visit_test_only":true,"production_private_consent_provider_available":false,"limits":p.limits};FileAccess.open("res://artifacts/d04_port_central_court_work_links_geometry.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(JSON.stringify({"status":result.status,"checks":checks,"errors":errors}));quit(0 if errors.is_empty()else 1)
