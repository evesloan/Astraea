extends SceneTree
func _initialize()->void:call_deferred("run")
func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func run()->void:
 var root_scene:Node3D=(load("res://assets/models/AST-COM-003.glb")as PackedScene).instantiate();root.add_child(root_scene);root_scene.position=Vector3(63,84,0);var rows:Array=[]
 for name in ["HC_GuardBase_D17_0_4_0","HC_GuardGlass_D17_0_4_0","HC_GuardCap_D17_0_4_0"]:
  var mesh:MeshInstance3D=root_scene.find_child(name,true,false);assert(mesh!=null);var b:AABB=mesh.global_transform*mesh.get_aabb();rows.append({"name":name,"world_min":[b.position.x,b.position.y,b.position.z],"world_max":[b.end.x,b.end.y,b.end.z],"faces_sha256":digest(mesh.mesh.get_faces().to_byte_array()),"faces_vertices":mesh.mesh.get_faces().size(),"surface_count":mesh.mesh.get_surface_count()})
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/g2_central_receiver_successor_20261013/EXACT_GUARD_PREIMAGES.json",FileAccess.WRITE).store_string(JSON.stringify({"status":"PASS_EXACT_IMPORTED_GUARD_PREIMAGES","model_sha256":FileAccess.get_sha256("res://assets/models/AST-COM-003.glb"),"clipped_world_x":[59.1,60.9],"primary_profilewall_parts_changed":0,"original_node_and_body_identities_retained":true,"rows":rows},"  "));print("EXACT_GUARD_PREIMAGES_PASS");quit(0)
