extends SceneTree
const P:="res://atrium_terrace_inhabitation_20261022/"
func _initialize()->void:call_deferred("run")
func own(node:Node,owner:Node)->void:
 for child in node.get_children():child.owner=owner;own(child,owner)
func bake(receipt:String,name:String,path:String)->Dictionary:
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/"+receipt))
 assert(FileAccess.get_sha256("res://"+str(d.runtime))==str(d.runtime_sha256))
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://"+str(d.runtime),state)==OK)
 var scene:=doc.generate_scene(state);scene.name=name;var contacts:=0
 for mesh:MeshInstance3D in scene.find_children("*","MeshInstance3D",true,false):
  if bool(mesh.get_meta("extras",{}).get("physical_contact",false)):mesh.create_trimesh_collision();contacts+=1
 own(scene,scene);var pack:=PackedScene.new();assert(pack.pack(scene)==OK);assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(pack,path)==OK)
 var row:={"scene":path,"sha256":FileAccess.get_sha256(path),"source_sha256":d.runtime_sha256,"contact_meshes":contacts};scene.free();return row
func run()->void:
 var rows:={"terraces":bake("BUILD.json","UpperAtriumTerraceInhabitation20261022",P+"runtime/UpperAtriumInhabitation_r001.scn"),"ceiling":bake("CEILING_BUILD.json","AtriumLanternCeiling20261022",P+"runtime/AtriumLanternCeiling_r002.scn")}
 var out:=FileAccess.open(P+"evidence/BAKE.json",FileAccess.WRITE);out.store_string(JSON.stringify(rows,"\t")+"\n");out.close();print("TERRACE_AND_CEILING_BAKED ",JSON.stringify(rows));quit()
