extends SceneTree
const LIGHTING=preload("res://spatial_instance_cells_20261026/ship_lighting.gd")
const PACKAGE=preload("res://spatial_instance_cells_20261026/ship_package.gd")
class Residency extends Node:
 var entries:Array=[]
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 var ship:=Node3D.new();root.add_child(ship)
 var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
 var systems:=Node.new();systems.name="ShipSystems";ship.add_child(systems)
 var residency:=Residency.new();residency.name="ReceivedRoomResidency";systems.add_child(residency)
 var budget:Node=load("res://night_garden_court_completion_20261022/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 for i in 73:
  var light:=OmniLight3D.new();light.position=Vector3(i,2,0);space.add_child(light);budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true
 var representation:=PACKAGE.new();ship.add_child(representation);var installed:Dictionary=representation.install(ship);assert(not installed.has("failed"))
 var filler:=Node.new();space.add_child(filler)
 for i in 120000:filler.add_child(Node.new())
 var dynamic:=OmniLight3D.new();dynamic.position=Vector3(5,7,9);space.add_child(dynamic)
 await process_frame
 assert(representation.light_refs.has(dynamic.get_instance_id()),"New ordinary light must be tracked")
 var old_times:Array=[];var new_times:Array=[];var comparisons:=0
 for iteration in 5:
  var start:=Time.get_ticks_usec();var original:Dictionary=LIGHTING.lighting(ship);old_times.append(Time.get_ticks_usec()-start)
  var known:Array=[]
  for id:int in representation.light_refs:
   var light:Light3D=representation.light_refs[id].get_ref()
   if light!=null and light.is_inside_tree() and ship.is_ancestor_of(light):known.append(light)
  start=Time.get_ticks_usec();var indexed:Dictionary=LIGHTING.lighting(ship,known);new_times.append(Time.get_ticks_usec()-start)
  assert(original==indexed,"Registry changed exact light descriptors");comparisons+=1
  dynamic.position+=Vector3(1,0,0)
 var expired_id:int=dynamic.get_instance_id();dynamic.free()
 var probe:=Node3D.new();space.add_child(probe)
 await process_frame
 representation.source_lighting(probe)
 assert(not representation.light_refs.has(expired_id),"Expired ordinary light retained")
 old_times.sort();new_times.sort()
 var result:Dictionary={"status":"PASS","exact_descriptor_comparisons":comparisons,"nonlight_nodes":120000,"live_lights":73,"ordinary_add_move_free_preserved":true,"old_scene_discovery_median_usec":old_times[2],"registry_descriptor_median_usec":new_times[2],"scope":"Isolated discovery cost, not actual ship FPS or total activation cost"}
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();ship.free();quit()
