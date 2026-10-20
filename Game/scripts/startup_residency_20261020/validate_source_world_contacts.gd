extends SceneTree
func pose(mesh:Node3D,visual:Node3D)->Transform3D:
 var result:=mesh.transform;var parent:=mesh.get_parent()
 while parent!=visual:
  assert(parent!=null)
  if parent is Node3D:result=parent.transform*result
  parent=parent.get_parent()
 return result
func signatures(faces:PackedVector3Array)->Array[String]:
 var result:Array[String]=[]
 for i in range(0,faces.size(),3):result.append(var_to_bytes(PackedVector3Array([faces[i],faces[i+1],faces[i+2]])).hex_encode())
 result.sort();return result
func _initialize()->void:
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/source_contacts_world.json"))
 var triangles:=0;var cells:=0
 for file in index.models:
  var row:Dictionary=index.models[file];assert(FileAccess.get_sha256(file)==str(row.source_sha256))
  var visual:Node3D=load(file).instantiate();var expected:Array[String]=[];var actual:Array[String]=[]
  for key in row.meshes:
   var mesh:MeshInstance3D=visual.get_node(key)
   expected.append_array(signatures(pose(mesh,visual)*mesh.mesh.get_faces()))
  for cell in row.collision_cells:
   assert(FileAccess.get_sha256(cell.path)==str(cell.sha256))
   var shape:ConcavePolygonShape3D=load(cell.path);var faces:=shape.get_faces();var lo:Array=cell.bounds_min;var hi:Array=cell.bounds_max
   var bounds:=AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2])).grow(.001)
   for vertex in faces:assert(bounds.has_point(vertex))
   actual.append_array(signatures(faces));cells+=1
  actual.sort();expected.sort();assert(expected==actual,"Exact oriented contact triangle multiset changed "+str(file));triangles+=expected.size();visual.free()
 print("SOURCE_WORLD_CONTACT_EXACT_PASS ",JSON.stringify({"models":index.models.size(),"triangles":triangles,"cells":cells,"world_local_orientation_multiplicity_and_bounds_exact":true}));quit()
