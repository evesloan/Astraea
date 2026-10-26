extends RefCounted
# Candidate full-resolution static cells. Original editable sources are immutable.
# Imported LOD selection is replaced by full source triangles; measure extra distant primitives.
const CELL:=8.0
const DRAW:=["layers","cast_shadow","extra_cull_margin","gi_mode","ignore_occlusion_culling","sorting_offset","sorting_use_aabb_center"]
static func pose(n:Node3D,root:Node3D)->Transform3D:
 var t:=n.transform;var p:=n.get_parent()
 while p!=root:
  assert(p is Node3D);t=p.transform*t;p=p.get_parent()
 return t
static func eligible(n:MeshInstance3D,root:Node3D)->bool:
 if not n.mesh is ArrayMesh or n.mesh.get_surface_count()!=1 or n.mesh.get_blend_shape_count()!=0:return false
 if n.cast_shadow not in [GeometryInstance3D.SHADOW_CASTING_SETTING_OFF,GeometryInstance3D.SHADOW_CASTING_SETTING_ON]:return false
 if n.get_script()!=null or n.skin!=null or n.skeleton!=NodePath("") or n.material_overlay!=null or n.transparency!=0:return false
 if n.custom_aabb!=AABB() or n.visibility_parent!=NodePath("") or n.visibility_range_begin!=0 or n.visibility_range_end!=0:return false
 if n.mesh.surface_get_primitive_type(0)!=Mesh.PRIMITIVE_TRIANGLES:return false
 var arrays:Array=n.mesh.surface_get_arrays(0)
 for channel:int in [Mesh.ARRAY_BONES,Mesh.ARRAY_WEIGHTS,Mesh.ARRAY_CUSTOM0,Mesh.ARRAY_CUSTOM1,Mesh.ARRAY_CUSTOM2,Mesh.ARRAY_CUSTOM3]:
  if arrays[channel]!=null and not arrays[channel].is_empty():return false
 var mat:Material=n.get_active_material(0)
 if not mat is StandardMaterial3D or mat.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or mat.albedo_color.a<.999 or mat.next_pass!=null:return false
 if mat.uv1_triplanar or mat.uv2_triplanar or mat.billboard_mode!=BaseMaterial3D.BILLBOARD_DISABLED or mat.grow or mat.use_point_size:return false
 var ancestor:Node=n
 while ancestor!=root:
  if not ancestor is Node3D or not ancestor.visible or ancestor.get_script()!=null or ancestor.top_level:return false
  if ancestor is CollisionObject3D or ancestor is AnimationPlayer:return false
  ancestor=ancestor.get_parent()
 for child in n.get_children():
  if not child is StaticBody3D:return false
 var t:=pose(n,root)
 # SurfaceTool transform semantics are verified only for positive uniform scale.
 var scale:=t.basis.get_scale()
 if t.basis.determinant()<=0 or absf(scale.x-scale.y)>.00001 or absf(scale.x-scale.z)>.00001:return false
 return true
static func light_signature(box:AABB,layers:int,lights:Array)->String:
 var ids:Array[int]=[];var omni:=0;var spot:=0
 for light in lights:
  var id:int;var kind:int;var mask:int;var reach:float;var p:Vector3
  if light is Dictionary:
   id=light.id;kind=light.kind;mask=light.mask;reach=light.reach;p=light.position
  else:
   if not is_instance_valid(light):continue
   assert(light.is_inside_tree(),"Detached lights require their retained owner transform")
   id=light.get_instance_id();kind=0 if light is DirectionalLight3D else (1 if light is OmniLight3D else 2)
   mask=light.light_cull_mask;reach=0.0 if kind==0 else (light.omni_range if kind==1 else light.spot_range);p=light.global_position
  if mask&layers==0:continue
  if kind==0:ids.append(id);continue
  if p.distance_squared_to(p.clamp(box.position,box.end))>reach*reach:continue
  if kind==1:omni+=1
  else:spot+=1
  ids.append(id)
 if omni>8 or spot>8:return "OVER_LIMIT"
 ids.sort();return str(ids)
