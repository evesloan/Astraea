extends RefCounted
const CELLS=preload("res://spatial_instance_cells_20261026/runtime.gd")
const LIFECYCLE=preload("res://spatial_instance_cells_20261026/lifecycle.gd")
const BUDGET_SHA="99a1b9c1e986acc11c9b03a9a65515108e38a217a58a648b21cc68abac9d4c3a"
static func retained_position(light:Node3D,parents:Dictionary)->Variant:
 if light.is_inside_tree():return light.global_position
 var pose:=Transform3D.IDENTITY;var node:Node=light
 while node!=null:
  if node is Node3D:
   pose=node.transform*pose
   if node.top_level:return pose.origin
  if parents.has(node.get_instance_id()):
   var parent:Node3D=parents[node.get_instance_id()]
   if parent.is_inside_tree():return (parent.global_transform*pose).origin
   return null
  node=node.get_parent()
 return null
static func lighting(ship:Node3D,known_lights:Variant=null)->Dictionary:
 var budget:Node=ship.get_node("ShipSystems/LocalShadowSourceBudget")
 var script_path:String=budget.get_script().resource_path
 var accepted:Dictionary={"res://scripts/lighting_budget.gd":BUDGET_SHA,"res://night_garden_court_completion_20261022/lighting_budget.gd":"ef54af36bede98bab31e06d1116651fae8ab1ed19e0d0556ae493dc129c4c1e7"}
 # The retained court subclass changes pane visibility only; the exact inherited eight-source cap remains.
 if not accepted.has(script_path) or FileAccess.get_sha256(script_path)!=accepted[script_path] or budget.shadow_source_budget!=8 or FileAccess.get_sha256("res://scripts/lighting_budget.gd")!=BUDGET_SHA:
  return {"failed":"Exact unchanged eight-source light budget required"}
 var parents:Dictionary={}
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for entry:Dictionary in residency.entries:
  if not entry.attached:parents[entry.room.get_instance_id()]=entry.parent
 var lights:Array=[];var detached_lights:=0
 var registered:Array=budget.sources.duplicate();var ids:Dictionary={}
 # Include ordinary lights outside the budget too; they do not inherit its cap.
 registered.append_array(ship.find_children("*","Light3D",true,false) if known_lights==null else known_lights)
 for light in registered:
  if not is_instance_valid(light):continue
  if ids.has(light.get_instance_id()):continue
  ids[light.get_instance_id()]=true
  var position:Variant=retained_position(light,parents)
  if position==null:
   return {"failed":"Unresolved detached light owner; no sources modified","light_name":str(light.name)}
  if not light.is_inside_tree():detached_lights+=1
  lights.append({"id":light.get_instance_id(),"mask":light.light_cull_mask,"kind":0 if light is DirectionalLight3D else (1 if light is OmniLight3D else 2),"reach":0.0 if light is DirectionalLight3D else (light.omni_range if light is OmniLight3D else light.spot_range),"position":position,"managed_eight":bool(budget.requested_shadow.get(light.get_instance_id(),false))})
 return {"lights":lights,"detached_lights":detached_lights}
static func source_lighting(source:Node3D,ship_ref:WeakRef)->Dictionary:
 var ship:Node3D=ship_ref.get_ref()
 if ship==null:return {"failed":"Ship owner expired"}
 var snapshot:=lighting(ship)
 if snapshot.has("failed"):return snapshot
 var bounds:=AABB();var initialized:=false
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  var box:AABB=mesh.global_transform*mesh.get_aabb()
  bounds=bounds.merge(box) if initialized else box;initialized=true
 var relevant:Array=[]
 for light:Dictionary in snapshot.lights:
  if light.kind==0 or light.position.distance_squared_to(light.position.clamp(bounds.position,bounds.end))<=light.reach*light.reach:relevant.append(light)
 return {"lights":relevant}
