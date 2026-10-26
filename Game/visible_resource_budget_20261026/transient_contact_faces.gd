extends RefCounted
# Same TriangleMesh welding and face order as Mesh.get_faces(), without retaining
# an editor/intersection BVH on every render Mesh after collision construction.
static var calls:=0
static var face_bytes:=0
static var fallback_calls:=0
static func get_faces(mesh:Mesh)->PackedVector3Array:
 # PrimitiveMesh does not expose ArrayMesh primitive topology through GDScript.
 # Preserve its native extraction; imported ArrayMeshes are the measured target.
 if not mesh is ArrayMesh:
  fallback_calls+=1
  return mesh.get_faces()
 var faces:=PackedVector3Array()
 for surface in mesh.get_surface_count():
  var primitive:int=mesh.surface_get_primitive_type(surface)
  if primitive not in [Mesh.PRIMITIVE_TRIANGLES,Mesh.PRIMITIVE_TRIANGLE_STRIP]:continue
  var arrays:Array=mesh.surface_get_arrays(surface)
  var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
  var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
  var count:=indices.size() if not indices.is_empty() else vertices.size()
  if primitive==Mesh.PRIMITIVE_TRIANGLES:
   var start:=faces.size();faces.resize(start+count)
   for i in count:faces[start+i]=vertices[indices[i] if not indices.is_empty() else i]
  else:
   for i in range(2,count):
    var first:=i-2
    var second:=i if i%2 else i-1
    var third:=i-1 if i%2 else i
    faces.append(vertices[indices[first] if not indices.is_empty() else first])
    faces.append(vertices[indices[second] if not indices.is_empty() else second])
    faces.append(vertices[indices[third] if not indices.is_empty() else third])
 calls+=1
 if faces.is_empty():return faces
 var temporary:=TriangleMesh.new()
 var created:=temporary.create_from_faces(faces)
 if not created:
  push_error("Cannot construct exact transient contact triangles")
  return PackedVector3Array()
 var result:=temporary.get_faces();face_bytes+=result.size()*12
 return result
