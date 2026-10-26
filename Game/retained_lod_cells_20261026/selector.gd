extends RefCounted
const RULES=preload("res://spatial_instance_cells_20261026/rules.gd")
const OWNER=preload("res://static_bank_cells_20261026/render_owner.gd")
static var preserve_lods:=false
static var pending:Array[WeakRef]=[]
static func has_lods(mesh:Mesh)->bool:
 for surface:Dictionary in mesh.get("_surfaces"):
  if not surface.get("lods",[]).is_empty():return true
 return false
static func needs_original(records:Array)->bool:
 for row:Array in records:
  if has_lods(row[1]):return true
 return false
static func original_owner(mesh:MeshInstance3D,records:Array)->Node3D:
 var owner:Node3D=OWNER.new();owner.name=mesh.name+"_OriginalLODAndBounds"
 owner.records=records;mesh.get_parent().add_child(owner)
 mesh.free()
 return owner
static func apply(bank:Node3D,lights:Array)->Dictionary:
 var batches:=0;var fallbacks:=0;var original_draws:=0;var selected_draws:=0;var lod_cells:=0
 for mesh:MeshInstance3D in bank.find_children("*","MeshInstance3D",true,false):
  if not mesh.has_meta("precompiled_fallback"):continue
  var records:Array=mesh.get_meta("precompiled_fallback");assert(not records.is_empty())
  original_draws+=records.size()
  var over:bool=RULES.light_signature(mesh.global_transform*mesh.get_aabb(),mesh.layers,lights)=="OVER_LIMIT"
  var lod:bool=needs_original(records)
  if over or (preserve_lods and lod):
   selected_draws+=records.size();fallbacks+=1
   if lod and not over:lod_cells+=1
   original_owner(mesh,records)
  else:
   if lod:
    mesh.set_meta("retained_lod_records",records);pending.append(weakref(mesh));lod_cells+=1
   mesh.remove_meta("precompiled_fallback");selected_draws+=1;batches+=1
 return {"merged_cells":batches,"exact_per_mesh_fallback_cells":fallbacks,"saved_submissions":original_draws-selected_draws,"lod_cells":lod_cells,"preserve_imported_lods":preserve_lods,"policy":"Original source meshes, LOD indices/bias, bounds, materials and draw state restored for cells containing imported LODs; non-LOD compatible cells remain merged. Baseline comparison temporarily retains source records."}
static func switch_to_original_lods()->Dictionary:
 preserve_lods=true
 var cells:=0;var originals:=0;var expired:=0;var owners:Array=[]
 for reference:WeakRef in pending:
  var mesh:MeshInstance3D=reference.get_ref()
  if mesh==null:expired+=1;continue
  var records:Array=mesh.get_meta("retained_lod_records")
  originals+=records.size();cells+=1
  var owner:Node3D=original_owner(mesh,records);owners.append(weakref(owner))
 pending.clear()
 return {"cells":cells,"original_instances":originals,"expired_cells":expired,"owners":owners}
