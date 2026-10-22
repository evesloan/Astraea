@tool
extends "res://addons/astraea_raw_glb_export/export_plugin.gd"
func _get_name()->String:return "AstraeaConsolidatedSourceExport"
func _export_begin(features:PackedStringArray,is_debug:bool,path:String,flags:int)->void:
 super._export_begin(features,is_debug,path,flags)
 # Keep the original source guard intact: this native is read as exact bytes,
 # not imported or substituted for the retained runtime mesh.
 var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://royalty790_integration_20261022/evidence/INPUT_PINS.json"))
 var included:=0
 for file in pins:
  if not str(file).begins_with("Game/") or not str(file).ends_with(".blend"):continue
  var native_path:="res://"+str(file).trim_prefix("Game/")
  if FileAccess.get_sha256(native_path)!=str(pins[file]):
   _fail("Native source required by runtime guard is missing or changed: "+native_path)
   continue
  add_file(native_path,FileAccess.get_file_as_bytes(native_path),false)
  included+=1
 if included!=1:_fail("Expected exactly one Royalty native-source byte dependency")
