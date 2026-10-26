extends RefCounted
const RULES=preload("res://spatial_instance_cells_20261026/rules.gd")
static func apply(bank:Node3D,lights:Array)->Dictionary:
 if OS.get_environment("ASTRAEA_LOD_COMPARISON")=="1":return load("res://retained_lod_cells_20261026/selector.gd").apply(bank,lights)
 var batches:=0;var fallback_cells:=0;var original_draws:=0;var selected_draws:=0
 for mesh:MeshInstance3D in bank.find_children("*","MeshInstance3D",true,false):
  if not mesh.has_meta("precompiled_fallback"):continue
  var records:Array=mesh.get_meta("precompiled_fallback")
  assert(not records.is_empty())
  original_draws+=records.size()
  if RULES.light_signature(mesh.global_transform*mesh.get_aabb(),mesh.layers,lights)=="OVER_LIMIT":
   var owner:Node3D=load("res://static_bank_cells_20261026/render_owner.gd").new()
   owner.name=mesh.name+"_ExactLightFallback";owner.records=records;mesh.get_parent().add_child(owner)
   selected_draws+=records.size();fallback_cells+=1;mesh.free()
  else:
   mesh.remove_meta("precompiled_fallback");selected_draws+=1;batches+=1
 return {"merged_cells":batches,"exact_per_mesh_fallback_cells":fallback_cells,"saved_submissions":original_draws-selected_draws,"policy":"No overflow light selection changes: incompatible cells use exact original renderer records, without original scene nodes"}
