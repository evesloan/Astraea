extends SceneTree
func _initialize()->void:
 for name in ["bootstrap","launcher","presentation","ship","roof_handoff"]:
  var script=load("res://scripts/runtime_contracts_20261022/"+name+".gd")
  assert(script!=null and script.can_instantiate())
 print("NEW_SCRIPT_PARSE_PASS");quit()
