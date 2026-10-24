extends Node
# Mount exact guard inputs before loading the retained launcher or ship.
func _ready()->void:
 if OS.has_feature("astraea_contract_pack"):
  var receipt_path:="res://runtime_source_contracts_receipt.json"
  if not FileAccess.file_exists(receipt_path):
   _stop("Missing sealed source-contract receipt");return
  var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(receipt_path))
  if FileAccess.get_sha256("res://runtime_source_contracts.pck")!=str(receipt.sha256):
   _stop("Source-contract pack digest differs");return
  if not ProjectSettings.load_resource_pack("res://runtime_source_contracts.pck"):
   _stop("Cannot mount exact runtime sources");return
  if FileAccess.get_sha256("res://scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json")!=str(receipt.manifest_sha256):
   _stop("Source-contract manifest differs");return
 var launcher:PackedScene=load("res://scenes/launcher_family_aft_court_integrated_20261024.tscn")
 add_child(launcher.instantiate())
func _stop(reason:String)->void:
 push_error(reason)
 var label:=Label.new();label.text="Launch blocked: "+reason;add_child(label)
