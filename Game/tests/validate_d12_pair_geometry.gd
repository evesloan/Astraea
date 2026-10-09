extends SceneTree
var aliases:Dictionary={}
var reverse_aliases:Dictionary={}
const NAME_MAP_SHA="50604ceba9259ba26592de34d5adfc3ddeaf5446f0ce272b68010130c46edab6"
func _initialize()->void:call_deferred("run")
func run()->void:
 var ship:Node3D=load("res://scripts/ship.gd").new()
 var space:=Node3D.new();space.name="ShipSpace";ship.add_child(space)
 var pair:Node3D=load("res://scripts/d12_pair_receiving.gd").build(ship)
 assert(pair.transform==Transform3D.IDENTITY)
 var guard=load("res://tests/medical_triage_successor_guard.gd")

 guard._crew_validate_model(pair.get_node("D12_directory_07/Source"),"D12_directory_07_entry_successor.glb",205)
 var imported0:Node3D=load("res://assets/models/D12_directory_07_entry_successor.glb").instantiate()
 aliases={};reverse_aliases={}
 validate_import(imported0,"D12_directory_07_entry_successor.glb",205)
 validate_normals(imported0,"D12_directory_07_entry_successor.glb")
 imported0.free()
 print("D12_GEOMETRY_PASS D12_directory_07_entry_successor.glb")
 guard._crew_validate_model(pair.get_node("D12_directory_08/Source"),"D12_directory_08_entry_successor.glb",2126)
 var imported1:Node3D=load("res://assets/models/D12_directory_08_entry_successor.glb").instantiate()
 aliases={};reverse_aliases={}
 assert(FileAccess.get_sha256("res://data/architecture/d12_pair/READING_IMPORT_IDENTITY_MAP.json")==NAME_MAP_SHA)
 aliases=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/d12_pair/READING_IMPORT_IDENTITY_MAP.json")).source_to_runtime
 for key in aliases:assert(not reverse_aliases.has(aliases[key]));reverse_aliases[aliases[key]]=key
 validate_import(imported1,"D12_directory_08_entry_successor.glb",2126)
 validate_normals(imported1,"D12_directory_08_entry_successor.glb")
 imported1.free()
 print("D12_GEOMETRY_PASS D12_directory_08_entry_successor.glb")
 guard._crew_validate_model(pair.get_node("AuthoredReceivingGuards"),"AST-RCV-D12-PAIR-001.glb",116)
 var imported2:Node3D=load("res://assets/models/AST-RCV-D12-PAIR-001.glb").instantiate()
 aliases={};reverse_aliases={}
 validate_import(imported2,"AST-RCV-D12-PAIR-001.glb",116)
 validate_normals(imported2,"AST-RCV-D12-PAIR-001.glb")
 imported2.free()
 print("D12_GEOMETRY_PASS AST-RCV-D12-PAIR-001.glb")
 ship.free()
 print("PASS: D12 production loader exact raw-source imported positions/UV/winding/normal storage/materials and mesh-exact static contacts; full-scene walking separate")
 quit()

func validate_import(source: Node3D, filename: String, mesh_count: int) -> void:
 var guard=load("res://tests/medical_triage_successor_guard.gd")
 var actual: Dictionary={}
 for node in source.find_children("*","Node3D",true,false):
  var source_name:String=str(reverse_aliases.get(str(node.name),str(node.name)))
  assert(not actual.has(source_name));actual[source_name]=node
 # Decode the pinned GLB independently; a second imported template alone cannot
 # establish that the importer preserved the source's actual position/UV arrays.
 var blob:=FileAccess.get_file_as_bytes("res://assets/models/"+filename)
 assert(blob.decode_u32(0)==0x46546c67 and blob.decode_u32(4)==2 and blob.decode_u32(8)==blob.size())
 var json_size:=int(blob.decode_u32(12))
 assert(blob.decode_u32(16)==0x4e4f534a)
 var document: Dictionary=JSON.parse_string(blob.slice(20,20+json_size).get_string_from_utf8())
 var binary_start:=20+json_size
 var binary_size:=int(blob.decode_u32(binary_start))
 assert(blob.decode_u32(binary_start+4)==0x004e4942 and binary_start+8+binary_size==blob.size())
 var binary:=blob.slice(binary_start+8)
 assert(document.nodes.size()==actual.size())
 var parents: Dictionary={}
 for index in range(document.nodes.size()):
  for child in document.nodes[index].get("children",[]):
   assert(not parents.has(int(child)),"Derivative source must be a unique-parent tree")
   parents[int(child)]=index
 var source_triangles:=0
 var source_meshes:=0
 var material_seen: Dictionary={}
 for index in range(document.nodes.size()):
  var record: Dictionary=document.nodes[index]
  var name_key:=str(record.name)
  assert(actual.has(name_key),"Every original identity and generated batch must survive import")
  var node: Node3D=actual[name_key] as Node3D
  assert(node!=null)
  var parent: Node=source if not parents.has(index) else actual[str(document.nodes[int(parents[index])].name)]
  assert(node.get_parent()==parent,"Exact source parentage must survive import")
  assert(node.position==guard._team_lounge_v(record.get("translation",[0,0,0])),"Exact source local translation must survive import")
  if not record.has("mesh"): continue
  assert(node is MeshInstance3D)
  var visual: MeshInstance3D=node as MeshInstance3D
  var expected_mesh: Dictionary=document.meshes[int(record.mesh)]
  assert(visual.mesh.get_surface_count()==expected_mesh.primitives.size())
  source_meshes+=1
  for surface in range(expected_mesh.primitives.size()):
   var primitive: Dictionary=expected_mesh.primitives[surface]
   assert(int(primitive.get("mode",4))==4 and primitive.attributes.has("POSITION") and primitive.attributes.has("TEXCOORD_0"))
   var position_accessor:Dictionary=guard._team_lounge_accessor(document,binary,int(primitive.attributes.POSITION))
   var uv_accessor:Dictionary=guard._team_lounge_accessor(document,binary,int(primitive.attributes.TEXCOORD_0))
   assert(position_accessor.type=="VEC3" and uv_accessor.type=="VEC2" and position_accessor.component_type==5126 and uv_accessor.component_type==5126)
   assert(position_accessor.count==uv_accessor.count)
   var positions: PackedFloat32Array=position_accessor.bytes.to_float32_array()
   var uvs: PackedFloat32Array=uv_accessor.bytes.to_float32_array()
   var indices:PackedInt32Array=guard._team_lounge_source_indices(document,binary,primitive,int(position_accessor.count))
   assert(indices.size()%3==0)
   var keys: Array[String]=[]
   keys.resize(int(position_accessor.count))
   for vertex in range(keys.size()): keys[vertex]=guard._team_lounge_corner_key(Vector3(positions[vertex*3],positions[vertex*3+1],positions[vertex*3+2]),Vector2(uvs[vertex*2],uvs[vertex*2+1]))
   var expected: Dictionary={}
   for start in range(0,indices.size(),3):
    # glTF counter-clockwise winding is reversed by Godot's importer.
    var corners: Array[String]=[keys[indices[start]],keys[indices[start+2]],keys[indices[start+1]]]
    var key:String=guard._team_lounge_oriented_triangle(corners)
    expected[key]=int(expected.get(key,0))+1
   assert(guard._team_lounge_import_surface(visual.mesh,surface)==expected,"Exact derivative position/UV/winding/multiplicity must survive; no degenerate-face exemption")
   source_triangles+=int(indices.size()/3)
   var material_index:=int(primitive.material)
   var material: Material=visual.get_active_material(surface)
   assert(material!=null and material.resource_name==str(document.materials[material_index].name),"Exact source material assignment required")
   if material_seen.has(material_index): assert(material_seen[material_index]==material)
   else: material_seen[material_index]=material
 assert(source_meshes==mesh_count)
 if mesh_count==1290: assert(source_triangles==191456)

func normal_keys(mesh:Mesh,surface:int)->Dictionary:
 var a:Array=mesh.surface_get_arrays(surface)
 var order:PackedInt32Array=a[Mesh.ARRAY_INDEX]
 if order.is_empty():
  for i in range(a[Mesh.ARRAY_VERTEX].size()):order.append(i)
 var keys:Array[String]=[]
 for i in range(a[Mesh.ARRAY_VERTEX].size()):
  keys.append(var_to_bytes(a[Mesh.ARRAY_VERTEX][i]).hex_encode()+":"+var_to_bytes(a[Mesh.ARRAY_NORMAL][i]).hex_encode()+":"+var_to_bytes(a[Mesh.ARRAY_TEX_UV][i]).hex_encode())
 var result:Dictionary={}
 var guard=load("res://tests/medical_triage_successor_guard.gd")
 for start in range(0,order.size(),3):
  var corners:Array[String]=[keys[order[start]],keys[order[start+1]],keys[order[start+2]]]
  var key:String=guard._team_lounge_oriented_triangle(corners)
  result[key]=int(result.get(key,0))+1
 return result
func validate_normals(source:Node3D,file:String)->void:
 var guard=load("res://tests/medical_triage_successor_guard.gd")
 var blob:Dictionary=guard._sports_sign_glb(file)
 var doc:Dictionary=blob.document
 for n in doc.nodes:
  if not n.has("mesh"):continue
  var actual:MeshInstance3D=source.find_child(str(aliases.get(str(n.name),str(n.name))),true,false)
  assert(actual!=null)
  assert(not n.has("matrix"),"Explicit matrix source needs its own exact decoder")
  var q:Array=n.get("rotation",[0.0,0.0,0.0,1.0])
  var scale_data:Array=n.get("scale",[1.0,1.0,1.0])
  var pos:Array=n.get("translation",[0.0,0.0,0.0])
  var expected_transform:=Transform3D(Basis(Quaternion(q[0],q[1],q[2],q[3])).scaled(Vector3(scale_data[0],scale_data[1],scale_data[2])),Vector3(pos[0],pos[1],pos[2]))
  assert(actual.transform==expected_transform,"Exact source transform mismatch: "+file+"/"+str(n.name))
  var primitives:Array=doc.meshes[int(n.mesh)].primitives
  for surface in range(primitives.size()):
   var prim:Dictionary=primitives[surface]
   var pa:Dictionary=guard._team_lounge_accessor(doc,blob.binary,int(prim.attributes.POSITION))
   var na:Dictionary=guard._team_lounge_accessor(doc,blob.binary,int(prim.attributes.NORMAL))
   var ua:Dictionary=guard._team_lounge_accessor(doc,blob.binary,int(prim.attributes.TEXCOORD_0))
   var pv:PackedFloat32Array=pa.bytes.to_float32_array()
   var nv:PackedFloat32Array=na.bytes.to_float32_array()
   var uv:PackedFloat32Array=ua.bytes.to_float32_array()
   var positions:=PackedVector3Array();var normals:=PackedVector3Array();var uvs:=PackedVector2Array()
   for i in range(int(pa.count)):
    positions.append(Vector3(pv[i*3],pv[i*3+1],pv[i*3+2]))
    normals.append(Vector3(nv[i*3],nv[i*3+1],nv[i*3+2]))
    uvs.append(Vector2(uv[i*2],uv[i*2+1]))
   var order:PackedInt32Array=guard._team_lounge_source_indices(doc,blob.binary,prim,int(pa.count))
   for i in range(0,order.size(),3):
    var swap:int=order[i+1];order[i+1]=order[i+2];order[i+2]=swap
   var arrays:Array=[];arrays.resize(Mesh.ARRAY_MAX)
   arrays[Mesh.ARRAY_VERTEX]=positions;arrays[Mesh.ARRAY_NORMAL]=normals;arrays[Mesh.ARRAY_TEX_UV]=uvs;arrays[Mesh.ARRAY_INDEX]=order
   var expected:=ArrayMesh.new()
   expected.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
   assert(normal_keys(actual.mesh,surface)==normal_keys(expected,0),"Source normal storage-equivalence mismatch: "+file+"/"+str(n.name)+"/"+str(surface))
