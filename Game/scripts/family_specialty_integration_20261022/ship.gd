extends "res://scripts/sunset_court_finish_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="family_d16_receiving_20261016/package.gd":
  assert(FileAccess.get_sha256("res://family_specialty_bank_20261022/adapter_r002.gd")=="23b8f681fa0e1a95b976f8f134ca303cadf71f8bc8bae9f5b54c2f07150b86ac")
  load("res://family_specialty_bank_20261022/adapter_r002.gd").build(self)
