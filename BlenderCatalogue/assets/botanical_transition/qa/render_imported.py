"""Final actual imported GLB views, no source-scene substitutions."""
import bpy,json,hashlib,math,sys,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
PREFLIGHT='--preflight-only'in sys.argv
SELECTED=sys.argv[sys.argv.index('--views')+1].split(',')if '--views'in sys.argv else None
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/'source/AST-BOT-010.blend';glb=ROOT/'exports/AST-BOT-010.glb';hashes={'blend':sha(source),'glb':sha(glb)}
bpy.ops.import_scene.gltf(filepath=str(glb));components=[o for o in bpy.context.scene.objects if o.type=='MESH']
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=64;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.cycles.use_denoising=False
sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.39,.44,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
mat=bpy.data.materials.new('QA_ONLY_floor');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.23,.25,.27,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=200,location=(.9,.5,-.004));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat)
def point(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('key',(1.8,-3.5,5),650,4),('fill',(2,3,3.5),550,3),('side',(-2,-1,3),400,3)]:
 d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=loc;d.energy=power;d.shape='DISK';d.size=size;point(o,(.9,.5,.4))
d=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(cam);sc.camera=cam
views=[{'key':'standing_front_640','camera_m':[3.25,-4,1.65],'target_m':[.85,.25,.38],'resolution':[640,360],'lens':52,'full':True,'purpose':'Ordinary standing Z1.65; complete useful seat and front approach, with rising planted edge behind'}, {'key':'seated_front_640','camera_m':[2.50,-3.70,1.15],'target_m':[.85,.27,.39],'resolution':[640,360],'lens':45,'full':True,'purpose':'Ordinary seated eye Z1.15, complete supported sitting ribbon'}, {'key':'rear_maintenance_640','camera_m':[-1.85,4.15,1.65],'target_m':[.95,.28,.40],'resolution':[640,360],'lens':50,'full':True,'purpose':'Ordinary standing rear; soil level change and unplanted maintenance side, later trailing sweep not represented'}, {'key':'soil_retaining_detail_960','camera_m':[2.4,-1.8,1.8],'target_m':[.90,.40,.42],'resolution':[960,720],'lens':50,'ortho':2.4,'full':False,'purpose':'Higher intentional construction view of lower/upper soil, real riser wall, back-set upper coping and supported seat'}, {'key':'native_seam_detail_960','camera_m':[.65,-1.5,1.08],'target_m':[0,.10,.32],'resolution':[960,720],'lens':50,'ortho':1.38,'full':False,'purpose':'Actual imported unchanged004 end and010 start joint at 2mm; intentional joint crop'}]
if SELECTED:views=[v for v in views if v['key']in SELECTED]
context=[]
for v in views:
 if v['key']=='native_seam_detail_960':
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(CAT/'assets/botanical_planter/AST-BOT-004.glb'));context=[o for o in bpy.data.objects if o not in before]
  for o in context:
   if o.parent is None:o.matrix_world=Matrix.Translation(Vector((-2.4,0,0)))@o.matrix_world
 cam.location=v['camera_m'];point(cam,v['target_m']);cam.data.type='ORTHO'if 'ortho'in v else 'PERSP';cam.data.lens=v['lens']
 if 'ortho'in v:cam.data.ortho_scale=v['ortho']
 sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.filepath=str(ROOT/'qa'/(v['key']+'.png'))
 v['frame_preflight']=frame.assert_full_frame(sc,cam,components,.035)if v['full']else frame.frame_report(sc,cam,components,.035)
 if not PREFLIGHT:bpy.ops.render.render(write_still=True)
 for o in context:bpy.data.objects.remove(o,do_unlink=True)
 context=[]
assert hashes=={'blend':sha(source),'glb':sha(glb)}
report={'renderer':'Blender4.3.2 Eevee64samples','scope':'Actual imported native GLB component inspection only; no host/actor/species/game/structural certification','hashes':hashes,'old004_glb_sha256':sha(CAT/'assets/botanical_planter/AST-BOT-004.glb'),'source_export_unchanged_after_capture':True,'views':views,'preflight_only':PREFLIGHT}
(ROOT/('qa/camera_preflight.json'if PREFLIGHT else 'qa/render_evidence.json')).write_text(json.dumps(report,indent=2)+'\n');print('IMPORTED_RENDER_PREFLIGHT_PASS'if PREFLIGHT else 'IMPORTED_RENDER_PASS')
