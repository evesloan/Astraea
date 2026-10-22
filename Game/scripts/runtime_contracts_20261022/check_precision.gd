extends SceneTree
func _initialize()->void:
 var args:=OS.get_cmdline_user_args()
 if args.size()>0:
  assert(ProjectSettings.load_resource_pack(args[0]))
  if args.size()>1 and args[1]=="overlay":assert(ProjectSettings.load_resource_pack("res://runtime_source_contracts.pck"))
 var paths:Array=JSON.parse_string(FileAccess.get_file_as_string("/workspace/Astraea-recovered-e6274e77-20261021/Game/scripts/runtime_contracts_20261022/PRECISION_MODELS.json"))
 var result:Array=[]
 for path:String in paths:
  var scene:PackedScene=load(path);assert(scene!=null)
  var state:=scene.get_state();var meshes:=0;var surfaces:=0;var compressed:=0;var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256)
  for n in state.get_node_count():
   for p in state.get_node_property_count(n):
    if state.get_node_property_name(n,p)!="mesh":continue
    var mesh:Mesh=state.get_node_property_value(n,p)
    if mesh==null:continue
    meshes+=1
    for s in mesh.get_surface_count():
     surfaces+=1
     if mesh.surface_get_format(s)&Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES:compressed+=1
    hash.update(mesh.get_faces().to_byte_array())
  assert(meshes>0 and compressed==0,"Actual imported precision mesh is compressed: "+path)
  result.append({"path":path,"meshes":meshes,"surfaces":surfaces,"compressed_surfaces":compressed,"faces_sha256":hash.finish().hex_encode()})
 var output:=OS.get_environment("ASTRAEA_CHECK_OUTPUT")
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close()
 print("PRECISION_CHECK ",result.size()," actual imported models; no compressed surfaces")
 quit()
