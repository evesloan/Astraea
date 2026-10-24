extends "res://scripts/family_aft_court_integration_20261024/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="received_sections.gd":
  var result:Node3D=load("res://clinical_room_receiving_20261024/adapter.gd").build(self)
  if result==null:
   push_error("Clinical room receiving integration failed")
   get_tree().quit(1)
