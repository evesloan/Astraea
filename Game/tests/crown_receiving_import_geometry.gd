extends SceneTree
func _initialize()->void:
 call_deferred("run")
func run()->void:
 var ship:Node3D=load("res://scripts/ship.gd").new()
 var district:=Node3D.new()
 root.add_child(district)
 load("res://scripts/central_command_crown.gd").build(district,ship)
 await physics_frame
 await physics_frame
 var crown:Node=district.get_node("CentralCommandCrown_WIP")
 assert(crown!=null)
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/crown_batch/runtime_manifest.json"))
 var guard=load("res://tests/medical_triage_successor_guard.gd")
 for section in data.sections:
  var wrapper:Node3D=crown.get_node("CrownBatchInteriors_SourceOnly/"+str(section.root_name)+"/Source")
  assert(wrapper.transform==Transform3D.IDENTITY)
  guard._crew_validate_model(wrapper,str(section.model_file),int(section.mesh_count))
  var imported:Node3D=(load("res://assets/models/"+str(section.model_file)) as PackedScene).instantiate()
  guard._movement_validate_import(imported,str(section.model_file),int(section.mesh_count))
  validate_normals(imported,str(section.model_file))
  imported.free()
  print("CROWN_GEOMETRY_ROOM_PASS "+str(section.programme_key))
 ship.free()
 print("PASS: Crown actual runtime import positions, UV, winding, source-normal storage equivalence, materials, identities and concave contacts")
 quit()
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
  var actual:MeshInstance3D=source.find_child(str(n.name),true,false)
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
