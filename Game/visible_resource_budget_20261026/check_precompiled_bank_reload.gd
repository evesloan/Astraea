extends SceneTree
var output:String
func _initialize()->void:
 for a:String in OS.get_cmdline_user_args():
  if a.begins_with("--output="):output=a.substr(9)
 call_deferred("run")
func run()->void:
 var rows:Array=[]
 for file:String in ["AST-CRW-G3-003_current_columns_r001","G3_REMAINING_BANK_RECEIVERS_r001"]:
  var path:="res://precompiled_bank_cells_20261026/r005/"+file+".scn"
  var packed:PackedScene=load(path);var node:Node3D=packed.instantiate();packed=null;root.add_child(node)
  var contacts:=0;var records:=0;var cells:=0
  for body:StaticBody3D in node.find_children("*","StaticBody3D",true,false):
   if body.get_script()!=null and body.get_script().resource_path=="res://precompiled_bank_cells_20261026/contact_cell.gd":
    cells+=1;records+=body.records.size()
    for id:int in body.get_shape_owners():contacts+=body.shape_owner_get_shape_count(id)
  assert(records==contacts,"Serialized contact bindings differ")
  rows.append({"file":file,"nodes":node.find_children("*","",true,false).size()+1,"meshes":node.find_children("*","MeshInstance3D",true,false).size(),"contact_cells":cells,"contact_records":records,"actual_shape_bindings":contacts})
  node.free();await process_frame
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close();quit()
