extends SceneTree
const P="res://night_garden_view_galleries_20261022/"
func _initialize():call_deferred("run")
func own(n:Node,top:Node):
 for c in n.get_children():c.owner=top;own(c,top)
func run():
 var receipt:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(P+"evidence/BUILD_r002.json"))
 var baseline:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_garden_partition_20261021/index.json")).rooms
 var records:Dictionary={}
 DirAccess.make_dir_recursive_absolute(P+"runtime/shells")
 for row in receipt.rooms:
  var old:Dictionary=baseline[row.model_file]
  assert(FileAccess.get_sha256(old.shell_path)==old.shell_sha256)
  assert(FileAccess.get_sha256("res://"+row.export)==row.export_sha256)
  var shell:Node3D=load(old.shell_path).instantiate();root.add_child(shell)
  var doc:=GLTFDocument.new();var state:=GLTFState.new();assert(doc.append_from_file("res://"+row.export,state)==OK)
  var source:Node3D=doc.generate_scene(state);root.add_child(source)
  var before:MeshInstance3D=shell.find_child(row.batch,true,false)
  var after:MeshInstance3D=source.find_child(row.batch,true,false)
  assert(before!=null and after!=null)
  before.mesh=after.mesh;before.global_transform=after.global_transform
  var additions:=0
  for m:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
   if m==after:continue
   assert(str(m.name).begins_with("NVG_"))
   var copy:MeshInstance3D=m.duplicate();shell.add_child(copy);copy.global_transform=m.global_transform;additions+=1
  assert(additions==5)
  own(shell,shell)
  var packed:=PackedScene.new();assert(packed.pack(shell)==OK)
  var path:=P+"runtime/shells/NG"+str(int(row.index))+"_ViewShell_r002.scn"
  assert(not FileAccess.file_exists(path));assert(ResourceSaver.save(packed,path)==OK)
  records[row.model_file]={"original_shell_sha256":old.shell_sha256,"shell_path":path,"shell_sha256":FileAccess.get_sha256(path),"rear_x":row.rear_x,"interior_sign":row.interior_sign,"index":row.index,"private_detail_sha256":old.detail_sha256}
  shell.free();source.free()
 assert(records.size()==16)
 var f:=FileAccess.open(P+"evidence/DERIVED_SHELLS.json",FileAccess.WRITE);f.store_string(JSON.stringify(records,"  ")+"\n");f.close()
 print("VIEW_SHELLS 16 derived; original30 shells and detail files preserved")
 quit()
