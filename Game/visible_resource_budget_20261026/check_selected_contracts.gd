extends SceneTree
func _initialize()->void:
 var owner:=Node3D.new()
 var valid:bool=load("res://aquatic_tram_interior_20261026/integration/adapter.gd").verify(owner)
 print("SELECTED_ASSEMBLY_CONTRACTS ",valid);owner.free();quit(0 if valid else 1)
