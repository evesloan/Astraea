extends SceneTree
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func signature(detail:Node3D)->Array:
 var values:Array=[]
 for shape:CollisionShape3D in detail.find_children("*","CollisionShape3D",true,false):
  var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256)
  assert(shape.shape is ConcavePolygonShape3D)
  hash.update(var_to_bytes(shape.shape.get_faces()))
  values.append([str(detail.get_path_to(shape)),shape.global_transform,hash.finish().hex_encode(),shape.shape.backface_collision])
 return values
func run()->void:
 var report_path:="res://precompiled_private_cells_20261026/FAMILY_COMPILE.json"
 var report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(report_path))
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new()
 var rows:Array=[];var checked_vertices:=0;var maximum_delta:=0.0
 for row:Dictionary in report.rows:
  assert(FileAccess.get_sha256(row.source)==row.source_sha256 and FileAccess.get_sha256(row.compiled)==row.sha256)
  var original:Node3D=load(str(row.source)).instantiate();root.add_child(original);manager.contacts(original)
  var expected:Array=signature(original)
  var detail:Node3D=load(str(row.compiled)).instantiate();root.add_child(detail)
  assert(signature(detail)==expected,"Exact room contact payloads, owners and poses must survive serialization")
  var merged:=0
  for mesh:MeshInstance3D in detail.find_children("*","MeshInstance3D",true,false):
   if not mesh.has_meta("precompiled_fallback"):continue
   var records:Array=mesh.get_meta("precompiled_fallback");var cursor:=0
   var actual:PackedVector3Array=load("res://precompiled_private_cells_20261026/merge.gd").raw_faces(mesh.mesh)
   for record:Array in records:
    var source:Mesh=record[1]
    var vertices:PackedVector3Array=load("res://precompiled_private_cells_20261026/merge.gd").raw_faces(source)
    for vertex:Vector3 in vertices:
     var wanted:Vector3=record[0]*vertex
     var found:Vector3=mesh.transform*actual[cursor]
     var delta:=wanted.distance_to(found);maximum_delta=maxf(maximum_delta,delta)
     assert(delta<=.00005,"Original full-resolution source triangles changed beyond existing float tolerance")
     cursor+=1;checked_vertices+=1
   assert(cursor==actual.size());merged+=1
  var refs:Array[WeakRef]=[]
  for mesh:MeshInstance3D in detail.find_children("*","MeshInstance3D",true,false):
   if mesh.mesh!=null:refs.append(weakref(mesh.mesh))
  var selected:Dictionary=load("res://precompiled_bank_cells_20261026/select_lighting.gd").apply(detail,[])
  assert(selected.saved_submissions==row.compilation.saved_submissions)
  assert(signature(detail)==expected)
  rows.append({"room_id":row.room_id,"contacts":expected.size(),"merged_cells":merged,"selected":selected})
  original.free();detail.free();expected.clear()
  await process_frame;await process_frame
  # References shared with retained original resources are covered by teardown of both roots.
  var expired:=0
  for reference:WeakRef in refs:
   if reference.get_ref()==null:expired+=1
  rows[-1].expired_mesh_references=expired;rows[-1].mesh_references=refs.size()
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"rooms":rows,"checked_vertices":checked_vertices,"maximum_source_delta_m":maximum_delta,"scope":"All47 serialized rooms: exact original contact payload/owner/pose, source triangle positions, empty-light selection. Actual ship lighting, lifecycle selection and visual comparison still pending."},"\t"));f.close();manager.free();quit()
