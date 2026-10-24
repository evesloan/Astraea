extends SceneTree
const P:="res://night_garden_lower_receiving_20261024/"
func _initialize()->void:call_deferred("run")
func source_path(n:Node)->String:
 while n!=null:
  if not n.scene_file_path.is_empty():return n.scene_file_path
  n=n.get_parent()
 return ""
func run()->void:
 var main:Node=load("res://scenes/main_retained_enclosure_integrated_20261024.tscn").instantiate();root.add_child(main)
 var ship:Node3D=main.get_node("World360/Astraea")
 while not ship.get_meta("runtime_ready",false):await process_frame
 for frame in range(3):await physics_frame
 paused=true
 var package:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://night_garden_lower_bank_20261022/PACKAGE.json"))
 var probes:Array=[]
 for room:Dictionary in package.rooms:
  var a:Dictionary=room.allocation;var x0:float=a.allocation_x[0];var x1:float=a.allocation_x[1];var z0:float=a.allocation_z[0];var z1:float=a.allocation_z[1];var y:float=a.floor_y
  var points:Array=[Vector3((x0+x1)/2,y,(z0+z1)/2),Vector3(x0+.4,y,z0+.4),Vector3(x1-.4,y,z0+.4),Vector3(x0+.4,y,z1-.4),Vector3(x1-.4,y,z1-.4),Vector3(84,y,(z0+z1)/2)]
  probes.append({"id":int(a.source_envelope_index),"room_id":a.proposed_runtime_id,"points":points,"hits":[]})
 var candidates:Array=[];var multimesh_context:Array=[]
 var volumes:Array=[AABB(Vector3(68,83.4,-113),Vector3(32,1.1,46)),AABB(Vector3(68,83.4,67),Vector3(32,1.1,46)),AABB(Vector3(68,87.9,-113),Vector3(32,1.1,46)),AABB(Vector3(68,87.9,67),Vector3(32,1.1,46))]
 for mesh:MeshInstance3D in ship.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  var box:AABB=mesh.global_transform*mesh.get_aabb();var near:=false
  for volume:AABB in volumes:
   if box.intersects(volume):near=true;break
  if not near:continue
  var relevant:=false
  for probe:Dictionary in probes:
   for point:Vector3 in probe.points:
    if point.x>=box.position.x-.01 and point.x<=box.end.x+.01 and point.z>=box.position.z-.01 and point.z<=box.end.z+.01 and point.y>=box.position.y-.05 and point.y<=box.end.y+.4:relevant=true;break
   if relevant:break
  if not relevant:continue
  # Inspect installed geometry even when distance residency has hidden contacts.
  var faces:PackedVector3Array=mesh.global_transform*mesh.mesh.get_faces();var used:=false
  for probe:Dictionary in probes:
   for index in range(probe.points.size()):
    var point:Vector3=probe.points[index]
    if point.x<box.position.x-.01 or point.x>box.end.x+.01 or point.z<box.position.z-.01 or point.z>box.end.z+.01 or point.y<box.position.y-.05 or point.y>box.end.y+.4:continue
    var best:Variant=null
    for i in range(0,faces.size(),3):
     var hit:Variant=Geometry3D.segment_intersects_triangle(point+Vector3.UP*.05,point-Vector3.UP*.4,faces[i],faces[i+1],faces[i+2])
     if hit!=null and(best==null or hit.y>best.y):best=hit
    if best!=null:
     probe.hits.append({"point_index":index,"y":best.y,"mesh":str(mesh.get_path()),"mesh_resource":mesh.mesh.resource_path,"scene_source":source_path(mesh),"visible":mesh.is_visible_in_tree()});used=true
  if used:candidates.append({"path":str(mesh.get_path()),"bounds_min":str(box.position),"bounds_max":str(box.end),"scene_source":source_path(mesh),"extras":mesh.get_meta("extras",{})})
 for mesh:MultiMeshInstance3D in ship.find_children("*","MultiMeshInstance3D",true,false):
  var box:AABB=mesh.global_transform*mesh.get_aabb()
  for volume:AABB in volumes:
   if box.intersects(volume):multimesh_context.append({"path":str(mesh.get_path()),"count":mesh.multimesh.instance_count,"min":str(box.position),"max":str(box.end)});break
 for probe:Dictionary in probes:
  probe.points=probe.points.map(func(p):return [p.x,p.y,p.z])
 var report:={"status":"ACTUAL_INSTALLED_SOURCE_INSPECTED","runtime_ready":true,"scene":"res://scenes/main_retained_enclosure_integrated_20261024.tscn","rooms":probes,"floor_owner_meshes":candidates,"nearby_multimesh_context":multimesh_context,"geometry_added":false,"suite_source_unchanged":true,"scope":"Existing actual ship only; five private-allocation floor points plus one street point per retained room. Includes hidden mesh geometry. Mesh.get_faces may snap0.1mm; this is ownership diagnosis, not final precision/contact acceptance. MultiMesh bounds are listed separately, not silently treated as absent."}
 FileAccess.open(P+"evidence/INSTALLED_OWNERS.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n")
 print("NIGHT_GARDEN_INSTALLED_OWNERS rooms=",probes.size()," owner_meshes=",candidates.size()," nearby_batches=",multimesh_context.size())
 main.free();await process_frame;quit()
