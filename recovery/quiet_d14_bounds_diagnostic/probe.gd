extends SceneTree
func _initialize()->void:call_deferred("run")
func vv(a:Vector3)->Array:return [a.x,a.y,a.z]
func run()->void:
 # Use the laptop existing import cache; no pack mount, importer or ship construction.
 var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/quiet_d14_receiving_20261016/RECEIPT.json"))
 var rows:Array=[]
 for r:Dictionary in receipt.walls:
  var path:String="res://"+str(r.path).trim_prefix("Game/")
  for raw in [false]:
   var scene:Node3D
   if raw:
    var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file(path,state,64)==OK);scene=doc.generate_scene(state)
   else:scene=load(path).instantiate()
   var mesh:MeshInstance3D=scene.find_child(r.name,true,false)
   if mesh==null:mesh=scene.find_child("PATCH_"+str(r.name),true,false)
   if mesh==null:push_error("MISSING "+str(r.name));scene.free();continue
   var b:=mesh.get_aabb();var faces:=mesh.mesh.get_faces();var lo:=faces[0];var hi:=lo
   for v:Vector3 in faces:lo=lo.min(v);hi=hi.max(v)
   var compressed:=0
   for s in mesh.mesh.get_surface_count():
    if mesh.mesh.surface_get_format(s)&Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES:compressed+=1
   rows.append({"name":r.name,"raw":raw,"aabb_min":vv(b.position),"aabb_max":vv(b.end),"face_min":vv(lo),"face_max":vv(hi),"expected_min":r.min,"expected_max":r.max,"compressed_surfaces":compressed,"source_sha256":FileAccess.get_sha256(path),"triangles":faces.size()/3})
   var duplicate_mesh:Mesh=mesh.mesh.duplicate()
   for surface in duplicate_mesh.get_surface_count():duplicate_mesh.surface_set_material(surface,mesh.mesh.surface_get_material(surface))
   rows[-1]["after_duplicate_material_min"]=vv(duplicate_mesh.get_aabb().position);rows[-1]["after_duplicate_material_max"]=vv(duplicate_mesh.get_aabb().end)
   rows[-1]["import_config_sha256"]=FileAccess.get_sha256(path+".import")
   rows[-1]["engine"]=Engine.get_version_info().string
   scene.free()
 var args:=OS.get_cmdline_user_args();assert(args.size()==1,"Supply a new output JSON path after --");assert(not FileAccess.file_exists(args[0]),"Refuse overwrite of diagnostic receipt");var f:=FileAccess.open(args[0],FileAccess.WRITE);f.store_string(JSON.stringify(rows,"  "));f.close();print(JSON.stringify(rows));quit()
