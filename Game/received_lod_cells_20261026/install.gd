extends RefCounted
const CELLS=preload("res://received_lod_cells_20261026/runtime.gd")
static func install(ship:Node3D)->Dictionary:
 var source:Node3D=ship.get_node("ShipSpace/Districts/ReceivedSections")
 var snapshot:Dictionary=load("res://precompiled_private_cells_20261026/lighting_r002.gd").lighting(ship)
 if snapshot.has("failed"):return snapshot
 var totals:Dictionary={"saved_submissions":0,"converted_mesh_instances":0,"batch_count":0,"source_lod_meshes_untouched":0,"owners":[]}
 for room:Node3D in source.get_children():
  if room.has_meta("received_lod_restore"):continue
  var bounds:=AABB();var initialized:=false
  for mesh:MeshInstance3D in room.find_children("*","MeshInstance3D",true,false):
   if mesh.mesh==null:continue
   var box:AABB=mesh.global_transform*mesh.get_aabb()
   bounds=bounds.merge(box) if initialized else box;initialized=true
  if not initialized:continue
  var relevant:Array=[]
  for light:Dictionary in snapshot.lights:
   if light.kind==0 or light.position.distance_squared_to(light.position.clamp(bounds.position,bounds.end))<=light.reach*light.reach:relevant.append(light)
  var row:Dictionary=CELLS.compact(room,relevant)
  row.owner=str(room.get_path());totals.owners.append(row)
  for key:String in ["saved_submissions","converted_mesh_instances","batch_count","source_lod_meshes_untouched"]:totals[key]+=row[key]
  var callback:Callable=func()->void:
   if room.has_meta("received_lod_restore") and not CELLS.restore(room):push_error("Received cell restoration refused before release")
  room.tree_exiting.connect(callback,CONNECT_ONE_SHOT)
 return totals
static func restore(ship:Node3D)->Dictionary:
 var result:Dictionary={"ok":true,"owners":0}
 for room:Node3D in ship.get_node("ShipSpace/Districts/ReceivedSections").get_children():
  if room.has_meta("received_lod_restore"):
   result.ok=CELLS.restore(room) and result.ok;result.owners+=1
 return result
