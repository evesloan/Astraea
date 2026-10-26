extends SceneTree
func _initialize()->void:
 for path:String in ["res://orchard_tram_interior_20261025/integration/component_sweep.gd","res://orchard_tram_interior_20261025/integration/check_installed_components.gd"]:
  var script:Script=load(path)
  if script==null or not script.can_instantiate():quit(2);return
  print("PARSE_PASS "+path)
 quit(0)
