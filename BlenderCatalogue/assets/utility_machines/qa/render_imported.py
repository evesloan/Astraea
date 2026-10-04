"""Imported actual GLB evidence only; stage aids do not enter deliverables.
Preflight: blender -b -t 2 --python qa/render_imported.py -- --preflight
Render after slot approval: blender -b -t 2 --python qa/render_imported.py
"""
import bpy,math,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
PREFLIGHT='--preflight' in sys.argv
plans={
'pump_standing_640':{'id':'AST-ENG-001','location':[2.60,-3.60,1.65],'target':[0,.27,.47],'res':[640,360],'lens':43,'full':True,'caption':'P-01 | camera at 1.65 m | real open ports at 0.60 m'},
'filter_standing_640':{'id':'AST-ENG-002','location':[2.40,-3.60,1.65],'target':[0,0,.82],'res':[640,360],'lens':38,'full':True,'caption':'F-02 | camera at 1.65 m | vertical service lid + front access'},
'pump_coupling_detail':{'id':'AST-ENG-001','location':[1.65,1.85,1.35],'target':[0,.43,.51],'res':[1280,960],'ortho':1.46,'full':False,'caption':'Drive, removable coupling guard and connected shaped mountings'},
'filter_lid_detail':{'id':'AST-ENG-002','location':[1.20,-1.80,2.18],'target':[0,0,1.33],'res':[1280,960],'ortho':1.15,'full':False,'caption':'Six lid clamps, gasket seam, grip centreline and upward service direction'},
'pump_full_detail':{'id':'AST-ENG-001','location':[2.60,-3.60,2.35],'target':[0,.28,.46],'res':[1280,960],'ortho':2.65,'full':True,'caption':'Pump skid | front cover on open service collar; no operating rating'},
'filter_full_detail':{'id':'AST-ENG-002','location':[2.0,-3.2,2.40],'target':[0,0,.81],'res':[1280,960],'ortho':2.90,'full':True,'caption':'Filter vessel | splayed supported feet and preserved service lid'}}
def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def mat(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;return m
def stage():
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=32;sc.cycles.use_denoising=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_percentage=100
 sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.55
 sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.24,.28,.30,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006));bpy.context.object.name='QA_ONLY_neutral_floor';bpy.context.object.data.materials.append(mat('QA_ONLY_floor',(.22,.25,.26)))
 for name,loc,power,size in [('key',(-3,-4,5),1100,4),('fill',(4,-2,2.7),700,3),('rim',(-1,4,4),1000,3)]:
  data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=loc;data.energy=power;data.shape='DISK';data.size=size;aim(ob,(0,.2,.7))
 data=bpy.data.cameras.new('QA_ONLY_camera');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);sc.camera=ob;data.clip_start=.01;data.clip_end=250;return ob
report={'scope':'Imported actual GLB component evidence in neutral stage. No room reconstruction, engine gameplay, certified maintenance clearance or physical ratings.','renderer':'EEVEE_NEXT 32 samples, no denoiser','views':{}}
for name,plan in plans.items():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 path=BASE/'exports'/f"{plan['id']}.glb";bpy.ops.import_scene.gltf(filepath=str(path));objects=[ob for ob in bpy.data.objects if ob.type=='MESH'];cam=stage();sc=bpy.context.scene
 cam.location=plan['location'];aim(cam,plan['target']);cam.data.type='ORTHO' if 'ortho'in plan else'PERSP';cam.data.ortho_scale=plan.get('ortho',3);cam.data.lens=plan.get('lens',48);sc.render.resolution_x,sc.render.resolution_y=plan['res']
 frame=q.frame_report(sc,cam,objects,margin=.045)
 if plan['full'] and not frame['passes']:raise RuntimeError(name+' framing failed '+str(frame))
 report['views'][name]={'camera':plan,'framing':frame,'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'full_component_required':plan['full'],'intentional_crop':not plan['full']}
 if not PREFLIGHT:
  sc.render.filepath=str(BASE/'qa'/f'{name}_raw.png');sc.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
(BASE/'qa'/('camera_preflight.json' if PREFLIGHT else'render_evidence.json')).write_text(json.dumps(report,indent=2)+'\n');print('PREFLIGHT_PASS' if PREFLIGHT else'RENDER_PASS')
