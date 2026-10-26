extends "res://tram_live_route_20261026/check_ownership.gd"
func operate(assembly:Node3D)->Dictionary:
 var result:Dictionary=load("res://spatial_instance_cells_20261026/package.gd").install(ship)
 require(not result.has("failed") and int(result.get("saved_potential_submissions",0))>=3000,"Installed batching must justify movement comparison")
 if failures>0:return {"stage":"candidate_not_warranted","candidate":result}
 return await super.operate(assembly)
