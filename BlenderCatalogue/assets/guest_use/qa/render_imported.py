"""Bounded sequential component views of actual GLB imports. QA lights are aids only."""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
PREFLIGHT='--preflight'in sys.argv;ONLY=sys.argv[sys.argv.index('--only')+1]if'--only'in sys.argv else None
plans={
'001_standing_640':{'id':'AST-GST-001','location':[1.40,-2.9,1.65],'target':[0,-.03,.76],'res':[640,360],'lens':35,'full':True,'offset':0,'purpose':'Ordinary standing1.65m eye height: slender blade, switch, supported hood and split base'},
'001_reading_detail_1280':{'id':'AST-GST-001','location':[.85,.48,1.10],'target':[0,-.09,1.33],'res':[1280,960],'ortho':.76,'full':False,'offset':0,'purpose':'Rear underside of hood, recessed diffuser, retaining clip and substantial neck support; rocker shown in ordinary front view'},
'002_standing_640':{'id':'AST-GST-002','location':[.68,-1.24,1.65],'target':[0,-.09,1.36],'res':[640,360],'lens':55,'full':True,'offset':1.36,'purpose':'Ordinary standing1.65m eye height at proposed1.36m mount centre; wall plane is QA aid'},
'002_mount_detail_1280':{'id':'AST-GST-002','location':[.48,-.85,1.08],'target':[0,-.11,1.39],'res':[1280,960],'ortho':.72,'full':True,'offset':1.36,'purpose':'Wall plate, fixing bosses, braced arm, retained diffuser and rocker'},
'003_standing_640':{'id':'AST-GST-003','location':[1.15,-2.6,1.65],'target':[0,0,.44],'res':[640,360],'lens':44,'full':True,'offset':0,'purpose':'Ordinary standing1.65m eye height: open luggage landing, right personal tray and shelf'},
'003_support_detail_1280':{'id':'AST-GST-003','location':[1.50,-2.20,1.55],'target':[0,-.01,.44],'res':[1280,960],'ortho':1.80,'full':True,'offset':0,'purpose':'Actual support slats/rails and unequal-height open personal storage, no drawer'},
'001_chair_reading_context_640':{'id':'AST-GST-001','location':[1.20,-3.35,1.22],'target':[-.22,0,.74],'res':[640,360],'lens':34,'full':True,'offset':0,'context':True,'purpose':'Compact existing chair/lamp QA scale arrangement from proposed1.22m seated eye; no actor/room/fit claim'}
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.82;return m
def stage(wall):
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.render.threads_mode='FIXED';sc.render.threads=3;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.25
 sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.29,.30,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat('QA_ONLY_floor',(.28,.29,.30)))
 if wall:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.041,1.4));o=bpy.context.object;o.name='QA_ONLY_wall_mount_plane';o.dimensions=(4,.08,3);o.data.materials.append(mat('QA_ONLY_wall',(.30,.31,.32)))
 for name,loc,power,size in [('key',(-3,-4,5),1050,4),('fill',(4,-2,3),600,3),('rear',(-1,4,4),850,3)]:
  data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=loc;data.energy=power;data.shape='DISK';data.size=size;aim(o,(0,0,.8))
 data=bpy.data.cameras.new('QA_ONLY_camera');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);sc.camera=o;data.clip_start=.01;data.clip_end=250;return o
report={'scope':'Actual imported GLBs, neutral Blender Eevee inspection only. No game renderer, runtime lighting, room allocation, species-fit or active physics evidence.','views':{}}
if ONLY and(BASE/'qa/render_evidence.json').exists()and not PREFLIGHT:report['views']=json.loads((BASE/'qa/render_evidence.json').read_text())['views']
for name,p in plans.items():
 if ONLY and ONLY not in(name,p['id']):continue
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);path=BASE/'exports'/f"{p['id']}.glb";bpy.ops.import_scene.gltf(filepath=str(path));asset=list(bpy.context.scene.objects)
 for ob in asset:
  if ob.parent is None:ob.location.z+=p['offset']
 context_data=None
 if p.get('context'):
  for ob in asset:
   if ob.parent is None:ob.location.x=-.77;ob.location.y=.14;ob.rotation_euler.z=math.radians(25)
  before=set(bpy.context.scene.objects);cp=CAT/'assets/furniture/AST-FUR-002_day_reading_chair.glb';bpy.ops.import_scene.gltf(filepath=str(cp));chair=[o for o in bpy.context.scene.objects if o not in before];asset+=chair
  context_data={'chair_path':str(cp.relative_to(CAT)),'chair_glb_sha256':sha(cp),'lamp_placement_source_m':[-.77,.14,0],'lamp_yaw_source_degrees':25,'status':'Visual scale and approach inspection only; no actor fit, balance or lighting simulation'}
 bpy.context.view_layer.update();objects=[o for o in asset if o.type=='MESH'];cam=stage(p['offset']>0);sc=bpy.context.scene;cam.location=p['location'];aim(cam,p['target']);cam.data.type='ORTHO'if'ortho'in p else'PERSP';cam.data.ortho_scale=p.get('ortho',3);cam.data.lens=p.get('lens',42);sc.render.resolution_x,sc.render.resolution_y=p['res'];frame=q.frame_report(sc,cam,objects,margin=.045)
 if p['full']and not frame['passes']:raise RuntimeError(name+' framing failed '+str(frame))
 report['views'][name]={'camera':p,'framing':frame,'glb_sha256':sha(path),'source_sha256_at_capture':sha(BASE/'source'/f"{p['id']}.blend"),'intentional_crop':not p['full'],'context':context_data}
 if not PREFLIGHT:sc.render.filepath=str(BASE/'qa'/f'{name}.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
(BASE/'qa'/('camera_preflight.json'if PREFLIGHT else'render_evidence.json')).write_text(json.dumps(report,indent=2)+'\n');print('PREFLIGHT_PASS'if PREFLIGHT else'RENDER_PASS')
