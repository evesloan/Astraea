extends "res://scripts/clinical_room_receiving_integration_20261024/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="received_sections.gd":
  var result:Node3D=load("res://clinical_return_links_20261024/adapter.gd").build(self)
  if result==null:
   push_error("Clinical through-route integration failed")
   get_tree().quit(1)
