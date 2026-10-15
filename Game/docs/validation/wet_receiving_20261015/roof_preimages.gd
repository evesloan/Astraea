extends SceneTree
func digest(b:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(b);return h.finish().hex_encode()
func _initialize()->void:
 var rows:Array=[]
 for spec in[["TIDAL","AST-RES-TIDAL_lift_fit_r003.glb","TG_Batch_283"],["QUIET","QUIET_GROVE_ARCHITECTURE_lift_r003.glb","QG_Batch_462"]]:
  var model:Node3D=(load("res://assets/models/"+spec[1])as PackedScene).instantiate();var mesh:MeshInstance3D=model.find_child(spec[2],true,false);assert(mesh!=null)
  var a:Array=mesh.mesh.surface_get_arrays(0);var b:AABB=mesh.get_aabb();rows.append({"kit":spec[0],"model":spec[1],"source_sha256":FileAccess.get_sha256("res://assets/models/"+spec[1]),"node":spec[2],"faces_sha256":digest(mesh.mesh.get_faces().to_byte_array()),"surfaces":mesh.mesh.get_surface_count(),"vertices":a[Mesh.ARRAY_VERTEX].size(),"face_vertices":mesh.mesh.get_faces().size(),"min":[b.position.x,b.position.y,b.position.z],"max":[b.end.x,b.end.y,b.end.z],"extras":mesh.get_meta("extras",{})});model.free()
 FileAccess.open("/workspace/astraea-integration-cutoff-20261013/approved_combined_receivers_20261014/wet_receiving/EXACT_ROOF_PREIMAGES.json",FileAccess.WRITE).store_string(JSON.stringify(rows,"  "));print("PASS_EXACT_ROOF_PREIMAGES");quit(0)
