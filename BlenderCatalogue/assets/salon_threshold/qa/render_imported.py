"""Actual imported GLB inspection; paired quiet/cove, separate arrival portal.
Only run when the lead has released the sequential render slot.
"""
import bpy,bmesh,math,json,hashlib,importlib.util,sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
PREFLIGHT='--preflight' in sys.argv
ONLY=sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else None
PLANS={
 'portal_standing_640':{'ids':['AST-SAL-001'],'location':[5.8,-8.4,1.65],'target':[0,.64,1.70],'lens':45,'res':[640,360],'full':True,'purpose':'Normal1.65m standing view: empty arrival opening, substantial side feet, deep walnut soffit and recessed acoustic face'},
 'quiet_joined_standing_640':{'ids':['AST-SAL-003','AST-SAL-002'],'location':[5.4,-8.3,1.65],'target':[0,1.4,1.77],'lens':37,'res':[640,360],'full':True,'purpose':'Normal1.65m standing view: actual joined rising shelter, continuous quiet seat/back/cove, empty approach and useful shelves'},
 'quiet_joined_seated_640':{'ids':['AST-SAL-003','AST-SAL-002'],'location':[-5.4,-7.5,1.22],'target':[0,1.45,1.86],'lens':35,'res':[640,360],'full':True,'purpose':'Proposed1.22m seated-eye inspection, showing lower rising cove bearing side and quiet seating without species/seat registration'},
 'quiet_section_detail_1280':{'ids':['AST-SAL-003','AST-SAL-002'],'location':[5.7,-4.2,3.7],'target':[-1.2,1.6,1.88],'ortho':6.6,'res':[1280,960],'full':False,'section':True,'purpose':'Actual imported meshes cut atX0.20 solely for QA, exposing hollow approach, seat plinth, rear wall-to-cove and reserved front transition seam'},
 'portal_profile_detail_1280':{'ids':['AST-SAL-001'],'location':[-.8,-3.4,2.2],'target':[2.12,.56,1.80],'ortho':3.70,'res':[1280,960],'full':False,'purpose':'Deliberate close crop of deep jamb/soffit, inset front acoustic field, walnut return and restrained material joints'}
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def mat(n,c):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.84;return m
def stage():
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=40;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.12
 s.world=bpy.data.worlds.new('QA_ONLY_neutral_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.29,.31,.33,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
 bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.004));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat('QA_ONLY_neutral_floor',(.29,.30,.31)))
 for n,p,e,size in [('key',(-4,-5,7),1900,5),('fill',(5,-3,5),1250,5),('rear',(-2,5,7),1750,4),('under',(-1,-2,2.8),130,3)]:
  d=bpy.data.lights.new('QA_ONLY_'+n,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=p;d.energy=e;d.shape='DISK';d.size=size;aim(o,(0,1.3,1.6))
 d=bpy.data.cameras.new('QA_ONLY_camera');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);s.camera=o;d.clip_start=.02;d.clip_end=120;return o
report={'scope':'Actual GLB component/section QA, not a room, installed host, game view, runtime lighting or species-fit claim','views':{}}
if ONLY and (BASE/'qa/render_evidence.json').exists():report['views']=json.loads((BASE/'qa/render_evidence.json').read_text())['views']
for name,p in PLANS.items():
 if ONLY and ONLY!=name:continue
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);asset=[];files=[]
 for ident in p['ids']:
  path=BASE/'exports'/f'{ident}.glb';before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(path));obs=[o for o in bpy.context.scene.objects if o not in before]
  if ident=='AST-SAL-002':
   for o in obs:
    if o.parent is None:o.location.x-=3.1
  asset+=obs;files.append({'id':ident,'relative_path':'exports/'+ident+'.glb','sha256':sha(path),'source_sha256':sha(BASE/'source'/f'{ident}.blend'),'translation_source_m':[-3.1,0,0] if ident=='AST-SAL-002' else[0,0,0]})
 bpy.context.view_layer.update();objects=[o for o in asset if o.type=='MESH']
 if p.get('section'):
  for o in objects:
   bm=bmesh.new();bm.from_mesh(o.data);local=o.matrix_world.inverted()@Vector((.2,0,0));normal=o.matrix_world.to_3x3().inverted()@Vector((1,0,0));bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=local,plane_no=normal,clear_outer=True,clear_inner=False);bm.to_mesh(o.data);bm.free()
 cam=stage();sc=bpy.context.scene;cam.location=p['location'];aim(cam,p['target']);cam.data.type='ORTHO' if 'ortho' in p else'PERSP';cam.data.ortho_scale=p.get('ortho',10);cam.data.lens=p.get('lens',40);sc.render.resolution_x,sc.render.resolution_y=p['res'];frame=q.frame_report(sc,cam,objects,margin=.025)
 if p['full'] and not frame['passes']:raise RuntimeError(name+' framing failed '+str(frame))
 report['views'][name]={'camera':p,'framing':frame,'assets':files,'intentional_crop':not p['full'],'source_assets_are_unmodified':True,'section_operation':'QA-onlyX0.20 open uncapped cut of imported meshes; cut faces are not construction cavities' if p.get('section') else None,'qa_context_dependencies':[]}
 if not PREFLIGHT:sc.render.image_settings.file_format='PNG';sc.render.filepath=str(BASE/'qa'/f'{name}.png');bpy.ops.render.render(write_still=True)
(BASE/'qa'/('camera_preflight.json' if PREFLIGHT else'render_evidence.json')).write_text(json.dumps(report,indent=2)+'\n');print('PREFLIGHT_PASS' if PREFLIGHT else'RENDER_PASS')
