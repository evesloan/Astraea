extends "res://tram_live_route_20261026/check_ownership.gd"
var representation:Node
func operate(assembly:Node3D)->Dictionary:
 representation=load("res://spatial_instance_cells_20261026/ship_package.gd").new()
 representation.name="StaticSourceRepresentation";ship.add_child(representation)
 var result:Dictionary=representation.install(ship)
 require(not result.has("failed") and int(result.get("saved_potential_submissions",0))>=10000,"Broad static source batching must justify movement")
 if failures>0:return {"stage":"candidate_not_warranted","candidate":result}
 return await super.operate(assembly)
func _process(delta:float)->bool:
 var prior:int=next_sample
 var result:bool=super._process(delta)
 if representation!=null and is_instance_valid(representation) and next_sample!=prior:
  print("SHIP_INSTANCE_SAMPLE ",JSON.stringify(representation.statistics()))
 return result
