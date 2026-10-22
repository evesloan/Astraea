extends "res://scripts/d04_detail_batches_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="quiet_grove_adoption.gd":
  assert(FileAccess.get_sha256("res://quiet_court_illumination_20261022/adapter.gd") == "bb47a9f9a1fa32a351b4ec93c3812812b370acf89132d27dab78234404968875")
  assert(FileAccess.get_sha256("res://quiet_court_illumination_20261022/SURFACES.json") == "c298dbfdb88180727cfd059a8be3dad45e364ab977aefe7d12db9e7600e29fb0")
  load("res://quiet_court_illumination_20261022/adapter.gd").build(self)
