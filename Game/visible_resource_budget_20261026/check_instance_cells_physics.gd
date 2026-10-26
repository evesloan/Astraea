extends SceneTree
const CELLS=preload("res://spatial_instance_cells_20261026/runtime.gd")
var output:String
var rows:Array=[]
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 for name:String in ["SOL_D10_directory_06_source001.glb","SOL_D09_directory_03_source001.glb","SOL_D11_directory_05_source001.glb","SOL_D11_directory_07_source001.glb","SOL_D11_directory_03_source001.glb","SOL_D11_directory_04_source001.glb","SOL_D10_directory_10_source001.glb","SOL_D09_directory_07_source001.glb","SOL_D01_directory_10_remaining_r001.glb"]:
  var source:="res://assets/models/"+name
  var packed:PackedScene=load(source);var node:Node3D=packed.instantiate();root.add_child(node)
  var contacts:Dictionary={}
  for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
   load("res://scripts/static_contact_cache.gd").attach(mesh)
  for body:CollisionObject3D in node.find_children("*","CollisionObject3D",true,false):contacts[str(node.get_path_to(body))]={"id":body.get_instance_id(),"pose":body.global_transform,"layer":body.collision_layer,"mask":body.collision_mask}
  var before:=OS.get_static_memory_usage();var video_before:=Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
  var result:Dictionary=CELLS.compact(node,node.find_children("*","Light3D",true,false))
  for path:String in contacts:
   var body:CollisionObject3D=node.get_node(path);var saved:Dictionary=contacts[path]
   assert(body.get_instance_id()==saved.id and body.global_transform==saved.pose and body.collision_layer==saved.layer and body.collision_mask==saved.mask)
  result.physics_identity_checks=contacts.size()
  var weak_resources:Array[WeakRef]=[]
  for batch:MultiMeshInstance3D in node.find_children("*","MultiMeshInstance3D",true,false):weak_resources.append(weakref(batch.multimesh));weak_resources.append(weakref(batch.multimesh.mesh))
  await process_frame
  rows.append({"source":source,"source_sha256":FileAccess.get_sha256(source),"before_static":before,"after_static":OS.get_static_memory_usage(),"before_video":video_before,"after_video":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),"candidate":result})
  var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
  node.free();packed=null
  for i in 3:await process_frame
  for ref:WeakRef in weak_resources:assert(ref.get_ref()==null,"Instance resource retained after owner teardown")
 quit()
