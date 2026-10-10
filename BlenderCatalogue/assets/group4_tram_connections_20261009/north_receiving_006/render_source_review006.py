from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');S=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/boarding_north_005';B=lambda p:(p[0],-p[2],p[1]);G=lambda p:(p[0],p[2],-p[1])
def studio():
 s=bpy.context.scene;ref=bpy.data.collections['UNEXPORTED_REFERENCE_AND_STUDIO'];s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=640;s.render.resolution_y=480;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.14,.14,.14);s.view_settings.view_transform='AgX'
 def move(o):
  for c in list(o.users_collection):c.objects.unlink(o)
  ref.objects.link(o)
 bpy.ops.object.camera_add();cam=bpy.context.object;move(cam);s.camera=cam;cam.data.lens=35;lights=[]
 for i in range(3):
  bpy.ops.object.light_add(type='AREA');o=bpy.context.object;move(o);o.data.energy=[1600,1900,1000][i];o.data.size=[12,14,8][i];lights.append(o)
 return s,ref,cam,lights
def look(o,p):o.rotation_euler=(Vector(B(p))-o.location).to_track_quat('-Z','Y').to_euler()
def capture(name,eye,target):
 for i,o in enumerate(lights):o.location=B([(target[0]-8,target[1]+8,target[2]-8),(target[0]+8,target[1]+9,target[2]+3),(target[0]-2,target[1]+5,target[2]+8)][i]);look(o,target)
 cam.location=B(eye);look(cam,target);s.render.filepath=str(W/('SOURCE_REVIEW_'+name+'.png'));bpy.ops.render.render(write_still=True)
def import_ref(path,at=(0,0,0)):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));obs=set(bpy.data.objects)-before;wrap=bpy.data.objects.new('UNSAVED_CONTEXT_'+Path(path).stem,None);ref.objects.link(wrap)
 for o in obs:
  for c in list(o.users_collection):c.objects.unlink(o)
  ref.objects.link(o)
 for o in obs:
  if o.parent not in obs:m=o.matrix_world.copy();o.parent=wrap;o.matrix_world=m
 wrap.location=B(at);return obs

bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_North_Receiving_006.blend'));s,ref,cam,lights=studio()
import_ref(S/'AST-TRM-G4-020_foremid_north_candidate.glb')
import_ref(R/'Game/assets/models/AST-CIR-005_fore_midship_cinema2_d11.glb',(0,0,-272))
import_ref(R/'Game/assets/models/SOL_D09_directory_03_source001.glb',(-8,52.5,-250))
# Existing actual floor tops are unsaved display context, without any region edits.
C={};exec((R/'BlenderCatalogue/assets/group4_tram_connections_20261009/receiving_module_003/source_contact_math.py').read_text(),C)
for q in json.loads((R/'Game/data/generated/structural_meshes.json').read_text())['regions']:
 if q.get('floor_y')!=52.5 or q['id'] not in ['D09_fore_route','D09_fore_midship_public_core_floor']:continue
 vs=[];fs=[]
 for tri in q['triangles']:
  poly=[list(p) for p in tri]
  for ax,v,gt in [(0,-20,True),(0,4,False),(1,-270,True),(1,-220,False)]:poly=C['clip'](poly,ax,v,gt) if poly else []
  if len(poly)<3:continue
  off=len(vs);vs.extend([B((x,52.5,z)) for x,z in poly]);fs.append(tuple(off+i for i in range(len(poly))))
 if fs:
  me=bpy.data.meshes.new('UNSAVED_ACTUAL_FLOOR_'+q['id']);me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['warm_stone']);ob=bpy.data.objects.new(me.name,me);ref.objects.link(ob)
if '--lift-only' not in sys.argv:
 cam.data.lens=35;capture('north_stair_receiving',(-19.5,57.0,-269.5),(-10.5,54.0,-259.6))
# Explicit unsaved cutaway: hide only four new floor panels to expose below-floor pit receiving.
for o in bpy.data.collections['NORTH_RECEIVING_006_SOURCE'].objects:
 if o.name.startswith('N006_MissingOnlyFloor_'):o.hide_render=True
cam.data.lens=38;capture('north_lift_receiving_cutaway',(-6.5,54.7,-231),(-11.2,52.6,-223.2))
print('TWO_NORTH_RECEIVING_VIEWS_COMPLETE; unsaved context/cutaway only; native and export unchanged')
