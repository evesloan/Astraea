extends RefCounted
# Candidate: exact compressed vertex buffers, translation-normalized, instanced in8m cells.
const RULES=preload("res://spatial_instance_cells_20261026/ship_rules.gd")
const CELL:=8.0
static func translate_surface(row:Dictionary,origin:Vector3)->void:
 if (int(row.format)&Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES)==0:
  assert((int(row.format)&Mesh.ARRAY_FLAG_USE_2D_VERTICES)==0)
  var bytes:PackedByteArray=row.vertex_data.duplicate();var count:int=row.vertex_count
  assert(bytes.size()>=count*12)
  for i in count:
   for axis in 3:bytes.encode_float(i*12+axis*4,bytes.decode_float(i*12+axis*4)-origin[axis])
  row.vertex_data=bytes
 row.aabb=AABB(row.aabb.position-origin,row.aabb.size);row.erase("material");row.erase("lods")
static func normalized(mesh:ArrayMesh)->Dictionary:
 var raw:Array=mesh.get("_surfaces").duplicate(true)
 if raw.size()!=1:return {}
 var origin:Vector3=raw[0].aabb.position
 translate_surface(raw[0],origin)
 var shadow:Array=[]
 if mesh.shadow_mesh!=null:
  shadow=mesh.shadow_mesh.get("_surfaces").duplicate(true)
  for row:Dictionary in shadow:
   translate_surface(row,origin)
 var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(var_to_bytes([raw,shadow]));var key:=hash.finish().hex_encode()
 return {"key":key,"raw":raw,"shadow":shadow,"origin":origin}
static func compact(root:Node3D,lights:Array)->Dictionary:
 assert(not root.has_meta("exact_instance_restore"),"Restore representation before rebuilding")
 var restoration:Array=[];var generated:Array=[]
 var bins:Dictionary={};var normalized_by_id:Dictionary={};var canonical:Dictionary={}
 var source_count:=0;var eligible_count:=0;var light_rejections:=0;var rule_rejections:=0;var lod_rejections:=0
 for node:MeshInstance3D in root.find_children("*","MeshInstance3D",true,false):
  source_count+=1
  if not RULES.eligible(node,root):rule_rejections+=1;continue
  var has_lod:=false
  for surface:Dictionary in node.mesh.get("_surfaces"):
   if not surface.get("lods",[]).is_empty():has_lod=true
  if node.mesh.shadow_mesh!=null:
   for surface:Dictionary in node.mesh.shadow_mesh.get("_surfaces"):
    if not surface.get("lods",[]).is_empty():has_lod=true
  # Use full source geometry instead of lower-detail LODs; no surface is omitted.
  if has_lod:lod_rejections+=1
  var pose:Transform3D=RULES.pose(node,root);var box:AABB=pose*node.get_aabb()
  if box.size[box.size.max_axis_index()]>CELL:continue
  var signature:String=RULES.light_signature(root.global_transform*box,node.layers,lights)
  if signature=="OVER_LIMIT":light_rejections+=1;continue
  # Reject spatial/light-incompatible members before copying and hashing vertex buffers.
  var id:=node.mesh.get_instance_id()
  if not normalized_by_id.has(id):normalized_by_id[id]=normalized(node.mesh)
  var record:Dictionary=normalized_by_id[id]
  if record.is_empty():continue
  var center:=box.get_center();var cell:=Vector3i(floori(center.x/CELL),floori(center.y/CELL),floori(center.z/CELL))
  var state:Array=[]
  for prop:String in RULES.DRAW:state.append(node.get(prop))
  var mirrored:=pose.basis.determinant()<0
  var key:String=str(mirrored)+":"+str(cell)+":"+record.key+":"+str(node.get_active_material(0).get_instance_id())+":"+str(state)+":"+signature
  if not bins.has(key):bins[key]={"members":[],"bounds":box,"state":state,"signature":signature,"record":record,"material":node.get_active_material(0),"mirrored":mirrored}
  var combined:AABB=bins[key].bounds.merge(box)
  if combined.size[combined.size.max_axis_index()]>CELL:continue
  if RULES.light_signature(root.global_transform*combined,node.layers,lights)!=signature:light_rejections+=1;continue
  bins[key].bounds=combined;bins[key].members.append({"node":node,"pose":pose*Transform3D(Basis.IDENTITY,record.origin),"original_pose":pose});eligible_count+=1
 var batches:=0;var converted:=0;var checked_vertices:=0
 for key:String in bins:
  var bin:Dictionary=bins[key]
  if bin.members.size()<2:continue
  var record:Dictionary=bin.record
  if not canonical.has(record.key):
   var mesh:=ArrayMesh.new();mesh.set("_surfaces",record.raw)
   if not record.shadow.is_empty():
    var shadow:=ArrayMesh.new();shadow.set("_surfaces",record.shadow);mesh.shadow_mesh=shadow
   canonical[record.key]=mesh
  var mesh:ArrayMesh=canonical[record.key]
  var mm:=MultiMesh.new();mm.transform_format=MultiMesh.TRANSFORM_3D;mm.mesh=mesh;mm.instance_count=bin.members.size()
  var batch_pose:=Transform3D(Basis(Vector3(-1,0,0),Vector3(0,1,0),Vector3(0,0,1)),Vector3.ZERO) if bin.mirrored else Transform3D.IDENTITY
  var target:PackedVector3Array=mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
  for i in bin.members.size():
   var row:Dictionary=bin.members[i]
   var original:PackedVector3Array=row.node.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
   assert(original.size()==target.size())
   for v in original.size():
    assert((row.original_pose*original[v]).distance_to(row.pose*target[v])<.00005,"Canonical translated vertex mismatch");checked_vertices+=1
   var instance_pose:Transform3D=batch_pose.affine_inverse()*row.pose
   assert(instance_pose.basis.determinant()>0,"Per-instance winding must remain positive")
   for v in original.size():assert((row.original_pose*original[v]).distance_to(batch_pose*instance_pose*target[v])<.00005,"Factored reflection changed geometry")
   mm.set_instance_transform(i,instance_pose)
  var batch:=MultiMeshInstance3D.new();batch.name="ExactInstanceCell_%04d"%batches;batch.multimesh=mm;batch.material_override=bin.material
  for i in RULES.DRAW.size():batch.set(RULES.DRAW[i],bin.state[i])
  batch.transform=batch_pose
  root.add_child(batch)
  generated.append(weakref(batch))
  for row:Dictionary in bin.members:
   var original:MeshInstance3D=row.node
   var overrides:Array=[]
   for surface in original.mesh.get_surface_count():overrides.append(original.get_surface_override_material(surface))
   restoration.append({"node":weakref(original),"mesh":original.mesh,"overrides":overrides})
   original.mesh=null;row.erase("node");converted+=1
  batches+=1
 root.set_meta("exact_instance_restore",{"rows":restoration,"batches":generated})
 return {"source_meshes":source_count,"eligible_meshes":eligible_count,"converted_mesh_instances":converted,"batch_count":batches,"saved_submissions":converted-batches,"canonical_meshes":canonical.size(),"checked_vertices":checked_vertices,"light_rejections":light_rejections,"rule_rejections":rule_rejections,"source_lod_meshes_full_resolution":lod_rejections,"policy":"8m maximum cells; exact original mesh-node identities and physics; reversible full-resolution geometry; original resources retained while active, no memory-saving claim"}

static func restore(root:Node3D)->bool:
 if not root.has_meta("exact_instance_restore"):return true
 var state:Dictionary=root.get_meta("exact_instance_restore")
 for row:Dictionary in state.rows:
  var node:MeshInstance3D=row.node.get_ref()
  if node==null or node.mesh!=null:
   push_error("Instance representation destination changed; refusing restoration")
   return false
 for row:Dictionary in state.rows:
  var node:MeshInstance3D=row.node.get_ref();node.mesh=row.mesh
  for surface in row.overrides.size():node.set_surface_override_material(surface,row.overrides[surface])
 for reference:WeakRef in state.batches:
  var batch:MultiMeshInstance3D=reference.get_ref()
  if batch!=null:
   batch.visible=false;batch.multimesh=null;batch.queue_free()
 root.remove_meta("exact_instance_restore")
 return true

