extends "res://scripts/family_specialty_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="family_d16_receiving_20261016/package.gd":
  assert(FileAccess.get_sha256("res://family_enclosure_finish_20261022/adapter.gd")=="a2cf9167d4e8739ff579e6d3949326993d687d7fb7647e404a7e07933431ff43")
  load("res://family_enclosure_finish_20261022/adapter.gd").build(self)
