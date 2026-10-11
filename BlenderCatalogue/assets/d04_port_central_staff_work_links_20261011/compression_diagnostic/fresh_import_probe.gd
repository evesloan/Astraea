extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 var constants:Dictionary={}
 for name in ClassDB.class_get_integer_constant_list("EditorSceneFormatImporter"):
  if "COMPRESSION"in name:constants[name]=ClassDB.class_get_integer_constant("EditorSceneFormatImporter",name)
 print("COMPRESSION_CONSTANTS ",constants)
 assert(constants.size()==1)
 var doc:=GLTFDocument.new();var state:=GLTFState.new();var err:=doc.append_from_file("/tmp/astraea_court_mesh_compression_probe/source.glb",state,8);assert(err==OK)
 var source:Node3D=doc.generate_scene(state);root.add_child(source);var rows:Dictionary={}
 for name in ["PCK_D04HC3_east_Soil_1","PCK_D04HC3_east_Planter_1","PCK_D04HC3_east_LeafMass_1_0","PCK_D04HC3_east_LeafMass_1_1","PCK_D04HC3_east_LeafMass_1_2"]:
  var mesh:MeshInstance3D=source.find_child(name,true,false);assert(mesh!=null);var faces:Array=[]
  for v in mesh.mesh.get_faces():var p:Vector3=mesh.global_transform*v;faces.append([p.x,p.y,p.z])
  rows[name]=faces
 FileAccess.open("/tmp/astraea_court_mesh_compression_probe/fresh_import_faces.json",FileAccess.WRITE).store_string(JSON.stringify({"flags":constants,"source_sha256":FileAccess.get_sha256("/tmp/astraea_court_mesh_compression_probe/source.glb"),"faces":rows},"  "));quit()
