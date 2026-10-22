extends SceneTree
func _initialize()->void:
 for name:String in ["ship","launcher","presentation","bootstrap"]:
  var script:Script=load("res://scripts/quiet_court_illumination_integration_20261022/"+name+".gd")
  assert(script!=null and script.can_instantiate())
 for name:String in ["ship","main","launcher","bootstrap"]:
  var scene:PackedScene=load("res://scenes/"+name+"_quiet_court_illumination_20261022.tscn")
  assert(scene!=null)
 assert(ProjectSettings.get_setting("application/run/main_scene")=="res://scenes/bootstrap_quiet_court_illumination_20261022.tscn")
 print("QUIET_ILLUMINATION_ENTRYPOINTS_PASS");quit()
