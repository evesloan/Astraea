extends "res://scripts/night_garden_lower_courts_integration_20261024/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="approved_receivers_20261014/package.gd":
  var district:Node3D=load("res://family_aft_court_20261024/adapter.gd").build(self)
  if district==null:
   push_error("Family aft court integration failed")
   get_tree().quit(1)
