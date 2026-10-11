extends SceneTree
const W="/workspace/astraea-recovered-532087b9-20261010T083844Z/BlenderCatalogue/assets/lower_staff_aft_receiving_20261011/"
func _initialize()->void:call_deferred("run")
func run()->void:
 var main:Node=load("res://scenes/main.tscn").instantiate();root.add_child(main)
 for i in range(120):await physics_frame
 var ship:Node3D=main.get_node("World360/Astraea");var space:=ship.get_world_3d().direct_space_state
 var routes:Array=[];var shafts:Array=[];var seams:Array=[]
 var points:Array=[]
 for z in range(70,300,6):points.append(Vector3(-56.5,0,z))
 for x in range(-56,-2,3):points.append(Vector3(x,0,300))
 for at in [Vector3(-46,0,69),Vector3(-48,0,69),Vector3(-50,0,69),Vector3(-54,0,69),Vector3(-56.5,0,69),Vector3(-6,0,300),Vector3(-4,0,300),Vector3(0,0,300)]:points.append(at)
 for at in points:
  var cap:=CapsuleShape3D.new();cap.height=2.4;cap.radius=.5;cap.margin=.001
  var q:=PhysicsShapeQueryParameters3D.new();q.shape=cap;q.transform=Transform3D(Basis.IDENTITY,at+Vector3.UP*1.25)
  var hits:=space.intersect_shape(q,64);var ray:=PhysicsRayQueryParameters3D.create(at+Vector3.UP*.05,at-Vector3.UP*.4);ray.hit_back_faces=true;var h:=space.intersect_ray(ray)
  routes.append({"at":[at.x,at.y,at.z],"blockers":hits.map(func(v):return str(v.collider.get_path())),"floor":{}if h.is_empty()else{"point":[h.position.x,h.position.y,h.position.z],"owner":str(h.collider.get_path())}})
 for at in [Vector3(-48,1.65,69),Vector3(-4,1.65,300)]:
  ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(-51,0,432)if at.z>400 else at)
  for frame in range(8):await physics_frame
  var box:=BoxShape3D.new();box.size=Vector3(5,6,5);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,at);var hits:=space.intersect_shape(q,256);var seen:Dictionary={};var rows:Array=[]
  for h in hits:
   var mesh:Node=h.collider.get_parent()
   if not mesh is MeshInstance3D or seen.has(str(mesh.get_path())):continue
   seen[str(mesh.get_path())]=true;var a:AABB=mesh.global_transform*mesh.get_aabb();var verts:Array=[]
   for v in mesh.mesh.get_faces():var t:Vector3=mesh.global_transform*v;verts.append([t.x,t.y,t.z])
   rows.append({"name":str(mesh.name),"path":str(mesh.get_path()),"bounds":[[a.position.x,a.position.y,a.position.z],[a.end.x,a.end.y,a.end.z]],"world_triangle_vertices":verts})
  seams.append({"at":[at.x,at.y,at.z],"meshes":rows})
 var feet:Array=[]
 var sites:Array=[]
 for z in range(70,298,9):
  for x in [-58.12,-54.88]:sites.append(Vector3(x,-.24,z))
 for x in [-53.0,-49.0]:
  for z in [67.38,70.62]:sites.append(Vector3(x,-.24,z))
 for x in [-53.0,-44.0,-35.0,-26.0,-17.0,-8.0]:
  for z in [298.38,301.62]:sites.append(Vector3(x,-.24,z))
 for at in sites:
  if at.z>390:
   ship.get_node("ShipSystems/ReceivedRoomResidency").prepare_position(Vector3(-51,0,432))
   await physics_frame
  var corners:Array=[];var y:=-INF;var okay:=true
  for dx in [-.12,.12]:
   for dz in [-.12,.12]:
    var ray:=PhysicsRayQueryParameters3D.create(Vector3(at.x+dx,-.245,at.z+dz),Vector3(at.x+dx,-5,at.z+dz));ray.hit_back_faces=true;var h:=space.intersect_ray(ray)
    var owner:=str(h.collider.get_path())if not h.is_empty()else"NO_CONTACT";okay=okay and not h.is_empty()and h.normal.y>.15 and ("HUL_KeelPan"in owner or "HUL_LowerBand"in owner)
    if not h.is_empty():y=maxf(y,h.position.y);corners.append({"at":[h.position.x,h.position.y,h.position.z],"owner":owner,"normal_y":h.normal.y})
  feet.append({"top":[at.x,at.y,at.z],"source_max_y":y,"accepted":okay,"corners":corners})
 var candidate_volumes:Array=[]
 for row in [[-58.3,67.2,-54.7,301.8],[-58.3,67.2,-48.0,70.8],[-58.3,298.2,-4.0,301.8]]:
  var box:=BoxShape3D.new();box.size=Vector3(row[2]-row[0],3.6,row[3]-row[1]);var q:=PhysicsShapeQueryParameters3D.new();q.shape=box;q.transform=Transform3D(Basis.IDENTITY,Vector3((row[0]+row[2])/2,1.56,(row[1]+row[3])/2));var hits:=space.intersect_shape(q,256)
  candidate_volumes.append({"rect":row,"blockers":hits.map(func(v):return str(v.collider.get_path()))})
 FileAccess.open(W+"SITE_PREFLIGHT004.json",FileAccess.WRITE).store_string(JSON.stringify({"routes":routes,"support_feet":feet,"source_seams":seams,"candidate_volumes":candidate_volumes},"  "));print("Lower aft actual-source survey complete");quit()
