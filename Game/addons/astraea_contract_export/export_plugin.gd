@tool
extends "res://addons/astraea_consolidated_export/export_plugin.gd"
const MANIFEST := "res://scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json"
func _get_name()->String:return "AstraeaExactSourceContracts"
func _export_begin(features:PackedStringArray,is_debug:bool,path:String,flags:int)->void:
 super._export_begin(features,is_debug,path,flags)
 var rows:Array=JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
 var scratch:=OS.get_environment("ASTRAEA_CONTRACT_PACK_TMP")
 if scratch.is_empty():
  _fail("Set ASTRAEA_CONTRACT_PACK_TMP to a unique disposable output path")
  return
 var pack:=PCKPacker.new()
 if pack.pck_start(scratch)!=OK:
  _fail("Cannot create exact source contract pack")
  return
 for row:Dictionary in rows:
  if FileAccess.get_sha256(row.path)!=row.sha256:
   _fail("Exact source changed; regenerate and review manifest: "+str(row.path))
   return
  if pack.add_file(row.path,row.path)!=OK:
   _fail("Cannot retain source: "+str(row.path))
   return
 if pack.flush()!=OK:
  _fail("Cannot finish source contract pack")
  return
 var receipt:={"sha256":FileAccess.get_sha256(scratch),"manifest_sha256":FileAccess.get_sha256(MANIFEST),"files":rows.size()}
 add_file("res://runtime_source_contracts.pck",FileAccess.get_file_as_bytes(scratch),false)
 add_file("res://runtime_source_contracts_receipt.json",JSON.stringify(receipt).to_utf8_buffer(),false)
