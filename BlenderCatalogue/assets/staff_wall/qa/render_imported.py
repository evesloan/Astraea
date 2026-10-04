"""Reproducible imported-GLB staff component checks and labelled evidence.
No room or game geometry; QA-only floor, lights and cameras. Eevee, no OIDN.
Use -- --preflight-only to check sources and cameras without rendering.
"""
import bpy,bmesh,json,math,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
PREFLIGHT='--preflight-only' in sys.argv

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def point(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def import_asset(ident,location,yaw=0):
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/(ident+'.glb')))
 T=Matrix.Translation(Vector(location))@Matrix.Rotation(math.radians(yaw),4,'Z')
 obs=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
 for ob in obs:ob.matrix_world=T@ob.matrix_world;ob.name=ident+'_'+ob.name
 return obs

def source_checks():
 rows=[]
 for path in sorted(ROOT.glob('*.blend')):
  bpy.ops.wm.open_mainfile(filepath=str(path));parts=[];issues=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   bm=bmesh.new();bm.from_mesh(ob.data);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
   if nonmanifold or volume<=0:issues.append(ob.name)
   parts.append({'name':ob.name,'nonmanifold_edges':nonmanifold,'signed_volume_m3':volume,'editable_modifiers':[m.type for m in ob.modifiers]})
  rows.append({'source':path.name,'sha256':sha(path),'source_mesh_parts':len(parts),'parts':parts,'issues':issues,'status':'PASS' if not issues else 'FAIL'})
 (ROOT/'qa/source_reload_validation.json').write_text(json.dumps(rows,indent=2));assert all(r['status']=='PASS' for r in rows)
 return rows

source_checks()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
placements=[{'asset_id':'AST-STF-002','translation_m':[0,0,0],'rotation_z_deg':0}, {'asset_id':'AST-STF-001','translation_m':[.3,0,0],'rotation_z_deg':0}, {'asset_id':'AST-STF-001','translation_m':[0,-1.5,0],'rotation_z_deg':90}, {'asset_id':'AST-STF-003','translation_m':[1.5,0,0],'rotation_z_deg':0}]
components=[]
for p in placements:components+=import_asset(p['asset_id'],p['translation_m'],p['rotation_z_deg'])
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.render.threads_mode='FIXED';sc.render.threads=4
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.cycles.use_denoising=False
sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.39,.44,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
mat=bpy.data.materials.new('QA_ONLY_floor');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.20,.23,.26,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
bpy.ops.mesh.primitive_plane_add(size=200,location=(.5,-.5,-.004));bpy.context.object.name='QA_ONLY_floor';bpy.context.object.data.materials.append(mat)
for name,loc,power,size in [('key',(2.5,-3.5,6),800,4),('fill',(4,1,3.3),600,3),('side',(-2,-4,3),500,3)]:
 data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=loc;data.energy=power;data.shape='DISK';data.size=size;point(ob,(.6,-.5,1.2))
data=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(cam);sc.camera=cam
views=[
 {'key':'joined_full_silhouette_640','camera_m':[4.8,-6.5,3.7],'target_m':[.6,-.6,1.3],'resolution':[640,360],'ortho_scale':5.9,'lens_mm':48,'requires_full_frame':True,'purpose':'Complete joined arrangement silhouette, all three imported final GLBs'},
 {'key':'joined_eye_height_640','camera_m':[4.7,-6.7,1.65],'target_m':[.52,-.53,1.65],'resolution':[640,360],'ortho_scale':None,'lens_mm':48,'requires_full_frame':False,'purpose':'Eye is exactly Z1.65 m. Component context only; no actor or route certification'},
 {'key':'corner_bumper_cove_detail_1280','camera_m':[1.25,-1.62,.88],'target_m':[.13,-.16,.50],'resolution':[1280,720],'ortho_scale':1.42,'lens_mm':48,'requires_full_frame':False,'purpose':'Intentional construction crop: true L guard joint, foot cove and panel seams'},
 {'key':'closed_terminal_detail_1280','camera_m':[2.68,-.87,1.36],'target_m':[1.525,-.045,1.30],'resolution':[960,1280],'ortho_scale':3.0,'lens_mm':48,'requires_full_frame':False,'purpose':'Closed folded terminal, tapered rubber cap and end of floor cove'}]
for v in views:
 cam.location=v['camera_m'];point(cam,v['target_m']);cam.data.type='ORTHO' if v['ortho_scale'] else 'PERSP';cam.data.lens=v['lens_mm']
 if v['ortho_scale']:cam.data.ortho_scale=v['ortho_scale']
 sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.filepath=str(ROOT/'qa'/(v['key']+'.png'))
 v['frame_preflight']=frame.assert_full_frame(sc,cam,components,.035) if v['requires_full_frame'] else frame.frame_report(sc,cam,components,.035)
 v['intentional_framing_limit']='none' if v['requires_full_frame'] else 'Construction/detail or ordinary-height contextual frame may omit parts outside the stated purpose'
 if not PREFLIGHT:bpy.ops.render.render(write_still=True)
manifest={'evidence_scope':'Blender imported-GLB component evidence only; no game, room, rig, physics or route acceptance','renderer':'BLENDER_EEVEE_NEXT','samples':48,'denoising':False,'source_export_hashes':[{'asset_id':f'AST-STF-00{i}','blend_sha256':sha(ROOT/f'AST-STF-00{i}.blend'),'glb_sha256':sha(ROOT/f'AST-STF-00{i}.glb')} for i in range(1,4)],'assembly_instances':placements,'views':views,'inspection_helpers':'Neutral floor, area lights and cameras excluded from authored assets','preflight_only':PREFLIGHT}
(ROOT/'qa/render_evidence.json').write_text(json.dumps(manifest,indent=2))
print('STAFF_WALL_PREFLIGHT_OK' if PREFLIGHT else 'STAFF_WALL_IMPORTED_RENDER_COMPLETE')
