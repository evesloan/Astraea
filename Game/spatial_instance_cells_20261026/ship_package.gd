extends Node
# Opt-in broad static-source renderer. No production scene is changed by this file.
const PACKAGE=preload("res://spatial_instance_cells_20261026/package.gd")
const LIFECYCLE=preload("res://spatial_instance_cells_20261026/ship_lifecycle.gd")
var ship_ref:WeakRef
var contracts:Dictionary={}
var registered:Dictionary={}
var initial_rows:Array=[]
var rejected_dynamic:=0
var rejected_unretained:=0
var scheduled:Dictionary={}
func scope(node:Node)->bool:
 if not node is Node3D or not node.scene_file_path.ends_with(".glb"):return false
 var ship:Node3D=ship_ref.get_ref()
 if ship==null:return false
 var current:Node=node
 while current!=null and current!=ship:
  if current is CollisionObject3D or current is AnimationPlayer or current.get_script()!=null:
   rejected_dynamic+=1;return false
  if current!=node and registered.has(current.get_instance_id()):return false
  current=current.get_parent()
 # Detached registered received rooms are explicitly traversed during install only.
 return current==ship
func attach_source(node:Node3D)->Dictionary:
 if registered.has(node.get_instance_id()):return {}
 if not node.find_children("*","AnimationPlayer",true,false).is_empty() or not node.find_children("*","AnimationTree",true,false).is_empty():
  rejected_dynamic+=1;return {}
 var path:String=node.scene_file_path
 if not contracts.has(path):rejected_unretained+=1;return {}
 if FileAccess.get_sha256(path)!=contracts[path]:
  push_error("Retained static render source changed: "+path);return {"failed":"source_hash"}
 var controller:Node=LIFECYCLE.new();controller.name="ExactInstanceLifecycle"
 controller.light_provider=PACKAGE.source_lighting.bind(ship_ref)
 registered[node.get_instance_id()]=weakref(node)
 node.add_child(controller)
 if node.is_inside_tree():controller.activate()
 var row:Dictionary=controller.last_result.duplicate()
 row.source=path;row.owner=str(node.get_path()) if node.is_inside_tree() else str(node.name)
 return row
func added(node:Node)->void:
 if not scope(node):return
 if scheduled.has(node.get_instance_id()):return
 scheduled[node.get_instance_id()]=true
 activate_later.call_deferred(weakref(node),node.get_instance_id())
func activate_later(reference:WeakRef,id:int)->void:
 # Synchronous source receiving/contact creation finishes before this deferred call.
 scheduled.erase(id)
 var node:Node3D=reference.get_ref()
 if node==null or not node.is_inside_tree() or not scope(node):return
 var row:=attach_source(node)
 if not row.is_empty():print("SHIP_INSTANCE_ACTIVATION ",JSON.stringify(row))
func statistics()->Dictionary:
 var saved:=0;var batches:=0;var converted:=0;var active:=0;var expired:Array=[]
 for id:int in registered:
  var node:Node3D=registered[id].get_ref()
  if node==null:expired.append(id);continue
  var controller:Node=node.get_node_or_null("ExactInstanceLifecycle")
  if node.is_inside_tree() and node.has_meta("exact_instance_restore") and controller!=null:
   active+=1;saved+=int(controller.last_result.get("saved_submissions",0));batches+=int(controller.last_result.get("batch_count",0));converted+=int(controller.last_result.get("converted_mesh_instances",0))
 for id:int in expired:registered.erase(id)
 return {"active_sources":active,"registered_sources":registered.size(),"saved_potential_submissions":saved,"batches":batches,"converted_originals":converted,"dynamic_rejections":rejected_dynamic,"unretained_rejections":rejected_unretained}
func install(ship:Node3D)->Dictionary:
 ship_ref=weakref(ship)
 contracts=JSON.parse_string(FileAccess.get_file_as_string("res://spatial_instance_cells_20261026/STATIC_SOURCE_PINS.json"))
 var snapshot:=PACKAGE.lighting(ship)
 if snapshot.has("failed"):return snapshot
 var pending:Array[Node]=[ship.get_node("ShipSpace/Districts")]
 while not pending.is_empty():
  var node:Node=pending.pop_back()
  if scope(node):
   var row:=attach_source(node)
   if row.has("failed"):return row
   if not row.is_empty():
    initial_rows.append(row);print("SHIP_INSTANCE_SOURCE ",JSON.stringify(row))
   continue
  for child:Node in node.get_children():pending.append(child)
 # Reattached rooms and newly loaded private detail enter through the normal owner lifecycle.
 ship.get_tree().node_added.connect(added)
 var result:=statistics();result.initial_rows=initial_rows;result.selected_default=false
 print("SHIP_INSTANCE_INSTALL ",JSON.stringify(result));return result
