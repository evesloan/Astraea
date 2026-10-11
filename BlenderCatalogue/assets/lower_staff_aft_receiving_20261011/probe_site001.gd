extends SceneTree
const W="/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/lower_staff_aft_receiving_20261011/"
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var routes:Array=[];var shafts:Array=[];var seams:Array=[]
 var points:Array=[]
 for z in range(-55,285,10):points.append(Vector3(-49 if z>=-40 and z<=40 else -57,0,z))
 for z in [280,290,300,440,450,460,480,490]:
  for x in [-57,-49,-33,-25,-21]:
   for y in [0,16.5]:points.append(Vector3(x,y,z))
 for at in points:
  var cap:=CapsuleShape3D.new();cap.height=2.4;cap.radius=.5;cap.margin=.001
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*1.25)
  var hits:=space.intersect_shape(q,64);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.4);ray.hit_back_faces=true;var h:=space.intersect_ray(ray)
  routes.append({"at":[at.x,at.y,at.z],"blockers":hits.map(func(v):return str(v.collider.get_path())),"floor":{}if h.is_empty()else{"point":[h.position.x,h.position.y,h.position.z],"owner":str(h.collider.get_path())}})
 for z in [290.0,490.0,-283.0]:
  var box:=BoxShape3D.new();box.size=Vector3(4.4,22.9,4.4);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(-25,8.25,z));var hits:=space.intersect_shape(q,256)
  var pre:Array=[]
  for h in hits:
   var mesh:Node=h.collider.get_parent();var row={"owner":str(h.collider.get_path())}
   if mesh is MeshInstance3D:
    var a:AABB=mesh.global_transform*mesh.get_aabb();row.bounds=[[a.position.x,a.position.y,a.position.z],[a.end.x,a.end.y,a.end.z]]
   pre.append(row)
  shafts.append({"center_z":z,"blockers":pre})
 for z in [-60.0,284.0,290.0,445.4,490.0]:
  var box:=BoxShape3D.new();box.size=Vector3(45,3.3,6);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3(-40,1.65 if z==-60 else 18.15,z));var hits:=space.intersect_shape(q,256);var seen:Dictionary={};var rows:Array=[]
  for h in hits:
   var mesh:Node=h.collider.get_parent()
   if not mesh is MeshInstance3D or seen.has(str(mesh.get_path())):continue
   seen[str(mesh.get_path())]=true;var a:AABB=mesh.global_transform*mesh.get_aabb();var verts:Array=[]
   for v in mesh.mesh.get_faces():var t:Vector3=mesh.global_transform*v;verts.append([t.x,t.y,t.z])
   rows.append({"name":str(mesh.name),"path":str(mesh.get_path()),"bounds":[[a.position.x,a.position.y,a.position.z],[a.end.x,a.end.y,a.end.z]],"world_triangle_vertices":verts})
  seams.append({"z":z,"meshes":rows})
 FileAccess.open(W+"SITE_PREFLIGHT001.json",FileAccess.WRITE).store_string(JSON.stringify({"routes":routes,"shaft_candidates":shafts,"source_seams":seams},"  "));print("Lower aft actual-source survey complete");quit()
