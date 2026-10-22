extends "res://scripts/sunset_court_finish_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="family_d16_receiving_20261016/package.gd":
  assert(FileAccess.get_sha256("res://family_specialty_bank_20261022/adapter.gd")=="ac97552a128a5de2a5c80b2a889de0b738c782a29e7615783a6a69a36c123cc0")
  load("res://family_specialty_bank_20261022/adapter.gd").build(self)
