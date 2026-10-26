extends Node3D
# Exact retained meshes/LODs/materials, each with its original renderer culling box.
# Replace scene-node overhead, not geometry. No draw-call reduction is claimed here.
var records:Array=[]
var instances:Array[RID]=[]
func _ready()->void:
 set_notify_transform(true)
 refresh()
func refresh()->void:
 if not is_inside_tree():return
 if instances.is_empty():
  for row:Array in records:
   var rid:=RenderingServer.instance_create();instances.append(rid)
   RenderingServer.instance_set_base(rid,row[1].get_rid())
   RenderingServer.instance_attach_object_instance_id(rid,get_instance_id())
   RenderingServer.instance_set_layer_mask(rid,row[3])
   RenderingServer.instance_geometry_set_cast_shadows_setting(rid,row[4])
   RenderingServer.instance_set_extra_visibility_margin(rid,row[5])
   RenderingServer.instance_geometry_set_flag(rid,RenderingServer.INSTANCE_FLAG_USE_BAKED_LIGHT,row[6]==GeometryInstance3D.GI_MODE_STATIC)
   RenderingServer.instance_geometry_set_flag(rid,RenderingServer.INSTANCE_FLAG_USE_DYNAMIC_GI,row[6]==GeometryInstance3D.GI_MODE_DYNAMIC)
   RenderingServer.instance_geometry_set_flag(rid,RenderingServer.INSTANCE_FLAG_IGNORE_OCCLUSION_CULLING,row[7])
   RenderingServer.instance_set_pivot_data(rid,row[8],row[9])
   RenderingServer.instance_geometry_set_lod_bias(rid,row[10])
   RenderingServer.instance_geometry_set_material_override(rid,row[2].get_rid())
 for i in instances.size():
  RenderingServer.instance_set_scenario(instances[i],get_world_3d().scenario)
  RenderingServer.instance_set_transform(instances[i],global_transform*records[i][0])
  RenderingServer.instance_set_visible(instances[i],is_visible_in_tree())
func _notification(what:int)->void:
 if what==NOTIFICATION_TRANSFORM_CHANGED or what==NOTIFICATION_VISIBILITY_CHANGED or what==NOTIFICATION_ENTER_WORLD:
  if not records.is_empty():refresh()
 elif what==NOTIFICATION_EXIT_WORLD:
  for rid:RID in instances:RenderingServer.free_rid(rid)
  instances.clear()
 elif what==NOTIFICATION_PREDELETE:
  records.clear()
