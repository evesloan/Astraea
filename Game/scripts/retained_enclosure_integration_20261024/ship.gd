extends "res://scripts/sunset_enclosure_integration_20261024/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="star_atlas_d17_standard_batch.gd":
  var enclosure:Node3D=load("res://star_atlas_enclosure_integration_20261024/adapter.gd").build(self)
  if enclosure==null:
   push_error("Retained StarAtlas enclosure integration failed")
   get_tree().quit(1)
