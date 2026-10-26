extends SceneTree
const FACES=preload("res://visible_resource_budget_20261026/transient_contact_faces.gd")
const CACHE=preload("res://scripts/static_contact_cache.gd")
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 var paths:Array[String]=["res://assets/models/SOL_D07_directory_01_remaining_batch.glb","res://atrium_terrace_inhabitation_20261022/runtime/UpperAtriumInhabitation_r003.scn"]
 var results:Array=[]
 for path:String in paths:
  var packed:PackedScene=load(path);var visual:Node3D=packed.instantiate();root.add_child(visual)
  var meshes:Dictionary={}
  for node:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):meshes[node.mesh.get_instance_id()]=node.mesh
  var checked:=0;var bytes:=0
  for mesh:Mesh in meshes.values():
   var expected:PackedVector3Array=mesh.get_faces()
   assert(FACES.get_faces(mesh)==expected,"Transient welding/face order differs from original Mesh.get_faces")
   var node:=MeshInstance3D.new();node.mesh=mesh;root.add_child(node);CACHE.attach(node)
   var shape:ConcavePolygonShape3D=node.get_child(0).get_child(0).shape
   assert(shape.get_faces()==expected and node.mesh==mesh,"Shared contact pool/mesh identity changed")
   bytes+=expected.size()*12;checked+=1;node.free()
  results.append({"source":path,"sha256":FileAccess.get_sha256(path),"exact_mesh_and_shape_comparisons":checked,"face_bytes":bytes})
  print("EXACT_TRANSIENT_CONTACTS ",JSON.stringify(results[-1]))
  visual.free();packed=null;meshes.clear()
  await process_frame
 # Primitive strips and multiple surfaces use the same native ordering too.
 var strip:=ArrayMesh.new();var arrays:Array=[];arrays.resize(Mesh.ARRAY_MAX);arrays[Mesh.ARRAY_VERTEX]=PackedVector3Array([Vector3.ZERO,Vector3.RIGHT,Vector3.UP,Vector3(1,1,0)])
 strip.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLE_STRIP,arrays)
 assert(FACES.get_faces(strip)==strip.get_faces())
 var indexed:=ArrayMesh.new();arrays[Mesh.ARRAY_INDEX]=PackedInt32Array([0,1,2,3]);indexed.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLE_STRIP,arrays)
 assert(FACES.get_faces(indexed)==indexed.get_faces())
 var extra:Array=[];extra.resize(Mesh.ARRAY_MAX);extra[Mesh.ARRAY_VERTEX]=PackedVector3Array([Vector3(0,0,1),Vector3(1,0,1),Vector3(0,1,1)])
 indexed.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,extra)
 assert(FACES.get_faces(indexed)==indexed.get_faces())
 var group:=Node3D.new();root.add_child(group);var selected:Array[Node]=[];var expected_group:=PackedVector3Array()
 var box:=BoxMesh.new();box.material=StandardMaterial3D.new()
 for i in 2:
  var part:=MeshInstance3D.new();part.mesh=box;part.position=Vector3(i*3,2,1);part.rotation.y=.4*i;group.add_child(part);selected.append(part)
  for vertex:Vector3 in box.get_faces():expected_group.append(part.transform*vertex)
 CACHE.attach_group(group,selected)
 assert(group.get_node("RoomStaticContacts/SharedRoomTriangles").shape.get_faces()==expected_group)
 group.free()
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"results":results,"triangle_strip_match":true,"calls":FACES.calls,"primitive_fallback_calls":FACES.fallback_calls,"group_transforms_match":true},"\t"));f.close();quit()
