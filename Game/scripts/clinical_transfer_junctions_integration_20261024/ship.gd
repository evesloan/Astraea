extends "res://scripts/clinical_return_links_integration_20261024/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="remaining_batch_receiving.gd":
  var result:Node3D=load("res://clinical_transfer_junctions_20261024/adapter.gd").build(self)
  if result==null:
   push_error("Clinical transfer junction integration failed")
   get_tree().quit(1)
