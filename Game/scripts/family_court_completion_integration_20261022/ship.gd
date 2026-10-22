extends "res://scripts/family_specialty_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="family_d16_receiving_20261016/package.gd":
  assert(FileAccess.get_sha256("res://family_court_completion_20261022/adapter_r004.gd")=="7228e0ccc3522cc73408e224cee4bcb17e978b1780cabb0bef97c95e77da3980")
  load("res://family_court_completion_20261022/adapter_r004.gd").build(self)
