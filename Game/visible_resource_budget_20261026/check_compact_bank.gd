extends SceneTree
var output:String
var rows:Array=[]
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func sample(stage:String)->void:
 rows.append({"stage":stage,"static_bytes":OS.get_static_memory_usage(),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"video_bytes":Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)})
func run()->void:
 var host:Node3D=load("res://visible_resource_budget_20261026/bank_fixture_host.gd").new();host.name="Fixture";root.add_child(host)
 var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 sample("before")
 var bank:Node3D=load("res://scripts/group3_remaining_crew_20261019/package.gd").build(host)
 await process_frame
 sample("original")
 var bodies:Dictionary={};var doors:Dictionary={}
 for body:CollisionObject3D in bank.find_children("*","CollisionObject3D",true,false):bodies[str(bank.get_path_to(body))]={"id":body.get_instance_id(),"pose":body.global_transform,"layer":body.collision_layer,"mask":body.collision_mask}
 for node in bank.get_children():
  if node.get_script()!=null:doors[str(node.name)]=node.get_instance_id()
 var start:=Time.get_ticks_usec()
 var result:Dictionary=load("res://visible_resource_budget_20261026/compact_cells_candidate.gd").build(bank,budget.sources)
 result.elapsed_us=Time.get_ticks_usec()-start
 var checks:=0
 for path:String in bodies:
  var body:CollisionObject3D=bank.get_node(path);var saved:Dictionary=bodies[path]
  assert(body.get_instance_id()==saved.id and body.global_transform.is_equal_approx(saved.pose) and body.collision_layer==saved.layer and body.collision_mask==saved.mask);checks+=1
 for name:String in doors:assert(bank.get_node(name).get_instance_id()==doors[name]);checks+=1
 await process_frame
 sample("compacted")
 rows.append({"candidate":result,"identity_checks":checks,"production_selected":false})
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(rows,"\t"));f.close()
 host.free();quit()
