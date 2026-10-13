extends RefCounted
static func digest(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
static func clip(poly:Array,axis:int,plane:float,less:bool)->Array:
 var result:Array=[]
 if poly.is_empty():return result
 var s:Dictionary=poly[-1];var ds:float=s.p[axis]-plane
 for e:Dictionary in poly:
  var de:float=e.p[axis]-plane;var ins:bool=ds<=0 if less else ds>=0;var ine:bool=de<=0 if less else de>=0
  if ins!=ine:
   var f:float=ds/(ds-de);result.append({"p":s.p.lerp(e.p,f),"n":s.n.lerp(e.n,f),"uv":s.uv.lerp(e.uv,f)})
  if ine:result.append(e)
  s=e;ds=de
 return result
static func subtract(tri:Array,box:Array)->Array:
 var pieces:Array=[];var inside:Array=tri
 for spec in [[0,box[0],false],[0,box[1],true],[1,box[2],false],[1,box[3],true],[2,box[4],false],[2,box[5],true]]:
  var outside:Array=clip(inside,spec[0],spec[1],not spec[2]);if outside.size()>=3:pieces.append(outside)
  inside=clip(inside,spec[0],spec[1],spec[2]);if inside.is_empty():break
 return pieces
static func apply(ship:Node3D,owner:Node3D,site:Dictionary)->void:
 assert(FileAccess.get_sha256("res://assets/models/"+str(site.receiver_model))==str(site.receiver_sha256));var root:Node=ship.get_node("ShipSpace/Districts/"+str(site.receiver_root));var saved_meshes:Array=[];var saved_shapes:Array=[]
 for row in site.guard_preimages:
  var node:MeshInstance3D=root.find_child(str(row.name),true,false);assert(node!=null and node.global_transform.is_equal_approx(Transform3D.IDENTITY));var extra:Dictionary=node.get_meta("extras",{});assert(extra.get("category","")in["guard","public_glass"]);assert(digest(node.mesh.get_faces().to_byte_array())==str(row.faces_sha256));assert(node.find_children("*","CollisionShape3D",true,false).size()==1)
 for row in site.guard_preimages:
  var node:MeshInstance3D=root.find_child(str(row.name),true,false);var old:Mesh=node.mesh;var shape:CollisionShape3D=node.find_children("*","CollisionShape3D",true,false)[0];var output:=ArrayMesh.new();saved_meshes.append(old);saved_shapes.append(shape.shape)
  for surface in range(old.get_surface_count()):
   var a:Array=old.surface_get_arrays(surface);var vs:PackedVector3Array=a[Mesh.ARRAY_VERTEX];var ns:PackedVector3Array=a[Mesh.ARRAY_NORMAL];var uv:PackedVector2Array=a[Mesh.ARRAY_TEX_UV];var ix:PackedInt32Array=a[Mesh.ARRAY_INDEX];var count:int=ix.size()if not ix.is_empty()else vs.size();var tool:=SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES);tool.set_material(old.surface_get_material(surface));var emitted:=0
   for start in range(0,count,3):
    var triangle:Array=[]
    for j in range(3):
     var index:int=ix[start+j]if not ix.is_empty()else start+j;triangle.append({"p":vs[index],"n":ns[index],"uv":uv[index]if not uv.is_empty()else Vector2.ZERO})
    for poly:Array in subtract(triangle,site.mask):
     for j in range(1,poly.size()-1):
      for v:Dictionary in [poly[0],poly[j],poly[j+1]]:tool.set_normal(v.n);tool.set_uv(v.uv);tool.add_vertex(v.p);emitted+=1
   assert(emitted>0);tool.commit(output)
  node.mesh=output;shape.shape=output.create_trimesh_shape();shape.shape.margin=.001
 owner.set_meta(str(site.key)+"_original_guard_meshes",saved_meshes);owner.set_meta(str(site.key)+"_original_guard_shapes",saved_shapes)
