extends SceneTree
const P:="res://night_garden_receiving_courts_20261022/"
func _initialize()->void:call_deferred("run")
func own(node:Node,owner:Node)->void:
 for child in node.get_children():child.owner=owner;own(child,owner)
func run()->void:
 var d:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/ENTRANCES.json"))
 assert(FileAccess.get_sha256("res://"+str(d.runtime))==d.runtime_sha256)
 var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://"+str(d.runtime),state)==OK)
 var scene:=doc.generate_scene(state);scene.name="NightGardenD15CourtEntrances_r004"
 var meshes:=scene.find_children("*","MeshInstance3D",true,false)
 var solids:Array[Node]=[]
 for mesh:MeshInstance3D in meshes:
  var extra:Dictionary=mesh.get_meta("extras",{})
  if str(extra.get("material_role",""))=="hospitality_glass":
   var glass:=ShaderMaterial.new();glass.shader=load("res://shaders/hospitality_glass.gdshader");mesh.material_override=glass
  if str(mesh.name).begins_with("NGRC_") or (bool(extra.get("runtime_collision",false)) and str(extra.get("collision_policy",""))!="no_collision_detail"):solids.append(mesh)
 load("res://scripts/static_contact_cache.gd").attach_group(scene,solids)
 var contacts:=scene.find_children("*","StaticBody3D",true,false).size()
 own(scene,scene)
 var pack:=PackedScene.new();assert(pack.pack(scene)==OK)
 var path:=P+"runtime/CourtEntrances_r004_policy.scn";assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(pack,path)==OK)
 var out:=FileAccess.open(P+"evidence/ENTRANCES_BAKE_POLICY.json",FileAccess.WRITE);out.store_string(JSON.stringify({"scene":path,"sha256":FileAccess.get_sha256(path),"contacts":contacts,"source_sha256":d.runtime_sha256},"\t")+"\n");out.close()
 scene.free();print("RECEIVING_BAKED ",contacts);quit()
