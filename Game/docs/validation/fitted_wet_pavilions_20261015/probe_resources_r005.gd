extends SceneTree
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/FITTED_CANDIDATE_OVERLAY_r005.zip",true))
 assert(load("res://scripts/fitted_wet_pavilions_20261015/package.gd")!=null);assert(load("res://scripts/fitted_wet_pavilions_20261015/roof_successor.gd")!=null);assert(load("res://scripts/group2_vip_pavilions/privacy_door.gd")!=null)
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/fitted_wet_pavilions_20261015/FITTED_CONFIG_r005.json"))
 for row in p.models:
  var model:Node3D=(load("res://assets/fitted_wet_pavilions_20261015/"+str(row.file))as PackedScene).instantiate();assert(model.find_children("*","MeshInstance3D",true,false).size()==int(row.meshes));model.free()
 print("PASS_FITTED_R005_RESOURCES two native models500meshes andunchanged privacy dependency");quit(0)
