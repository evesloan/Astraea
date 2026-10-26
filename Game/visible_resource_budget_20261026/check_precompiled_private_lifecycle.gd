extends SceneTree
class Residency extends Node:
 var entries:Array=[]
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 var host:=Node3D.new();root.add_child(host);host.set_meta("runtime_ready",true)
 var systems:=Node.new();systems.name="ShipSystems";host.add_child(systems)
 var residency:=Residency.new();residency.name="ReceivedRoomResidency";systems.add_child(residency)
 var budget:Node=load("res://night_garden_court_completion_20261022/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new();host.add_child(manager);manager.host=host;manager.loads=7;manager.releases=3
 var report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://precompiled_private_cells_20261026/FAMILY_COMPILE.json"))
 manager.index=JSON.parse_string(FileAccess.get_file_as_string(report.index)).rooms
 var installed:Dictionary=load("res://precompiled_private_cells_20261026/install.gd").install(manager)
 assert(manager.loads==7 and manager.releases==3)
 var activations:=0;var expired:=0;var identities:=0
 for file:String in manager.index:
  var record:Dictionary=manager.index[file];var home:=Node3D.new();home.name=record.room_id;host.add_child(home)
  var original_id:=home.get_instance_id()
  var entry:Dictionary={"home":weakref(home),"record":record,"detail":null,"hidden":0.0}
  for iteration in 2:
   manager._load_entry(entry);assert(is_instance_valid(entry.detail));activations+=1
   assert(entry.detail.name=="ResidentPrivateFurnishings" and entry.detail.get_parent()==home)
   var same:Node=entry.detail;var loads:int=manager.loads;manager._load_entry(entry);assert(entry.detail==same and manager.loads==loads)
   var reference:WeakRef=weakref(entry.detail)
   manager._release_entry(entry);same=null
   await process_frame;await process_frame
   assert(reference.get_ref()==null and entry.detail==null);expired+=1
   assert(home.get_instance_id()==original_id and str(home.name)==record.room_id);identities+=1
  home.free()
 assert(manager.compiled_loads==94 and manager.loads==101 and manager.releases==97)
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"installed":installed,"activations":activations,"released_detail_roots":expired,"preserved_room_identities":identities,"compiled_loads":manager.compiled_loads,"scope":"All47 rooms loaded/released/reactivated through the actual inherited manager methods, exact same manager object and prior counters/state. Empty-light fixture; actual ship lighting and frame times remain untested."},"\t"));f.close();host.free();quit()
