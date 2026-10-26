extends RefCounted
const CELLS=preload("res://spatial_instance_cells_20261026/runtime.gd")
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
static func install(ship:Node3D)->Dictionary:
 assert(not ship.has_meta("spatial_instance_cells"),"Single runtime representation owner")
 var sources:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://spatial_instance_cells_20261026/SOURCES.json"))
 for path:String in sources:
  if FileAccess.get_sha256(path)!=sources[path]:push_error("Instance source changed: "+path);return {"failed":"source_hash"}
 var pending:Array[Node]=[ship.get_node("ShipSpace")];var roots:Array[Node3D]=[]
 while not pending.is_empty():
  var node:Node=pending.pop_back()
  if sources.has(node.scene_file_path):roots.append(node);continue
  for child:Node in node.get_children():pending.append(child)
 var parents:Dictionary={}
 var residency:Node=ship.get_node("ShipSystems/ReceivedRoomResidency")
 for entry:Dictionary in residency.entries:
  if not entry.attached:parents[entry.room.get_instance_id()]=entry.parent
 var lights:Array=[];var detached_lights:=0
 for light in ship.get_node("ShipSystems/LocalShadowSourceBudget").sources:
  if not is_instance_valid(light):continue
  var position:Variant=retained_position(light,parents)
  if position==null:
   return {"failed":"Unresolved detached light owner; no sources modified","light_name":str(light.name)}
  if not light.is_inside_tree():detached_lights+=1
  lights.append({"id":light.get_instance_id(),"mask":light.light_cull_mask,"kind":0 if light is DirectionalLight3D else (1 if light is OmniLight3D else 2),"reach":0.0 if light is DirectionalLight3D else (light.omni_range if light is OmniLight3D else light.spot_range),"position":position})
 var rows:Array=[];var saved:=0
 for node:Node3D in roots:
  var bounds:=AABB();var initialized:=false
  for mesh:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
   var box:AABB=mesh.global_transform*mesh.get_aabb()
   bounds=bounds.merge(box) if initialized else box;initialized=true
  var relevant:Array=[]
  for light:Dictionary in lights:
   if light.kind==0 or light.position.distance_squared_to(light.position.clamp(bounds.position,bounds.end))<=light.reach*light.reach:relevant.append(light)
  var row:Dictionary=CELLS.compact(node,relevant)
  row.potential_lights=relevant.size()
  row.owner=str(ship.get_path_to(node));row.source=node.scene_file_path;rows.append(row);saved+=int(row.saved_submissions)
 var report:={"sources_found":roots.size(),"detached_lights_accounted":detached_lights,"saved_potential_submissions":saved,"rows":rows,"selected_default":false,"scope":"Whitelisted retained public models only; no dynamic residency or lower Arrivals source modified"}
 ship.set_meta("spatial_instance_cells",report);print("SPATIAL_INSTANCE_INSTALL ",JSON.stringify(report))
 return report
