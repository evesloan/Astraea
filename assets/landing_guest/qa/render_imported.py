"""Bounded sequential component views of actual GLB imports. QA lights are aids only."""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
PREFLIGHT='--preflight'in sys.argv;ONLY=sys.argv[sys.argv.index('--only')+1]if'--only'in sys.argv else None
plans={
'001_standing_640':{'id':'AST-LND-001','location':[2.90,-5.4,1.65],'target':[0,.33,1.4],'res':[640,360],'lens':38,'full':True,'offset':0,'fixture':True,'purpose':'Ordinary 1.65 m standing eye: canted readable directory, full-depth return and local cove; existing sconce is QA context'},
'001_cove_receiver_detail_1280':{'id':'AST-LND-001','location':[1.2,-1.7,1.95],'target':[.15,.43,2.35],'res':[1280,960],'lens':48,'full':False,'offset':0,'fixture':True,'purpose':'Intentional upper crop: terminated cove, liner and true supported receiver with existing sconce'},
'002_standing_640':{'id':'AST-LND-002','location':[1.65,-2.90,1.65],'target':[0,.34,.53],'res':[640,360],'lens':44,'full':True,'offset':0,'purpose':'Ordinary standing eye shows distinct single waiting contact, luggage slab and fixed open retrieval bay'},
'002_waiting_640':{'id':'AST-LND-002','location':[1.60,-2.90,1.19],'target':[0,.35,.54],'res':[640,360],'lens':46,'full':True,'offset':0,'purpose':'Proposed 1.19 m waiting-eye inspection shows shaped back, seat crown, real cheek supports and preserved lower openings; no actor'}
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
 if p.get('fixture'):
  before=set(bpy.context.scene.objects);cp=CAT/'assets/guest_use/exports/AST-GST-002.glb';bpy.ops.import_scene.gltf(filepath=str(cp));fixture=[o for o in bpy.context.scene.objects if o not in before]
  for ob in fixture:
   if ob.parent is None:ob.location=(.49,.47,1.93)
  asset+=fixture;context_data={'catalogue_id':'AST-GST-002','glb_path':str(cp.relative_to(CAT)),'glb_sha256':sha(cp),'source_local_transform_4x4':[[1,0,0,.49],[0,1,0,.47],[0,0,1,1.93],[0,0,0,1]],'status':'Existing fixture shown only as QA mating context; excluded from new exports and new count'}
 bpy.context.view_layer.update();objects=[o for o in asset if o.type=='MESH'];cam=stage(p['offset']>0);sc=bpy.context.scene;cam.location=p['location'];aim(cam,p['target']);cam.data.type='ORTHO'if'ortho'in p else'PERSP';cam.data.ortho_scale=p.get('ortho',3);cam.data.lens=p.get('lens',42);sc.render.resolution_x,sc.render.resolution_y=p['res'];frame=q.frame_report(sc,cam,objects,margin=.045)
 if p['full']and not frame['passes']:raise RuntimeError(name+' framing failed '+str(frame))
 report['views'][name]={'camera':p,'framing':frame,'glb_sha256':sha(path),'source_sha256_at_capture':sha(BASE/'source'/f"{p['id']}.blend"),'intentional_crop':not p['full'],'context':context_data,'generator_sha256_at_capture':sha(BASE/'source/build_landing_guest.py')}
 if not PREFLIGHT:sc.render.filepath=str(BASE/'qa'/f'{name}.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);report['views'][name]['source_sha256_after_capture']=sha(BASE/'source'/f"{p['id']}.blend");report['views'][name]['glb_sha256_after_capture']=sha(path);report['views'][name]['image_sha256']=sha(BASE/'qa'/f'{name}.png')
(BASE/'qa'/('camera_preflight.json'if PREFLIGHT else'render_evidence.json')).write_text(json.dumps(report,indent=2)+'\n');print('PREFLIGHT_PASS'if PREFLIGHT else'RENDER_PASS')
