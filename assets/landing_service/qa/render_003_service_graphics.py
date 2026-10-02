"""Final hash-bound actual-import standing/service evidence, sequential EEVEE.
Neutral QA floor/lights/cameras and AST-STF-006 are context only.
--preflight-only runs all camera checks without rendering.
"""
import bpy,json,hashlib,sys,math,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];PRE='--preflight-only' in sys.argv
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
API=json.loads((BASE/'interface_api.json').read_text())['assets']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[BASE/'source/build_landing_service.py',Path(__file__),CAT/'standards/qa_frame.py',BASE/'interface_api.json']+[BASE/sub/f'AST-LND-00{i}.{ext}' for i in(3,4) for sub,ext in [('source','blend'),('exports','glb')]]+[CAT/'assets/staff_overhead/exports/AST-STF-006.glb']
inputs += [BASE/'textures/manifest.json']+sorted((BASE/'textures').glob('*.png'))
hashes={str(p.relative_to(CAT)):sha(p) for p in inputs}
for name in('component_checks','glb_validation','collision_checks'):
 report=json.loads((BASE/'qa'/f'{name}.json').read_text());assert report['all_passed'],f'{name} not passed'
for row in json.loads((BASE/'qa/component_checks.json').read_text())['results']:assert row['source_sha256']==sha(BASE/'source'/f"{row['id']}.blend"),'Stale source check'
for row in json.loads((BASE/'qa/glb_validation.json').read_text())['results']:assert row['sha256']==sha(BASE/row['file']),'Stale native check'

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def import_glb(path,T=None):
 old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));new=[o for o in bpy.data.objects if o not in old];roots=[o for o in new if o.parent not in new]
 if T:
  for o in roots:o.matrix_world=T@o.matrix_world
 return [o for o in new if o.type=='MESH']
def setup(ident):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 components=import_glb(BASE/'exports'/f'{ident}.glb')
 if API[ident].get('fixture_context'):
  ctx=API[ident]['fixture_context'];components+=import_glb((BASE/ctx['existing_export']).resolve(),Matrix(ctx['matrix_source_local']))
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.cycles.use_denoising=False
 world=bpy.data.worlds.new('QA_ONLY_neutral_world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.4,.43,.46,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;sc.world=world;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
 mat=bpy.data.materials.new('QA_ONLY_floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.22,.245,.25,1);bs.inputs['Roughness'].default_value=.88
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));bpy.context.object.name='QA_ONLY_open_floor';bpy.context.object.data.materials.append(mat)
 for name,loc,power,size in [('key',(2.8,-4,5.5),700,4),('fill',(-3,-1,3),420,3),('back',(1,3,4),550,3)]:
  d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,(0,.23,1.2))
 d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);sc.camera=cam;return sc,cam,components
views=[
 {'key':'003_supported_return_standing_640','id':'AST-LND-003','camera_m':[2.5,-5.2,1.65],'target_m':[0,.225,1.25],'resolution':[640,360],'lens_mm':38,'full_frame':True,'purpose':'Ordinary 1.65m eye-height view of complete control return and full unchanged supported fixture'},
 {'key':'003_control_fixture_service_1280','id':'AST-LND-003','camera_m':[1.10,-2.25,1.65],'target_m':[0,.25,1.77],'resolution':[1280,960],'lens_mm':48,'full_frame':False,'purpose':'Intentional service crop of physical separate controls, lowered cover, receiver and guarded fixture; no floor view claim'},
 {'key':'004_fixed_edge_standing_640','id':'AST-LND-004','camera_m':[2.25,-3.2,1.65],'target_m':[0,.375,.52],'resolution':[640,360],'lens_mm':45,'full_frame':True,'purpose':'Ordinary standing view of complete fixed inspection/retrieval furnishing, front approach and actual contact floor'},
 {'key':'004_retrieval_service_1280','id':'AST-LND-004','camera_m':[-1.7,-2.8,1.20],'target_m':[0,.40,.55],'resolution':[1280,960],'lens_mm':51,'full_frame':True,'purpose':'Lower service viewpoint exposes actual retrieval mouth, fixed tray support and deliberate corner protection termination; no actor/cart fit'}]
views=[v for v in views if v['id']=='AST-LND-003']
frames=[]
# Check every camera before any final render.
for v in views:
 sc,cam,components=setup(v['id']);cam.location=v['camera_m'];aim(cam,v['target_m']);cam.data.type='PERSP';cam.data.lens=v['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=v['resolution'];r=frame.assert_full_frame(sc,cam,components,.03) if v['full_frame'] else frame.frame_report(sc,cam,components,.03);v['frame_preflight']=r;v['camera_rotation_euler_radians']=list(cam.rotation_euler);v['clip_start_m']=cam.data.clip_start;v['clip_end_m']=cam.data.clip_end
 if not v['full_frame']:v['crop_disclosure']='Construction detail crop explicitly omits floor/base and lower control return'
frames=views
(BASE/'qa/camera_preflight_003_graphics.json').write_text(json.dumps({'passed':True,'inputs':hashes,'views':views},indent=2))
if not PRE:
 for v in views:
  assert all(sha(CAT/p)==h for p,h in hashes.items()),'Inputs changed after preflight'
  sc,cam,components=setup(v['id']);cam.location=v['camera_m'];aim(cam,v['target_m']);cam.data.type='PERSP';cam.data.lens=v['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.filepath=str(BASE/'qa'/(v['key']+'.png'));bpy.ops.render.render(write_still=True);v['image_sha256']=sha(Path(sc.render.filepath))
 assert all(sha(CAT/p)==h for p,h in hashes.items()),'Inputs changed during final capture'
 out={'scope':'Actual imported-GLB Blender component evidence only; no host room, actor/cart, photometric, mechanical or engine acceptance','renderer':'BLENDER_EEVEE_NEXT','samples':64,'denoising':False,'inputs_before':hashes,'inputs_after':{p:sha(CAT/p) for p in hashes},'source_hashes_unchanged':True,'script':str(Path(__file__).relative_to(CAT)),'views':views,'qa_context':'Neutral floor, studio area lights/camera, reused unchanged AST-STF-006 mounted from interface_api exact transform; all excluded from new production GLBs'}
 (BASE/'qa/render_003_graphics_evidence.json').write_text(json.dumps(out,indent=2))
print('LANDING_SERVICE_PREFLIGHT_OK' if PRE else 'LANDING_SERVICE_RENDER_OK')
