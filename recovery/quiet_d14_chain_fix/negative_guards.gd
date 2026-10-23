extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 assert(ProjectSettings.load_resource_pack("/tmp/quiet-chain-test.pck"))
 var host:=Node3D.new();root.add_child(host);var space:=Node3D.new();space.name="ShipSpace";host.add_child(space)
 var checks:Array=[]
 for label:String in ["quiet_d13","quiet_d16","family_d13","family_d14","family_d15","family_d16"]:
  var path:="res://data/"+label+"_receiving_20261016/RECEIPT.json"
  var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path));receipt.source_pins["Game/scripts/quiet_d14_receiving_20261016/package.gd"]="0".repeat(64)
  var file:=FileAccess.open("/tmp/negative-receipt.json",FileAccess.WRITE);file.store_string(JSON.stringify(receipt));file.close()
  var pack:=PCKPacker.new();assert(pack.pck_start("/tmp/negative-"+label+".pck")==OK);assert(pack.add_file(path,"/tmp/negative-receipt.json")==OK);assert(pack.flush()==OK);assert(ProjectSettings.load_resource_pack("/tmp/negative-"+label+".pck"))
  print("EXPECTED_REJECTION_BEGIN ",label)
  var result:Node3D=load("res://scripts/"+label+"_receiving_20261016/package.gd").build(host)
  assert(result==null and space.get_child_count()==0);checks.append({"case":label+" corrupted predecessor pin","rejected_before_mutation":true})
  print("EXPECTED_REJECTION_PASS ",label)
  assert(ProjectSettings.load_resource_pack("/tmp/quiet-chain-test.pck"))
 var districts:=Node3D.new();districts.name="Districts";space.add_child(districts)
 var district:=Node3D.new();district.name="QuietGrove17Specialty20261022";districts.add_child(district);district.set_meta("original_guard_batches_replaced",11);district.set_meta("reserved_rests",19)
 var receiving:=Node3D.new();receiving.name="QuietGrove17Receiving_r001";district.add_child(receiving)
 var owner:=MeshInstance3D.new();owner.name="QG_Batch_38";owner.mesh=BoxMesh.new();receiving.add_child(owner)
 var before:=owner.mesh;owner.position=Vector3(1,0,0)
 print("EXPECTED_REJECTION_BEGIN changed_owner_transform")
 var result:Dictionary=load("res://scripts/delivery_quiet_d14_20261023/composition.gd").prepare(host,{"name":"QG_Batch_38"})
 assert(result.is_empty() and owner.mesh==before);checks.append({"case":"changed owner transform","rejected_before_mutation":true})
 owner.position=Vector3.ZERO
 print("EXPECTED_REJECTION_BEGIN changed_owner_mesh")
 result=load("res://scripts/delivery_quiet_d14_20261023/composition.gd").prepare(host,{"name":"QG_Batch_38"})
 assert(result.is_empty() and owner.mesh==before);checks.append({"case":"changed owner mesh","rejected_before_mutation":true})
 var file:=FileAccess.open("/tmp/quiet_chain_negative_validation.json",FileAccess.WRITE);file.store_string(JSON.stringify({"status":"PASS","expected_assertions":8,"checks":checks},"  "));file.close();print("NEGATIVE_GUARDS_PASS ",checks.size());host.free();quit()
