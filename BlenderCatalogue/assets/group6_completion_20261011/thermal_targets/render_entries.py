"""Actual saved thermal entry source cutaways. Native never resaved."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
records=[]
for i in ['02','03']:
 bpy.ops.wm.open_mainfile(filepath=str(P/f'ThermalEntries_{i}_r003.blend'));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1800;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 s.world=bpy.data.worlds.new('Thermal source review world');s.world.color=(.3,.35,.4);s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD'
 for m in bpy.data.materials:
  if m.use_nodes:
   n=m.node_tree.nodes.get('Principled BSDF')
   if n:m.diffuse_color=n.inputs['Base Color'].default_value
 hidden=[]
 for o in s.objects:
  if o.type=='MESH' and any(t in o.name.lower() for t in ['roof','bathing_enclosure','spring_shell','threshold_']):
   if not o.hide_render:o.hide_render=True;hidden.append(o.name)
 bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=500
 def xyz(p):return Vector((p[0],-p[2],p[1]))
 views=[(f'SOURCE_THERMAL_{i}_WIDE003',(70,90,-376),(31,44,-432),85),(f'SOURCE_THERMAL_{i}_ENTRY003',(40,57,-430),(34,44.5,-436.5),17)] if i=='02' else [(f'SOURCE_THERMAL_{i}_WIDE003',(-70,90,-162),(-31,44,-216),85),(f'SOURCE_THERMAL_{i}_ENTRY003',(-45,57,-218),(-34,44.5,-222),21)]
 for name,eye,target,scale in views:
  drained=[]
  if 'ENTRY' in name:
   for o in s.objects:
    if o.type=='MESH' and 'water' in o.name.lower() and not o.hide_render:o.hide_render=True;drained.append(o.name)
  cam.location=xyz(eye);cam.rotation_euler=(xyz(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
  records.append({'image':name+'.png','native':f'ThermalEntries_{i}_r003.blend','eye_xyz':eye,'target_xyz':target,'orthographic_scale_m':scale,'hidden_for_cutaway':hidden+drained,'native_resaved':False,'presentation':'Actual retained reviewed thermal source with new entry-only successors. Neutral geometry/base-color cutaway; current entrance correction native is absent and entrance unchanged at runtime. Water hidden in entry detail only. No game lighting, swim/temperature/gravity or final-art acceptance.'})
  for name in drained:bpy.data.objects[name].hide_render=False
(P/'SOURCE_VIEW_RECEIPT003.json').write_text(json.dumps(records,indent=2)+'\n')
