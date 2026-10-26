extends SceneTree
const CELLS=preload("res://spatial_instance_cells_20261026/runtime.gd")
const RULES=preload("res://spatial_instance_cells_20261026/rules.gd")
const LEASE=preload("res://group2_resource_lifetime_20261025/mesh_lease.gd")
const PACKAGE=preload("res://spatial_instance_cells_20261026/package.gd")
class ResidencyFixture extends Node:
 var entries:Array=[]
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func run()->void:
 var lights:Array=[]
 for i in 73:lights.append({"id":i+1,"kind":1,"mask":1,"reach":100.0,"position":Vector3.ZERO,"managed_eight":true})
 var box:=AABB(Vector3.ZERO,Vector3.ONE)
 assert(RULES.light_signature(box,1,lights)!="OVER_LIMIT")
 lights.append({"id":100,"kind":1,"mask":1,"reach":100.0,"position":Vector3.ZERO})
 assert(RULES.light_signature(box,1,lights)=="OVER_LIMIT")
 lights.pop_back()
 var ship:=Node3D.new();root.add_child(ship)
 var host:=Node3D.new();host.name="ShipSpace";ship.add_child(host)
 var systems:=Node.new();systems.name="ShipSystems";ship.add_child(systems)
 var residency:=ResidencyFixture.new();residency.name="ReceivedRoomResidency";systems.add_child(residency)
 var budget:Node=load("res://scripts/lighting_budget.gd").new();budget.name="LocalShadowSourceBudget";systems.add_child(budget)
 for i in 73:
  var light:=OmniLight3D.new();light.omni_range=100.0;light.visible=false;host.add_child(light)
  budget.sources.append(light);budget.requested_shadow[light.get_instance_id()]=true
 var path:="res://assets/models/SOL_D10_directory_06_source001.glb"
 var packed:PackedScene=load(path);var room:=Node3D.new();host.add_child(room)
 var visual:Node3D=packed.instantiate();room.add_child(visual)
 assert(LEASE.bind(room,visual,packed,path,true));packed=null
 var identity:Dictionary={};var contacts:Dictionary={};var rows:Array=[]
 for node:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  load("res://scripts/static_contact_cache.gd").attach(node)
  node.set_surface_override_material(0,node.get_active_material(0))
  identity[node.get_instance_id()]={"node":weakref(node),"pose":node.transform,"parent":node.get_parent().get_instance_id(),"material":node.get_active_material(0)}
 for body:CollisionObject3D in visual.find_children("*","CollisionObject3D",true,false):contacts[body.get_instance_id()]={"node":weakref(body),"pose":body.transform,"layer":body.collision_layer,"mask":body.collision_mask}
 var entry:Dictionary={"room":room,"parent":host,"attached":true};residency.entries.append(entry)
 var installed:Dictionary=PACKAGE.install(ship)
 assert(not installed.has("failed") and installed.saved_potential_submissions>1000)
 var controller:Node=visual.get_node("ExactInstanceLifecycle")
 for cycle in 2:
  controller.activate()
  var result:Dictionary=controller.last_result.duplicate()
  assert(result.saved_submissions>1000)
  var resources:Array=[]
  for batch:MultiMeshInstance3D in visual.find_children("*","MultiMeshInstance3D",true,false):
   if batch.multimesh!=null:resources.append(weakref(batch.multimesh));resources.append(weakref(batch.multimesh.mesh))
  entry.attached=false;host.remove_child(room)
  assert(not visual.has_meta("exact_instance_restore"),"Tree exit must restore before mesh lease suspension")
  for id:int in identity:
   var saved:Dictionary=identity[id];var node:MeshInstance3D=saved.node.get_ref()
   assert(node!=null and node.get_instance_id()==id and node.transform==saved.pose and node.get_parent().get_instance_id()==saved.parent and node.get_active_material(0)==saved.material and node.get_surface_override_material(0)==saved.material)
  for id:int in contacts:
   var saved:Dictionary=contacts[id];var body:CollisionObject3D=saved.node.get_ref()
   assert(body.get_instance_id()==id and body.transform==saved.pose and body.collision_layer==saved.layer and body.collision_mask==saved.mask)
  var original_resources:Array=[]
  for node:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):original_resources.append(weakref(node.mesh))
  var suspended:=LEASE.suspend(room)
  assert(suspended==identity.size())
  for i in 3:await process_frame
  for reference:WeakRef in resources:assert(reference.get_ref()==null,"Batch resources survive release")
  for reference:WeakRef in original_resources:assert(reference.get_ref()==null,"Original resources survive release")
  assert(LEASE.resume(room));entry.attached=true;host.add_child(room)
  result.cycle=cycle;result.original_nodes_preserved=identity.size();result.contact_bodies_preserved=contacts.size();result.suspended=suspended;rows.append(result)
 room.free();ship.free()
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"cycles":rows,"managed_light_count":73,"unmanaged_overflow_rejected":true},"\t"));f.close();quit()
