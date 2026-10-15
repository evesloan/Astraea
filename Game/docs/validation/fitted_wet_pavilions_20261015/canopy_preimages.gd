extends SceneTree
func digest(b:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(b);return h.finish().hex_encode()
func _initialize()->void:
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/TRAM_REMAINING_G8_OVERLAY.zip",true))
 assert(ProjectSettings.load_resource_pack("/workspace/astraea-integration-cutoff-20261013/dining_public_core_20261015/CANDIDATE_OVERLAY.zip",true))
 assert(load("res://scripts/dining_public_core_20261015/package.gd")!=null)
 var model:Node3D=(load("res://assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb")as PackedScene).instantiate();var rows:Array=[]
 for key in["QG_Batch_171","QG_Batch_172"]:
  var mesh:MeshInstance3D=model.find_child(key,true,false);rows.append({"node":key,"faces_sha256":digest(mesh.mesh.get_faces().to_byte_array()),"face_vertices":mesh.mesh.get_faces().size(),"translation_y":2.2,"transform_bytes_hex":var_to_bytes(mesh.transform).hex_encode(),"extras":mesh.get_meta("extras",{})})
 model.free();FileAccess.open("/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/CANOPY_EXACT_PREIMAGES_r007.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "));print("PASS_CANOPY_PREIMAGES_AND_DINING_SOURCE_PARSE");quit(0)
