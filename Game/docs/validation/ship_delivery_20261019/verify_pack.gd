extends "res://tests/validate_ship_delivery_20261019.gd"
func _initialize()->void:
 var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/ship-delivery-20261019/PACK_SOURCE_PINS.json"))
 var bad:Array=[]
 for path in pins:
  if FileAccess.get_sha256("res://"+str(path))!=str(pins[path]):bad.append(path)
 var r:Dictionary={"status":"PASS" if bad.is_empty()else"FAIL","source_files":pins.size(),"failures":bad,"scope":"Exact source bytes required by runtime: GLBs, JSON/CSV/text data, scripts and shaders read from exported PCK outside the source checkout."}
 FileAccess.open("/workspace/ship-delivery-20261019/PACK_SOURCE_INTEGRITY.json",FileAccess.WRITE).store_string(JSON.stringify(r,"  "))
 print("PACK_SOURCE_INTEGRITY ",r.status," files=",pins.size()," failure_count=",bad.size())
 if not bad.is_empty():quit(1);return
 var exported:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/ship-delivery-20261019/EXPORTED_RESOURCE_PINS.json"))
 var changed:Array=[]
 for path in exported:
  if FileAccess.get_sha256(str(path))!=str(exported[path]):changed.append(path)
 var rr:Dictionary={"status":"PASS"if changed.is_empty()else"FAIL","exported_resources":exported.size(),"failures":changed,"scope":"Exported resource payloads retained byte-for-byte; enriched import metadata checked separately."}
 FileAccess.open("/workspace/ship-delivery-20261019/PACK_RESOURCE_INTEGRITY.json",FileAccess.WRITE).store_string(JSON.stringify(rr,"  "))
 print("PACK_RESOURCE_INTEGRITY ",rr.status," files=",exported.size()," failure_count=",changed.size())
 if not changed.is_empty():quit(1);return
 var metadata:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("/workspace/ship-delivery-20261019/IMPORT_METADATA_PINS.json"))
 var metadata_bad:Array=[]
 for path in metadata:
  var content:String=FileAccess.get_file_as_string(path);var at:int=content.find("[params]")
  if content.sha256_text()!=str(metadata[path].sha256) or at<0 or content.substr(at).sha256_text()!=str(metadata[path].source_params_sha256):metadata_bad.append(path)
 var mr:Dictionary={"status":"PASS"if metadata_bad.is_empty()else"FAIL","enriched_import_files":metadata.size(),"failures":metadata_bad,"scope":"Original source import parameters restored without modifying exported remap prefixes or imported model bytes."}
 FileAccess.open("/workspace/ship-delivery-20261019/PACK_IMPORT_METADATA.json",FileAccess.WRITE).store_string(JSON.stringify(mr,"  "))
 print("PACK_IMPORT_METADATA ",mr.status," files=",metadata.size()," failure_count=",metadata_bad.size())
 if not metadata_bad.is_empty():quit(1);return
 super._initialize()
