"""Actual imported GLB evidence. Heavy renders must be serialized by family lead."""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
PREFLIGHT='--preflight'in sys.argv
ONLY=sys.argv[sys.argv.index('--only')+1]if'--only'in sys.argv else None
plans={
'003_threequarter_640':{'id':'AST-HSP-003','location':[1.35,-1.9,1.92],'target':[0,0,1.18],'res':[640,360],'ortho':1.65,'full':True,'offset':.9,'purpose':'Neutral actual-GLB overview on proposed0.90 m host QA block'},
'003_standing_640':{'id':'AST-HSP-003','location':[.38,-1.80,1.65],'target':[0,-.03,1.19],'res':[640,360],'lens':42,'full':True,'offset':.9,'purpose':'Ordinary1.65 m standing eye height; guest controls and cup bay'},
'003_cup_bay_detail':{'id':'AST-HSP-003','location':[.71,-1.20,1.48],'target':[0,-.08,1.18],'res':[1280,960],'ortho':.76,'full':False,'offset':.9,'purpose':'Real spout mouths, annular cup rests, catch floor and small control hierarchy'},
'004_threequarter_640':{'id':'AST-HSP-004','location':[2.15,-2.8,2.15],'target':[0,0,.65],'res':[640,360],'ortho':3.35,'full':True,'offset':0,'purpose':'Neutral guest-side actual GLB overview'},
'004_standing_640':{'id':'AST-HSP-004','location':[.45,-2.8,1.65],'target':[0,0,.60],'res':[640,360],'lens':35,'full':True,'offset':0,'purpose':'Ordinary1.65 m standing eye height; guest receiving slot and drop ledge'},
'004_staff_extraction_detail':{'id':'AST-HSP-004','location':[1.65,2.30,1.91],'target':[0,.35,.79],'res':[1280,960],'ortho':1.85,'full':False,'offset':0,'extract':.40,'purpose':'Actual caddy root translated+Y0.40 m for hand-supported removal inspection; open rear, grip and rails; no loaded full-extension support claim'},
'004_receiving_detail':{'id':'AST-HSP-004','location':[1.04,-1.60,1.43],'target':[0,-.035,.935],'res':[1280,960],'ortho':1.37,'full':False,'offset':0,'purpose':'Actual guest drop, receiving compartment and header opening'}}
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
def stage(offset):
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=32;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.35
 sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.29,.30,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat('QA_ONLY_floor',(.24,.25,.26)))
 if offset:
  bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.45));o=bpy.context.object;o.name='QA_ONLY_proposed_host_0.90m';o.dimensions=(1.15,.78,.90);o.data.materials.append(mat('QA_ONLY_host',(.32,.33,.33)))
 for name,loc,power,size in [('key',(-3,-4,5),1100,4),('fill',(4,-2,3),650,3),('rear',(-1,4,4),900,3)]:
  data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=loc;data.energy=power;data.shape='DISK';data.size=size;aim(o,(0,0,.8))
 data=bpy.data.cameras.new('QA_ONLY_camera');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);sc.camera=o;data.clip_start=.01;data.clip_end=250;return o
report={'scope':'Actual GLB imports in neutral inspection stage; host/floor are QA aids. No room, food system, engine or species fit certification.','views':{}}
if ONLY and(BASE/'qa/render_evidence.json').exists()and not PREFLIGHT:report['views']=json.loads((BASE/'qa/render_evidence.json').read_text())['views']
for name,p in plans.items():
 if ONLY and p['id']!=ONLY:continue
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);path=BASE/'exports'/f"{p['id']}.glb";bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update();asset=[o for o in bpy.context.scene.objects];roots=[o for o in asset if o.parent is None]
 for ob in roots:ob.location.z+=p['offset']
 if p.get('extract'):bpy.data.objects['RECEIVING_CADDY'].location.y+=p['extract']
 bpy.context.view_layer.update();objects=[o for o in asset if o.type=='MESH'];cam=stage(p['offset']);sc=bpy.context.scene;cam.location=p['location'];aim(cam,p['target']);cam.data.type='ORTHO' if 'ortho'in p else'PERSP';cam.data.ortho_scale=p.get('ortho',3);cam.data.lens=p.get('lens',42);sc.render.resolution_x,sc.render.resolution_y=p['res'];frame=q.frame_report(sc,cam,objects,margin=.045)
 if p['full']and not frame['passes']:raise RuntimeError(name+' framing failed '+str(frame))
 report['views'][name]={'camera':p,'framing':frame,'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_sha256_at_capture':hashlib.sha256((BASE/'source'/f"{p['id']}.blend").read_bytes()).hexdigest(),'intentional_crop':not p['full']}
 if not PREFLIGHT:sc.render.filepath=str(BASE/'qa'/f'{name}.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
(BASE/'qa'/('camera_preflight.json' if PREFLIGHT else'render_evidence.json')).write_text(json.dumps(report,indent=2)+'\n');print('PREFLIGHT_PASS'if PREFLIGHT else'RENDER_PASS')
