"""Hash-bound actual-import evidence. --preflight-only never renders or changes production."""
import bpy,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];PRE='--preflight-only'in sys.argv
sp=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(sp);sp.loader.exec_module(frame)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[BASE/'source/build_handling.py',BASE/'textures/draw_handling_art.py',BASE/'marker_api.json',BASE/'collision_proposals.json',BASE/'manifest.json',BASE/'dependency_manifest.json',Path(__file__),CAT/'standards/qa_frame.py']+[BASE/sub/(ident+'.'+ext)for ident in('AST-HSK-003','AST-HSK-004')for sub,ext in[('source','blend'),('exports','glb')]]
hashes={str(p.relative_to(CAT)):sha(p)for p in inputs}
for n in('source_checks','collision_checks'):assert json.loads((BASE/'qa'/(n+'.json')).read_text())['all_passed'],n
views=[
 {'id':'AST-HSK-003','key':'003_standing_640','camera_m':[2.5,-3.5,1.65],'target_m':[0,0,.54],'resolution':[640,360],'lens_mm':44,'purpose':'Ordinary standing eye-height: clean and used zones, open storage, physical floor supports'},
 {'id':'AST-HSK-003','key':'003_lower_service_1280','camera_m':[-2.4,-3.1,.95],'target_m':[0,0,.55],'resolution':[1280,960],'lens_mm':53,'purpose':'Lower service view: actual legs, retained shelf bearing, front folded nose and zone markings'},
 {'id':'AST-HSK-004','key':'004_standing_640','camera_m':[1.85,-2.55,1.65],'target_m':[0,0,.54],'resolution':[640,360],'lens_mm':42,'purpose':'Ordinary standing eye-height: lowered retrieval rim, true tapered USED-only volume and caster floor contact'},
 {'id':'AST-HSK-004','key':'004_rear_service_1280','camera_m':[-1.65,2.20,1.45],'target_m':[0,0,.61],'resolution':[1280,960],'lens_mm':42,'purpose':'Rear service view: supported liner, retained hoop and rear grip with fingerspace'}]
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def setup(v):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(BASE/'exports'/(v['id']+'.glb')));obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.image_settings.file_format='PNG';sc.cycles.use_denoising=False;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
 world=bpy.data.worlds.new('QA_ONLY_neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.43,.46,.48,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;sc.world=world
 mat=bpy.data.materials.new('QA_ONLY_floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.22,.245,.25,1);bs.inputs['Roughness'].default_value=.88;bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));bpy.context.object.data.materials.append(mat)
 for name,loc,power,size in[('key',(2.8,-3.8,5.0),700,4),('fill',(-3,-1,3),420,3),('rear',(1,3,4),550,3)]:
  d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;aim(o,(0,0,.7))
 d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);sc.camera=cam;cam.location=v['camera_m'];cam.data.lens=v['lens_mm'];aim(cam,v['target_m']);return sc,cam,obs
for v in views:
 sc,cam,obs=setup(v);v['frame_preflight']=frame.assert_full_frame(sc,cam,obs,.035);v['camera_rotation_euler_radians']=list(cam.rotation_euler);v['clip_start_m']=cam.data.clip_start;v['clip_end_m']=cam.data.clip_end
(BASE/'qa/camera_preflight.json').write_text(json.dumps({'all_passed':True,'inputs':hashes,'views':views},indent=2)+'\n')
if not PRE:
 for v in views:
  assert all(sha(CAT/p)==h for p,h in hashes.items()),'Production changed during capture';sc,cam,obs=setup(v);sc.render.filepath=str(BASE/'qa'/(v['key']+'.png'));bpy.ops.render.render(write_still=True);v['image_sha256']=sha(Path(sc.render.filepath))
 assert all(sha(CAT/p)==h for p,h in hashes.items()),'Frozen production changed'
 (BASE/'qa/render_evidence.json').write_text(json.dumps({'renderer':'BLENDER_EEVEE_NEXT','samples':64,'denoising':False,'scope':'Actual imported GLB; neutral floor/lights/cameras only, no original ship, operations, species, load or engine acceptance','inputs_before':hashes,'inputs_after':{p:sha(CAT/p)for p in hashes},'production_unchanged':True,'views':views},indent=2)+'\n')
print('HANDLING_PREFLIGHT_OK'if PRE else'HANDLING_RENDER_OK')
