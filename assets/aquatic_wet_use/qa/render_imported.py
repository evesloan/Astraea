"""Frozen native GLB imports in a neutral component inspection scene; no host/game/body acceptance."""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preflight='--preflight'in args
selected=args[args.index('--views')+1].split(',')if'--views'in args else['009_standing','009_vessel','009_rear','010_standing','010_head','010_rear']
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plans={
'009_standing':dict(ident='AST-AQU-009',loc=(2.55,-4.45,1.65),target=(0,0,.76),res=(640,360),lens=52,full=True,purpose='Ordinary eye height; full crescent pedestal silhouette, vessel opening and front control'),
'009_vessel':dict(ident='AST-AQU-009',loc=(.80,-1.75,1.55),target=(0,-.04,1.04),res=(960,720),lens=62,full=False,purpose='Higher ordinary-height close view of actual vessel landing, open collector, capped outlet and bounded control'),
'009_rear':dict(ident='AST-AQU-009',loc=(-1.95,3.2,1.65),target=(0,.13,.73),res=(640,480),lens=52,full=True,purpose='Ordinary-height rear service plate and complete support path'),
'010_standing':dict(ident='AST-AQU-010',loc=(3.2,-5.6,1.65),target=(0,0,1.09),res=(640,360),lens=50,full=True,purpose='Ordinary eye height; full floor-supported rinse blade, protected head and control'),
'010_head':dict(ident='AST-AQU-010',loc=(.95,-1.45,1.65),target=(0,-.055,1.96),res=(960,720),lens=58,full=False,purpose='Ordinary-height upward detail; real head/gusset/spine joins and closed downward interface'),
'010_rear':dict(ident='AST-AQU-010',loc=(-3.0,4.5,1.65),target=(0,.10,1.07),res=(640,480),lens=55,full=True,purpose='Ordinary-height rear removable plate and tapered load rails')}
evidence={'scope':'Component inspection only; neutral floor/lights/cameras are QA aids, no room, game, fluid or body acceptance','engine':'BLENDER_EEVEE_NEXT','samples':64,'denoising':False,'views':{}}
for name in selected:
 p=plans[name];ident=p['ident'];path=BASE/'exports'/f'{ident}.glb';source=BASE/'source'/f'{ident}.blend';before={'glb':sha(path),'source':sha(source),'manifest':sha(BASE/f'{ident}.manifest.json'),'marker_api':sha(BASE/'marker_api.json'),'collision_proposals':sha(BASE/'collision_proposals.json')}
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(path));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.65
 sc.world=bpy.data.worlds.new('QA_ONLY_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.26,.28,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001));floor=bpy.context.object;floor.name='QA_ONLY_neutral_floor';m=bpy.data.materials.new('QA_ONLY_floor');m.diffuse_color=(.13,.17,.17,1);floor.data.materials.append(m)
 for tag,loc,power,size in[('key',(-3,-4,5),1600,4),('fill',(3,-1,3),900,4),('rear',(0,4,4),1200,3)]:
  d=bpy.data.lights.new('QA_ONLY_'+tag,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,(0,0,1))
 d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);cam.location=p['loc'];aim(cam,p['target']);d.lens=p['lens'];d.clip_start=.01;sc.camera=cam;sc.render.resolution_x,sc.render.resolution_y=p['res'];frame=q.frame_report(sc,cam,obs,margin=.035)
 if p['full']and not frame['passes']:raise RuntimeError(name+' full-frame failure '+str(frame))
 row={'camera':p,'framing':frame,'hashes_before':before}
 if not preflight:
  sc.render.filepath=str(BASE/'qa'/f'{name}.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);row['image_sha256']=sha(BASE/'qa'/f'{name}.png')
 row['hashes_after']={'glb':sha(path),'source':sha(source),'manifest':sha(BASE/f'{ident}.manifest.json'),'marker_api':sha(BASE/'marker_api.json'),'collision_proposals':sha(BASE/'collision_proposals.json')};row['source_export_metadata_unchanged']=row['hashes_after']==before;evidence['views'][name]=row
out=BASE/'qa'/('camera_preflight.json'if preflight else'render_evidence.json')
if out.exists()and not preflight:
 old=json.loads(out.read_text());old['views'].update(evidence['views']);evidence=old
out.write_text(json.dumps(evidence,indent=2)+'\n');print('PREFLIGHT_PASS'if preflight else'RENDER_COMPLETE')
