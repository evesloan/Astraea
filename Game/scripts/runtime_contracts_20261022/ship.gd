extends "res://scripts/quiet_court_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="aft_adjunct_care_20261015/package.gd":
  set_meta("fitted_roof_contact_handoff",load("res://scripts/runtime_contracts_20261022/roof_handoff.gd").prepare(self))
