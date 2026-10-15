extends RefCounted
static func digest(b:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(b);return h.finish().hex_encode()
static func apply(ship:Node3D,owner:Node3D,rows:Array)->void:
 assert(FileAccess.get_sha256("res://assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb")=="dff1f06ddf94d665dfbe86e9451d4737551b109f103b11cf90d203f1c78db62a")
 var root:Node=ship.get_node("ShipSpace/Districts/QuietGroveReceivingCandidate")
 for row in rows:
  var node:MeshInstance3D=root.find_child(str(row.node),true,false);assert(node!=null and var_to_bytes(node.transform).hex_encode()==str(row.transform_bytes_hex));assert(digest(node.mesh.get_faces().to_byte_array())==str(row.faces_sha256));var old:Transform3D=node.transform;node.position.y+=float(row.translation_y)
  for body:CollisionObject3D in node.find_children("*","CollisionObject3D",true,false):body.force_update_transform()
  assert(node.basis.is_equal_approx(old.basis)and digest(node.mesh.get_faces().to_byte_array())==str(row.faces_sha256));owner.set_meta(str(row.node)+"_original_canopy_pose",old)
 owner.set_meta("retained_arrival_canopy_rigid_raise_m",2.2)
