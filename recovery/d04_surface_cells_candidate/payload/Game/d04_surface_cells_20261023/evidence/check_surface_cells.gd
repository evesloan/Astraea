extends SceneTree
func _initialize()->void:call_deferred("run")
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var helper=load("res://d04_surface_cells_20261023/batcher.gd")
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://d04_detail_batches_20261022/runtime_r004/INDEX.json"));var rows:Array=[]
 for file:String in index.rooms:
  var scene:Node3D=load(index.rooms[file].detail_path).instantiate();root.add_child(scene)
  var ids:Dictionary={}
  for n:MeshInstance3D in scene.find_children("*","MeshInstance3D",true,false):ids[n.get_instance_id()]={"mesh":n.mesh,"transform":n.global_transform,"visible":n.visible,"shadow":n.cast_shadow}
  var before_contacts:=scene.find_children("*","CollisionObject3D",true,false).size();var start:=Time.get_ticks_usec()
  var result:Dictionary=helper.build(scene,[])
  helper.set_enabled(scene,true)
  for group:Dictionary in result.groups:
   assert(group.bounds.size[group.bounds.size.max_axis_index()]<=4.0)
   for member:Dictionary in group.members:assert(ids.has(member.node.get_instance_id()))
   assert(group.batch.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_OFF)
  helper.set_enabled(scene,false)
  for id:int in ids:
   var n:MeshInstance3D=instance_from_id(id);assert(n!=null and n.mesh==ids[id].mesh and n.global_transform==ids[id].transform and n.visible==ids[id].visible and n.cast_shadow==ids[id].shadow)
  assert(scene.find_children("*","CollisionObject3D",true,false).size()==before_contacts)
  rows.append({"file":file,"source_meshes":result.source_meshes,"saved_submissions":result.saved_submissions,"batches":result.batch_count,"triangles":result.triangles_reencoded,"build_us":Time.get_ticks_usec()-start,"original_nodes_meshes_transforms_visibility_contacts_preserved":true});scene.free()
 var f:=FileAccess.open("/tmp/d04_surface_cells_check.json",FileAccess.WRITE);f.store_string(JSON.stringify({"status":"PASS","scope":"All120 retained D04 details; no lights fixture upper bound, not whole ship performance","rows":rows},"  "));f.close();print("SURFACE_CELLS_PASS ",rows.size());quit()
