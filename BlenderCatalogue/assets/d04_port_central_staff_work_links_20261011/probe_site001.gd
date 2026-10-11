extends SceneTree
func vec(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
func _initialize()->void:call_deferred("run")
func run()->void:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_central_staff_work_links_20261011/AUDIT_INPUT_PLAN.json"))
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var d:Node3D=ship.get_node("ShipSpace/Districts");var space:=ship.get_world_3d().direct_space_state;var meshes:Array=[];var floors:Array=[];var bearings:Array=[];var stances:Array=[]
 var targets:Array=p.cuts.duplicate();targets.append_array(p.moves)
 for row in targets:
  var mesh:MeshInstance3D=d.get_node(row.source_root).find_child(row.name,true,false);assert(mesh!=null);var a:AABB=mesh.global_transform*mesh.get_aabb();var faces:Array=[]
  for v in mesh.mesh.get_faces():var q:Vector3=mesh.global_transform*v;faces.append([q.x,q.y,q.z])
  meshes.append({"name":row.name,"source_root":row.source_root,"bounds":[[a.position.x,a.position.y,a.position.z],[a.end.x,a.end.y,a.end.z]],"world_triangle_vertices":faces})
 for gate in p.gates:
  for x in [-65.8,-65.5,-65.4,-65.2,-64.8,-64.6,-64.5,-64.4]:
   var at:=Vector3(x,16.55,gate.z);var q:=PhysicsRayQueryParameters3D.create(at,at-Vector3.UP*.4);var h:=space.intersect_ray(q);floors.append({"gate":gate.name,"at":[x,16.5,gate.z],"hit":{}if h.is_empty()else{"owner":str(h.collider.get_path()),"y":h.position.y}})
  for x in [-65.65,-64.35]:
   for z in [gate.z-.65,gate.z+.65]:
    var q:=PhysicsRayQueryParameters3D.create(Vector3(x,16.15,z),Vector3(x,16.35,z));q.hit_back_faces=true;var h:=space.intersect_ray(q);bearings.append({"gate":gate.name,"at":[x,16.26,z],"hit":{}if h.is_empty()else{"owner":str(h.collider.get_path()),"point":[h.position.x,h.position.y,h.position.z],"normal":[h.normal.x,h.normal.y,h.normal.z]}})
  for x in [-63.2,-66,-67,-68]:
   var box:=CapsuleShape3D.new();box.height=1.8;box.radius=.3;box.margin=.001;var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(x,17.425,gate.z));var hits:=space.intersect_shape(q,64);stances.append({"gate":gate.name,"at":[x,16.5,gate.z],"blockers":hits.map(func(h):return str(h.collider.get_path()))})
 FileAccess.open("/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/d04_port_central_staff_work_links_20261011/SITE_PREFLIGHT.json",FileAccess.WRITE).store_string(JSON.stringify({"meshes":meshes,"floors":floors,"bearings":bearings,"stances":stances},"  "));print("Court work-link site preflight complete");quit()
