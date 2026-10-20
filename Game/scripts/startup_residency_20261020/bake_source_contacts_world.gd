extends SceneTree
const OUT:="res://assets/runtime/startup_residency_20261020/source_contacts_world/"
func pose(mesh:Node3D,visual:Node3D)->Transform3D:
 var result:=mesh.transform;var parent:=mesh.get_parent()
 while parent!=visual:
  assert(parent!=null)
  if parent is Node3D:result=parent.transform*result
  parent=parent.get_parent()
 return result
func sha(bytes:PackedByteArray)->String:
 var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(bytes);return hash.finish().hex_encode()
func _initialize()->void:
 DirAccess.make_dir_recursive_absolute(OUT)
 var config:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/startup_residency_20261020/source_contact_candidates.json"))
 var result:={"schema":"astraea.immutable_source_contact_cells.v2","models":{}}
 for row in config.models:
  var path:=str(row.file);assert(FileAccess.get_sha256(path)==str(row.sha256))
  var visual:Node3D=load(path).instantiate();var bins:={};var records:={}
  for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
   var collide:bool=str(mesh.name) in row.collision_names if row.has("collision_names") else (mesh.visible and not str(mesh.name).begins_with("ALC_VisualFloor"))
   var cursor:Node=mesh.get_parent()
   while cursor!=null:
    if cursor is StaticBody3D:collide=false
    cursor=cursor.get_parent()
   for surface in range(mesh.mesh.get_surface_count()):
    var mat:=mesh.get_active_material(surface)
    if not mat is BaseMaterial3D or mat.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or mat.albedo_color.a<.999:collide=false
   if not collide:continue
   var original:=mesh.mesh.get_faces();var faces:=pose(mesh,visual)*original
   records[str(visual.get_path_to(mesh))]={"faces_sha256":sha(var_to_bytes(original)),"triangles":original.size()/3}
   for i in range(0,faces.size(),3):
    var center:=(faces[i]+faces[i+1]+faces[i+2])/3.
    var key:="%d_%d_%d"%[floori(center.x/24.),floori(center.y/24.),floori(center.z/24.)]
    if not bins.has(key):bins[key]=PackedVector3Array()
    bins[key].append(faces[i]);bins[key].append(faces[i+1]);bins[key].append(faces[i+2])
  var cells:=[]
  for key in bins:
   var vertices:PackedVector3Array=bins[key];var bounds:=AABB(vertices[0],Vector3.ZERO)
   for vertex in vertices:bounds=bounds.expand(vertex)
   var shape:=ConcavePolygonShape3D.new();shape.set_faces(vertices)
   var file:=OUT+path.get_file().trim_suffix(".glb")+"_"+str(key)+".res";assert(ResourceSaver.save(shape,file)==OK)
   cells.append({"id":key,"path":file,"sha256":FileAccess.get_sha256(file),"bounds_min":[bounds.position.x,bounds.position.y,bounds.position.z],"bounds_max":[bounds.end.x,bounds.end.y,bounds.end.z],"triangles":vertices.size()/3})
  result.models[path]={"source_sha256":row.sha256,"old_contact_name":row.old_contact_name,"meshes":records,"collision_cells":cells}
  visual.free();print("SOURCE_WORLD_CONTACT_BAKE ",path," meshes ",records.size()," cells ",cells.size())
 var output:=FileAccess.open("res://data/architecture/startup_residency_20261020/source_contacts_world.json",FileAccess.WRITE);output.store_string(JSON.stringify(result,"\t"));output.close();quit()
