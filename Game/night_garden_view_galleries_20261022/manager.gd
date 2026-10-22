extends "res://scripts/night_garden_residency_20261022/manager.gd"
const VIEW_P="res://night_garden_view_galleries_20261022/"
var view_records:Dictionary={}
func setup(ship:Node3D)->void:
 super.setup(ship)
 view_records=JSON.parse_string(FileAccess.get_file_as_string(VIEW_P+"evidence/DERIVED_SHELLS.json"))
 assert(view_records.size()==16)
 for file in view_records:
  var delta:Dictionary=view_records[file]
  assert(index[file].shell_sha256==delta.original_shell_sha256)
  assert(index[file].detail_sha256==delta.private_detail_sha256)
  index[file].shell_path=delta.shell_path;index[file].shell_sha256=delta.shell_sha256
func contacts(visual:Node3D)->void:
 super.contacts(visual)
 for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
  var extra:Dictionary=mesh.get_meta("extras",{})
  var name_s:=str(mesh.name)
  var new_pane:=name_s.begins_with("NVG_") and name_s.ends_with("PrivateViewPane")
  var original_pane:=name_s.begins_with("NG") and (name_s.ends_with("OvalAtriumGlass") or name_s.ends_with("ScreenedStreetGlass"))
  if not (new_pane or original_pane):continue
  if new_pane:assert(extra.has("private_view_plane_x") and extra.has("private_view_sign"))
  var plane:float=float(extra.private_view_plane_x) if new_pane else (mesh.global_transform*mesh.get_aabb()).get_center().x
  var inside:float=float(extra.private_view_sign) if new_pane else 1.0
  var glass:=ShaderMaterial.new();glass.shader=load(VIEW_P+"private_view.gdshader")
  glass.set_shader_parameter("plane_x",plane);glass.set_shader_parameter("interior_sign",inside)
  mesh.material_override=glass
