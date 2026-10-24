extends RefCounted
const P := "res://clinical_room_receiving_20261024/"
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func require_ok(ok:bool,message:String)->bool:
 if not ok:push_error("Clinical receiving: "+message)
 return ok
static func clip(poly:Array,axis:int,plane:float,less:bool)->Array:
 if poly.is_empty():return []
 var out:Array=[];var previous:Dictionary=poly[-1];var dp:float=previous.p[axis]-plane
 for current:Dictionary in poly:
  var dc:float=current.p[axis]-plane;var a:bool=dp<=0 if less else dp>=0;var b:bool=dc<=0 if less else dc>=0
  if a!=b:
   var t:float=dp/(dp-dc);out.append({"p":previous.p.lerp(current.p,t),"n":previous.n.lerp(current.n,t).normalized(),"uv":previous.uv.lerp(current.uv,t)})
  if b:out.append(current)
  previous=current;dp=dc
 return out
static func subtract(poly:Array,z:float)->Array:
 var outside:Array=[];var inside:Array=poly
 for boundary:Array in [[1,21.0,false],[1,23.4,true],[2,z-1.8,false],[2,z+1.8,true]]:
  var part:Array=clip(inside,int(boundary[0]),float(boundary[1]),not bool(boundary[2]))
  if part.size()>=3:outside.append(part)
  inside=clip(inside,int(boundary[0]),float(boundary[1]),bool(boundary[2]))
  if inside.is_empty():break
 return outside
static func emit(st:SurfaceTool,poly:Array,inverse:Transform3D,basis:Basis)->void:
 for i in range(1,poly.size()-1):
  for index:int in [0,i,i+1]:
   var row:Dictionary=poly[index];st.set_normal((basis*row.n).normalized());st.set_uv(row.uv);st.add_vertex(inverse*row.p)
static func cut_wall(mesh:MeshInstance3D,row:Dictionary)->void:
 var prior:Mesh=mesh.mesh;var replacement:=ArrayMesh.new();var inverse:Transform3D=mesh.global_transform.affine_inverse();var normal_inverse:Basis=mesh.global_basis.transposed()
 for surface in range(prior.get_surface_count()):
  var arrays:Array=prior.surface_get_arrays(surface);var points:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX];var normals:PackedVector3Array=arrays[Mesh.ARRAY_NORMAL];var uvs:PackedVector2Array=arrays[Mesh.ARRAY_TEX_UV];var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
  if indices.is_empty():
   indices.resize(points.size())
   for i in range(points.size()):indices[i]=i
  var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES);st.set_material(prior.surface_get_material(surface))
  for start in range(0,indices.size(),3):
   var poly:Array=[]
   for offset in range(3):
    var index:int=indices[start+offset];poly.append({"p":mesh.global_transform*points[index],"n":(mesh.global_basis.inverse().transposed()*normals[index]).normalized(),"uv":uvs[index]})
   var polygons:Array=[poly]
   for cut:Dictionary in row.cuts:
    var next:Array=[]
    for q:Array in polygons:next.append_array(subtract(q,float(cut.z)))
    polygons=next
   for q:Array in polygons:emit(st,q,inverse,normal_inverse)
  # Source-skin clipping preserves outside UVs/normals; close only the new
  # jamb/head reveals. The existing floor remains the threshold owner.
  var x0:float=row.world_bounds[0][0];var x1:float=row.world_bounds[1][0]
  for cut:Dictionary in row.cuts:
   var z:float=cut.z
   for spec:Array in [[Vector3(x0,21,z-1.8),Vector3(x1,21,z-1.8),Vector3(x1,23.4,z-1.8),Vector3(x0,23.4,z-1.8),Vector3(0,0,1)],[Vector3(x1,21,z+1.8),Vector3(x0,21,z+1.8),Vector3(x0,23.4,z+1.8),Vector3(x1,23.4,z+1.8),Vector3(0,0,-1)],[Vector3(x0,23.4,z-1.8),Vector3(x1,23.4,z-1.8),Vector3(x1,23.4,z+1.8),Vector3(x0,23.4,z+1.8),Vector3.DOWN]]:
    var q:Array=[]
    for i in [0,3,2,1]:q.append({"p":spec[i],"n":spec[4],"uv":Vector2(spec[i].z,spec[i].y)*.5})
    emit(st,q,inverse,normal_inverse)
  st.commit(replacement)
 var shapes:Array=mesh.find_children("*","CollisionShape3D",true,false);var contact:CollisionShape3D=shapes[0];var margin:float=contact.shape.margin
 mesh.mesh=replacement;contact.shape=replacement.create_trimesh_shape();contact.shape.margin=margin
 mesh.set_meta("clinical_receiving_original_faces",prior.get_faces().size()/3);mesh.set_meta("clinical_receiving_openings",row.cuts.size())
static func build(ship:Node3D)->Node3D:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"))
 for path:String in plan.source_pins:
  if path.begins_with("Game/")and not require_ok(FileAccess.get_sha256("res://"+path.trim_prefix("Game/"))==plan.source_pins[path],"Retained bytes changed: "+path):return null
 var clinical:Node3D=ship.get_node_or_null("ShipSpace/Group3CompleteClinical")
 if not require_ok(clinical!=null and not clinical.get_meta("operating_gates_or_dispatch_admitted",false),"Retained closed clinical network required"):return null
 var owners:={};var originals:={};var materials:={}
 for mesh:MeshInstance3D in clinical.find_children("*","MeshInstance3D",true,false):
  for si in range(mesh.mesh.get_surface_count()):
   var material:Material=mesh.get_active_material(si)
   if material!=null:materials[str(material.resource_name).trim_prefix("ASTRAEA_")]=material
 for row:Dictionary in plan.rooms:
  var room:Node3D=ship.get_node_or_null("ShipSpace/Districts/ReceivedSections/"+str(row.key))
  if not require_ok(room!=null and not room.has_node("ClinicalRoomReceiving20261024"),"Unique retained room: "+str(row.key)):return null
  var meshes:Array=room.find_children("*","MeshInstance3D",true,false)
  if not require_ok(meshes.size()==row.source_mesh_count,"Exact original room mesh count: "+str(row.key)):return null
  owners[row.key]=room
  for mesh:MeshInstance3D in meshes:originals[str(mesh.get_path())]={"mesh":mesh.mesh,"pose":mesh.global_transform}
 for row:Dictionary in plan.walls:
  var mesh:MeshInstance3D=owners[row.room].find_child(row.source_name,true,false)
  if not require_ok(mesh!=null,"Retained wall missing"):return null
  var bounds:AABB=mesh.global_transform*mesh.get_aabb();var shapes:Array=mesh.find_children("*","CollisionShape3D",true,false)
  if not require_ok(mesh.mesh.get_faces().size()==int(row.source_triangles)*3 and bounds.position.distance_to(v(row.world_bounds[0]))<.0002 and bounds.end.distance_to(v(row.world_bounds[1]))<.0002 and shapes.size()==1,"Exact wall/contact preimage: "+str(row.room)):return null
 for row:Dictionary in plan.parts:
  if not require_ok(materials.has(row.role),"Original material absent: "+str(row.role)):return null
 var receipt:=Node3D.new();receipt.name="ClinicalRoomReceiving20261024";ship.get_node("ShipSpace").add_child(receipt)
 for row:Dictionary in plan.walls:cut_wall(owners[row.room].find_child(row.source_name,true,false),row)
 var groups:={};var roots:={}
 for key:String in owners:
  var root:=Node3D.new();root.name="ClinicalRoomReceiving20261024";owners[key].add_child(root);root.top_level=true;root.global_transform=Transform3D.IDENTITY;roots[key]=root
 for row:Dictionary in plan.parts:
  var key:String=str(row.room)+"/"+str(row.role)
  if not groups.has(key):groups[key]=[]
  groups[key].append(row)
 var batches:=0
 for key:String in groups:
  var rows:Array=groups[key];var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES);st.set_material(materials[rows[0].role]);var names:Array=[]
  for row:Dictionary in rows:
   names.append(row.name)
   for face:Array in row.faces:
    for i in range(1,face.size()-1):
     var a:=v(row.verts[face[0]]);var b:=v(row.verts[face[i]]);var c:=v(row.verts[face[i+1]]);var normal:Vector3=(b-a).cross(c-a).normalized()
     for index:int in [face[0],face[i+1],face[i]]:
      var point:Vector3=v(row.verts[index]);st.set_normal(normal);st.set_uv(Vector2(point.x,point.z)*.5 if absf(normal.y)>.7 else Vector2(point.z,point.y)*.5);st.add_vertex(point)
  var mesh:=MeshInstance3D.new();mesh.name="ReceivingBatch_%03d"%batches;mesh.mesh=st.commit();mesh.set_meta("authored_parts",names);roots[rows[0].room].add_child(mesh);load("res://scripts/static_contact_cache.gd").attach(mesh);batches+=1
 # Shared opaque source cassette resources; no persistent IDs or operation are
 # invented. Each complete closed cassette is one local room-owned instance.
 var template:Node3D=load(plan.source_gate).instantiate();var gate_scenes:Array=[]
 for original:MeshInstance3D in template.find_children("*","MeshInstance3D",true,false):
  var transform:Transform3D=original.transform;var parent:Node3D=original.get_parent()
  while parent!=template:transform=parent.transform*transform;parent=parent.get_parent()
  gate_scenes.append({"name":original.name,"mesh":original.mesh,"transform":transform,"material":original.material_override})
 template.free()
 var lamps:Array[Light3D]=[]
 for port:Dictionary in plan.ports:
  var gate:=Node3D.new();gate.name=str(port.id)+"_ClosedSourceCassette";roots[port.room].add_child(gate);gate.position=v(port.gate_position);gate.rotation.y=float(port.gate_yaw);gate.set_meta("clinical_operation_admitted",false);gate.set_meta("persistent_id_assigned",false);var contacts:Array[Node]=[]
  for item:Dictionary in gate_scenes:
   var mesh:=MeshInstance3D.new();mesh.name=item.name;mesh.mesh=item.mesh;mesh.transform=item.transform;mesh.material_override=item.material;gate.add_child(mesh);contacts.append(mesh)
  load("res://scripts/static_contact_cache.gd").attach_group(gate,contacts)
  for row:Dictionary in port.lights:
   var lamp:=SpotLight3D.new();lamp.name=row.name;roots[port.room].add_child(lamp);lamp.position=v(row.position);lamp.rotation.x=-PI/2;lamp.light_color=Color(row.color[0],row.color[1],row.color[2]);lamp.light_energy=row.energy;lamp.spot_range=row.range;lamp.spot_angle=65;lamp.shadow_enabled=true;lamp.visible=false;lamp.set_meta("fixture_powered",true);lamps.append(lamp)
 load("res://scripts/receiving_source_lights.gd").register(lamps,ship)
 var changed:=0
 for path:String in originals:
  var mesh:MeshInstance3D=ship.get_node(path);var before:Dictionary=originals[path]
  if not require_ok(mesh.global_transform.is_equal_approx(before.pose),"Original pose changed"):return null
  if mesh.mesh!=before.mesh:changed+=1
 if not require_ok(changed==3,"Only three original enclosure resources may change"):return null
 receipt.set_meta("rooms",8);receipt.set_meta("interfaces",16);receipt.set_meta("new_floor_m2",plan.new_floor_m2);receipt.set_meta("parts",plan.parts.size());receipt.set_meta("batches",batches);receipt.set_meta("original_meshes",originals.size());receipt.set_meta("changed_original_meshes",changed);receipt.set_meta("new_capacity",0);receipt.set_meta("clinical_operation_admitted",false);receipt.set_meta("visual_accepted",false)
 return receipt
