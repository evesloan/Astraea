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
 var metadata:Dictionary=n.get_meta("extras",{})
 for key:String in ["runtime_interaction","native_moving_ownership","motion_type","existing_controller","persistent_id"]:
  if metadata.has(key):return false
 if not n.mesh is ArrayMesh or n.mesh.get_surface_count()!=1 or n.mesh.get_blend_shape_count()!=0:return false
 if n.cast_shadow not in [GeometryInstance3D.SHADOW_CASTING_SETTING_OFF,GeometryInstance3D.SHADOW_CASTING_SETTING_ON]:return false
 if n.get_script()!=null or n.skin!=null or n.skeleton!=NodePath("") or n.material_overlay!=null or n.transparency!=0:return false
 if n.custom_aabb!=AABB() or n.visibility_parent!=NodePath("") or n.visibility_range_begin!=0 or n.visibility_range_end!=0:return false
 if n.mesh.surface_get_primitive_type(0)!=Mesh.PRIMITIVE_TRIANGLES:return false
 var format:int=n.mesh.surface_get_format(0)
 if format&(Mesh.ARRAY_FORMAT_BONES|Mesh.ARRAY_FORMAT_WEIGHTS|Mesh.ARRAY_FORMAT_CUSTOM0|Mesh.ARRAY_FORMAT_CUSTOM1|Mesh.ARRAY_FORMAT_CUSTOM2|Mesh.ARRAY_FORMAT_CUSTOM3):return false
 var mat:Material=n.get_active_material(0)
 if not mat is StandardMaterial3D or mat.transparency!=BaseMaterial3D.TRANSPARENCY_DISABLED or mat.albedo_color.a<.999 or mat.next_pass!=null:return false
 if mat.uv1_triplanar or mat.uv2_triplanar or mat.billboard_mode!=BaseMaterial3D.BILLBOARD_DISABLED or mat.grow or mat.use_point_size:return false
 var ancestor:Node=n
 while ancestor!=root:
  if not ancestor is Node3D or not ancestor.visible or ancestor.get_script()!=null or ancestor.top_level:return false
  if ancestor is CollisionObject3D or ancestor is AnimationPlayer:return false
  ancestor=ancestor.get_parent()
 for child in n.get_children():
  if not child is StaticBody3D or child.get_script()!=null:return false
 var t:=pose(n,root)
 # Mirrored uniform transforms are factored onto a separate batch owner.
 # Per-instance transforms remain positive; nonuniform scale stays excluded.
 var scale:=t.basis.get_scale().abs()
 if absf(t.basis.determinant())<.000001 or absf(scale.x-scale.y)>.00001 or absf(scale.x-scale.z)>.00001:return false
 return true
static func light_signature(box:AABB,layers:int,lights:Array)->String:
 var ids:Array[int]=[];var omni:=0;var spot:=0;var managed_omni:=0;var managed_spot:=0
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
  var managed:bool=light is Dictionary and bool(light.get("managed_eight",false))
  if kind==1:
   if managed:managed_omni+=1
   else:omni+=1
  else:
   if managed:managed_spot+=1
   else:spot+=1
  ids.append(id)
 # A verified shared eight-source budget is mutual exclusion, not omitted lighting.
 # Keep every potential ID in the signature and count unmanaged sources separately.
 if omni+mini(managed_omni,8)>8 or spot+mini(managed_spot,8)>8:return "OVER_LIMIT"
 ids.sort();return str(ids)
