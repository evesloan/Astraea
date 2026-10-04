"""Actual imported-GLB component evidence; neutral studio, not game/room fit."""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];preflight='--preflight'in args;ids=args[args.index('--ids')+1].split(',')if'--ids'in args else['005','006'];views=args[args.index('--views')+1].split(',')if'--views'in args else['ordinary','use','detail']
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def mat(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;return m
plans={
'005':{'ordinary':{'location':(2,-2.8,1.75),'target':(0,0,.43),'ortho':2.65,'res':[640,360],'full':True,'meaning':'Guest presentation and shaped storage silhouette'},'use':{'location':(-1.35,2.55,1.65),'target':(0,.02,.47),'lens':42,'res':[640,360],'full':True,'meaning':'Staff standing-eye view, exposed reachable stock compartments'},'detail':{'location':(-.95,1.7,1.15),'target':(-.035,.07,.46),'ortho':1.12,'res':[1280,960],'full':False,'meaning':'Rear shelf supports, physical tray/plate stock and divider clearances'}},
'006':{'ordinary':{'location':(1.8,-2.5,1.65),'target':(0,.04,.44),'ortho':2.40,'res':[640,360],'full':True,'meaning':'Two-tier trolley proportions, useful levels and continuous supports'},'use':{'location':(-1.15,2.25,1.65),'target':(0,.02,.47),'lens':42,'res':[640,360],'full':True,'meaning':'Staff standing-eye push grip and clear top tray surface'},'detail':{'location':(-.83,-1.0,.48),'target':(-.15,-.13,.17),'ortho':.67,'res':[1280,960],'full':False,'meaning':'Wheel/fork clearance, floor contact, support and lower-tier joint'}}}
evidence={'scope':'Actual imported GLB in neutral inspection environment only. No game rendering, species-fit, room fit or dynamic behavior.','engine':'BLENDER_EEVEE_NEXT','taa_samples':64,'denoiser':False,'assets':{}}
for suffix in ids:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);aid='AST-HSP-'+suffix;path=BASE/'exports'/(aid+'.glb');bpy.ops.import_scene.gltf(filepath=str(path));objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];sc=bpy.context.scene
 sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.65
 sc.world=bpy.data.worlds.new('QA_ONLY_neutral');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.24,.27,.29,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001));floor=bpy.context.object;floor.name='QA_ONLY_floor';floor.data.materials.append(mat('QA_ONLY_floor_mat',(.14,.17,.18)))
 for name,loc,power,size in[('key',(-3,-4,5),1250,4),('fill',(3,-.5,3.5),950,3),('rear',(0,4,4),1200,3)]:
  d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,(0,0,.45))
 d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);sc.camera=cam;d.clip_start=.01;d.clip_end=200
 row={'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((BASE/'source'/(aid+'.blend')).read_bytes()).hexdigest(),'views':{}}
 for name in views:
  p=plans[suffix][name];cam.location=p['location'];aim(cam,p['target']);d.type='ORTHO'if'ortho'in p else'PERSP';d.ortho_scale=p.get('ortho',2);d.lens=p.get('lens',48);sc.render.resolution_x,sc.render.resolution_y=p['res'];frame=q.frame_report(sc,cam,objects,margin=.035)
  if p['full']and not frame['passes']:raise RuntimeError(aid+' '+name+' failed frame: '+str(frame))
  row['views'][name]={'camera':p,'framing':frame,'crop_intent':'none'if p['full']else'purposeful detail crop'}
  if not preflight:sc.render.filepath=str(BASE/'qa'/(suffix+'_'+name+'_raw.png'));sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
 evidence['assets'][aid]=row
(BASE/'qa'/('camera_preflight.json'if preflight else'render_evidence.json')).write_text(json.dumps(evidence,indent=2)+'\n');print('PREFLIGHT_PASS'if preflight else'RENDER_COMPLETE')
