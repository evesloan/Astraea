extends SceneTree
func signatures(faces:PackedVector3Array)->Array[String]:
 var result:Array[String]=[]
 for i in range(0,faces.size(),3):
  result.append(var_to_bytes(PackedVector3Array([faces[i],faces[i+1],faces[i+2]])).hex_encode())
 result.sort();return result
func _initialize()->void:
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/group7_contacts.json"))
 var triangles:=0;var meshes:=0;var cells:=0
 for file in index.models:
  var row:Dictionary=index.models[file];var source:="res://assets/models/"+str(file)
  assert(FileAccess.get_sha256(source)==str(row.source_sha256))
  var visual:Node3D=(load(source) as PackedScene).instantiate()
  for key in row.meshes:
   var mesh:MeshInstance3D=visual.get_node(key);var expected:=signatures(mesh.mesh.get_faces());var actual:Array[String]=[]
   for cell in row.meshes[key].collision_cells:
    assert(FileAccess.get_sha256(cell.path)==str(cell.sha256))
    var shape:ConcavePolygonShape3D=load(cell.path)
    var faces:=shape.get_faces()
    var lo:Array=cell.bounds_min;var hi:Array=cell.bounds_max
    var box:=AABB(Vector3(lo[0],lo[1],lo[2]),Vector3(hi[0]-lo[0],hi[1]-lo[1],hi[2]-lo[2])).grow(0.0001)
    for vertex in faces:assert(box.has_point(vertex))
    actual.append_array(signatures(faces));cells+=1
   actual.sort();assert(expected==actual,"Triangle multiset mismatch "+str(file)+"/"+str(key))
   triangles+=expected.size();meshes+=1
  visual.free()
 print("GROUP7_EXACT_CONTACTS_PASS ",JSON.stringify({"models":index.models.size(),"meshes":meshes,"triangles":triangles,"cells":cells,"triangle_orientation_and_multiplicity":true,"bounds_cover_every_vertex":true}))
 quit()
