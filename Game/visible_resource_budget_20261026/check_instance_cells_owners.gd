extends SceneTree
const CELLS=preload("res://visible_resource_budget_20261026/translated_instance_cells_candidate.gd")
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
  var before:=OS.get_static_memory_usage();var video_before:=Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
  var result:Dictionary=CELLS.compact(node,node.find_children("*","Light3D",true,false))
  await process_frame
  rows.append({"source":source,"source_sha256":FileAccess.get_sha256(source),"before_static":before,"after_static":OS.get_static_memory_usage(),"before_video":video_before,"after_video":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),"candidate":result})
  var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
  node.free();packed=null
  for i in 3:await process_frame
 quit()
