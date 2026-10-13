extends RefCounted
static func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
static func clip(poly:Array,plane:float,left:bool)->Array:
 var out:Array=[]
 if poly.is_empty():return out
 var s:Dictionary=poly[-1];var ds:float=s.p.x-plane
 for e:Dictionary in poly:
  var de:float=e.p.x-plane;var sin:bool=ds<=0 if left else ds>=0;var ein:bool=de<=0 if left else de>=0
  if sin!=ein:
   var f:float=ds/(ds-de);out.append({"p":s.p.lerp(e.p,f),"n":s.n.lerp(e.n,f),"uv":s.uv.lerp(e.uv,f)})
  if ein:out.append(e)
  s=e;ds=de
 return out
static func vertex(tool:SurfaceTool,v:Dictionary)->void:
 tool.set_normal(v.n);tool.set_uv(v.uv);tool.add_vertex(v.p)
static func apply(ship:Node3D,owner:Node3D,p:Dictionary)->void:
 assert(FileAccess.get_sha256("res://assets/models/AST-COM-003.glb")==str(p.model_sha256));var architecture:Node3D=ship.find_child("StarboardHouseUpperArchitecture",true,false);var source_meshes:Array=[];var source_shapes:Array=[]
 # Verify ALL original guard preimages before applying any successor.
 for row in p.rows:
  var node:MeshInstance3D=architecture.find_child(str(row.name),true,false);assert(node!=null and node.global_transform.basis.is_equal_approx(Basis.IDENTITY));var b:AABB=node.global_transform*node.get_aabb()
  assert(b.position.distance_to(Vector3(row.world_min[0],row.world_min[1],row.world_min[2]))<.001 and b.end.distance_to(Vector3(row.world_max[0],row.world_max[1],row.world_max[2]))<.001);assert(digest(node.mesh.get_faces().to_byte_array())==str(row.faces_sha256));assert(node.mesh.get_surface_count()==row.surface_count);assert(node.find_children("*","CollisionShape3D",true,false).size()==1)
 for row in p.rows:
  var node:MeshInstance3D=architecture.find_child(str(row.name),true,false);var old:Mesh=node.mesh;var shape:CollisionShape3D=node.find_children("*","CollisionShape3D",true,false)[0];source_meshes.append(old);source_shapes.append(shape.shape);var bounds:AABB=node.get_aabb();var left:float=p.clipped_world_x[0]-node.global_position.x;var right:float=p.clipped_world_x[1]-node.global_position.x;var result:=ArrayMesh.new()
  for surface in range(old.get_surface_count()):
   var arrays:Array=old.surface_get_arrays(surface);var vs:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX];var ns:PackedVector3Array=arrays[Mesh.ARRAY_NORMAL];var uv:PackedVector2Array=arrays[Mesh.ARRAY_TEX_UV];var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX];var tool:=SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES);tool.set_material(old.surface_get_material(surface));var size:int=indices.size()if not indices.is_empty()else vs.size()
   for start in range(0,size,3):
    var tri:Array=[]
    for j in range(3):
     var index:int=indices[start+j]if not indices.is_empty()else start+j;tri.append({"p":vs[index],"n":ns[index],"uv":uv[index]if not uv.is_empty()else Vector2.ZERO})
    for poly:Array in [clip(tri,left,true),clip(tri,right,false)]:
     for j in range(1,poly.size()-1):vertex(tool,poly[0]);vertex(tool,poly[j]);vertex(tool,poly[j+1])
   # Close only the newly exposed cut ends; original outer surfaces retain source normals/UV interpolation/materials.
   for spec in [{"x":left,"normal":Vector3.RIGHT},{"x":right,"normal":Vector3.LEFT}]:
    var x:float=spec.x;var pts:Array=[Vector3(x,bounds.position.y,bounds.position.z),Vector3(x,bounds.end.y,bounds.position.z),Vector3(x,bounds.end.y,bounds.end.z),Vector3(x,bounds.position.y,bounds.end.z)]
    for ids:Array in [[0,1,2],[0,2,3]]:
     var a:Vector3=pts[ids[0]];var b:Vector3=pts[ids[1]];var c:Vector3=pts[ids[2]]
     if (b-a).cross(c-a).dot(spec.normal)>0:var swap:=b;b=c;c=swap
     for at:Vector3 in [a,b,c]:vertex(tool,{"p":at,"n":spec.normal,"uv":Vector2(at.z,at.y)})
   tool.commit(result)
  node.mesh=result;shape.shape=result.create_trimesh_shape();shape.shape.margin=.001
 owner.set_meta("original_guard_mesh_resources",source_meshes);owner.set_meta("original_guard_contact_resources",source_shapes);owner.set_meta("bounded_guard_successor_parts",3);owner.set_meta("guard_crossing_width_m",1.8)
