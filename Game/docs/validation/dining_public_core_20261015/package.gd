extends RefCounted
static func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
static func build(ship:Node3D)->Node3D:
 var p:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/dining_public_core_20261015/NATIVE_VERIFICATION.json"))
 assert(FileAccess.get_sha256("res://assets/models/"+str(p.source_file))==str(p.source_sha256))
 assert(FileAccess.get_sha256("res://assets/dining_public_core_20261015/FORWARD_D10_DINING_PUBLIC_BRANCHES_r001.glb")==str(p.model_sha256))
 assert(ship.get_node_or_null("ShipSpace/DiningD10CorePublicBranches")==null)
 var original:Node3D=ship.get_node("ShipSpace/Districts/ForwardPublicCore_WIP/PrimaryCoreEnclosure")
 var variant:Node3D=(load("res://assets/dining_public_core_20261015/FORWARD_D10_DINING_PUBLIC_BRANCHES_r001.glb")as PackedScene).instantiate()
 var group:=Node3D.new();group.name="DiningD10CorePublicBranches";ship.get_node("ShipSpace").add_child(group)
 var witnesses:Array=[]
 for row in p.walls:
  var mesh:MeshInstance3D=original.find_child(str(row.source_name),true,false);assert(mesh!=null)
  assert(mesh.global_transform.is_equal_approx(Transform3D(Basis.IDENTITY,Vector3(0,0,-432))))
  assert(mesh.mesh.get_faces().size()==int(row.source_triangles)*3)
  var bounds:AABB=mesh.get_aabb();var lo:Array=row.input_bounds_local[0];var hi:Array=row.input_bounds_local[1];assert(bounds.position.distance_to(Vector3(lo[0],lo[1],lo[2]))<.0001 and bounds.end.distance_to(Vector3(hi[0],hi[1],hi[2]))<.0001)
  var collider:CollisionShape3D=mesh.find_children("*","CollisionShape3D",true,false)[0];assert(collider.shape is ConcavePolygonShape3D)
  assert(digest(collider.shape.get_faces().to_byte_array())==digest(mesh.mesh.get_faces().to_byte_array()))
  var replacement:MeshInstance3D=variant.find_child(str(row.replacement_name).validate_node_name(),true,false);assert(replacement!=null)
  assert(replacement.transform.is_equal_approx(Transform3D.IDENTITY));assert(replacement.mesh.get_surface_count()==mesh.mesh.get_surface_count())
  var before:Mesh=mesh.mesh;var prior:Shape3D=collider.shape;var edited:Mesh=replacement.mesh.duplicate()
  for i in range(edited.get_surface_count()):edited.surface_set_material(i,before.surface_get_material(i))
  mesh.mesh=edited;collider.shape=edited.create_trimesh_shape();collider.shape.margin=prior.margin
  group.set_meta(str(row.source_name).replace("-","_")+"_retained_original_mesh",before);group.set_meta(str(row.source_name).replace("-","_")+"_retained_original_shape",prior)
  witnesses.append({"source_node":str(mesh.get_path()),"original_faces_sha256":digest(before.get_faces().to_byte_array()),"new_faces_sha256":digest(edited.get_faces().to_byte_array()),"original_node_pose_preserved":true})
 variant.free();group.set_meta("exact_selected_wall_preimages",witnesses);group.set_meta("default_main_adoption",false);group.set_meta("operating_food_hygiene_pressure_capacity_admission",false)
 return group
