extends RefCounted
const DATA:="res://scripts/delivery_quiet_d14_20261023/COMPOSITION.json"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func prepare(ship:Node3D,row:Dictionary)->Dictionary:
 assert(FileAccess.get_sha256(DATA)=="694d83cf39fe88d58608eab124e2874dc52f716631a112a00dbe129b5ec48504")
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(DATA))
 assert(FileAccess.get_sha256(data.source_scene)==data.source_scene_sha256)
 assert(FileAccess.get_sha256("res://data/quiet_d14_receiving_20261016/RECEIPT.json")==data.receipt_sha256)
 assert(FileAccess.get_sha256("res://quiet_grove_specialty_20261022/adapter_r002.gd")==data.source_adapter_sha256)
 var district:Node3D=ship.get_node("ShipSpace/Districts/QuietGrove17Specialty20261022")
 assert(district.get_meta("original_guard_batches_replaced")==11 and district.get_meta("reserved_rests")==19)
 var choices:Array=data.rows.filter(func(r):return str(r.name)==str(row.name));assert(choices.size()==1)
 var contract:Dictionary=choices[0]
 var owner:MeshInstance3D=district.get_node("QuietGrove17Receiving_r001/"+str(row.name))
 assert(owner.global_transform.is_equal_approx(Transform3D.IDENTITY))
 assert(owner.mesh.get_surface_count()==1 and owner.mesh.get_faces().size()==int(contract.preimage_triangles)*3)
 assert(owner.mesh.get_faces().to_byte_array().hex_encode().sha256_text()==contract.preimage_faces_hex_sha256)
 assert(owner.get_aabb().position.distance_to(v(contract.preimage_min))<.0002 and owner.get_aabb().end.distance_to(v(contract.preimage_max))<.0002)
 var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
 for triangle:Array in contract.triangles:
  for vertex:Dictionary in triangle:
   st.set_normal(v(vertex.n));st.set_uv(Vector2(vertex.uv[0],vertex.uv[1]))
   if vertex.has("t"):st.set_tangent(Plane(vertex.t[0],vertex.t[1],vertex.t[2],vertex.t[3]))
   st.add_vertex(v(vertex.p))
 var mesh:ArrayMesh=st.commit();assert(mesh.get_faces().size()==int(contract.result_triangles)*3)
 # Same absolute source-bound tolerance; no relaxation or source-receipt rewrite.
 assert(mesh.get_aabb().position.distance_to(v(row.min))<.0002 and mesh.get_aabb().end.distance_to(v(row.max))<.0002)
 return {"owner":owner,"mesh":mesh}
