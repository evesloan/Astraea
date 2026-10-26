extends SceneTree
const DEST:="res://precompiled_private_cells_20261026/family_r002/"
var output:String
var copies:Dictionary={}
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func independent(r:Resource)->Resource:
 if r==null:return null
 var id:=r.get_instance_id()
 if not copies.has(id):copies[id]=r.duplicate(true)
 return copies[id]
func own(node:Node,top:Node)->void:
 node.scene_file_path=""
 if node is MeshInstance3D and node.mesh!=null:
  node.mesh=independent(node.mesh);node.material_override=independent(node.material_override)
  for surface in node.mesh.get_surface_count():node.set_surface_override_material(surface,independent(node.get_surface_override_material(surface)))
  if node.has_meta("precompiled_fallback"):
   for row:Array in node.get_meta("precompiled_fallback"):row[1]=independent(row[1]);row[2]=independent(row[2])
 for child:Node in node.get_children():child.owner=top;own(child,top)
func run()->void:
 var index_path:="res://family_specialty_bank_20261022/evidence/INDEX_R002.json"
 var records:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(index_path)).rooms
 var manager:Node=load("res://scripts/night_garden_residency_20261022/manager.gd").new()
 var rows:Array=[]
 for file:String in records:
  var record:Dictionary=records[file]
  assert(FileAccess.get_sha256(record.detail_path)==record.detail_sha256)
  var detail:Node3D=load(str(record.detail_path)).instantiate();root.add_child(detail)
  var before_nodes:=detail.find_children("*","",true,false).size()+1
  var before_meshes:=0
  for mesh:MeshInstance3D in detail.find_children("*","MeshInstance3D",true,false):
   if mesh.mesh!=null:
    assert(str(detail.get_path_to(mesh)) in record.detail_mesh_paths)
    before_meshes+=1
  assert(before_meshes==record.detail_mesh_paths.size())
  manager.contacts(detail)
  var contacts:Array=[]
  for shape:CollisionShape3D in detail.find_children("*","CollisionShape3D",true,false):contacts.append([shape,shape.shape,shape.global_transform])
  var compiled:Dictionary=load("res://precompiled_private_cells_20261026/merge.gd").build(detail,[])
  var freed:=0
  for group:Dictionary in compiled.groups:
   group.batch.visible=true
   for member:Dictionary in group.members:
    var mesh:MeshInstance3D=member.node
    assert(load("res://precompiled_bank_cells_20261026/compiler.gd").safe_contact(mesh))
    assert(mesh.get_child_count()==0,"Private opaque contacts must remain on original independent room owner")
    mesh.free();freed+=1
  for contact:Array in contacts:assert(is_instance_valid(contact[0]) and contact[0].shape==contact[1] and contact[0].global_transform==contact[2])
  detail.remove_meta("surface_cells");compiled.erase("groups")
  detail.set_meta("precompiled_private_source",record.detail_path)
  detail.set_meta("precompiled_private_source_sha256",record.detail_sha256)
  var path:=DEST+file.get_basename()+".scn";assert(not FileAccess.file_exists(path))
  own(detail,detail)
  var packed:=PackedScene.new();assert(packed.pack(detail)==OK)
  assert(ResourceSaver.save(packed,path,ResourceSaver.FLAG_COMPRESS)==OK)
  var row:Dictionary={"model_file":file,"room_id":record.room_id,"source":record.detail_path,"source_sha256":record.detail_sha256,"compiled":path,"sha256":FileAccess.get_sha256(path),"before_nodes":before_nodes,"after_nodes":detail.find_children("*","",true,false).size()+1,"source_meshes":before_meshes,"freed_visual_nodes":freed,"contact_shapes_preserved":contacts.size(),"compilation":compiled}
  rows.append(row);print("PRIVATE_PRECOMPILED_ROOM ",JSON.stringify(row))
  detail.free();packed=null;copies.clear();contacts.clear()
  await process_frame
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"index":index_path,"index_sha256":FileAccess.get_sha256(index_path),"rows":rows,"status":"UNSELECTED; reload, exact geometry/contact, current-light and presentation checks pending"},"\t"));f.close()
 manager.free();quit()
