extends SceneTree
var owned_resources: Dictionary = {}
var source_model_path := ""
var failed := false
func stop(message: String) -> void:
 push_error(message)
 failed = true
func _initialize() -> void: call_deferred("run")
func xyz(value: Vector3) -> Array: return [value.x,value.y,value.z]
func run() -> void:
 var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
 var output := {"schema":"astraea.private_shell_residency.v1","rooms":{}}
 DirAccess.make_dir_recursive_absolute("res://assets/runtime/startup_residency_20261020/private_shells")
 for record in config.rooms:
  source_model_path = "res://assets/models/"+str(record.model_file)
  assert(FileAccess.get_sha256(source_model_path)==record.sha256)
  owned_resources.clear()
  var source: Node3D = load(source_model_path).instantiate()
  root.add_child(source)
  assert(source.find_children("*","Light3D",true,false).is_empty(),"Imported source lights need persistent ownership")
  var detail_paths: Array[String] = []
  var shell_paths: Array[String] = []
  var box := AABB()
  var first := true
  var detail_box:=AABB()
  var first_detail:=true
  for node in source.find_children("*","Node",true,false): assert(node.get_script()==null,"Only immutable source nodes can unload")
  for mesh: MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
   var extra: Dictionary = mesh.get_meta("extras",{})
   var label := str(mesh.name).to_lower().replace("_","").replace("-","").replace(".","").replace(" ","")
   assert(not ("previewground" in label or bool(extra.get("preview_only",false)) or bool(extra.get("presentation_only",false)) or bool(extra.get("exclude_from_production",false))))
   var bound: AABB = mesh.global_transform*mesh.get_aabb()
   box = bound if first else box.merge(bound)
   first = false
   var path := str(source.get_path_to(mesh))
   # Keep every explicit architectural/built-in role and every unknown mesh.
   # Only identified retained catalogue furnishings are private detail.
   if mesh.get_child_count()==0 and not extra.has("construction_role") and (extra.has("retained_component_id") or extra.has("catalogue_id")):
    detail_paths.append(path)
    detail_box=bound if first_detail else detail_box.merge(bound)
    first_detail=false
   else: shell_paths.append(path)
  assert(not detail_paths.is_empty() and not shell_paths.is_empty())
  for path in detail_paths: source.get_node(path).free()
  for mesh: MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
   mesh.mesh=own_resource(mesh.mesh)
   if mesh.material_override!=null:mesh.material_override=own_resource(mesh.material_override)
   if mesh.material_overlay!=null:mesh.material_overlay=own_resource(mesh.material_overlay)
   for surface in range(mesh.mesh.get_surface_count()):
    if mesh.get_surface_override_material(surface)!=null:mesh.set_surface_override_material(surface,own_resource(mesh.get_surface_override_material(surface)))
  own_children(source,source)
  var packed:=PackedScene.new()
  assert(packed.pack(source)==OK)
  var path:="res://assets/runtime/startup_residency_20261020/private_shells/"+str(record.model_file).get_basename()+".scn"
  assert(ResourceSaver.save(packed,path)==OK)
  var row: Dictionary=record.duplicate(true)
  row.merge({"shell_path":path,"shell_sha256":FileAccess.get_sha256(path),"shell_mesh_paths":shell_paths,"detail_mesh_paths":detail_paths,"bounds_min":xyz(box.position),"bounds_max":xyz(box.end),"detail_bounds_min":xyz(detail_box.position),"detail_bounds_max":xyz(detail_box.end)},true)
  output.rooms[record.model_file]=row
  print("PRIVATE_SHELL_BAKED ",record.model_file," shell=",shell_paths.size()," detail=",detail_paths.size())
  source.free()
  owned_resources.clear()
 var handle:=FileAccess.open("res://data/architecture/startup_residency_20261020/private_shells.json",FileAccess.WRITE)
 handle.store_string(JSON.stringify(output,"  ")+"\n")
 quit(1 if failed else 0)
func own_children(node: Node, owner_node: Node) -> void:
 for child in node.get_children():
  child.owner = owner_node
  own_children(child, owner_node)

func own_value(value):
 if value is Resource:
  return own_resource(value)
 if value is Array:
  var copied: Array = value.duplicate()
  for i in range(copied.size()):
   copied[i] = own_value(copied[i])
  return copied
 if value is Dictionary:
  var copied: Dictionary = value.duplicate()
  for key in copied:
   copied[key] = own_value(copied[key])
  return copied
 return value

func own_resource(resource: Resource) -> Resource:
 if resource == null:
  return null
 if resource is Shader and not resource.resource_path.is_empty() and resource.resource_path.ends_with(".gdshader"):
  return resource # Preserve the named glass shader contract used by lighting rays.
 var identity := resource.get_instance_id()
 if owned_resources.has(identity):
  return owned_resources[identity]
 if resource is Texture2D:
  # Standalone imported textures remain legitimate external references.
  # GLB-owned textures must not refer back to a scene subresource table.
  var reference := resource.resource_path
  if not reference.is_empty() and not reference.contains("::") and reference != source_model_path:
   return resource
  var pixels: Image = resource.get_image()
  if pixels == null or pixels.is_empty():
   stop("Could not detach imported texture: " + reference)
   return null
  if pixels.is_compressed() and pixels.decompress() != OK:
   stop("Could not decompress imported texture: " + reference)
   return null
  var texture := ImageTexture.create_from_image(pixels)
  texture.resource_name = resource.resource_name
  owned_resources[identity] = texture
  return texture
 var copied := resource.duplicate(false)
 if copied == null:
  stop("Could not duplicate imported resource: " + resource.resource_path)
  return null
 copied.resource_path = ""
 owned_resources[identity] = copied
 for property in resource.get_property_list():
  if int(property.usage) & PROPERTY_USAGE_STORAGE == 0:
   continue
  var key := str(property.name)
  if key in ["resource_path", "resource_local_to_scene", "resource_name", "script"]:
   continue
  var value = resource.get(key)
  if value is Resource or value is Array or value is Dictionary:
   copied.set(key, own_value(value))
 if copied is ArrayMesh:
  for surface in range(copied.get_surface_count()):
   copied.surface_set_material(surface, own_resource(resource.surface_get_material(surface)))
 return copied

