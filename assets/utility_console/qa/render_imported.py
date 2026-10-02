"""Source reload checks and actual imported GLB evidence, EEVEE_NEXT/no denoiser.
Run first with -- --preflight-only; acquire lead's heavy-render slot for full run.
"""
import bpy,bmesh,sys,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1];PREFLIGHT='--preflight-only' in sys.argv
spec=importlib.util.spec_from_file_location('frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source/AST-ENG-003.blend'));source=[];issues=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);non=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
 source.append({'name':o.name,'nonmanifold_edges':non,'signed_volume_m3':vol,'modifiers':[m.type for m in o.modifiers],'parent':o.parent.name if o.parent else None})
 if non or vol<=0:issues.append(o.name)
images=[{'name':i.name,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images if i.type=='IMAGE']
(ROOT/'qa/source_reload_checks.json').write_text(json.dumps({'status':'PASS' if not issues else 'FAIL','parts':source,'issues':issues,'images':images},indent=2));assert not issues
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'AST-ENG-003.glb'));components=[o for o in bpy.context.scene.objects if o.type=='MESH'];roots=[o for o in bpy.context.scene.objects if not o.parent]
for o in roots:o.location.z+=1.45
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.cycles.use_denoising=False;sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.31,.35,.39,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
def point(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
mat=bpy.data.materials.new('QA_ONLY_wall_backdrop');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.25,.285,.30,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=6,location=(0,.003,1.45),rotation=(math.pi/2,0,0));wall=bpy.context.object;wall.name='QA_ONLY_wall_contact_backdrop';wall.data.materials.append(mat)
for name,loc,power,size in [('key',(-1.8,-2.5,4.1),500,3),('fill',(2,-1.5,2.5),260,2),('rim',(-.4,1.5,3.8),240,2)]:
 data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=loc;data.energy=power;data.shape='DISK';data.size=size;point(o,(0,-.13,1.45))
data=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(cam);sc.camera=cam
views=[
 {'key':'actualGLB_standing_640','camera_blender_m':[0,-2.05,1.65],'target_blender_m':[0,-.12,1.42],'resolution':[640,360],'lens_mm':43,'ortho_scale':None,'full_frame':True,'purpose':'Ordinary 1.65 m eye, proposed 1.45 m wall datum, actual GLB; no room or actor fit proof'},
 {'key':'actualGLB_threequarter_640','camera_blender_m':[1.25,-2.35,1.75],'target_blender_m':[0,-.12,1.41],'resolution':[640,360],'lens_mm':52,'ortho_scale':None,'full_frame':True,'purpose':'Shaped recessed face, individual tactile controls, cable organisation and wall support projection'},
 {'key':'actualGLB_use_640','camera_blender_m':[.10,-.85,1.65],'target_blender_m':[0,-.20,1.49],'resolution':[640,360],'lens_mm':28,'ortho_scale':None,'full_frame':False,'purpose':'Close ordinary 1.65 m standing-eye use view at proposed approach; intentional case/tail crop, no actor reach certification'},
 {'key':'actualGLB_controls_detail_1280','camera_blender_m':[.34,-1.32,1.56],'target_blender_m':[.04,-.20,1.46],'resolution':[1280,720],'lens_mm':55,'ortho_scale':None,'full_frame':False,'purpose':'Static schematic print, separate control cap/selector forms and real vent gaps; deliberate lower cable crop'},
 {'key':'actualGLB_rear_mounts_detail_1280','camera_blender_m':[1.35,2.2,1.90],'target_blender_m':[0,-.06,1.42],'resolution':[1280,720],'lens_mm':48,'ortho_scale':None,'full_frame':True,'purpose':'Rear mount pads, standoff cleats and cable interfaces with QA wall hidden'}]
for v in views:
 wall.hide_render='rear' in v['key'];wall.hide_viewport=wall.hide_render;cam.location=v['camera_blender_m'];point(cam,v['target_blender_m']);cam.data.type='PERSP';cam.data.lens=v['lens_mm'];cam.data.clip_start=.01;cam.data.clip_end=100
 sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.filepath=str(ROOT/'qa'/(v['key']+'.png'))
 v['frame_preflight']=frame.assert_full_frame(sc,cam,components,.025) if v['full_frame'] else frame.frame_report(sc,cam,components,.025)
 if not PREFLIGHT:bpy.ops.render.render(write_still=True)
report={'evidence_scope':'Blender component evidence from actual GLB import; no engine, room, interactive control or actor certification','renderer':'BLENDER_EEVEE_NEXT','denoiser':False,'samples':48,'views':views,'glb_sha256':hashlib.sha256((ROOT/'AST-ENG-003.glb').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'source/AST-ENG-003.blend').read_bytes()).hexdigest(),'preflight_only':PREFLIGHT,'qa_helpers':'Only lights, camera and bounded neutral wall backdrop, excluded from source/export'}
(ROOT/'qa'/('camera_preflight.json' if PREFLIGHT else 'render_evidence.json')).write_text(json.dumps(report,indent=2));print('CONSOLE_PREFLIGHT_OK' if PREFLIGHT else 'CONSOLE_RENDER_COMPLETE')
