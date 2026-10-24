extends RefCounted
const P:="res://clinical_return_links_20261024/"
const SKIN=preload("res://clinical_room_receiving_20261024/adapter.gd")
static func v(a:Array)->Vector3:return Vector3(a[0],a[1],a[2])
static func require_ok(ok:bool,message:String)->bool:
 if not ok:push_error("Clinical return links: "+message)
 return ok
static func subtract_box(poly:Array,b:Array)->Array:
 var outside:Array=[];var inside:Array=poly
 for boundary:Array in [[0,b[0],false],[0,b[2],true],[1,20.9,false],[1,25.21,true],[2,b[1],false],[2,b[3],true]]:
  var part:Array=SKIN.clip(inside,int(boundary[0]),float(boundary[1]),not bool(boundary[2]))
  if part.size()>=3:outside.append(part)
  inside=SKIN.clip(inside,int(boundary[0]),float(boundary[1]),bool(boundary[2]))
  if inside.is_empty():break
 return outside
static func cut_partition(mesh:MeshInstance3D,boxes:Array)->void:
 var source:Mesh=mesh.mesh;var successor:=ArrayMesh.new();var inverse:Transform3D=mesh.global_transform.affine_inverse()
 for si in range(source.get_surface_count()):
  var arrays:Array=source.surface_get_arrays(si);var positions:PackedVector3Array=arrays[Mesh.ARRAY_VERTEX];var normals:PackedVector3Array=arrays[Mesh.ARRAY_NORMAL];var uvs:PackedVector2Array=arrays[Mesh.ARRAY_TEX_UV];var indices:PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
  if indices.is_empty():
   indices.resize(positions.size())
   for i in range(positions.size()):indices[i]=i
  var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES);st.set_material(source.surface_get_material(si))
  for start in range(0,indices.size(),3):
   var poly:Array=[]
   for offset in range(3):
    var i:int=indices[start+offset];poly.append({"p":mesh.global_transform*positions[i],"n":(mesh.global_basis.inverse().transposed()*normals[i]).normalized(),"uv":uvs[i]})
   var fragments:Array=[poly]
   for box:Array in boxes:
    var next:Array=[]
    for fragment:Array in fragments:next.append_array(subtract_box(fragment,box))
    fragments=next
   for fragment:Array in fragments:SKIN.emit(st,fragment,inverse,mesh.global_basis.transposed())
  st.commit(successor)
 var contact:CollisionShape3D=mesh.find_children("*","CollisionShape3D",true,false)[0];var margin:float=contact.shape.margin;mesh.mesh=successor;contact.shape=successor.create_trimesh_shape();contact.shape.margin=margin;mesh.set_meta("clinical_return_source_faces",source.get_faces().size()/3)
static func build(ship:Node3D)->Node3D:
 var plan:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"PLAN.json"));var space:Node3D=ship.get_node("ShipSpace")
 for path:String in plan.source_pins:
  if path.begins_with("Game/")and not require_ok(FileAccess.get_sha256("res://"+path.trim_prefix("Game/"))==plan.source_pins[path],"Retained source mismatch: "+path):return null
 var clinic:Node3D=space.get_node("Group3CompleteClinical");var architecture:Node3D=clinic.get_node("AST-MED-G3-007")
 if not require_ok(space.has_node("ClinicalRoomReceiving20261024")and not space.has_node("ClinicalReturnThroughLinks20261024")and not clinic.get_meta("operating_gates_or_dispatch_admitted",true),"Prior receiving and closed operation required"):return null
 var originals:={};var materials:={}
 for mesh:MeshInstance3D in clinic.find_children("*","MeshInstance3D",true,false):
  originals[str(mesh.get_path())]={"node":mesh,"mesh":mesh.mesh,"pose":mesh.global_transform}
  for si in range(mesh.mesh.get_surface_count()):
   var material:Material=mesh.get_active_material(si)
   if material!=null:materials[str(material.resource_name).trim_prefix("ASTRAEA_")]=material
 for row:Dictionary in plan.wall_preimages:
  var mesh:MeshInstance3D=architecture.get_node_or_null(row.name)
  if not require_ok(mesh!=null,"Partition owner missing: "+str(row.name)):return null
  var box:AABB=mesh.global_transform*mesh.get_aabb()
  if not require_ok(mesh.mesh.get_faces().size()==int(row.source_triangles)*3 and box.position.distance_to(v(row.world_bounds[0]))<.0002 and box.end.distance_to(v(row.world_bounds[1]))<.0002 and mesh.find_children("*","CollisionShape3D",true,false).size()==1,"Exact partition preimage: "+str(row.name)):return null
 var proxies:={}
 var static_gates:Node3D=clinic.get_node("AST-MED-G3-010")
 for row:Dictionary in plan.retained_gate_bindings:
  var proxy:Node3D=space.get_node_or_null("Districts/ReceivedSections/"+str(row.room)+"/ClinicalRoomReceiving20261024/"+str(row.receiver))
  if not require_ok(proxy!=null and proxy.position.distance_to(v(row.position))<.0002 and proxy.find_children("*","MeshInstance3D",true,false).size()==21,"Exact duplicate receiver preimage: "+str(row.room)):return null
  var canonical:Array=[]
  for name:String in row.canonical_mesh_names:
   var retained:MeshInstance3D=static_gates.find_child(name,true,false)
   if not require_ok(retained!=null,"Canonical gate mesh missing: "+name):return null
   canonical.append(str(retained.get_path()))
  proxies[proxy]={"owners":canonical,"room":row.room}
 var supports:={}
 for row:Dictionary in plan.protected_supports+[plan.pool_bearing]:
  var mesh:MeshInstance3D=space.get_node("Districts/"+str(row.owner)+"/"+str(row.name));supports[str(mesh.get_path())]={"mesh":mesh.mesh,"pose":mesh.global_transform}
 for row:Dictionary in plan.parts:
  if not require_ok(materials.has(row.role),"Material missing: "+str(row.role)):return null
 # Earlier room-source cassettes repeat an installed network closure at each terminal.
 # Retain the receiving node identity as a reference; original gate visuals and
 # contacts remain the sole physical owner, still closed and unadmitted.
 for proxy:Node3D in proxies:
  for child:Node in proxy.get_children():child.free()
  proxy.set_meta("retained_closed_gate_meshes",proxies[proxy].owners)
  proxy.set_meta("duplicate_source_meshes_removed",21)
 var root:=Node3D.new();root.name="ClinicalReturnThroughLinks20261024";space.add_child(root)
 for row:Dictionary in plan.wall_preimages:cut_partition(architecture.get_node(row.name),plan.cut_boxes_xz)
 var grouped:={};var zones:={}
 for route:Dictionary in plan.routes:
  var node:=Node3D.new();node.name=route.id;root.add_child(node);zones[route.id]=node
 for row:Dictionary in plan.parts:
  var key:String=str(row.zone)+"/"+str(row.role)
  if not grouped.has(key):grouped[key]=[]
  grouped[key].append(row)
 var batch:=0
 for key:String in grouped:
  var rows:Array=grouped[key];var st:=SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES);st.set_material(materials[rows[0].role]);var names:Array=[]
  for row:Dictionary in rows:
   names.append(row.name)
   for face:Array in row.faces:
    for i in range(1,face.size()-1):
     var a:=v(row.verts[face[0]]);var b:=v(row.verts[face[i]]);var c:=v(row.verts[face[i+1]]);var normal:Vector3=(b-a).cross(c-a).normalized()
     for index:int in [face[0],face[i+1],face[i]]:
      var point:=v(row.verts[index]);st.set_normal(normal);st.set_uv(Vector2(point.x,point.z)*.5 if absf(normal.y)>.7 else Vector2(point.z,point.y)*.5);st.add_vertex(point)
  var mesh:=MeshInstance3D.new();mesh.name="ThroughRouteBatch_%03d"%batch;mesh.mesh=st.commit();mesh.set_meta("authored_parts",names);zones[rows[0].zone].add_child(mesh);load("res://scripts/static_contact_cache.gd").attach(mesh);batch+=1
 var lamps:Array[Light3D]=[]
 for route:Dictionary in plan.routes:
  for row:Dictionary in route.lights:
   var light:=SpotLight3D.new();light.name=row.name;zones[route.id].add_child(light);light.position=v(row.position);light.rotation.x=-PI/2;light.spot_angle=65;light.spot_range=row.range;light.light_energy=row.energy;light.light_color=Color(row.color[0],row.color[1],row.color[2]);light.shadow_enabled=true;light.visible=false;light.set_meta("fixture_powered",true);lamps.append(light)
 load("res://scripts/receiving_source_lights.gd").register(lamps,ship)
 var changed:=0
 for path:String in originals:
  var before:Dictionary=originals[path];var mesh:MeshInstance3D=ship.get_node(path)
  if not require_ok(mesh==before.node and mesh.global_transform.is_equal_approx(before.pose),"Original node or pose changed"):return null
  if mesh.mesh!=before.mesh:changed+=1
 for path:String in supports:
  var mesh:MeshInstance3D=ship.get_node(path);var before:Dictionary=supports[path]
  if not require_ok(mesh.mesh==before.mesh and mesh.global_transform.is_equal_approx(before.pose),"Protected bearing changed"):return null
 if not require_ok(changed==plan.wall_preimages.size(),"Only named partition resources may change"):return null
 root.set_meta("retained_gate_bindings",proxies.size());root.set_meta("duplicate_gate_meshes_removed",proxies.size()*21);root.set_meta("original_clinical_meshes",originals.size());root.set_meta("changed_partitions",changed);root.set_meta("new_floor_m2",plan.new_floor_m2);root.set_meta("parts",plan.parts.size());root.set_meta("batches",batch);root.set_meta("new_capacity",0);root.set_meta("clinical_operation_admitted",false);root.set_meta("transfer_junctions_held",true);root.set_meta("visual_accepted",false)
 return root
