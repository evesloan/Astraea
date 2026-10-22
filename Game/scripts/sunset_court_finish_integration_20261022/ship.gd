extends "res://scripts/sunset_specialty_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="sunset_adoption.gd":
  assert(FileAccess.get_sha256("res://sunset_court_finish_20261022/adapter_r002.gd")=="f8c09c232fa8f3b1b727aaf8168ee984323dbadca23d1cdeb3cd4312753ebef5")
  load("res://sunset_court_finish_20261022/adapter_r002.gd").build(self)
