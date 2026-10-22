extends "res://scripts/quiet_court_illumination_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="quiet_grove_adoption.gd":
  assert(FileAccess.get_sha256("res://quiet_court_balance_20261022/adapter_r002.gd")=="a417d32bc9914e80d6abe8465e85e44bcbefeea3e956c10e8349afa170503873")
  load("res://quiet_court_balance_20261022/adapter_r002.gd").build(self)
