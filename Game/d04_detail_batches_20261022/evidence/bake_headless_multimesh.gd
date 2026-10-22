extends "res://scripts/startup_residency_20261020/bake_exact_visual.gd"
const OUT := "/workspace/Astraea-recovered-e6274e77-20261021/Game/d04_detail_batches_20261022/runtime_r003/"
const RES := "res://d04_detail_batches_20261022/runtime_r003/"
const GRID_M := 4.0
var canonical:Dictionary={}
var fingerprints:Dictionary={}
var file_receipts:Dictionary={}
func _initialize()->void:call_deferred("run")
func digest(value:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(value);return h.finish().hex_encode()
func identity(value:Variant)->Variant:
 if value is Resource:
  var id:int=value.get_instance_id()
  if fingerprints.has(id):return fingerprints[id]
  var state:Array=[value.get_class()]
  if value is Texture2D:
   var img:Image=value.get_image();assert(img!=null)
   state.append([img.get_width(),img.get_height(),img.get_format(),img.has_mipmaps(),digest(img.get_data())])
  else:
   for p:Dictionary in value.get_property_list():
    if int(p.usage)&PROPERTY_USAGE_STORAGE==0 or str(p.name) in ["resource_path","resource_name","resource_local_to_scene","script"]:continue
    state.append([str(p.name),identity(value.get(p.name))])
  var key:=digest(var_to_bytes(state));fingerprints[id]=key;return key
 if value is Array:
  var result:Array=[]
  for item in value:result.append(identity(item))
  return result
 if value is Dictionary:
  var result:Array=[];var keys:Array=value.keys();keys.sort()
  for key in keys:result.append([key,identity(value[key])])
  return result
 return value
func intern(original:Resource)->Resource:
 if original==null:return null
 var key:String=identity(original)
 if canonical.has(key):return canonical[key]
 var copy:Resource=own_resource(original)
 if copy is ArrayMesh:
  for s in copy.get_surface_count():copy.surface_set_material(s,intern(original.surface_get_material(s)))
  if original.shadow_mesh!=null:copy.shadow_mesh=intern(original.shadow_mesh)
 var file:=OUT+"shared/"+key+".res";assert(not FileAccess.file_exists(file))
 assert(ResourceSaver.save(copy,file,ResourceSaver.FLAG_COMPRESS)==OK)
 # Reference a single named resource; no external reference to the old detail scene.
 copy.take_over_path(RES+"shared/"+key+".res")
 assert(identity(copy)==key)
 canonical[key]=copy;file_receipts[RES+"shared/"+key+".res"]=FileAccess.get_sha256(file)
 return copy
func pose(node:Node3D,top:Node3D)->Transform3D:
 var t:=node.transform;var parent:=node.get_parent()
 while parent!=top:assert(parent is Node3D);t=parent.transform*t;parent=parent.get_parent()
 return t
func opaque(node:MeshInstance3D)->bool:
 if node.mesh==null or not node.mesh is ArrayMesh or node.material_overlay!=null or node.transparency!=0:return false
 for s in node.mesh.get_surface_count():
  var m:=node.get_active_material(s)
  if not m is StandardMaterial3D:return false
  if m.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or m.albedo_color.a<.999 or m.next_pass!=null:return false
 return true
func batchable(node:MeshInstance3D,top:Node3D)->bool:
 if not opaque(node) or node.get_child_count()!=0 or node.mesh.get_blend_shape_count()!=0 or node.skeleton!=NodePath(""):return false
 for s:Dictionary in node.mesh.get("_surfaces"):
  if not s.get("lods",[]).is_empty():return false
 for s in node.mesh.get_surface_count():
  var m:StandardMaterial3D=node.get_active_material(s)
  if m.uv1_triplanar or m.uv2_triplanar or m.billboard_mode!=BaseMaterial3D.BILLBOARD_DISABLED or m.grow:return false
 var ancestor:Node=node
 while ancestor!=top:
  if ancestor is Node3D and not ancestor.visible:return false
  ancestor=ancestor.get_parent()
 return true
func stats(root:Node)->Dictionary:
 var main:={};var shadows:={};var triangles:=0;var render_nodes:=0
 for n:MeshInstance3D in root.find_children("*","MeshInstance3D",true,false):
  if n.mesh==null:continue
  render_nodes+=1;main[n.mesh.get_instance_id()]=true;triangles+=n.mesh.get_faces().size()/3
  if n.mesh is ArrayMesh and n.mesh.shadow_mesh!=null:shadows[n.mesh.shadow_mesh.get_instance_id()]=true
 for n:MultiMeshInstance3D in root.find_children("*","MultiMeshInstance3D",true,false):
  render_nodes+=1;main[n.multimesh.mesh.get_instance_id()]=true;triangles+=(n.multimesh.mesh.get_faces().size()/3)*n.multimesh.instance_count
  if n.multimesh.mesh.shadow_mesh!=null:shadows[n.multimesh.mesh.shadow_mesh.get_instance_id()]=true
 return {"nodes":root.find_children("*","",true,false).size()+1,"render_nodes":render_nodes,"meshes":main.size(),"shadows":shadows.size(),"triangles":triangles}
func run()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var input:="res://data/architecture/startup_residency_20261020/private_shells_d04.json"
 assert(FileAccess.get_sha256(input)=="4f41f4c70165883e6789174225ed2a6172b6e659d8302b586434a68488cdbfdb")
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(input));var reports:Array=[]
 for file:String in index.rooms:
  var row:Dictionary=index.rooms[file];assert(FileAccess.get_sha256(row.detail_path)==row.detail_sha256)
  var scene:PackedScene=load(row.detail_path);var source:Node3D=scene.instantiate();var output:Node3D=source.duplicate(7);output.scene_file_path=""
  fingerprints.clear();owned_resources.clear();source_model_path=row.detail_path
  var before:=stats(source);var bins:Dictionary={};var mapping:Array=[];var removed_placeholders:=0
  for n:Node in output.find_children("*","",true,false):assert(n is Node3D and n.get_script()==null)
  for node:MeshInstance3D in output.find_children("*","MeshInstance3D",true,false):
   if node.mesh==null:
    if node.get_child_count()==0:node.free();removed_placeholders+=1
    continue
   if opaque(node):
    node.mesh=intern(node.mesh)
    if node.material_override!=null:node.material_override=intern(node.material_override)
    for s in node.mesh.get_surface_count():
     if node.get_surface_override_material(s)!=null:node.set_surface_override_material(s,intern(node.get_surface_override_material(s)))
   else:
    node.mesh=own_resource(node.mesh)
    if node.material_override!=null:node.material_override=own_resource(node.material_override)
   if not batchable(node,output):continue
   var state:Array=[]
   for property:String in DRAW_PROPERTIES:state.append(node.get(property))
   var override_keys:Array=[identity(node.material_override)]
   for s in node.mesh.get_surface_count():override_keys.append(identity(node.get_surface_override_material(s)))
   var transform:=pose(node,output);var bounds:AABB=transform*node.get_aabb();var center:=bounds.get_center();var cell:=Vector3i(floori(center.x/GRID_M),floori(center.y/GRID_M),floori(center.z/GRID_M))
   var key:=str(identity(node.mesh))+":"+digest(var_to_bytes(override_keys))+":"+digest(var_to_bytes(state))+":"+str(cell)
   if not bins.has(key):bins[key]={"nodes":[],"state":state,"bounds":bounds}
   # No batch exceeds the cell envelope; retain pieces that would enlarge it.
   var merged:AABB=bins[key].bounds.merge(bounds)
   if merged.size[merged.size.max_axis_index()]>GRID_M:continue
   bins[key].nodes.append(node);bins[key].bounds=merged
  var batch_checks:Array=[]
  for key:String in bins:
   var bin:Dictionary=bins[key]
   if bin.nodes.size()<2:continue
   var first:MeshInstance3D=bin.nodes[0]
   # MultiMesh has one material_override; per-surface overrides stay separate.
   var has_surface_override:=false
   for s in first.mesh.get_surface_count():
    if first.get_surface_override_material(s)!=null:has_surface_override=true
   if has_surface_override:continue
   var multi:=MultiMesh.new();multi.transform_format=MultiMesh.TRANSFORM_3D;multi.mesh=first.mesh;multi.instance_count=bin.nodes.size()
   var batch:=MultiMeshInstance3D.new();batch.name="D04RepeatedOpaque_%04d"%batch_checks.size();batch.multimesh=multi;batch.material_override=first.material_override
   for i in DRAW_PROPERTIES.size():batch.set(DRAW_PROPERTIES[i],bin.state[i])
   var members:Array=[]
   for i in bin.nodes.size():
    var node:MeshInstance3D=bin.nodes[i];var t:=pose(node,output);multi.set_instance_transform(i,t)
    members.append({"path":str(output.get_path_to(node)),"transform":var_to_str(t),"extras":var_to_str(node.get_meta("extras",{}))})
   output.add_child(batch);batch.owner=output
   batch_checks.append({"name":str(batch.name),"members":members,"mesh_signature":identity(first.mesh),"material_signature":identity(first.material_override),"state":bin.state})
   mapping.append({"batch":str(batch.name),"members":members,"bounds":var_to_str(bin.bounds)})
   for node:MeshInstance3D in bin.nodes:node.free()
  for n:Node in output.find_children("*","",true,false):n.owner=output
  var name:=file.trim_suffix(".glb")+".detail.scn";var target:=OUT+name;assert(not FileAccess.file_exists(target))
  var saved:=PackedScene.new();assert(saved.pack(output)==OK);assert(ResourceSaver.save(saved,target,ResourceSaver.FLAG_COMPRESS)==OK)
  var check_scene:PackedScene=ResourceLoader.load(target,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);var check:Node3D=check_scene.instantiate()
  for node:MeshInstance3D in check.find_children("*","MeshInstance3D",true,false):
   if node.mesh==null:continue
   var prior:MeshInstance3D=source.get_node(check.get_path_to(node));assert(prior!=null)
   assert(pose(node,check)==pose(prior,source));assert(identity(node.mesh)==identity(prior.mesh));assert(identity(node.material_override)==identity(prior.material_override))
   for p:String in DRAW_PROPERTIES:assert(identity(node.get(p))==identity(prior.get(p)))
   for s in node.mesh.get_surface_count():assert(identity(node.get_surface_override_material(s))==identity(prior.get_surface_override_material(s)))
  for entry:Dictionary in batch_checks:
   var node:MultiMeshInstance3D=check.get_node(entry.name);assert(identity(node.multimesh.mesh)==entry.mesh_signature);assert(identity(node.material_override)==entry.material_signature)
   for i in entry.members.size():assert(node.multimesh.get_instance_transform(i).is_equal_approx(str_to_var(entry.members[i].transform)))
   for i in DRAW_PROPERTIES.size():assert(identity(node.get(DRAW_PROPERTIES[i]))==identity(entry.state[i]))
  var after:=stats(check);assert(after.triangles==before.triangles and after.nodes<before.nodes)
  reports.append({"model":file,"room_id":row.room_id,"input_path":row.detail_path,"input_sha256":row.detail_sha256,"output_sha256":FileAccess.get_sha256(target),"before":before,"after":after,"removed_null_shell_placeholders":removed_placeholders,"multimesh_batches":batch_checks.size(),"source_to_batch":mapping})
  row.detail_path=RES+name;row.detail_sha256=FileAccess.get_sha256(target)
  check.free();output.free();source.free();owned_resources.clear();fingerprints.clear();bins.clear();batch_checks.clear();scene=null;saved=null;check_scene=null
  print("D04_EXACT_ROOM ",reports.size(),"/120 shared_resources=",canonical.size()," nodes ",before.nodes," -> ",after.nodes)
  await process_frame
 var f:=FileAccess.open(OUT+"INDEX.json",FileAccess.WRITE);f.store_string(JSON.stringify(index,"  "));f.close()
 f=FileAccess.open(OUT+"BAKE.json",FileAccess.WRITE);f.store_string(JSON.stringify({"rooms":reports,"shared_resource_files":file_receipts,"cell_limit_m":GRID_M,"mesh_buffers_reencoded":false,"lod_and_shadow_resources_preserved":true,"original_node_and_contact_policy_unchanged":true,"runtime_acceptance":false},"  "));f.close();quit()
