"""All-camera preflight first; exact imported-GLB hash-bound evidence, no production mutation."""
import bpy,json,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];PRE='--preflight-only'in sys.argv
sp=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(sp);sp.loader.exec_module(frame)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[BASE/'source/build_retail_work.py',BASE/'marker_api.json',BASE/'collision_proposals.json',BASE/'manifest.json',BASE/'dependency_manifest.json',Path(__file__),CAT/'standards/qa_frame.py']+sorted((BASE/'exports').glob('AST-*.glb'))+sorted((BASE/'source').glob('AST-*.blend'))
hashes={str(p.relative_to(CAT)):sha(p)for p in files}
views=[
 {'id':'AST-RTL-003','key':'003_guest_standing_640','camera_m':[2.65,-3.7,1.65],'target_m':[0,0,.62],'resolution':[640,360],'lens_mm':45,'purpose':'Ordinary standing height, guest parcel rest, original inactive parcel identity and grounded asymmetric workbench'},
 {'id':'AST-RTL-003','key':'003_staff_work_1280','camera_m':[2.30,3.4,1.90],'target_m':[0,0,.65],'resolution':[1280,960],'lens_mm':53,'purpose':'Raised staff-side inspection, clear wrapping surface, supported open stock shelves and quiet inactive control face'},
 {'id':'AST-RTL-004','key':'004_closed_detail_1280','camera_m':[-.76,-.98,.76],'target_m':[0,0,.15],'resolution':[1280,960],'lens_mm':58,'purpose':'Closed case detail: true seated cap, exterior ribs and supported broad lift grip'},
 {'id':'AST-RTL-004__open_lid_parked','key':'004_open_lid_parked_1280','camera_m':[1.22,-1.65,1.25],'target_m':[.29,0,.16],'resolution':[1280,960],'lens_mm':57,'purpose':'Open empty divided carrier and actual shell, detached lid parked on locator rim at inspection datum Z0'},
 {'id':'AST-RTL-004__handling','key':'004_detached_handling_1280','camera_m':[1.30,-1.80,1.25],'target_m':[.26,0,.27],'resolution':[1280,960],'lens_mm':55,'purpose':'Explicit unsupported manual carrier handling state, lower cavity and bearing rails visible; parked lid remains supported'},
 {'id':'AST-RTL-003','key':'004_on_guest_rest_standing_640','camera_m':[-2.8,-3.1,1.65],'target_m':[-.15,0,.69],'resolution':[640,360],'lens_mm':38,'container_on_bench':True,'purpose':'Ordinary standing-height640px actual case at witnessed bench parcel support; all context meshes are these two authorized components'}]

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def import_asset(name,offset=(0,0,0)):
 old=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(BASE/'exports'/(name+'.glb')));new=[o for o in bpy.context.scene.objects if o not in old]
 for ob in new:
  if ob.parent is None:ob.location+=Vector(offset)
 bpy.context.view_layer.update();return[o for o in new if o.type=='MESH']
def setup(v):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);obs=import_asset(v['id'])
 if v.get('container_on_bench'):
  patch=next(x for x in json.loads((BASE/'AST-RTL-004.manifest.json').read_text())['support_patches']if x['name']=='CASE_FLOOR_PATCH')
  trees=[BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get())for o in obs];witness=[]
  for p in patch['polygon_source_m']:
   q=Vector(p)+Vector((-.54,-.02,1.075));hits=[]
   for o,tree in zip(obs,trees):
    local=o.matrix_world.inverted()@(q+Vector((0,0,.002)));direction=o.matrix_world.inverted().to_3x3()@Vector((0,0,-1));hit,n,index,d=tree.ray_cast(local,direction,.004)
    if hit is not None:
     actual=o.matrix_world@hit;error=(actual-q).length
     if error<.00002:hits.append({'native_mesh':o.name,'actual_imported_source_position_m':list(actual),'error_m':error})
   assert hits,'Container support footprint missed actual bench top: '+str(q);witness.append({'requested_source_position_m':list(q),'hits':hits})
  v['container_support_witnesses']=witness;v['container_placement_source_m']=[-.54,-.02,1.075];v['container_placement_gltf_m']=[-.54,1.075,.02]
  obs+=import_asset('AST-RTL-004',(-.54,-.02,1.075))
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.image_settings.file_format='PNG';sc.cycles.use_denoising=False;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
 world=bpy.data.worlds.new('QA_ONLY_neutral');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.44,.46,.48,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;sc.world=world
 mat=bpy.data.materials.new('QA_ONLY_floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.225,.245,.25,1);bs.inputs['Roughness'].default_value=.86;bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.003));bpy.context.object.data.materials.append(mat)
 small=v['id'].startswith('AST-RTL-004');scale=.6 if small else 1
 for name,loc,power,size in[('key',(2.8,-3.8,5.),700,4),('fill',(-3,-1,3),420,3),('rim',(1,3,4),550,3)]:
  d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=Vector(loc)*scale;d.energy=power*scale*scale;d.shape='DISK';d.size=size*scale;aim(o,(0,0,.7 if not small else .18))
 d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);sc.camera=cam;cam.location=v['camera_m'];cam.data.lens=v['lens_mm'];cam.data.clip_start=.03;aim(cam,v['target_m']);return sc,cam,obs
for v in views:
 print('PREFLIGHT',v['key'],flush=True);sc,cam,obs=setup(v);v['frame_preflight']=frame.assert_full_frame(sc,cam,obs,.035);v['camera_rotation_euler_radians']=list(cam.rotation_euler);v['clip_start_m']=cam.data.clip_start;v['clip_end_m']=cam.data.clip_end
(BASE/'qa/camera_preflight.json').write_text(json.dumps({'all_passed':True,'inputs':hashes,'views':views},indent=2)+'\n')
if not PRE:
 for v in views:
  assert all(sha(CAT/p)==h for p,h in hashes.items()),'Frozen production changed during capture';sc,cam,obs=setup(v);sc.render.filepath=str(BASE/'qa'/(v['key']+'.png'));bpy.ops.render.render(write_still=True);v['image_sha256']=sha(Path(sc.render.filepath));(BASE/'qa/render_partial.json').write_text(json.dumps({'inputs':hashes,'completed_views':[x for x in views if'image_sha256'in x]},indent=2)+'\n')
 assert all(sha(CAT/p)==h for p,h in hashes.items()),'Production changed during capture'
 (BASE/'qa/render_evidence.json').write_text(json.dumps({'renderer':'BLENDER_EEVEE_NEXT','samples':64,'denoising':False,'scope':'Actual imported GLBs; neutral inspection floor/lights/cameras. No host shop, species/actor, load, operation or engine adoption. Handling tray is expressly unsupported/manual','inputs_before':hashes,'inputs_after':{p:sha(CAT/p)for p in hashes},'production_unchanged':True,'views':views},indent=2)+'\n')
print('RETAIL_WORK_PREFLIGHT_OK'if PRE else'RETAIL_WORK_RENDER_OK')
