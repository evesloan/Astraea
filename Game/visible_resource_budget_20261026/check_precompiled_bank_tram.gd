extends "res://tram_live_route_20261026/check_ownership.gd"
var bank_builder_replaced:=false
func _process(delta:float)->bool:
 if not bank_builder_replaced and is_instance_valid(ship):
  var queue:Array=ship.startup_deferred_builders
  for i in queue.size():
   var builder:Callable=queue[i]
   var source:Object=builder.get_object()
   if source is Script and source.resource_path=="res://scripts/group3_remaining_crew_20261019/package.gd":
    assert(ship.find_child("Group3RemainingCrewBank",true,false)==null,"Existing bank cannot be reconstructed in place")
    queue[i]=Callable(load("res://precompiled_bank_cells_20261026/runtime_package.gd"),"build").bind(ship)
    bank_builder_replaced=true;print("PRECOMPILED_BANK_BUILDER_BOUND_ONCE");break
 return super._process(delta)
func operate(assembly:Node3D)->Dictionary:
 require(bank_builder_replaced,"Original deferred bank builder replaced once before construction")
 if failures>0:return {"stage":"builder_not_bound"}
 var bank:Node3D=ship.find_child("Group3RemainingCrewBank",true,false)
 require(bank!=null and bank.has_meta("precompiled_crew_bank"),"Direct precompiled source loaded")
 if failures>0:return {"stage":"compiled_bank_missing"}
 var snapshot:Dictionary=load("res://spatial_instance_cells_20261026/ship_lighting.gd").lighting(ship)
 require(not snapshot.has("failed"),"Exact original light budget and all additional sources")
 if failures>0:return {"stage":"light_snapshot_failed"}
 var selected:Dictionary=load("res://precompiled_bank_cells_20261026/select_lighting.gd").apply(bank,snapshot.lights)
 selected.bank_nodes=bank.find_children("*","",true,false).size()+1
 print("PRECOMPILED_BANK_SELECTED ",JSON.stringify(selected))
 require(selected.saved_submissions>=7000 and selected.bank_nodes<=34000,"Meaningful direct representation reduction required")
 if failures>0:return {"stage":"precompiled_reduction_not_warranted","candidate":selected}
 var result:Dictionary=await super.operate(assembly);result.precompiled_bank=selected;return result
