extends "res://scripts/startup_residency_20261020/private_detail_residency.gd"
# One existing owner: preserve arrival preloading, rigid-body holds and visibility.
const NIGHT_INDEX="res://data/architecture/night_garden_partition_20261021/index.json"
const NIGHT_INDEX_SHA="3600f78ce774a447aefe91bf9ff21f6f1b63f6bf528f5437e846a98731e54857"
var night_files:Dictionary={}
func setup(ship:Node3D)->void:
 super.setup(ship)
 assert(FileAccess.get_sha256(NIGHT_INDEX)==NIGHT_INDEX_SHA)
 var added:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(NIGHT_INDEX)).rooms
 assert(added.size()==30)
 for file in added:
  assert(not index.has(file),"Original allocation must not be replaced")
  var record:Dictionary=added[file]
  assert(record.has("detail_path") and record.has("detail_sha256"))
  index[file]=record
  night_files[file]=true
func _load_entry(entry:Dictionary)->void:
 if not night_files.has(str(entry.record.model_file)):
  super._load_entry(entry)
  return
 if is_instance_valid(entry.detail):return
 var home:Node3D=entry.home.get_ref()
 if home==null:return
 var record:Dictionary=entry.record
 assert(FileAccess.get_sha256(record.detail_path)==record.detail_sha256)
 var detail:Node3D=load(str(record.detail_path)).instantiate()
 var seen:=0
 for mesh:MeshInstance3D in detail.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh==null:continue
  var extra:Dictionary=mesh.get_meta("extras",{})
  var label:=str(mesh.name).to_lower().replace("_","").replace("-","").replace(".","").replace(" ","")
  assert(not ("previewground" in label or bool(extra.get("preview_only",false)) or bool(extra.get("presentation_only",false)) or bool(extra.get("exclude_from_production",false))))
  assert(str(detail.get_path_to(mesh)) in record.detail_mesh_paths)
  seen+=1
 assert(seen==record.detail_mesh_paths.size())
 for path in record.shell_mesh_paths:assert(detail.get_node(str(path)).mesh==null)
 home.add_child(detail)
 contacts(detail)
 detail.name="ResidentPrivateFurnishings"
 entry.detail=detail
 entry.hidden=0.0
 loads+=1
