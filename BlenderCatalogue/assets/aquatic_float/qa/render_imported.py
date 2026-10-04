"""Actual imported GLB visual evidence. QA studio only, EEVEE_NEXT, no denoiser."""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else[];preflight='--preflight'in args;views=args[args.index('--views')+1].split(',') if '--views'in args else['silhouette','standing','handle','seat']
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def mat(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;return m
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);path=BASE/'exports/AST-AQU-006.glb';bpy.ops.import_scene.gltf(filepath=str(path));objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-1
sc.world=bpy.data.worlds.new('QA_ONLY_neutral_studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.2,.25,.29,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.169));floor=bpy.context.object;floor.name='QA_ONLY_studio_floor_not_water';floor.data.materials.append(mat('QA_ONLY_stage',(.115,.15,.16)))
for name,loc,power,size in [('key',(-2.5,-3.7,5),1400,4),('fill',(3,-1,3),850,4),('rim',(0,4,4),1100,3)]:
    data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=loc;data.energy=power;data.shape='DISK';data.size=size;aim(o,(0,0,.1))
data=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(cam);sc.camera=cam;data.clip_start=.01;data.clip_end=200
plans={'silhouette':{'location':(2.3,-3.2,2.65),'target':(0,0,.16),'res':(640,360),'ortho':3.65,'full':True,'caption':'AST-AQU-006 | imported GLB | sculpted coaming, recessed membrane, joined arched grips'},'standing':{'location':(2.50,-3.30,1.65),'target':(0,0,.14),'res':(640,360),'lens':48,'full':True,'caption':'Body-scale view | camera Z1.65 m | design waterline is Z0, no flotation simulation'},'handle':{'location':(1.30,-1.4,1.10),'target':(.46,-.08,.29),'res':(1280,960),'ortho':.95,'full':False,'caption':'Grip detail | closed arched grip + four welded flexible saddle contacts'},'seat':{'location':(-.20,-1.90,2.4),'target':(0,-.04,.12),'res':(1280,960),'ortho':1.62,'full':False,'caption':'Seat detail | concave teal membrane, flexible welt, actual central drain aperture'}}
evidence={'scope':'Component QA only. All lights/floor/camera are inspection aids. Not an in-game image or a physical flotation/fit test.','glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((BASE/'source/AST-AQU-006.blend').read_bytes()).hexdigest(),'engine':'BLENDER_EEVEE_NEXT','taa_samples':64,'denoising':False,'views':{}}
for name in views:
    p=plans[name];cam.location=p['location'];aim(cam,p['target']);cam.data.type='ORTHO'if'ortho'in p else'PERSP';cam.data.ortho_scale=p.get('ortho',3);cam.data.lens=p.get('lens',48);sc.render.resolution_x,sc.render.resolution_y=p['res'];frame=q.frame_report(sc,cam,objects,margin=.035)
    if p['full']and not frame['passes']:raise RuntimeError(name+' failed full frame '+str(frame))
    evidence['views'][name]={'camera':p,'framing':frame,'crop_intent':'none'if p['full']else'deliberate component detail'}
    if not preflight:sc.render.filepath=str(BASE/'qa'/f'{name}_raw.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
(BASE/'qa'/('camera_preflight.json'if preflight else'render_evidence.json')).write_text(json.dumps(evidence,indent=2)+'\n');print('PREFLIGHT_PASS'if preflight else'RENDER_COMPLETE')
