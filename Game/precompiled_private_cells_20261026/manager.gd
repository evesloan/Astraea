extends "res://scripts/night_garden_residency_20261022/manager.gd"
# Explicit opt-in successor. Original manager object, entries, witnesses and IDs survive.
var compiled_records:Dictionary={}
var compiled_light_refs:Dictionary={}
var compiled_loads:=0
var compiled_saved_submissions:=0
func compiled_node_added(node:Node)->void:
 if node is Light3D and is_instance_valid(host) and host.is_ancestor_of(node):compiled_light_refs[node.get_instance_id()]=weakref(node)
func compiled_lighting()->Dictionary:
 var known:Array=[]
 for id:int in compiled_light_refs.keys():
  var light:Light3D=compiled_light_refs[id].get_ref()
  if light==null:compiled_light_refs.erase(id)
  elif light.is_inside_tree() and host.is_ancestor_of(light):known.append(light)
 return load("res://precompiled_private_cells_20261026/lighting_r002.gd").lighting(host,known)
func _load_entry(entry:Dictionary)->void:
 var file:String=str(entry.record.model_file)
 if not compiled_records.has(file) or host==null or not bool(host.get_meta("runtime_ready",false)):
  super._load_entry(entry);return
 if is_instance_valid(entry.detail):return
 var home:Node3D=entry.home.get_ref()
 if home==null:return
 var row:Dictionary=compiled_records[file]
 assert(str(entry.record.room_id)==row.room_id and str(home.name)==row.room_id)
 assert(entry.record.detail_path==row.source and entry.record.detail_sha256==row.source_sha256)
 assert(FileAccess.get_sha256(row.source)==row.source_sha256 and FileAccess.get_sha256(row.compiled)==row.sha256)
 var lights:Dictionary=compiled_lighting();assert(not lights.has("failed"),str(lights))
 var detail:Node3D=load(str(row.compiled)).instantiate()
 assert(detail.get_meta("precompiled_private_source","")==row.source and detail.get_meta("precompiled_private_source_sha256","")==row.source_sha256)
 home.add_child(detail)
 var selected:Dictionary=load("res://precompiled_bank_cells_20261026/select_lighting.gd").apply(detail,lights.lights)
 detail.name="ResidentPrivateFurnishings";entry.detail=detail;entry.hidden=0.0;loads+=1
 compiled_loads+=1;compiled_saved_submissions+=selected.saved_submissions
 print("PRECOMPILED_PRIVATE_ACTIVATION ",JSON.stringify({"file":file,"room_id":row.room_id,"nodes":detail.find_children("*","",true,false).size()+1,"selected":selected,"inert_witnesses_excluded":lights.inert_witnesses_excluded,"witness_examples":lights.witness_examples}))
