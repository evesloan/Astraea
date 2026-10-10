"""Bounded native studio reviews only; no runtime or final appearance acceptance."""
from pathlib import Path
import bpy,math,json
from mathutils import Vector
W=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Port_Successor_002.blend'));s=bpy.context.scene
B=lambda p:(p[0],-p[2],p[1]);ref=bpy.data.collections['UNEXPORTED_REFERENCE_AND_STUDIO']
def mov(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 ref.objects.link(o)
def look(o,p):o.rotation_euler=(Vector(B(p))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;mov(cam);s.camera=cam;cam.data.lens=32
lights=[]
for i in range(3):
 bpy.ops.object.light_add(type='AREA');ob=bpy.context.object;mov(ob);ob.data.energy=[1500,1900,900][i];ob.data.size=[12,14,8][i];lights.append(ob)
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.14,.14,.14);s.view_settings.view_transform='AgX'
views=[('foremid','FORE_MIDSHIP_STATIC_SOURCE',(-2,64,-241),(-9,56,-218),-216),('aftmid','AFT_MIDSHIP_STATIC_SOURCE',(-13,63,244),(-1,56,217),216),('forward','FORWARD_STATIC_SOURCE',(-14,65,-460),(1,56,-434),-432),('central','CENTRAL_STATIC_SOURCE',(10,65,-91),(-7,55.7,-72),-72),('aft','AFT_STATIC_SOURCE',(-14,65,404),(1,56,430),432),('body','TRAM_EDITABLE_COMPONENT',(-4,3.8,5.5),(0,1.1,0),0)]
for name,col,eye,target,z in views:
 for co in bpy.data.collections:
  co.hide_render=co.name not in [col,'UNEXPORTED_REFERENCE_AND_STUDIO']
 # Rail is shown only where near the station; all other spans suppressed in studio by camera framing.
 if col!='TRAM_EDITABLE_COMPONENT':bpy.data.collections['CONTINUOUS_GUIDEWAY_SOURCE'].hide_render=False
 for i,o in enumerate(lights):
  o.location=B([(-8,64,z-8),(8,65,z+3),(-2,61,z+8)][i] if name!='body' else [(-3,6,1),(4,5,-3),(0,4,5)][i]);look(o,target)
 cam.location=B(eye);look(cam,target);cam.data.type='PERSP';cam.data.lens=32
 s.render.filepath=str(W/('SOURCE_REVIEW_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('SOURCE_REVIEW_SIX_COMPLETE native and exports unchanged')
