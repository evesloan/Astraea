extends SceneTree
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func transient_faces(mesh:Mesh)->PackedVector3Array:
 var faces:=PackedVector3Array()
 for surface in mesh.get_surface_count():
  assert(mesh.surface_get_primitive_type(surface)==Mesh.PRIMITIVE_TRIANGLES)
  var arrays:Array=mesh.surface_get_arrays(surface);var vertices:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
  var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX] if arrays[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
  if indices.is_empty():faces.append_array(vertices)
  else:
   var start:=faces.size();faces.resize(start+indices.size())
   for i in indices.size():faces[start+i]=vertices[indices[i]]
 var temporary:=TriangleMesh.new();assert(temporary.create_from_faces(faces))
 return temporary.get_faces()
func digest(faces:PackedVector3Array)->String:
 var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(faces.to_byte_array());return hash.finish().hex_encode()
func run()->void:
 var path:=OS.get_environment("ASTRAEA_CACHE_PROBE_SOURCE")
 if path.is_empty():path="res://assets/models/SOL_D07_directory_01_remaining_batch.glb"
 var packed:PackedScene=load(path);var node:Node3D=packed.instantiate();root.add_child(node)
 var meshes:Dictionary={}
 for part:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):meshes[part.mesh.get_instance_id()]=part.mesh
 var baseline:=OS.get_static_memory_usage();var hashes:Dictionary={};var face_bytes:=0
 var start:=Time.get_ticks_usec()
 for id:int in meshes:
  var faces:=transient_faces(meshes[id]);hashes[id]=digest(faces);face_bytes+=faces.size()*12
 var transient_us:=Time.get_ticks_usec()-start
 await process_frame
 var after_transient:=OS.get_static_memory_usage()
 start=Time.get_ticks_usec()
 for id:int in meshes:assert(digest(meshes[id].get_faces())==hashes[id],"TriangleMesh welding/face order differs")
 var cached_us:=Time.get_ticks_usec()-start
 await process_frame
 var result:={"source":path,"source_sha256":FileAccess.get_sha256(path),"unique_meshes":meshes.size(),"face_bytes":face_bytes,"baseline_static":baseline,"after_transient_static":after_transient,"after_cached_static":OS.get_static_memory_usage(),"transient_us":transient_us,"cached_us":cached_us,"exact_face_hashes_match":true,"scope":"Isolated measurement only; production contact and mesh code unchanged"}
 var file:=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close();node.free();quit()
