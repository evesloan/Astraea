extends "res://scripts/family_specialty_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="family_d16_receiving_20261016/package.gd":
  assert(FileAccess.get_sha256("res://family_reading_garden_20261022/adapter.gd")=="5c17ac6250fe1fafe3b7245e59c291aac7d89466d6be0adc741ec18ffa51d90b")
  load("res://family_reading_garden_20261022/adapter.gd").build(self)
