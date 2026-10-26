extends RefCounted
# Restricted to two retained immutable crew-bank imports, not arbitrary gameplay nodes.
const RULES=preload("res://spatial_instance_cells_20261026/rules.gd")
static var rejection:String=""
static func reject(reason:String)->bool:
 rejection=reason;return false
static func has_outgoing(node:Node)->bool:
 for signal_info:Dictionary in node.get_signal_list():
  if not node.get_signal_connection_list(signal_info.name).is_empty():return true
 return false
static func safe_contact(mesh:MeshInstance3D)->bool:
 if has_outgoing(mesh):return reject("Outgoing visual signal consumer")
 for key:StringName in mesh.get_meta_list():
  if key!=&"extras":return reject("ownership clause 10")
 var extra:Dictionary=mesh.get_meta("extras",{})
 for key:String in ["runtime_interaction","native_moving_ownership","motion_type","existing_controller","persistent_id"]:
  if extra.has(key):return reject("ownership clause 13")
 if not mesh.get_groups().is_empty():return reject("ownership clause 14")
 for connection:Dictionary in mesh.get_incoming_connections():
  var callback:Callable=connection.callable;var signal_value:Signal=connection.signal
  if callback.get_object()!=mesh or (not callback.is_custom() or callback.get_method()!=&"MeshInstance3D::_mesh_changed") or signal_value.get_object()!=mesh.mesh or signal_value.get_name()!=&"changed":return reject("ownership clause17 "+str({"object_same":callback.get_object()==mesh,"method":str(callback.get_method()),"custom":callback.is_custom(),"signal_object_same":signal_value.get_object()==mesh.mesh,"signal_name":str(signal_value.get_name()),"callable_text":str(callback)}))
 for child:Node in mesh.get_children():
  if not child is StaticBody3D or child.name!="StaticContact" or child.get_script()!=null:return reject("ownership clause 19")
  if has_outgoing(child):return reject("Outgoing contact signal consumer")
  if not child.get_meta_list().is_empty() or not child.get_groups().is_empty() or not child.get_incoming_connections().is_empty():return reject("ownership clause 20")
  if child.physics_material_override!=null or child.constant_linear_velocity!=Vector3.ZERO or child.constant_angular_velocity!=Vector3.ZERO:return reject("ownership clause 21")
  if child.collision_layer!=1 or child.collision_mask!=1 or child.collision_priority!=1.0 or child.get_child_count()!=1:return reject("ownership clause 22")
  var shape:Node=child.get_child(0)
  if not shape is CollisionShape3D or shape.get_script()!=null or shape.disabled or shape.shape==null or shape.get_child_count()!=0:return reject("ownership clause 24")
  if has_outgoing(shape):return reject("Outgoing shape signal consumer")
  if not shape.get_meta_list().is_empty() or not shape.get_groups().is_empty():return reject("ownership clause 25")
  for connection:Dictionary in shape.get_incoming_connections():
   var callback:Callable=connection.callable;var signal_value:Signal=connection.signal
   if callback.get_object()!=shape or (not callback.is_custom() or callback.get_method() not in [&"Node3D::update_gizmos",&"CollisionShape3D::_shape_changed"]) or signal_value.get_object()!=shape.shape or signal_value.get_name()!=&"changed":return reject("shape signal "+str({"object_same":callback.get_object()==shape,"method":str(callback.get_method()),"custom":callback.is_custom(),"signal_object_same":signal_value.get_object()==shape.shape,"signal_name":str(signal_value.get_name())}))
 return true
static func compile_source(source:Node3D,lights:Array)->Dictionary:
 # Preflight every possible member before changing this source. Scope remains fail-closed.
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  if RULES.eligible(mesh,source) and not safe_contact(mesh):
   var detail:Array=[]
   for child:Node in mesh.get_children():
    detail.append({"name":str(child.name),"meta":str(child.get_meta_list()),"groups":str(child.get_groups()),"incoming":str(child.get_incoming_connections()),"priority":child.get("collision_priority"),"layer":child.get("collision_layer"),"mask":child.get("collision_mask"),"children":child.get_child_count(),"shape_meta":str(child.get_child(0).get_meta_list()) if child.get_child_count()>0 else ""})
   return {"failed":"Referenced or nondefault contact owner","reason":rejection,"path":str(source.get_path_to(mesh)),"mesh_meta":str(mesh.get_meta_list()),"mesh_groups":str(mesh.get_groups()),"mesh_incoming":str(mesh.get_incoming_connections()),"contacts":detail}
 var visual:Node3D=load("res://static_bank_cells_20261026/render_owner.gd").new();visual.name="ExactStaticRenderOwner"
 var restoration:Dictionary={"rows":[]}
 for mesh:MeshInstance3D in source.find_children("*","MeshInstance3D",true,false):
  if not RULES.eligible(mesh,source):continue
  visual.records.append([RULES.pose(mesh,source),mesh.mesh,mesh.get_active_material(0),mesh.layers,mesh.cast_shadow,mesh.extra_cull_margin,mesh.gi_mode,mesh.ignore_occlusion_culling,mesh.sorting_offset,mesh.sorting_use_aabb_center,mesh.lod_bias])
  restoration.rows.append({"node":weakref(mesh),"mesh":mesh.mesh})
 var result:Dictionary={"source_meshes":restoration.rows.size(),"batch_count":1,"saved_submissions":0,"exact_renderer_instances":visual.records.size(),"original_lods_preserved":true}
 source.add_child(visual)
 var bins:Dictionary={};var freed_nodes:=0;var shapes:=0;var shape_refs:Array=[];var mesh_refs:Array=[]
 for row:Dictionary in restoration.rows:
  var node:MeshInstance3D=row.node.get_ref()
  var pose:Transform3D=RULES.pose(node,source);var box:AABB=pose*row.mesh.get_aabb()
  var center:=box.get_center();var key:=str(Vector3i(floori(center.x/8.0),floori(center.y/8.0),floori(center.z/8.0)))
  var candidates:Array=bins.get(key,[]);var slot:Dictionary={}
  for candidate:Dictionary in candidates:
   var union:AABB=candidate.bounds.merge(box)
   if union.size[union.size.max_axis_index()]<=8.0:slot=candidate;slot.bounds=union;break
  if slot.is_empty():
   var body:=StaticBody3D.new();body.name="ExactStaticCell_%04d"%freed_nodes;source.add_child(body)
   slot={"body":body,"bounds":box};candidates.append(slot);bins[key]=candidates
  var target:StaticBody3D=slot.body
  for old:StaticBody3D in node.get_children():
   var collider:CollisionShape3D=old.get_child(0)
   var contact_pose:Transform3D=source.global_transform.affine_inverse()*collider.global_transform
   var owner:=target.create_shape_owner(target)
   target.shape_owner_set_transform(owner,contact_pose)
   target.shape_owner_add_shape(owner,collider.shape)
   assert(target.shape_owner_get_shape(owner,0)==collider.shape and target.shape_owner_get_transform(owner).is_equal_approx(contact_pose))
   shape_refs.append(weakref(collider.shape));shapes+=1;freed_nodes+=2
  mesh_refs.append(weakref(row.mesh));node.free();freed_nodes+=1
 # No path proxies or active preimages retained. Rebuild from immutable imports on reconstruction.
 restoration.clear()
 var bodies:=0
 for list:Array in bins.values():bodies+=list.size()
 result.disposable_nodes_freed=freed_nodes;result.static_cell_bodies=bodies;result.exact_shape_bindings=shapes
 result.net_nodes_removed=freed_nodes-bodies-int(result.batch_count)
 return result
static func build(bank:Node3D,lights:Array)->Dictionary:
 assert(bank.name=="Group3RemainingCrewBank" and not bank.has_meta("static_bank_cells"))
 var definition:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_remaining_crew_20261019/PACKAGE.json"))
 var rows:Array=[]
 for file:String in definition.model_pins:
  var path:="res://assets/group3_remaining_crew_20261019/"+file
  assert(FileAccess.get_sha256(path)==definition.model_pins[file])
  var wrapper:Node3D=bank.get_node(file.trim_suffix(".glb"));assert(wrapper.get_child_count()==1)
  var source:Node3D=wrapper.get_child(0)
  var row:=compile_source(source,lights);row.source=path;rows.append(row)
  if row.has("failed"):return {"failed":row,"rows":rows}
 bank.set_meta("static_bank_cells",true)
 return {"rows":rows,"policy":"Two pinned immutable imports only; original per-mesh renderer bounds/LODs plus bounded physical cells; exact original shape resources/transforms; original doors, fixtures and bank/source roots retained; no active source-node proxies"}
