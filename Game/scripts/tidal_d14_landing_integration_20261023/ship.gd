extends "res://scripts/star_atlas_living_integration_20261022/ship.gd"
# Preserve all predecessors; install once after the actual Tidal receiving owner.
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="tidal_garden_adoption.gd":
  if FileAccess.get_sha256("res://tidal_d14_landing_20261023/adapter.gd")!="28e03f809fe168159b5434e0f391f4b43745f005be4aa4dd7823e22adfe40849":
   push_error("Tidal landing adapter bytes differ");return
  load("res://tidal_d14_landing_20261023/adapter.gd").after_step(self,label)
