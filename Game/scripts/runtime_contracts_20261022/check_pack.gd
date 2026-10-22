extends SceneTree
func _initialize()->void:
 var args:=OS.get_cmdline_user_args();assert(args.size()==2)
 assert(ProjectSettings.load_resource_pack(args[0]))
 var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://runtime_source_contracts_receipt.json"))
 assert(FileAccess.get_sha256("res://runtime_source_contracts.pck")==str(receipt.sha256))
 assert(ProjectSettings.load_resource_pack("res://runtime_source_contracts.pck"))
 var manifest_path:="res://scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json"
 assert(FileAccess.get_sha256(manifest_path)==str(receipt.manifest_sha256))
 var rows:Array=JSON.parse_string(FileAccess.get_file_as_string(manifest_path));var total:=0
 assert(rows.size()==int(receipt.files))
 for row:Dictionary in rows:
  assert(FileAccess.get_sha256(row.path)==row.sha256,"Packaged source mismatch: "+str(row.path))
  total+=int(row.bytes)
 var group5:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group5/CONSTRUCTION.json"));var scenes:=0
 for row:Dictionary in group5.fitout_revisions:
  assert(FileAccess.file_exists(row.scene_path))
  assert(load(str(row.scene_path)) is PackedScene)
  scenes+=1
 var pins:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://royalty790_integration_20261022/evidence/INPUT_PINS.json"));var pin_count:=0
 for path:String in pins:
  if not path.begins_with("Game/"):continue
  assert(FileAccess.get_sha256("res://"+path.trim_prefix("Game/"))==str(pins[path]),"Royalty retained source pin: "+path)
  pin_count+=1
 for script in ["bootstrap","launcher","presentation","ship","roof_handoff"]:
  assert(load("res://scripts/runtime_contracts_20261022/"+script+".gd") is Script)
 var result:={"exact_files":rows.size(),"exact_bytes":total,"group5_source_scenes":scenes,"royalty_source_pins":pin_count,"overlay_sha256":receipt.sha256,"ship_instantiated":false,"playable_accepted":false}
 var f:=FileAccess.open(args[1],FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close();print("PACK_CONTRACTS_PASS ",JSON.stringify(result));quit()
