extends SceneTree
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_court_routes_20261011/AUDIT_INPUT_PLAN.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var d:Node3D=ship.get_node("ShipSpace/Districts");var space:=ship.get_world_3d().direct_space_state;var meshes:Array=[];var floors:Array=[];var bearings:Array=[];var stances:Array=[]
 var targets:Array=p.cuts.duplicate();targets.append_array(p.moves)
 for row in targets:
  var mesh:MeshInstance3D=d.get_node(row.source_root).find_child(str(row.name).replace(".","_"),true,false);assert(mesh!=null);var a:AABB=mesh.global_transform*mesh.get_aabb();var faces:Array=[]
  for v in mesh.mesh.get_faces():var q:Vector3=mesh.global_transform*v;faces.append([q.x,q.y,q.z])
  meshes.append({"name":row.name,"source_root":row.source_root,"bounds":[[a.position.x,a.position.y,a.position.z],[a.end.x,a.end.y,a.end.z]],"world_triangle_vertices":faces})
 for point in p.route_samples+p.source_approach_samples:
  var at:=vec(point);var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits:=space.intersect_shape(q,64);var h:=space.intersect_ray(PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.4));stances.append({"at":point,"blockers":hits.map(func(x):return str(x.collider.get_path())),"floor":{}if h.is_empty()else{"y":h.position.y,"owner":str(h.collider.get_path())}})
 for gate in p.gates.slice(0,9):
  var at:=vec(gate.court_stance);var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits:=space.intersect_shape(q,64);stances.append({"gate":gate.name,"at":gate.court_stance,"blockers":hits.map(func(x):return str(x.collider.get_path()))})
 var supports:Array=[]
 for row in p.support_sites:
  var corners:Array=[];var highest:float=-INF
  for x in [row.x-row.half,row.x+row.half]:
   for z in [row.z-row.half,row.z+row.half]:
    var ray:=PhysicsRayQueryParameters3D.create(Vector3(x,16.01,z),Vector3(x,-5,z));ray.hit_back_faces=true;var h:=space.intersect_ray(ray)
    if h.is_empty():corners.append({"missing":true,"at":[x,16.01,z]});continue
    highest=max(highest,h.position.y);corners.append({"point":[h.position.x,h.position.y,h.position.z],"owner":str(h.collider.get_path()),"normal":[h.normal.x,h.normal.y,h.normal.z]})
  if not is_finite(highest):supports.append({"x":row.x,"z":row.z,"missing":true,"corners":corners});continue
  var box:=BoxShape3D.new();box.size=Vector3(row.half*2,16.25-highest-.13,row.half*2);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(row.x,(16.25+highest+.13)/2,row.z));var hits:=space.intersect_shape(q,64)
  supports.append({"x":row.x,"z":row.z,"half":row.half,"corners":corners,"column_bottom":highest+.12,"blockers":hits.map(func(h):return str(h.collider.get_path()))})
 var ledgers:Array=[]
 for row in p.ledger_sites:
  var corners:Array=[]
  for y in [16.29,16.46]:
   for z in [row.z-row.half_z,row.z+row.half_z]:
    var ray:=PhysicsRayQueryParameters3D.create(Vector3(row.x+(.2 if row.x>-40 else -.2),y,z),Vector3(row.x+(-.2 if row.x>-40 else .2),y,z));ray.hit_back_faces=true;var h:=space.intersect_ray(ray)
    if h.is_empty():corners.append({"missing":true});continue
    corners.append({"point":[h.position.x,h.position.y,h.position.z],"owner":str(h.collider.get_path()),"source_mesh":str(h.collider.get_parent().name)})
  ledgers.append({"site":row,"corners":corners})
 var roof_rows:Array=[]
 for point in p.route_samples:
  var at:=vec(point)+Vector3.UP*3.0;var box:=BoxShape3D.new();box.size=Vector3(1.2,.6,1.2);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,at);var hits:=space.intersect_shape(q,64);roof_rows.append({"at":[at.x,at.y,at.z],"blockers":hits.map(func(x):return str(x.collider.get_path()))})
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_aft_court_routes_20261011/SITE_PREFLIGHT002.json",FileAccess.WRITE).store_string(JSON.stringify({"meshes":meshes,"floors":floors,"bearings":bearings,"stances":stances,"supports":supports,"roof_rows":roof_rows,"ledgers":ledgers},"  "));print("Court work-link site preflight complete");quit()
