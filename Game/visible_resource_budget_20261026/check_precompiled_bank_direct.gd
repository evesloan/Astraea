extends SceneTree
var output:String
var samples:Array=[]
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func sample(stage:String)->void:samples.append({"stage":stage,"static_bytes":OS.get_static_memory_usage(),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"video_bytes":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)})
func run()->void:
 var host:Node3D=load("res://visible_resource_budget_20261026/bank_fixture_host.gd").new();root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 sample("before")
 var bank:Node3D=load("res://precompiled_bank_cells_20261026/runtime_package.gd").build(host)
 await process_frame;sample("original")
 var doors:Dictionary={}
 for child:Node in bank.get_children():
  if child.get_script()!=null:doors[child.name]={"id":child.get_instance_id(),"persistent_id":str(child.persistent_id),"pose":child.transform}
 var lights:Array=[]
 for light:Light3D in budget.sources:lights.append({"id":light.get_instance_id(),"kind":1,"mask":light.light_cull_mask,"reach":light.omni_range,"position":light.global_position,"managed_eight":true})
 var start:=Time.get_ticks_usec()
 var result:Dictionary=load("res://precompiled_bank_cells_20261026/select_lighting.gd").apply(bank,lights)
 assert(not result.has("failed"),str(result))
 result.elapsed_us=Time.get_ticks_usec()-start
 for name:String in doors:
  var door:Node3D=bank.get_node(name);assert(door.get_instance_id()==doors[name].id and str(door.persistent_id)==doors[name].persistent_id and door.transform==doors[name].pose)
 await process_frame;sample("compiled")
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"samples":samples,"result":result,"door_identity_checks":doors.size(),"default_selected":false},"\t"));f.close()
 host.free();quit()
