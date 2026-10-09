from pathlib import Path
import bpy,math,sys
from mathutils import Vector
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'Group4_Foremid_Tram_Source.blend'))
B=lambda p:(p[0],-p[2],p[1]);s=bpy.context.scene;cam=s.camera;s.cycles.samples=64;s.render.resolution_x=768;s.render.resolution_y=512
ref=bpy.data.collections['UNEXPORTED_REFERENCE_AND_STUDIO'];base_light=[]
for ob in ref.objects:
 if ob.type=='LIGHT':base_light.append(ob);ob.hide_render=True
# Source reviews are isolated studio images, not main-engine captures.
def look(ob,p):ob.rotation_euler=(Vector(B(p))-ob.location).to_track_quat('-Z','Y').to_euler()
lights=[]
for i,(pos,power,size) in enumerate([((-6,64,-223),1500,12),((6,65,-213),1900,14),((-2,61,-201),900,8)]):
 bpy.ops.object.light_add(type='AREA',location=B(pos));ob=bpy.context.object;ob.name='REVIEW_STUDIO_ONLY_'+str(i);ob.data.energy=power;ob.data.size=size;look(ob,(-3,55.6,-216));lights.append(ob)
def render(name,eye,target,centre=-216,plan=False):
 for ob in lights:ob.location.y-=centre+216-ob.get('last_offset',0);ob['last_offset']=centre+216;look(ob,(-3,55.6,centre))
 cam.location=B(eye);look(cam,target);cam.data.type='ORTHO' if plan else 'PERSP';cam.data.ortho_scale=76;cam.data.lens=26
 s.render.filepath=str(O/name);bpy.ops.render.render(write_still=True)
if '--other-stations-only' not in sys.argv:
 render('SOURCE_REVIEW_station_eye.png',(-5.2,57.75,-225),(-1.8,57.25,-214))
 render('SOURCE_REVIEW_station_overview.png',(10,62.5,-235),(-3,55.8,-216))
 for ob in bpy.data.collections['FORE_MIDSHIP_STATIC_SOURCE'].objects:
  if any(k in ob.name for k in ['Canopy_Profiled_Crown','Canopy_Recessed_Coral_Band','BoardingLift_Header']):ob.hide_render=True
 render('SOURCE_REVIEW_station_plan.png',(-1,92,-215),(-1,52,-215),plan=True)
 for ob in bpy.data.collections['FORE_MIDSHIP_STATIC_SOURCE'].objects:ob.hide_render=False
# Other stations need independent source composition review, not mirrored acceptance.
render('SOURCE_REVIEW_aftmid_eye.png',(-5.2,57.75,225),(-1.8,57.25,214),216)
render('SOURCE_REVIEW_forward_overview.png',(12,64,-459),(-2,56,-432),-432)
render('SOURCE_REVIEW_central_overview.png',(12,65,-104),(-4,56,-86),-86)
render('SOURCE_REVIEW_aft_overview.png',(12,64,405),(-2,56,432),432)
print('SOURCE_REVIEW_COMPLETE 7 bounded studio captures; native source unchanged')
