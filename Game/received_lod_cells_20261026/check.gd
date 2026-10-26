extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var results:Array=[]
 for name:String in ["SOL_D10_directory_06_source001.glb","SOL_D11_directory_05_source001.glb"]:
  var source:String="res://assets/models/"+name
  var node:Node3D=load(source).instantiate();root.add_child(node)
  var before:Array=[]
  for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
   before.append([mesh,mesh.mesh,mesh.layers,mesh.transform,mesh.get_active_material(0)])
  var row:Dictionary=load("res://received_lod_cells_20261026/runtime.gd").compact(node,[])
  assert(row.saved_submissions>0,"Fixture must engage repeated components")
  for preimage:Array in before:
   assert(preimage[0].mesh==preimage[1] and preimage[0].transform==preimage[3] and preimage[0].get_active_material(0)==preimage[4],"Original mesh/material/pose identity preserved")
   if preimage[0].layers==0:
    for surface:Dictionary in preimage[1].get("_surfaces"):assert(surface.get("lods",[]).is_empty(),"Imported LOD must remain original")
  assert(load("res://received_lod_cells_20261026/runtime.gd").restore(node))
  for preimage:Array in before:assert(preimage[0].layers==preimage[2] and preimage[0].mesh==preimage[1])
  row.source=source;row.sha256=FileAccess.get_sha256(source);results.append(row)
  node.free();await process_frame
 print("RECEIVED_COMPONENT_CHECK ",JSON.stringify(results));quit()
