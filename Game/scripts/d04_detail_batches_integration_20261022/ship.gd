extends "res://scripts/runtime_contracts_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="structural_floor_builder.gd":
  load("res://d04_detail_batches_20261022/adapter.gd").install(self)
