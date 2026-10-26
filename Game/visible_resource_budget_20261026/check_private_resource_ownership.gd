extends SceneTree
var output:String
func _initialize()->void:
 for arg:String in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.substr(9)
 call_deferred("run")
func count_resources(roots:Array)->Dictionary:
 var main:Dictionary={};var shadow:Dictionary={};var canonical:Dictionary={};var payload_bytes:=0
 for detail:Node3D in roots:
  var meshes:Array=[]
  for node:MeshInstance3D in detail.find_children("*","MeshInstance3D",true,false):
   if node.mesh!=null:meshes.append(node.mesh)
  for owner:Node3D in detail.find_children("*","Node3D",true,false):
   if owner.get_script()!=null and owner.get_script().resource_path=="res://static_bank_cells_20261026/render_owner.gd":
    for record:Array in owner.records:meshes.append(record[1])
  for mesh:ArrayMesh in meshes:
   main[mesh.get_instance_id()]=true
   if mesh.shadow_mesh==null or shadow.has(mesh.shadow_mesh.get_instance_id()):continue
   shadow[mesh.shadow_mesh.get_instance_id()]=true
   var bytes:PackedByteArray=load("res://group2_resource_lifetime_20261025/shadow_mesh_pool.gd").payload(mesh.shadow_mesh)
   if bytes.is_empty():continue
   payload_bytes+=bytes.size()
   var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(bytes);canonical[hash.finish().hex_encode()]=true
 return {"unique_main_meshes":main.size(),"unique_shadow_meshes":shadow.size(),"exact_unique_shadow_payloads":canonical.size(),"shadow_payload_bytes":payload_bytes}
func run()->void:
 var report:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://precompiled_private_cells_20261026/FAMILY_COMPILE.json"))
 var roots:Array=[]
 for row:Dictionary in report.rows:
  var detail:Node3D=load(str(row.source)).instantiate();root.add_child(detail);roots.append(detail)
 var original:=count_resources(roots)
 for detail:Node3D in roots:detail.free()
 roots.clear();await process_frame;await process_frame
 var lights:Array=[]
 for i in 9:lights.append({"id":i,"kind":1,"mask":1048575,"reach":100000.0,"position":Vector3.ZERO,"managed_eight":false})
 for row:Dictionary in report.rows:
  var detail:Node3D=load(str(row.compiled)).instantiate();root.add_child(detail)
  var selected:Dictionary=load("res://precompiled_bank_cells_20261026/select_lighting.gd").apply(detail,lights)
  assert(selected.merged_cells==0);roots.append(detail)
 var fallback:=count_resources(roots)
 for detail:Node3D in roots:detail.free()
 roots.clear();await process_frame;await process_frame
 var f:=FileAccess.open(output,FileAccess.WRITE);f.store_string(JSON.stringify({"original47":original,"compiled47_exact_fallback":fallback,"scope":"All47 concurrently resident room details, original then compiled exact-fallback path. Synthetic over-capacity lighting selects the same all-fallback mode observed in actual019; no ship/FPS claim. Counts identify candidate resource ownership, not total whole-ship allocation."},"\t"));f.close();quit()
