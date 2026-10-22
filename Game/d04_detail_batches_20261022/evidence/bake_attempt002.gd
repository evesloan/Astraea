extends "res://scripts/startup_residency_20261020/bake_exact_visual.gd"
# Named immutable derivative; original rooms, contacts, shells and native assets remain intact.
const OUTPUT := "/workspace/Astraea-recovered-e6274e77-20261021/Game/d04_detail_batches_20261022/runtime_r002/"
const PREFIX := "res://d04_detail_batches_20261022/runtime_r002/"
const GRID := 4.0
var signatures:Dictionary={}
func _initialize()->void:call_deferred("run_all")
func signature(value:Variant)->Variant:
 if value is Texture2D:
  var img:Image=value.get_image();assert(img!=null)
  return ["texture",img.get_width(),img.get_height(),img.get_format(),img.has_mipmaps(),digest_bytes(img.get_data())]
 if value is Resource:
  var id:int=value.get_instance_id()
  if signatures.has(id):return signatures[id]
  var rows:Array=[value.get_class()]
  for property:Dictionary in value.get_property_list():
   var key:String=property.name
   if int(property.usage)&PROPERTY_USAGE_STORAGE==0 or key in ["resource_path","resource_name","resource_local_to_scene","script"]:continue
   rows.append([key,signature(value.get(key))])
  var result:=digest_bytes(var_to_bytes(rows));signatures[id]=result;return result
 if value is Array:
  var rows:Array=[]
  for item in value:rows.append(signature(item))
  return rows
 if value is Dictionary:
  var rows:Array=[];var keys:Array=value.keys();keys.sort()
  for key in keys:rows.append([key,signature(value[key])])
  return rows
 return value
func digest_bytes(bytes:PackedByteArray)->String:
 var h:=HashingContext.new();h.start(HashingContext.HASH_SHA256);h.update(bytes);return h.finish().hex_encode()
func relative_pose(node:Node3D,top:Node3D)->Transform3D:
 var t:=node.transform;var parent:=node.get_parent()
 while parent!=top:
  assert(parent is Node3D);t=parent.transform*t;parent=parent.get_parent()
 return t
func reason(node:MeshInstance3D,top:Node3D,t:Transform3D)->String:
 if node.mesh==null:return "placeholder"
 if not node.mesh is ArrayMesh or node.mesh.get_surface_count()!=1:return "surface_layout"
 if node.mesh.get_blend_shape_count()!=0 or node.skeleton!=NodePath(""):return "deformation"
 if not t.basis.is_equal_approx(Basis.IDENTITY):return "rotated_or_scaled"
 var ancestor:Node=node
 while ancestor!=top:
  if ancestor is Node3D and not ancestor.visible:return "hidden_ancestor"
  ancestor=ancestor.get_parent()
 if node.material_overlay!=null or node.transparency!=0.0:return "instance_effect"
 if node.cast_shadow not in [GeometryInstance3D.SHADOW_CASTING_SETTING_OFF,GeometryInstance3D.SHADOW_CASTING_SETTING_ON]:return "special_shadow_mode"
 var material:=node.get_active_material(0)
 if not material is StandardMaterial3D:return "custom_material"
 if material.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or material.albedo_color.a<.999:return "transparency"
 if material.uv1_triplanar or material.uv2_triplanar or material.billboard_mode!=BaseMaterial3D.BILLBOARD_DISABLED or material.grow or material.next_pass!=null:return "material_local_semantics"
 var stored:Array=node.mesh.get("_surfaces")
 if not stored[0].get("lods",[]).is_empty():return "existing_lod"
 if node.mesh.surface_get_primitive_type(0)!=Mesh.PRIMITIVE_TRIANGLES:return "primitive"
 if (t*node.get_aabb()).size.max_axis_index()>=0 and (t*node.get_aabb()).size[(t*node.get_aabb()).size.max_axis_index()]>GRID:return "large_object"
 var arrays:Array=node.mesh.surface_get_arrays(0)
 for channel in [Mesh.ARRAY_CUSTOM0,Mesh.ARRAY_CUSTOM1,Mesh.ARRAY_CUSTOM2,Mesh.ARRAY_CUSTOM3,Mesh.ARRAY_BONES,Mesh.ARRAY_WEIGHTS]:
  if arrays[channel]!=null and not arrays[channel].is_empty():return "custom_channel"
 var shadow: ArrayMesh=node.mesh.shadow_mesh
 if node.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_ON and shadow==null:return "no_separate_shadow"
 return ""
func append_arrays(into:Array,source_arrays:Array,offset:Vector3)->void:
 var base:int=into[Mesh.ARRAY_VERTEX].size() if into[Mesh.ARRAY_VERTEX]!=null else 0
 for channel in Mesh.ARRAY_MAX:
  if channel==Mesh.ARRAY_INDEX:continue
  var values=source_arrays[channel]
  if values==null:continue
  values=values.duplicate()
  if channel==Mesh.ARRAY_VERTEX:
   for i in values.size():values[i]+=offset
  if into[channel]==null:into[channel]=values
  else:
   var combined=into[channel];combined.append_array(values);into[channel]=combined
 var ix:PackedInt32Array=source_arrays[Mesh.ARRAY_INDEX] if source_arrays[Mesh.ARRAY_INDEX]!=null else PackedInt32Array()
 if ix.is_empty():
  for i in source_arrays[Mesh.ARRAY_VERTEX].size():ix.append(i)
 for i in ix.size():ix[i]+=base
 if into[Mesh.ARRAY_INDEX]==null:into[Mesh.ARRAY_INDEX]=ix
 else:
  var combined:PackedInt32Array=into[Mesh.ARRAY_INDEX];combined.append_array(ix);into[Mesh.ARRAY_INDEX]=combined
func compare_arrays(expected:Array,actual:Array)->float:
 var largest:=0.0
 for channel in Mesh.ARRAY_MAX:
  var a=expected[channel];var b=actual[channel]
  if a==null or a.is_empty():assert(b==null or b.is_empty());continue
  assert(b!=null and a.size()==b.size())
  for i in a.size():
   var delta:=0.0
   if a[i] is Vector3 or a[i] is Vector2:delta=a[i].distance_to(b[i])
   elif a[i] is Color:delta=maxf(absf(a[i].r-b[i].r),maxf(absf(a[i].g-b[i].g),maxf(absf(a[i].b-b[i].b),absf(a[i].a-b[i].a))))
   elif a[i] is float:delta=absf(a[i]-b[i])
   else:assert(a[i]==b[i])
   largest=maxf(largest,delta)
 assert(largest<=.00001,"Surface channel drift exceeds ten microunits")
 return largest
func statistics(node:Node)->Dictionary:
 var meshes:={};var shadows:={};var triangles:=0
 for n:MeshInstance3D in node.find_children("*","MeshInstance3D",true,false):
  if n.mesh==null:continue
  meshes[n.mesh.get_instance_id()]=true;
  if n.cast_shadow!=GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY:triangles+=n.mesh.get_faces().size()/3
  if n.mesh is ArrayMesh and n.mesh.shadow_mesh!=null:shadows[n.mesh.shadow_mesh.get_instance_id()]=true
 return {"nodes":node.find_children("*","",true,false).size()+1,"meshes":meshes.size(),"shadows":shadows.size(),"triangles":triangles}
func run_all()->void:
 assert(ProjectSettings.load_resource_pack("/tmp/astraea-laptop-contract-1bc13d51/Astraea-1bc13d51.pck"))
 var old_path:="res://data/architecture/startup_residency_20261020/private_shells_d04.json"
 assert(FileAccess.get_sha256(old_path)=="4f41f4c70165883e6789174225ed2a6172b6e659d8302b586434a68488cdbfdb")
 var index:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(old_path));var reports:Array=[]
 for key:String in index.rooms:
  var record:Dictionary=index.rooms[key];assert(FileAccess.get_sha256(record.detail_path)==record.detail_sha256)
  var packed:PackedScene=load(record.detail_path);var original:Node3D=packed.instantiate();var output:Node3D=original.duplicate(7);output.scene_file_path=""
  signatures.clear();owned_resources.clear();source_model_path=record.detail_path
  for node:Node in output.find_children("*","",true,false):assert(node is Node3D and node.get_script()==null,"Detail carries behavior: refusing flatten/batch")
  var before:=statistics(original);var bins:Dictionary={};var held:Dictionary={};var mapping:Array=[]
  for node:MeshInstance3D in output.find_children("*","MeshInstance3D",true,false):
   var pose:=relative_pose(node,output);var why:=reason(node,output,pose)
   if not why.is_empty():held[why]=int(held.get(why,0))+1;continue
   var material:=node.get_active_material(0);var state:Array=[]
   for property:String in DRAW_PROPERTIES:state.append(node.get(property))
   var bounds:AABB=pose*node.get_aabb();var center:=bounds.get_center();var cell:=Vector3i(floori(center.x/GRID),floori(center.y/GRID),floori(center.z/GRID))
   var shadow:ArrayMesh=node.mesh.shadow_mesh
   var base_key:=str(cell)+":"+str(material.get_instance_id())+":"+str(node.mesh.surface_get_format(0))+":"+str(shadow.surface_get_format(0) if shadow!=null else 0)+":"+str(digest_bytes(var_to_bytes(state)))
   var key_bin:=base_key;var suffix:=0
   while bins.has(key_bin) and bins[key_bin].bounds.merge(bounds).size[bins[key_bin].bounds.merge(bounds).size.max_axis_index()]>GRID:
    suffix+=1;key_bin=base_key+":"+str(suffix)
   if not bins.has(key_bin):bins[key_bin]={"nodes":[],"bounds":bounds,"state":state,"material":material,"shadow":shadow!=null}
   bins[key_bin].nodes.append(node);bins[key_bin].bounds=bins[key_bin].bounds.merge(bounds)
  var checks:Array=[];var merged_nodes:=0
  for key_bin:String in bins:
   var bin:Dictionary=bins[key_bin]
   if bin.nodes.size()<2:continue
   var arrays:Array=[];arrays.resize(Mesh.ARRAY_MAX);var shadow_arrays:Array=[];shadow_arrays.resize(Mesh.ARRAY_MAX)
   var names:Array=[]
   for node:MeshInstance3D in bin.nodes:
    var pose:=relative_pose(node,output)
    append_arrays(arrays,node.mesh.surface_get_arrays(0),pose.origin)
    
    names.append({"path":str(output.get_path_to(node)),"name":str(node.name),"metadata":var_to_str(node.get_meta("extras",{}))})
   var mesh:=ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays);mesh.surface_set_material(0,own_resource(bin.material))
   
   var batch:=MeshInstance3D.new();batch.name="D04OpaqueCell_%04d"%checks.size();batch.mesh=mesh
   for i in DRAW_PROPERTIES.size():batch.set(DRAW_PROPERTIES[i],bin.state[i])
   batch.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
   output.add_child(batch);batch.owner=output
   checks.append({"name":str(batch.name),"arrays":arrays,"shadow_arrays":shadow_arrays,"has_shadow":bin.shadow,"material":signature(bin.material),"state":bin.state.duplicate()})
   checks[-1].state[DRAW_PROPERTIES.find("cast_shadow")]=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
   mapping.append({"batch":str(batch.name),"sources":names,"cell_bounds":var_to_str(bin.bounds)})
   merged_nodes+=bin.nodes.size()
   for node:MeshInstance3D in bin.nodes:
    assert(node.get_child_count()==0)
    if node.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_ON:
     var original_material:=node.get_active_material(0)
     node.mesh=own_resource(node.mesh.shadow_mesh)
     node.material_override=own_resource(original_material)
     node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
     node.set_meta("d04_preserved_shadow_only",true)
    else:node.free()
  # Old shell placeholders duplicate always-resident shells and carry no behavior.
  for node:MeshInstance3D in output.find_children("*","MeshInstance3D",true,false):
   if node.mesh==null and node.get_child_count()==0:node.free();continue
   if node.mesh!=null and not str(node.name).begins_with("D04OpaqueCell_") and not node.get_meta("d04_preserved_shadow_only",false):
    node.mesh=own_resource(node.mesh)
    if node.material_override!=null:node.material_override=own_resource(node.material_override)
    for surface in node.mesh.get_surface_count():
     if node.get_surface_override_material(surface)!=null:node.set_surface_override_material(surface,own_resource(node.get_surface_override_material(surface)))
  for node:Node in output.find_children("*","",true,false):node.owner=output
  var name:=key.trim_suffix(".glb")+".detail.scn";var file:=OUTPUT+name;assert(not FileAccess.file_exists(file),"Never overwrite a generated successor")
  var saved:=PackedScene.new();assert(saved.pack(output)==OK);assert(ResourceSaver.save(saved,file)==OK)
  var reloaded:PackedScene=ResourceLoader.load(file,"PackedScene",ResourceLoader.CACHE_MODE_IGNORE);var actual:Node3D=reloaded.instantiate();var maximum:=0.0
  for check:Dictionary in checks:
   var node:MeshInstance3D=actual.get_node(check.name);maximum=maxf(maximum,compare_arrays(check.arrays,node.mesh.surface_get_arrays(0)))
   assert(signature(node.get_active_material(0))==check.material,"Material changed")
   for i in DRAW_PROPERTIES.size():assert(node.get(DRAW_PROPERTIES[i])==check.state[i])
   assert(node.mesh.shadow_mesh==null)
  # Unbatched LOD/transparent/rotated pieces remain at the same paths and poses.
  var kept:=0
  for node:MeshInstance3D in actual.find_children("*","MeshInstance3D",true,false):
   if node.mesh==null or str(node.name).begins_with("D04OpaqueCell_"):continue
   var prior:MeshInstance3D=original.get_node(actual.get_path_to(node));assert(prior!=null)
   assert(relative_pose(node,actual)==relative_pose(prior,original))
   if node.get_meta("d04_preserved_shadow_only",false):
    assert(signature(node.mesh)==signature(prior.mesh.shadow_mesh))
    assert(signature(node.material_override)==signature(prior.get_active_material(0)))
    assert(node.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY)
   else:
    assert(signature(node.mesh)==signature(prior.mesh))
    assert(signature(node.material_override)==signature(prior.material_override))
   kept+=1
  var after:=statistics(actual);assert(after.triangles==before.triangles);assert(after.meshes+after.shadows<before.meshes+before.shadows and after.nodes<before.nodes)
  reports.append({"model":key,"room_id":record.room_id,"input_path":record.detail_path,"input_sha256":record.detail_sha256,"output_sha256":FileAccess.get_sha256(file),"before":before,"after":after,"merged_source_nodes":merged_nodes,"batch_nodes":checks.size(),"retained_pieces":kept,"maximum_channel_delta":maximum,"held_reasons":held,"source_to_batch":mapping})
  record.detail_path=PREFIX+name;record.detail_sha256=FileAccess.get_sha256(file)
  actual.free();output.free();original.free();owned_resources.clear();signatures.clear();checks.clear();bins.clear();packed=null;saved=null;reloaded=null
  print("D04_BATCH_ROOM ",reports.size(),"/",index.rooms.size()," ",key," ",before.meshes," -> ",after.meshes)
  await process_frame
 var f:=FileAccess.open(OUTPUT+"INDEX.json",FileAccess.WRITE);f.store_string(JSON.stringify(index,"  "));f.close()
 f=FileAccess.open(OUTPUT+"BAKE.json",FileAccess.WRITE);f.store_string(JSON.stringify({"source_revision":"82a03387","cell_limit_m":GRID,"rooms":reports,"gameplay_accepted":false,"fps_claim":false},"  "));f.close();quit()
