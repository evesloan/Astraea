from pathlib import Path
import bpy,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');S=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002';bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Receiving_Module_003.blend'));s=bpy.context.scene;B=lambda p:(p[0],-p[2],p[1]);ref=bpy.data.collections['UNEXPORTED_REFERENCE_AND_STUDIO']
# Frozen rail export imported only as unsaved visual context. It is never in module exports/native outputs.
bpy.ops.import_scene.gltf(filepath=str(S/'AST-TRM-G4-016_continuous_guideway.glb'))
for o in list(bpy.context.selected_objects):
 for c in list(o.users_collection):c.objects.unlink(o)
 ref.objects.link(o)
def mov(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 ref.objects.link(o)
def look(o,p):o.rotation_euler=(Vector(B(p))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;mov(cam);s.camera=cam;cam.data.lens=35
lights=[]
for i in range(3):
 bpy.ops.object.light_add(type='AREA');o=bpy.context.object;mov(o);o.data.energy=[1500,1900,1000][i];o.data.size=[12,14,8][i];lights.append(o)
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.14,.14,.14);s.view_settings.view_transform='AgX'
for name,eye,target in [('central',(49,64,-40),(40,58.4,-24)),('south',(-13,60,101),(-3,55.5,86)),('core_end',(-.5,62,-418),(-4.5,57.8,-413))]:
 for i,o in enumerate(lights):o.location=B([(target[0]-8,66,target[2]-8),(target[0]+8,66,target[2]+3),(target[0]-2,63,target[2]+8)][i]);look(o,target)
 cam.location=B(eye);look(cam,target);s.render.filepath=str(W/('SOURCE_REVIEW_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('THREE_RECEIVING_SOURCE_VIEWS_COMPLETE native and exports unchanged')
