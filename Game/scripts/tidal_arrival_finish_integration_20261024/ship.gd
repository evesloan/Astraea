extends "res://scripts/tidal_court_finish_integration_20261023/ship.gd"
# One additive package, after the unchanged receiving/adoption and surface finish.
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="tidal_garden_adoption.gd":
  if FileAccess.get_sha256("res://tidal_arrival_finish_20261024/adapter_r002.gd")!="8d47a3989d73d29b8efba4c360d247b600156136ad13026e58fe684f2ff42cbc":
   push_error("Tidal arrival adapter differs");return
  load("res://tidal_arrival_finish_20261024/adapter_r002.gd").build(self)
