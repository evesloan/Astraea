extends SceneTree
const INDEX="res://data/architecture/night_garden_partition_20261021/index.json"
var rooms:=0
var shells:=0
var details:=0
var surfaces:=0
var reloads:=0
func _initialize()->void:call_deferred("run")
func equal_value(a,b)->bool:
 if a is Texture2D:
  if not b is Texture2D:return false
  var ai:Image=a.get_image();var bi:Image=b.get_image()
  return ai.get_size()==bi.get_size() and ai.get_format()==bi.get_format() and ai.has_mipmaps()==bi.has_mipmaps() and ai.get_data()==bi.get_data()
 if a is Resource:
  if not b is Resource or a.get_class()!=b.get_class():return false
  for prop in a.get_property_list():
   if not(int(prop.usage)&PROPERTY_USAGE_STORAGE) or str(prop.name) in ["resource_path","resource_local_to_scene"]:continue
   if not equal_value(a.get(str(prop.name)),b.get(str(prop.name))):return false
  return true
 if a is Array:
  if not b is Array or a.size()!=b.size():return false
  for i in range(a.size()):
   if not equal_value(a[i],b[i]):return false
  return true
 if a is Dictionary:
  if not b is Dictionary or a.size()!=b.size():return false
  for k in a:
   if not b.has(k) or not equal_value(a[k],b[k]):return false
  return true
 return a==b
func compare_mesh(a:MeshInstance3D,b:MeshInstance3D)->void:
 assert(a.transform==b.transform and a.global_transform==b.global_transform,"Transform changed")
 assert(a.get_meta("extras",{})==b.get_meta("extras",{}),"Contact/material-role metadata changed")
 assert(a.mesh.get_surface_count()==b.mesh.get_surface_count())
 assert(a.layers==b.layers and a.cast_shadow==b.cast_shadow and a.visible==b.visible)
 for i in range(a.mesh.get_surface_count()):
  assert(var_to_bytes(a.mesh.surface_get_arrays(i))==var_to_bytes(b.mesh.surface_get_arrays(i)),"Vertex/index/normal/UV data changed")
  assert(a.mesh.surface_get_primitive_type(i)==b.mesh.surface_get_primitive_type(i))
  assert(equal_value(a.get_active_material(i),b.get_active_material(i)),"Material/texture data changed")
  surfaces+=1
func validate_room(file:String,record:Dictionary)->void:
 var source_path:="res://assets/models/"+file
 assert(FileAccess.get_sha256(source_path)==record.sha256)
 assert(FileAccess.get_sha256(record.shell_path)==record.shell_sha256)
 assert(FileAccess.get_sha256(record.detail_path)==record.detail_sha256)
 var doc:=GLTFDocument.new();var state:=GLTFState.new()
 assert(doc.append_from_file(source_path,state)==OK)
 var source:Node3D=doc.generate_scene(state)
 var shell:Node3D=load(str(record.shell_path)).instantiate()
 var detail:Node3D=load(str(record.detail_path)).instantiate()
 root.add_child(source);root.add_child(shell);root.add_child(detail)
 assert(source.find_children("*","MeshInstance3D",true,false).size()==record.shell_mesh_paths.size()+record.detail_mesh_paths.size())
 assert(shell.find_children("*","MeshInstance3D",true,false).size()==record.shell_mesh_paths.size())
 for path in record.shell_mesh_paths:
  compare_mesh(source.get_node(path),shell.get_node(path))
  assert(detail.get_node(path).mesh==null)
  shells+=1
 for path in record.detail_mesh_paths:
  assert(not shell.has_node(path))
  compare_mesh(source.get_node(path),detail.get_node(path))
  details+=1
 for scene_path in [record.shell_path,record.detail_path]:
  for dependency in ResourceLoader.get_dependencies(scene_path):
   assert(not str(dependency).contains("assets/models/"),"Bake still depends on full original GLB")
 source.free();shell.free();detail.free()
 rooms+=1
func reload_detail(record:Dictionary)->void:
 var detail:Node3D=load(str(record.detail_path)).instantiate();root.add_child(detail)
 var count:=0
 for mesh:MeshInstance3D in detail.find_children("*","MeshInstance3D",true,false):
  if mesh.mesh!=null:count+=1
 assert(count==record.detail_mesh_paths.size())
 detail.free();reloads+=1
func run()->void:
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(INDEX))
 assert(data.rooms.size()==30)
 for file in data.rooms:
  var record:Dictionary=data.rooms[file]
  validate_room(file,record)
  assert(not ResourceLoader.has_cached(record.detail_path),"Detailed PackedScene still strongly retained")
  for cycle in range(3):
   reload_detail(record)
   assert(not ResourceLoader.has_cached(record.detail_path),"Detailed PackedScene did not release")
  print("EXACT_PARTITION_PASS ",file)
 assert(shells==210 and details==1909)
 var result:={"rooms":rooms,"exact_architectural_meshes":shells,"exact_private_detail_meshes":details,"surfaces_compared":surfaces,"detail_load_free_cycles":reloads,"original_geometry_uv_normals_indices_transforms_materials_texture_pixels_and_contact_metadata_preserved":true,"no_original_glb_dependencies_in_saved_scenes":true,"packed_detail_resources_release":true,"main_integration":false,"private_controller_transition_acceptance":false,"visual_acceptance":false}
 var out:="res://docs/validation/night_garden_partition_20261021/EXACT_PARTITION.json"
 assert(not FileAccess.file_exists(out))
 var f:=FileAccess.open(out,FileAccess.WRITE);f.store_string(JSON.stringify(result,"  ")+"\n");f.close()
 print(JSON.stringify(result));quit()
