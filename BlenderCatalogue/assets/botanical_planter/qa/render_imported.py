"""Imported final GLB inspection only; no room/game lighting, physical or rig claim.
Use -- --preflight-only for cheap source + camera checks before serialized rendering.
"""
import bpy,bmesh,json,math,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
PREFLIGHT='--preflight-only' in sys.argv
SELECTED=sys.argv[sys.argv.index('--views')+1].split(',') if '--views' in sys.argv else None

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def point(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def source_checks():
 records=[]
 for p in sorted(ROOT.glob('*.blend')):
  bpy.ops.wm.open_mainfile(filepath=str(p));parts=[];issues=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   bm=bmesh.new();bm.from_mesh(ob.data);nm=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
   if nm or vol<=0:issues.append(ob.name)
   vs=[ob.matrix_world@v.co for v in ob.data.vertices]
   parts.append({'name':ob.name,'role':ob['material_role'],'nonmanifold_edges':nm,'signed_volume_m3':vol,'min_m':[min(v[i] for v in vs) for i in range(3)],'max_m':[max(v[i] for v in vs) for i in range(3)],'uv_layers':[u.name for u in ob.data.uv_layers],'editable_modifiers':[m.type for m in ob.modifiers]})
  records.append({'file':p.name,'sha256':sha(p),'parts':parts,'issues':issues,'status':'PASS' if not issues else 'FAIL'})
 (ROOT/'qa/source_reload_validation.json').write_text(json.dumps(records,indent=2));assert all(r['status']=='PASS' for r in records)
source_checks();bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
placements=json.loads((ROOT/'manifest.json').read_text())['assembly_instances'];placements.insert(0,{'asset_id':'derived/AST-BOT-006_START','translation_m':[0,0,0],'rotation_z_degrees':0});components=[]
for p in placements:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/(p['asset_id']+'.glb')))
 T=Matrix.Translation(Vector(p['translation_m']))@Matrix.Rotation(math.radians(p['rotation_z_degrees']),4,'Z')
 obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
 for ob in obs:ob.matrix_world=T@ob.matrix_world;ob.name=p['asset_id']+'_'+ob.name
 components+=obs
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.render.threads_mode='FIXED';sc.render.threads=4
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.cycles.use_denoising=False
sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.39,.44,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
mat=bpy.data.materials.new('QA_ONLY_floor');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.23,.25,.27,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=200,location=(2,.5,-.004));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat)
for name,loc,power,size in [('key',(1.8,-3.5,5),750,4),('fill',(4,2,3.5),600,3),('side',(-2,-1,3),400,3)]:
 data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=loc;data.energy=power;data.shape='DISK';data.size=size;point(ob,(2,.5,.4))
data=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(cam);sc.camera=cam
views=[
 {'key':'joined_three_quarter_640','camera_m':[5.8,-5.5,3.5],'target_m':[2.1,.4,.28],'resolution':[640,360],'ortho_scale':6.1,'lens_mm':45,'requires_full_frame':True,'purpose':'Complete chain of actual imported GLB straight, quarter-turn and closed terminal'},
 {'key':'joined_standing_640','camera_m':[5.6,-5.4,1.65],'target_m':[2.1,.40,.42],'resolution':[640,360],'ortho_scale':None,'lens_mm':45,'requires_full_frame':True,'purpose':'Ordinary standing eye Z1.65; clear front approach and continuous seat edge'},
 {'key':'joined_seated_640','camera_m':[3.8,-5.1,1.15],'target_m':[2.1,.4,.38],'resolution':[640,360],'ortho_scale':None,'lens_mm':36,'requires_full_frame':True,'purpose':'Ordinary seated eye Z1.15; seat/load relationships at seated observation height'},
 {'key':'seat_soil_support_detail_1280','camera_m':[3.25,-1.8,1.28],'target_m':[2.65,.22,.28],'resolution':[1280,720],'ortho_scale':2.4,'lens_mm':48,'requires_full_frame':False,'purpose':'Intentional construction crop: slatted timber bearing, coping, soil cavity, wall profile and flared brackets'},
 {'key':'closed_end_detail_960','camera_m':[5.35,2.42,1.15],'target_m':[3.53,1.18,.27],'resolution':[960,720],'ortho_scale':1.95,'lens_mm':48,'requires_full_frame':False,'purpose':'Intentional terminal crop: sealed basin end, connected timber termination and returned enamel coping'}]
if SELECTED:views=[v for v in views if v['key'] in SELECTED]
for v in views:
 cam.location=v['camera_m'];point(cam,v['target_m']);cam.data.type='ORTHO' if v['ortho_scale'] else 'PERSP';cam.data.lens=v['lens_mm']
 if v['ortho_scale']:cam.data.ortho_scale=v['ortho_scale']
 sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.filepath=str(ROOT/'qa'/(v['key']+'.png'))
 v['frame_preflight']=frame.assert_full_frame(sc,cam,components,.035) if v['requires_full_frame'] else frame.frame_report(sc,cam,components,.035)
 v['intentional_framing_limit']='none' if v['requires_full_frame'] else 'Construction detail; whole arrangement intentionally omitted'
 if not PREFLIGHT:bpy.ops.render.render(write_still=True)
report={'evidence_scope':'Blender imported-GLB component QA only; no game, room, actor, physics or load certification','renderer':'BLENDER_EEVEE_NEXT','denoising':False,'samples':48,'source_export_hashes':[{'asset_id':f'AST-BOT-00{i}','blend_sha256':sha(ROOT/f'AST-BOT-00{i}.blend'),'glb_sha256':sha(ROOT/f'AST-BOT-00{i}.glb')} for i in range(4,7)],'derived_start_closure_sha256':sha(ROOT/'derived/AST-BOT-006_START.glb'),'assembly_instances':placements,'views':views,'preflight_only':PREFLIGHT}
(ROOT/'qa/render_evidence.json').write_text(json.dumps(report,indent=2)+'\n')
print('PLANTER_PREFLIGHT_PASS' if PREFLIGHT else 'PLANTER_IMPORTED_RENDER_PASS')
