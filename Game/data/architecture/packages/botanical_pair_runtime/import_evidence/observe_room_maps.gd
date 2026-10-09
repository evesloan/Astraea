extends SceneTree
func _initialize()->void:
 call_deferred("_run")
func _run()->void:
 var args:=OS.get_cmdline_user_args()
 assert(args.size()==2)
 var filename:=args[0]
 var output:=args[1]
 var path:="res://assets/models/"+filename
 var state:=GLTFState.new()
 var document:=GLTFDocument.new()
 var result:=document.append_from_file(path,state)
 assert(result==OK,"Raw GLTF importer could not load pinned asset")
 var observed:=document.generate_scene(state)
 assert(observed!=null)
 var packed:PackedScene=load(path)
 assert(packed!=null)
 var actual:=packed.instantiate()
 var raw:Dictionary=state.json
 var mapping:Dictionary={}
 var evidence:Array=[]
 var used:Dictionary={}
 var mesh_nodes:=0
 var surfaces:=0
 var actual_nodes:=actual.find_children("*","Node3D",true,false)
 print("MAP_DIAGNOSTIC raw=",raw.nodes.size()," actual=",actual_nodes.size()," generated=",observed.find_children("*","Node3D",true,false).size()," actualroot=",actual.name," generatedroot=",observed.name)
 for node in actual_nodes:
  var counterpart:=observed.get_node_or_null(actual.get_path_to(node))
  if counterpart==null:print("ACTUAL_ONLY ",actual.get_path_to(node)," class=",node.get_class())
 assert(actual_nodes.size()==raw.nodes.size(),"Actual PackedScene node count differs from raw glTF")
 for index in range(raw.nodes.size()):
  var source_name:=str(raw.nodes[index].name)
  var gltf_node:GLTFNode=state.get_nodes()[index]
  assert(gltf_node.original_name==source_name,"Importer original node-index identity changed")
  var components:Array[String]=[gltf_node.resource_name]
  var parent_index:int=gltf_node.parent
  while parent_index>=0:
   components.push_front(state.get_nodes()[parent_index].resource_name)
   parent_index=state.get_nodes()[parent_index].parent
  var nodepath:=NodePath("/".join(components))
  var generated:Node=observed.get_node_or_null(nodepath)
  assert(generated!=null,"Missing importer node-index identity")
  var imported:Node=actual.get_node_or_null(nodepath)
  assert(imported!=null,"Actual PackedScene lacks observed importer path")
  assert(imported.get_class()==generated.get_class(),"Observed importer node class differs")
  assert(imported is Node3D and generated is Node3D)
  assert(imported.transform==generated.transform,"Observed importer node transform differs")
  assert(str(imported.name)==str(generated.name))
  assert(not used.has(str(imported.name)),"Runtime node names are not bijective")
  assert(not mapping.has(source_name),"Duplicate raw source name")
  mapping[source_name]=str(imported.name);used[str(imported.name)]=true
  if imported is MeshInstance3D:
   mesh_nodes+=1
   surfaces+=imported.mesh.get_surface_count()
  evidence.append({"source_index":index,"source_name":source_name,"importer_node_path":str(nodepath),"actual_runtime_name":str(imported.name),"actual_class":str(imported.get_class())})
 var receipt:={"schema":1,"source_sha256":FileAccess.get_sha256(path),"godot_version":str(Engine.get_version_info().string),"import_settings_sha256":FileAccess.get_sha256(path+".import"),"source_to_runtime":mapping,"method":"GLTFState.get_nodes()[raw node index] original_name/resource_name/parent observed importer identity, matched against actual saved PackedScene by exact hierarchy path, class, transform and name; no generic name normalization","actual_nodes":actual_nodes.size(),"mesh_nodes":mesh_nodes,"material_surfaces":surfaces,"node_index_evidence":evidence}
 var file:=FileAccess.open(output,FileAccess.WRITE)
 assert(file!=null)
 file.store_string(JSON.stringify(receipt,"  ")+"\n");file.close()
 actual.free();observed.free()
 print("PASS: actual importer node-index map ",filename," nodes=",mapping.size()," meshes=",mesh_nodes," surfaces=",surfaces)
 quit(0)
