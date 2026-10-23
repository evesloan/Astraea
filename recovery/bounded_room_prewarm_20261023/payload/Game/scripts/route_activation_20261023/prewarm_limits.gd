extends RefCounted
# Experimental admission only. Unknown sources never allocate a speculative scene.
# Byte allowance is a conservative source-derived estimate, NOT a measured RID/GPU cap.
const MANIFEST := "res://scripts/route_activation_20261023/prewarm_estimates.json"
const MAX_NODES := 2048
const MAX_MESHES := 1024
const MAX_FACE_VERTICES := 240000
const MAX_RESOURCES := 4096
const MAX_ESTIMATED_BYTES := 96 * 1024 * 1024
static var estimates:Dictionary={}
static func enabled()->bool:
 return OS.get_environment("ASTRAEA_ROOM_PREWARM")=="1" and OS.get_environment("ASTRAEA_STAGED_ROOM_ACTIVATION")=="1" and OS.get_environment("ASTRAEA_ROOM_ACTIVATION_QUEUE")=="1" and OS.get_environment("ASTRAEA_PACKED_CONTACT_FACES")=="1"
static func source_path(r:Dictionary)->String:
 var identity:Node=r.identity.get_ref()
 if identity==null:return ""
 if r.kind=="private_detail":return "res://assets/models/"+str(r.entry.record.model_file)
 if identity.has_meta("deferred_visual_scene"):return identity.get_meta("deferred_visual_scene").resource_path
 return str(identity.get_meta("deferred_visual_path",""))
static func generation(r:Dictionary)->String:
 var owner:Node=r.owner.get_ref();var identity:Node=r.identity.get_ref()
 if owner==null or identity==null:return ""
 var policy:Variant=r.entry.record if r.kind=="private_detail" else identity.get_meta("deferred_visual_collision_policy",{})
 var source_id:int=identity.get_meta("deferred_visual_scene").get_instance_id() if identity.has_meta("deferred_visual_scene") else 0
 return var_to_bytes([owner.get_instance_id(),identity.get_instance_id(),source_path(r),source_id,policy,r.entry.get("prewarm_generation",0),identity.get_meta("deferred_visual_meshes",0),OS.get_environment("ASTRAEA_PACKED_CONTACT_FACES"),OS.get_environment("ASTRAEA_PRIVATE_CONTACT_SINGLE_PASS")]).hex_encode().sha256_text()
static func estimate(r:Dictionary)->Dictionary:
 if not enabled() or not FileAccess.file_exists(MANIFEST):return {}
 if estimates.is_empty():
  var parsed:Variant=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
  if not parsed is Dictionary:return {}
  estimates=parsed.get("sources",{})
 var record:Dictionary=estimates.get(source_path(r),{})
 if record.is_empty():return {}
 for field in ["nodes","meshes","face_vertices","resources","estimated_bytes"]:
  if not record.has(field) or int(record[field])<=0:return {}
 if int(record.nodes)>MAX_NODES or int(record.meshes)>MAX_MESHES or int(record.face_vertices)>MAX_FACE_VERTICES or int(record.resources)>MAX_RESOURCES or int(record.estimated_bytes)>MAX_ESTIMATED_BYTES:return {}
 return record
static func admission(r:Dictionary)->Dictionary:
 var record:Dictionary=estimate(r)
 if record.is_empty() or not verified(record):return {}
 return record.duplicate(true)
static func verified(record:Dictionary)->bool:
 var dependencies:Dictionary=record.get("dependencies",{})
 if dependencies.is_empty():return false
 for file in dependencies:
  if not FileAccess.file_exists(file) or FileAccess.get_sha256(file)!=str(dependencies[file]):return false
 return true
static func actual_within_caps(visual:Node3D,record:Dictionary)->bool:
 # Check before face arrays/material overrides/collision allocation. The source/import
 # receipt admits scene allocation; these checks fail closed on an importer mismatch.
 var nodes:=visual.find_children("*","",true,false)
 if nodes.size()+1>int(record.nodes) or nodes.size()+1>MAX_NODES:return false
 var mesh_count:=0;var face_vertices:=0;var resources:Dictionary={}
 for node in nodes:
  if not node is MeshInstance3D:continue
  mesh_count+=1
  if node.mesh==null:continue
  if not node.mesh is ArrayMesh:return false
  var mesh:ArrayMesh=node.mesh
  resources[mesh.get_instance_id()]=true
  for surface in range(mesh.get_surface_count()):
   var count:int=mesh.surface_get_array_index_len(surface)
   face_vertices+=count if count>0 else mesh.surface_get_array_len(surface)
   var material:Material=node.get_active_material(surface)
   if material!=null:
    resources[material.get_instance_id()]=true
    if material is BaseMaterial3D:
     for slot in range(BaseMaterial3D.TEXTURE_MAX):
      var texture:Texture2D=material.get_texture(slot)
      if texture!=null:resources[texture.get_instance_id()]=true
 return mesh_count<=int(record.meshes) and mesh_count<=MAX_MESHES and face_vertices<=int(record.face_vertices) and face_vertices<=MAX_FACE_VERTICES and resources.size()+mesh_count*3+4<=int(record.resources) and resources.size()+mesh_count*3+4<=MAX_RESOURCES
