extends SceneTree
var existing:Dictionary={}
func collect(path:String)->void:
 var d:DirAccess=DirAccess.open(path);assert(d!=null,path);d.include_hidden=true;d.include_navigational=false
 for f in d.get_files():
  var full:String=path.path_join(f);existing[full]=FileAccess.get_sha256(full)
 for sub in d.get_directories():collect(path.path_join(sub))
func _initialize()->void:
 collect("res://")
 assert(existing.has("res://project.binary"))
 var originals:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/ship-delivery-20261019/PACK_SOURCE_PINS.json"))
 var pack:=PCKPacker.new();assert(pack.pck_start("/workspace/ship-delivery-20261019/Astraea-Integrated-Construction/Astraea.pck")==OK)
 DirAccess.make_dir_recursive_absolute("/workspace/ship-delivery-20261019/merged-import-metadata")
 var enriched:Dictionary={}
 var unchanged:Dictionary={}
 for path in existing:
  var native:String="/workspace/Astraea/Game/"+str(path).trim_prefix("res://")
  if str(path).ends_with(".import") and FileAccess.file_exists(native):
   var source_text:String=FileAccess.get_file_as_string(native)
   var start:int=source_text.find("[params]")
   if start>=0:
    var exported_text:String=FileAccess.get_file_as_string(path)
    assert(exported_text.find("[params]")==-1,path)
    var combined:String=exported_text+"\n"+source_text.substr(start)
    var temporary:String="/workspace/ship-delivery-20261019/merged-import-metadata/"+str(path).sha256_text()+".import"
    var file:FileAccess=FileAccess.open(temporary,FileAccess.WRITE);file.store_string(combined);file.close()
    assert(pack.add_file(path,temporary)==OK,path)
    enriched[path]={"sha256":combined.sha256_text(),"original_export_sha256":existing[path],"source_params_sha256":source_text.substr(start).sha256_text(),"exported_remap_prefix_unchanged":true}
    continue
  assert(pack.add_file(path,path)==OK,path);unchanged[path]=existing[path]
 var added:Array=[]
 for path in originals:
  var target:String="res://"+str(path)
  if existing.has(target):assert(existing[target]==originals[path],target);continue
  assert(pack.add_file(target,"/workspace/Astraea/Game/"+str(path))==OK,path);added.append(path)
 assert(pack.flush()==OK)
 FileAccess.open("/workspace/ship-delivery-20261019/EXPORTED_RESOURCE_PINS.json",FileAccess.WRITE).store_string(JSON.stringify(unchanged))
 FileAccess.open("/workspace/ship-delivery-20261019/IMPORT_METADATA_PINS.json",FileAccess.WRITE).store_string(JSON.stringify(enriched))
 var result:Dictionary={"status":"REPACKED_PENDING_READBACK","original_export_files":existing.size(),"added_original_source_files":added.size(),"unchanged_exported_resources":unchanged.size(),"import_metadata_enriched_with_original_params":enriched.size(),"exported_remap_prefixes_modified":false,"method":"Godot PCKPacker preserves exported resource payloads/remap prefixes, restores original import parameters, and adds exact original runtime data required by FileAccess integrity guards; no engine, geometry or controller changes."}
 FileAccess.open("/workspace/ship-delivery-20261019/REPACK_RECEIPT.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  "));print(result);quit()
