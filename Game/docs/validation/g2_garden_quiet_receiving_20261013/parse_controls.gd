extends SceneTree
func _initialize()->void:
 var script:Script=load("/workspace/astraea-integration-cutoff-20261013/g2_garden_receiving/validate_installed_and_service_controls.gd")
 assert(script!=null and script.can_instantiate())
 print("INSTALLED_CONTROLS_PARSER_PASS")
 quit(0)
