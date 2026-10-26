extends "res://visible_resource_budget_20261026/check_precompiled_bank_tram.gd"
var private_installed:Dictionary={}
func _process(delta:float)->bool:
 if private_installed.is_empty() and is_instance_valid(ship) and bool(ship.get_meta("runtime_ready",false)):
  private_installed=load("res://precompiled_private_cells_20261026/install.gd").install(ship.private_detail_residency)
  print("PRECOMPILED_PRIVATE_INSTALLED ",JSON.stringify(private_installed))
 return super._process(delta)
func operate(assembly:Node3D)->Dictionary:
 require(not private_installed.is_empty(),"Private successor installed on exact original manager object")
 if failures>0:return {"stage":"private_successor_not_installed"}
 var result:Dictionary=await super.operate(assembly)
 var manager:Node=ship.private_detail_residency
 result.precompiled_private={"installation":private_installed,"compiled_loads":manager.compiled_loads,"cumulative_saved_submissions":manager.compiled_saved_submissions,"residency":manager.statistics()}
 require(manager.compiled_loads>0,"Changed-state route must actually exercise compiled private detail")
 return result
