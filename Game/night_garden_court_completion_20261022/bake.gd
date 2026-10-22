extends SceneTree
const P:="res://night_garden_court_completion_20261022/"
func _initialize()->void:call_deferred("run")
func own(node:Node,owner:Node)->void:
 for child in node.get_children():child.owner=owner;own(child,owner)
func run()->void:
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_R002.json"))
 assert(FileAccess.get_sha256("res://"+str(d.runtime))==str(d.runtime_sha256))
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://"+str(d.runtime),state)==OK)
 var scene:=doc.generate_scene(state);scene.name="NightGardenReceivingCourts20261022"
 var contacts:=0
 for mesh:MeshInstance3D in scene.find_children("*","MeshInstance3D",true,false):
  var extra:Dictionary=mesh.get_meta("extras",{})
  if not bool(extra.get("physical_contact",false)):continue
  mesh.create_trimesh_collision();contacts+=1
 own(scene,scene);var pack:=PackedScene.new();assert(pack.pack(scene)==OK)
 var path:=P+"runtime/ResortCourts_r002.scn";assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(pack,path)==OK)
 var out:=FileAccess.open(P+"evidence/BAKE.json",FileAccess.WRITE);out.store_string(JSON.stringify({"scene":path,"sha256":FileAccess.get_sha256(path),"contacts":contacts,"source_sha256":d.runtime_sha256},"\t")+"\n");out.close();scene.free();print("RESORT_BAKED ",contacts);quit()
