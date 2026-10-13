extends SceneTree
func _initialize()->void:
 call_deferred("run")
func run()->void:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_services_20261011/SERVICES.json"))
 var map:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/astraea-integration-cutoff-20261013/G3_SERVICES_EXACT_EXPORT_LENS_MAPPING.json"))
 var scene:Node3D=load("res://assets/models/group3_d03_services_20261011/AST-STF-G3-048.glb").instantiate()
 root.add_child(scene)
 var rows:Array=[]
 for binding in map.mappings:
  assert(binding.pinned_export_opal_receivers.size()==1)
  var raw:String=str(binding.pinned_export_opal_receivers[0].mesh_name)
  assert(binding.pinned_export_opal_receivers[0].node_names.size()==1)
  var name:String=str(binding.pinned_export_opal_receivers[0].node_names[0]).validate_node_name()
  var mesh:MeshInstance3D=scene.find_child(name,true,false)
  assert(mesh!=null,"Canonical imported exact node "+name)
  var point:=Vector3(binding.position[0],binding.position[1],binding.position[2])
  var distance:float=nearest_face(mesh,point)
  print("EXACT_LENS ",name," face distance ",distance)
  assert(distance<=.025)
  rows.append({"fixture":binding.fixture,"source_mesh":raw,"imported_node":name,"faces":mesh.mesh.get_faces().size()/3,"face_distance_m":distance})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/G3_SERVICES_IMPORTED_LENS_NAME_PREFLIGHT.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_EXACT_SOURCE_TO_CANONICAL_IMPORTED_NODES","mappings":rows},"  "))
 scene.free();print("G3_SOURCE_IMPORTED_LENS_NAME_PREFLIGHT_PASS ",rows.size());quit(0)

func nearest_face(mesh:MeshInstance3D,point:Vector3)->float:
 var faces:PackedVector3Array=mesh.mesh.get_faces();var best:=INF
 for i in range(0,faces.size(),3):
  var a:Vector3=mesh.global_transform*faces[i];var b:Vector3=mesh.global_transform*faces[i+1];var c:Vector3=mesh.global_transform*faces[i+2]
  var normal:Vector3=(b-a).cross(c-a)
  if normal.length_squared()<1e-15:continue
  normal=normal.normalized();var projected:Vector3=point-normal*normal.dot(point-a)
  if (b-a).cross(projected-a).dot(normal)>=-1e-7 and (c-b).cross(projected-b).dot(normal)>=-1e-7 and (a-c).cross(projected-c).dot(normal)>=-1e-7:best=minf(best,point.distance_to(projected))
  for edge in [[a,b],[b,c],[c,a]]:
   var delta:Vector3=edge[1]-edge[0]
   if delta.length_squared()>1e-15:best=minf(best,point.distance_to(edge[0]+delta*clampf((point-edge[0]).dot(delta)/delta.length_squared(),0,1)))
 return best
