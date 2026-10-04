import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preflight='--preflight'in args
selected=args[args.index('--views')+1].split(',')if'--views'in args else['001_standing','001_bedding_detail','002_closed_standing','002_gathered_standing']
plans={'001_standing':dict(files=['AST-CRW-001'],loc=(3.2,-3.3,1.65),target=(0,1.0,.55),res=(640,360),lens=48,full=True,purpose='Ordinary standing eye, complete rest frame and supported bedding'), '001_bedding_detail':dict(files=['AST-CRW-001'],loc=(1.8,-.65,1.30),target=(0,1.25,.59),res=(960,640),lens=43,full=False,purpose='Ordinary seated-height bedding and headboard detail, not whole-object framing'), '002_closed_standing':dict(files=['AST-CRW-001','AST-CRW-002'],loc=(3.9,-3.6,1.65),target=(.10,1.0,1.04),res=(640,360),lens=38,full=True,purpose='Ordinary standing side view, supported closed curtain with real frame context'), '002_gathered_standing':dict(files=['AST-CRW-001','AST-CRW-002__gathered'],loc=(3.9,-3.6,1.65),target=(.10,1.0,1.04),res=(640,360),lens=38,full=True,purpose='Same ordinary eye and camera, supported gathered curtain and open approach')}
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
evidence={'scope':'Imported GLB component inspection only. Neutral floor/light/camera are QA aids, no original host or game renderer.','engine':'BLENDER_EEVEE_NEXT','samples':64,'denoising':False,'views':{}}
for name in selected:
 p=plans[name];files=[BASE/'exports'/(f+'.glb')for f in p['files']];inputs=files+[BASE/'source'/(f.split('__')[0]+'.blend')for f in p['files']]+[BASE/'interface_api.json',BASE/'collision_proposals.json',Path(__file__)];before={str(f.relative_to(CAT)):sha(f)for f in inputs}
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for f in files:bpy.ops.import_scene.gltf(filepath=str(f))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.4
 sc.world=bpy.data.worlds.new('QA_ONLY_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.20,.24,.26,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001));floor=bpy.context.object;floor.name='QA_ONLY_floor';m=bpy.data.materials.new('QA_ONLY_floor');m.diffuse_color=(.14,.16,.16,1);floor.data.materials.append(m)
 for tag,loc,power,size in[('key',(-3,-4,5),1600,4),('fill',(4,-1,4),1000,4),('rear',(0,4,4),1200,3)]:
  d=bpy.data.lights.new('QA_ONLY_'+tag,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,(0,1,1))
 d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);cam.location=p['loc'];aim(cam,p['target']);d.lens=p['lens'];d.clip_start=.01;sc.camera=cam;sc.render.resolution_x,sc.render.resolution_y=p['res'];frame=q.frame_report(sc,cam,obs,margin=.035)
 if p['full']and not frame['passes']:raise RuntimeError(name+' framing failure '+str(frame))
 row={'camera':p,'framing':frame,'hashes_before':before}
 if not preflight:
  sc.render.filepath=str(BASE/'qa'/f'{name}.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);row['image_sha256']=sha(BASE/'qa'/f'{name}.png')
 row['hashes_after']={str(f.relative_to(CAT)):sha(f)for f in inputs};row['inputs_unchanged']=before==row['hashes_after'];evidence['views'][name]=row
out=BASE/'qa'/('camera_preflight.json'if preflight else'render_evidence.json');out.write_text(json.dumps(evidence,indent=2));print('PREFLIGHT_PASS'if preflight else'RENDER_COMPLETE')
