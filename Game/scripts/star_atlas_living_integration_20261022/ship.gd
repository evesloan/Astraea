extends "res://scripts/family_enclosure_integration_20261022/ship.gd"
func _construction_step(label:String)->void:
 await super._construction_step(label)
 if label=="star_atlas_d17_standard_batch.gd":
  assert(FileAccess.get_sha256("res://star_atlas_living_commons_20261022/adapter.gd")=="849538f78d3330c6784c093e90e987e3b9cc78f7fa7d4e85994fb65081fc4e13")
  load("res://star_atlas_living_commons_20261022/adapter.gd").build(self)
