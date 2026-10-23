extends "res://scripts/star_atlas_living_integration_20261022/ship.gd"
func _ready()->void:
 var controller:Node=load("res://d04_surface_cells_20261023/controller.gd").new()
 controller.name="D04SurfaceCellResearch";add_child(controller);controller.setup(self)
 await super._ready()
