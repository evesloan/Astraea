extends RefCounted
const CELLS=preload("res://spatial_instance_cells_20261026/runtime.gd")
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
 var lights:Array=ship.get_node("ShipSystems/LocalShadowSourceBudget").sources
 var rows:Array=[];var saved:=0
 for node:Node3D in roots:
  var row:Dictionary=CELLS.compact(node,lights)
  row.owner=str(ship.get_path_to(node));row.source=node.scene_file_path;rows.append(row);saved+=int(row.saved_submissions)
 var report:={"sources_found":roots.size(),"saved_potential_submissions":saved,"rows":rows,"selected_default":false,"scope":"Whitelisted retained public models only; no dynamic residency or lower Arrivals source modified"}
 ship.set_meta("spatial_instance_cells",report);print("SPATIAL_INSTANCE_INSTALL ",JSON.stringify(report))
 return report
