"""Real retained source views. Camera/cutaway changes are never saved to native."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'AquaticCompletion_r018.blend'))
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1800;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('Source review studio world')
s.render.image_settings.file_format='PNG';s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.5;s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_specular_highlight=True;s.display.shading.background_type='WORLD';s.world.color=(.3,.35,.4)
for m in bpy.data.materials:
 if m.name.startswith('AQD_') and m.use_nodes:
  b=m.node_tree.nodes.get('Principled BSDF')
  if b:m.diffuse_color=b.inputs['Base Color'].default_value
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.clip_end=500;cam.data.lens=22
def xyz(p):return Vector((p[0],-p[2],p[1]))
records=[]
for name,eye,at,cut in [('SOURCE_AQUATIC_WIDE020',(120,96,279),(78,46,216),True),('SOURCE_RIVER_SOUTH020',(86,57,249),(79,44.9,237),False),('SOURCE_RIVER_NORTH020',(85,57,183),(75.9,44.9,195),False)]:
 hidden=[]
 if True:
  for o in s.objects:
   if o.type=='MESH' and o.name.startswith('AQD__') and any(t in o.name for t in ['opaque_roof','enclosure_','threshold_','east_boundary_','west_portal_header','portal_canopy']):
    if not o.hide_render:o.hide_render=True;hidden.append(o)
 if name.startswith('SOURCE_RIVER_'):
  for o in s.objects:
   if o.type=='MESH' and (o.get('kind')=='water_visual' or any(k in o.name.lower() for k in ['overlook','gallery','bridge','roof'])) and not o.hide_render:o.hide_render=True;hidden.append(o)
 cam.location=xyz(eye);cam.rotation_euler=(xyz(at)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=88 if cut else 16
 s.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
 records.append({'name':name,'eye_xyz':eye,'target_xyz':at,'source':'AquaticCompletion_r018.blend','hidden_for_cutaway':[o.name for o in hidden],'presentation':'Neutral Workbench studio; original source material colors, physical geometry and compiler proposal floors. Texture, ordinary game lighting, water gameplay, full ship and final art are not represented.','native_saved':False})
 for o in hidden:o.hide_render=False
(P/'RIVER_VIEW_RECEIPT020.json').write_text(json.dumps(records,indent=2)+'\n')
