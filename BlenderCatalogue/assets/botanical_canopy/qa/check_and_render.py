"""Reload editable source and render only actual imported GLB. No denoiser.
Use -- --preflight-only for cheap source/contact/framing checks without a render.
"""
import bpy,bmesh,math,json,sys,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('qa_frame',CAT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
PREFLIGHT='--preflight-only' in sys.argv
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'AST-BOT-001.blend'))
checks=[];issues=[];dg=bpy.context.evaluated_depsgraph_get();leaf_boundary=0
for ob in bpy.context.scene.objects:
 if ob.type not in ('MESH','CURVE'):continue
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg));me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
 raw_boundary=sum(e.is_boundary for e in bm.edges)
 if ob.type=='CURVE':bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
 folded=ob.get('semantic_kind')=='open_folded_leaf_surfaces'
 if not folded and (nonmanifold or volume<=0):issues.append({'object':ob.name,'issue':'Closed support topology/volume','boundary':boundary,'nonmanifold':nonmanifold,'volume':volume})
 if folded:leaf_boundary+=boundary
 checks.append({'name':ob.name,'type':ob.type,'semantic_kind':ob.get('semantic_kind'),'triangles':len(me.loop_triangles),'raw_curve_cap_split_boundary_edges':raw_boundary if ob.type=='CURVE' else None,'boundary_edges_after_geometric_weld':boundary,'nonmanifold_edges':nonmanifold,'signed_volume_m3':volume if not folded else None,'editable_path_points':len(ob.data.splines[0].points) if ob.type=='CURVE' else None})
 bm.free();bpy.data.meshes.remove(me)
leaf_contact_count=0
for ob in bpy.context.scene.objects:
 if ob.get('semantic_kind')!='open_folded_leaf_surfaces':continue
 for i,record in enumerate(json.loads(ob['leaf_attachment_records'])):
  base=ob.data.vertices[i*8].co;petiole=bpy.data.objects[record['petiole']];tip=Vector(petiole.data.splines[0].points[-1].co[:3]);gap=(base-tip).length;leaf_contact_count+=1
  if gap>1e-6:issues.append({'object':ob.name,'leaf_index':i,'issue':'Leaf-to-petiole gap in actual source','gap_m':gap})
contacts=json.loads((ROOT/'qa/support_contacts.json').read_text())
for c in contacts['branch_contacts']:
 ob=bpy.data.objects[c['child']];actual=Vector(ob.data.splines[0].points[0].co[:3]);record=Vector(c['start_m'])
 if (actual-record).length>1e-6:issues.append({'object':ob.name,'issue':'Recorded contact differs from actual path'})
 parent=bpy.data.objects[c['parent']];best=999
 pts=parent.data.splines[0].points
 for p,q in zip(pts[:-1],pts[1:]):
  a,b=Vector(p.co[:3]),Vector(q.co[:3]);v=b-a;t=max(0,min(1,(actual-a).dot(v)/v.length_squared));distance=(actual-a-v*t).length;radius=p.radius+(q.radius-p.radius)*t;best=min(best,distance-radius)
 if best>0:issues.append({'object':ob.name,'issue':'Child root lies outside actual parent radius','clearance_m':best})
report={'status':'PASS' if not issues else 'FAIL','source_sha256':sha(ROOT/'AST-BOT-001.blend'),'objects':len(checks),'curve_paths':sum(c['type']=='CURVE' for c in checks),'closed_support_count':sum(c['type']=='CURVE' for c in checks),'leaf_groups':sum(c['type']=='MESH' for c in checks),'leaf_boundary_edges_intentional':leaf_boundary,'support_contacts_checked':len(contacts['branch_contacts']),'actual_leaf_to_petiole_contacts_checked':leaf_contact_count,'parts':checks,'issues':issues,'scope':'Source reload; evaluated curve caps checked after a 1e-6 m coincident-vertex weld (also performed for final GLB); support topology and path-to-parent contact; not runtime physics'}
(ROOT/'qa/source_reload_validation.json').write_text(json.dumps(report,indent=2));assert not issues,issues
if '--checks-only' in sys.argv:
 print('CANOPY_SOURCE_CHECKS_OK');sys.exit(0)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'AST-BOT-001.glb'));components=[o for o in bpy.context.scene.objects if o.type=='MESH']
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=48;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.cycles.use_denoising=False
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
sc.world=bpy.data.worlds.new('QA_ONLY_neutral_world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.37,.40,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
mat=bpy.data.materials.new('QA_ONLY_ground');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.22,.235,.24,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004));bpy.context.object.name='QA_ONLY_ground';bpy.context.object.data.materials.append(mat)
for name,loc,power,size in [('key',(-3,-4,6),850,4),('fill',(4,-1,3.5),480,4),('back',(1,4,5),700,3)]:
 data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=loc;data.energy=power;data.shape='DISK';data.size=size;aim(o,(0,0,1.4))
data=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(cam);sc.camera=cam
views=[
 {'key':'canopy_imported_full_640','camera_m':[4.7,-7.0,4.1],'target_m':[.0,.0,1.36],'resolution':[640,360],'ortho_scale':6.90,'requires_full_frame':True,'purpose':'Complete actual-GLB silhouette with visible trunk and layered leaf groups'},
 {'key':'canopy_imported_standing_640','camera_m':[4.4,-7.3,1.65],'target_m':[0,0,1.33],'resolution':[640,360],'ortho_scale':None,'lens_mm':45,'requires_full_frame':True,'purpose':'Standing eye Z1.65 m from soil plane; neutral component proof, not seated placement'},
 {'key':'canopy_imported_branch_detail_1280','camera_m':[-2.9,-4.3,2.70],'target_m':[-.16,-.04,1.86],'resolution':[1280,720],'ortho_scale':3.05,'requires_full_frame':False,'purpose':'Intentional upper trunk and crown detail crop: overlapping support joins, thin folded leaf profiles and opaque materials'}]
for v in views:
 cam.location=v['camera_m'];aim(cam,v['target_m']);cam.data.type='ORTHO' if v['ortho_scale'] else 'PERSP';cam.data.lens=v.get('lens_mm',48)
 if v['ortho_scale']:cam.data.ortho_scale=v['ortho_scale']
 sc.render.resolution_x,sc.render.resolution_y=v['resolution'];sc.render.filepath=str(ROOT/'qa'/(v['key']+'_raw.png'))
 v['frame_preflight']=frame.assert_full_frame(sc,cam,components,.045) if v['requires_full_frame'] else frame.frame_report(sc,cam,components,.045)
 if not PREFLIGHT:bpy.ops.render.render(write_still=True)
(ROOT/'qa/render_evidence.json').write_text(json.dumps({'asset_id':'AST-BOT-001','evidence_scope':'Blender imported-GLB component QA only','glb_sha256':sha(ROOT/'AST-BOT-001.glb'),'renderer':'BLENDER_EEVEE_NEXT','render_samples':48,'denoising':False,'views':views,'preflight_only':PREFLIGHT,'qa_helpers_excluded_from_asset':'floor, lights, camera'},indent=2))
print('CANOPY_PREFLIGHT_OK' if PREFLIGHT else 'CANOPY_IMPORTED_RENDER_COMPLETE')
