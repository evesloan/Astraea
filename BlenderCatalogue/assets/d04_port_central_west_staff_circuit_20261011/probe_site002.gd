extends SceneTree
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011/CANDIDATE_PLAN.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var d:Node3D=ship.get_node("ShipSpace/Districts");var space:=ship.get_world_3d().direct_space_state;var meshes:Array=[];var floors:Array=[];var bearings:Array=[];var stances:Array=[]
 var targets:Array=p.cuts.duplicate();targets.append_array(p.moves)
 for row in targets:
  var mesh:MeshInstance3D=d.get_node(row.source_root).find_child(row.name,true,false);assert(mesh!=null);var a:AABB=mesh.global_transform*mesh.get_aabb();var faces:Array=[]
  for v in mesh.mesh.get_faces():var q:Vector3=mesh.global_transform*v;faces.append([q.x,q.y,q.z])
  meshes.append({"name":row.name,"source_root":row.source_root,"bounds":[[a.position.x,a.position.y,a.position.z],[a.end.x,a.end.y,a.end.z]],"world_triangle_vertices":faces})
 for gate in p.gates:
  for x in [-104,gate.pivot[0],gate.wall_x,gate.court_stance[0]]:
   var at:=Vector3(x,16.5,gate.z);var cap:=CapsuleShape3D.new();cap.height=1.8;cap.radius=.3;cap.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*.925);var hits:=space.intersect_shape(q,64);stances.append({"gate":gate.name,"at":[x,16.5,gate.z],"blockers":hits.map(func(h):return str(h.collider.get_path()))})
 var supports:Array=[]
 for row in p.support_sites:
  var corners:Array=[];var highest:float=-INF
  for x in [row.x-row.half,row.x+row.half]:
   for z in [row.z-row.half,row.z+row.half]:
    var ray:=PhysicsRayQueryParameters3D.create(Vector3(x,16.01,z),Vector3(x,-5,z));ray.hit_back_faces=true;var h:=space.intersect_ray(ray)
    assert(not h.is_empty());highest=max(highest,h.position.y);corners.append({"point":[h.position.x,h.position.y,h.position.z],"owner":str(h.collider.get_path()),"normal":[h.normal.x,h.normal.y,h.normal.z]})
  var box:=BoxShape3D.new();box.size=Vector3(row.half*2,16.25-highest-.13,row.half*2);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(row.x,(16.25+highest+.13)/2,row.z));var hits:=space.intersect_shape(q,64)
  supports.append({"x":row.x,"z":row.z,"half":row.half,"corners":corners,"column_bottom":highest+.12,"blockers":hits.map(func(h):return str(h.collider.get_path()))})
 var roof_rows:Array=[]
 for a in [Vector3(-104,19.5,-100.6),Vector3(-104,19.5,-71.6),Vector3(-104,19.5,0),Vector3(-104,19.5,57.6),Vector3(-80,19.5,-100.6)]:
  var box:=BoxShape3D.new();box.size=Vector3(1.2,.6,1.2);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,a);var hits:=space.intersect_shape(q,64);roof_rows.append({"at":[a.x,a.y,a.z],"blockers":hits.map(func(h):return str(h.collider.get_path()))})
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://assets/models/D04_PORT_CENTRAL_COMBINEDSTRUCTURE_r002.glb",state,8)==OK);var fresh:Node3D=doc.generate_scene(state);root.add_child(fresh);var fresh_faces:Dictionary={}
 for row in p.moves:
  var mesh:MeshInstance3D=fresh.find_child(row.name,true,false);var vs:Array=[]
  for at in mesh.mesh.get_faces():var q:Vector3=mesh.global_transform*at;vs.append([q.x,q.y,q.z])
  fresh_faces[row.name]=vs
 FileAccess.open("res://../BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011/FRESH_IMPORT_FACES.json",FileAccess.WRITE).store_string(JSON.stringify({"selected_flags":8,"source_sha256":FileAccess.get_sha256("res://assets/models/D04_PORT_CENTRAL_COMBINEDSTRUCTURE_r002.glb"),"faces":fresh_faces},"  "))
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_central_west_staff_circuit_20261011/SITE_PREFLIGHT.json",FileAccess.WRITE).store_string(JSON.stringify({"meshes":meshes,"floors":floors,"bearings":bearings,"stances":stances,"supports":supports,"roof_rows":roof_rows},"  "));print("Court work-link site preflight complete");quit()
