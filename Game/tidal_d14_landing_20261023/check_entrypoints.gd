extends SceneTree
func _initialize()->void:
 var paths:=["res://scripts/tidal_d14_landing_integration_20261023/ship.gd","res://scripts/tidal_d14_landing_integration_20261023/bootstrap.gd","res://scripts/tidal_d14_landing_integration_20261023/launcher.gd","res://scripts/tidal_d14_landing_integration_20261023/presentation.gd"]
 for path in paths:
  var script=load(path)
  if script==null or not script.can_instantiate():push_error("entrypoint parse failed: "+path);quit(1);return
 print("TIDAL_ENTRYPOINT_PARSE PASS 4 script resources; no ship instantiation")
 quit()
