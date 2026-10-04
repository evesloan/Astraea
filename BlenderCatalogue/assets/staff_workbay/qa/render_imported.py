"""Labelled imported-GLB component-only Eevee evidence. No game or room geometry."""
from pathlib import Path
import sys,math,json,hashlib
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parents[1]
sys.path.insert(0,str(BASE/'standards'))
from qa_frame import frame_report
SLUG='AST-STF-007_supply_work_cabinet';GLB=ROOT/(SLUG+'.glb')
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
preflight='preflight' in args
views={
 '01_closed_threequarter_640':{'size':[640,360],'loc':[2.55,-3.4,2.0],'target':[0,-.03,.57],'type':'ORTHO','ortho':3.55,'angle':0,'full':True,'label':'Closed | 0.94 m worktop | full silhouette'},
 '02_open105_threequarter_640':{'size':[640,360],'loc':[2.55,-3.4,2.0],'target':[-.04,-.20,.56],'type':'ORTHO','ortho':3.75,'angle':-105,'full':True,'label':'Open 105 deg | real shelves + hinge + handle'},
 '03_standing_eye_1650mm_640':{'size':[640,360],'loc':[1.8,-2.75,1.65],'target':[0,-.07,.58],'type':'PERSP','lens':32,'angle':-105,'full':True,'label':'Standing eye 1.650 m | imported GLB open'},
 '04_hinge_storage_detail_1280':{'size':[1280,720],'loc':[-1.7,-2.1,1.62],'target':[-.44,-.16,.65],'type':'ORTHO','ortho':1.65,'angle':-65,'full':False,'label':'Detail | 65 deg intermediate door + folded construction'},
}
selected=[k for k in views if not args or preflight or k in args]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(GLB))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];pivot=bpy.data.objects['AST-STF-007_door_hinge_pivot'];pivot.rotation_mode='XYZ'
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=64;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.world=bpy.data.worlds.new('QA_neutral_world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.51,.55,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.45
floor=bpy.data.materials.new('QA_only_floor');floor.diffuse_color=(.16,.18,.20,1);floor.use_nodes=True;floor.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.16,.18,.20,1);floor.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.72
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.name='QA_ONLY_ground_plane';bpy.context.object.data.materials.append(floor)
for name,loc,power,size in [('QA_key',(-3,-4,5),800,4),('QA_fill',(3,-1,3.5),600,3),('QA_rim',(0,3,4.5),850,3)]:
 data=bpy.data.lights.new(name,'AREA');ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.5))-ob.location).to_track_quat('-Z','Y').to_euler();data.energy=power;data.shape='DISK';data.size=size
camdata=bpy.data.cameras.new('QA_component_camera');cam=bpy.data.objects.new('QA_component_camera',camdata);s.collection.objects.link(cam);s.camera=cam;camdata.clip_start=.03;camdata.clip_end=250
# Blender importer already restores Z-up. Record the pivot and floor datum explicitly.
reports=[]
for name in selected:
 cfg=views[name];pivot.rotation_euler.z=math.radians(cfg['angle']);s.render.resolution_x,s.render.resolution_y=cfg['size'];s.render.resolution_percentage=100
 cam.location=cfg['loc'];cam.rotation_euler=(Vector(cfg['target'])-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type=cfg['type'];camdata.ortho_scale=cfg.get('ortho',3);camdata.lens=cfg.get('lens',50);bpy.context.view_layer.update()
 angle=math.radians(cfg['angle']);expected=Matrix.Translation(Vector((-.837,-.317,.2)))@Matrix.Rotation(angle,4,'Z')
 pose_error=max(abs(pivot.matrix_world[row][col]-expected[row][col]) for row in range(4) for col in range(4))
 assert pose_error<.000001,('Actual pivot matrix does not match intended door angle',cfg['angle'],pose_error)
 grip=bpy.data.objects['AST-STF-007_door_handle_staff_rubber'];actual_landmark=grip.matrix_world@grip.data.vertices[0].co
 report=frame_report(s,cam,objects,margin=.055);rec={'file':name+'.png','description':cfg['label'],'camera':cfg,'frame_preflight':report,'pivot_world_m':list(pivot.matrix_world.translation),'actual_pivot_matrix':[[float(v) for v in row] for row in pivot.matrix_world],'intended_pivot_matrix_error_max':pose_error,'actual_handle_vertex_world_m':list(actual_landmark),'rotation_mode_asserted':pivot.rotation_mode,'source_sha256':hashlib.sha256((ROOT/(SLUG+'.blend')).read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(GLB.read_bytes()).hexdigest(),'renderer':'Blender 4.3.2 Eevee 64 samples, neutral component inspection','scope':'Imported GLB Blender component evidence; no game, room, route or rig acceptance'};reports.append(rec)
 if cfg['full'] and not report['passes']:raise RuntimeError('Framing preflight failed '+name+': '+str(report))
 if not preflight:
  s.render.filepath=str(ROOT/'qa'/(name+'.png'));bpy.ops.render.render(write_still=True)
  rec['png_sha256_unlabelled']=hashlib.sha256((ROOT/'qa'/(name+'.png')).read_bytes()).hexdigest()
path=ROOT/'qa'/('camera_preflight.json' if preflight else 'RENDER_MANIFEST.json')
if path.exists() and not preflight:
 old=json.loads(path.read_text());reports=([r for r in old if r['file'] not in {x['file'] for x in reports}]+reports)
path.write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
