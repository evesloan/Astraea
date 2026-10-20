extends SceneTree
const OUT:="res://assets/runtime/startup_residency_20261020/group7_contacts/"
func _initialize()->void:
 DirAccess.make_dir_recursive_absolute(OUT)
 var result:={"schema":"astraea.exact_group7_contacts.v1","models":{}}
 for contract in ["res://data/architecture/GROUP7_COMPLETION.json","res://data/consolidated_all_eight_20261013/G7_ADDITIONAL.json"]:
  var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(contract))
  for row in data.models:
   var path:="res://assets/models/"+str(row.file)
   assert(FileAccess.get_sha256(path)==str(row.sha256))
   var visual:Node3D=(load(path) as PackedScene).instantiate()
   var records:={};var count:=0
   for mesh:MeshInstance3D in visual.find_children("*","MeshInstance3D",true,false):
    if not str(mesh.get_meta("extras",{}).get("contact_category","")).begins_with("solid_"):continue
    var opaque:=true
    for surface in range(mesh.mesh.get_surface_count()):
     var mat:=mesh.get_active_material(surface)
     if not mat is BaseMaterial3D or mat.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or mat.albedo_color.a<0.999:opaque=false
    if not opaque:continue
    var faces:=mesh.mesh.get_faces();var bins:={}
    for i in range(0,faces.size(),3):
     var center:=(faces[i]+faces[i+1]+faces[i+2])/3.0
     var key:="%d_%d_%d"%[floori(center.x/24.),floori(center.y/24.),floori(center.z/24.)]
     if not bins.has(key):bins[key]=PackedVector3Array()
     bins[key].append(faces[i]);bins[key].append(faces[i+1]);bins[key].append(faces[i+2])
    var cells:=[]
    for key in bins:
     var vertices:PackedVector3Array=bins[key]
     var bounds:=AABB(vertices[0],Vector3.ZERO)
     for vertex in vertices:bounds=bounds.expand(vertex)
     var shape:=ConcavePolygonShape3D.new();shape.set_faces(vertices)
     var resource_path:=OUT+str(row.file).trim_suffix(".glb")+"_%04d_%s.res"%[count,key]
     assert(ResourceSaver.save(shape,resource_path)==OK)
     cells.append({"id":str(count)+"_"+key,"path":resource_path,"sha256":FileAccess.get_sha256(resource_path),"bounds_min":[bounds.position.x,bounds.position.y,bounds.position.z],"bounds_max":[bounds.end.x,bounds.end.y,bounds.end.z],"triangles":vertices.size()/3})
    records[str(visual.get_path_to(mesh))]={"collision_cells":cells,"faces_sha256":sha(var_to_bytes(faces)),"triangles":faces.size()/3}
    count+=1
   result.models[str(row.file)]={"source_sha256":row.sha256,"meshes":records}
   visual.free()
   print("CONTACT_BAKE ",row.file," opaque meshes ",count)
 var f:=FileAccess.open("res://data/architecture/startup_residency_20261020/group7_contacts.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close();quit()
func sha(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
