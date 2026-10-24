extends "res://scripts/tidal_d14_landing_integration_20261023/ship.gd"
# Add only the five-level surface/fixture successor after retained receiving.
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="tidal_garden_adoption.gd":
  if FileAccess.get_sha256("res://tidal_court_finish_20261023/adapter_r002.gd")!="446e60b18ccefd647c3039ae0cb17a0152386df79d323daeb2bed84045a8ec85":
   push_error("Tidal court finish adapter differs");return
  load("res://tidal_court_finish_20261023/adapter_r002.gd").build(self)
