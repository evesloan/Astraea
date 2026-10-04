"""Actual imported clinical components, two privacy states, no recovered room."""
from pathlib import Path
import bpy,json,math,hashlib,sys,importlib.util
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT/'plan.json').read_text());PREFLIGHT='--preflight' in sys.argv
TAG=sys.argv[sys.argv.index('--tag')+1] if '--tag' in sys.argv else 'r01';assert TAG.replace('_','').isalnum();RUN=OUT/TAG;RUN.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SCRIPT_SHA=sha(Path(__file__));PLAN_SHA=sha(OUT/'plan.json')
spec=importlib.util.spec_from_file_location('qa_frame',ROOT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def matrix(p,a):return Matrix.Translation(Vector(p))@Matrix.Rotation(math.radians(a),4,'Z')
def imp(path,key,tr):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/path));objects=[o for o in bpy.context.scene.objects if o not in before];root=bpy.data.objects.new('QA_PLACEMENT_'+key,None);bpy.context.collection.objects.link(root)
 for o in objects:
  if o.parent is None:o.parent=root
 root.matrix_world=tr;bpy.context.view_layer.update();return [o for o in objects if o.type=='MESH']
def geometry(objects):
 pts=[];tri=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in objects:
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();off=len(pts);pts.extend(o.matrix_world@v.co for v in m.vertices);tri.extend(tuple(off+i for i in t.vertices) for t in m.loop_triangles);ev.to_mesh_clear()
 assert pts and tri;return pts,tri
def bounds(pts):return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
def overlap(b,z):return all(min(b['max'][i],z['max_source_m'][i])-max(b['min'][i],z['min_source_m'][i])>1e-5 for i in range(3))
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC'
parts={};records=[];frozen=[('standards/qa_frame.py',sha(ROOT/'standards/qa_frame.py')), (PLAN['privacy_source_interface'],sha(ROOT/PLAN['privacy_source_interface']))]
for item in PLAN['items']:
 hashes={k:sha(ROOT/item[k]) for k in ['path','source_path','manifest_path']};tr=matrix(item['source_origin_m'],item['source_z_rotation_deg']);obs=imp(item['path'],item['key'],tr);pts,tri=geometry(obs);b=bounds(pts)
 assert b['min'][2]>=-1e-5 and abs(b['min'][2])<1e-4,'Component must retain its floor datum'
 assert not overlap(b,PLAN['empty_component_approach']),(item['key'],'inspection approach intrusion')
 parts[item['key']]={'tr':tr,'objects':obs,'points':pts,'triangles':tri,'tree':BVHTree.FromPolygons(pts,tri,all_triangles=True),'record':item};records.append({**item,'hashes':hashes,'actual_source_bounds_m':b,'triangles':len(tri),'source_transform':[list(r) for r in tr]});frozen += [(item[k],h) for k,h in hashes.items()]
open_path=PLAN['privacy_state_exports']['open'];tr=parts['privacy']['tr'];obs=imp(open_path,'privacy_open',tr);pts,tri=geometry(obs);b=bounds(pts);assert not overlap(b,PLAN['empty_component_approach'])
parts['privacy_open']={'tr':tr,'objects':obs,'points':pts,'triangles':tri,'tree':BVHTree.FromPolygons(pts,tri,all_triangles=True)};frozen.append((open_path,sha(ROOT/open_path)))
states={'closed':parts['privacy'],'open':parts['privacy_open']};state_record={'open_export':open_path,'open_sha256':sha(ROOT/open_path),'open_bounds':b,'triangles':len(tri),'new_design':False}
# Only privacy mesh rays claim privacy behavior; other objects remain actual use context.
field=json.loads((ROOT/PLAN['privacy_source_interface']).read_text());privacy_checks=[]
for state,part in states.items():
 for row in field['rays']:
  a=tr@Vector(row['eye_source_m']);b=tr@Vector(row['target_source_m']);delta=b-a;blocked=part['tree'].ray_cast(a,delta.normalized(),delta.length)[0] is not None;expected=row['expected_'+state]=='blocked';assert blocked==expected,(state,row['name']);privacy_checks.append({'state':state,'name':row['name'],'blocked':blocked,'expected_blocked':expected,'passed':True})
 # Exact middle pad plateau is a physical component surface, never a body pose.
 support=parts['support'];meta=json.loads((ROOT/support['record']['manifest_path']).read_text());w=next(v for v in meta['physical_and_proposal_markers'] if v['name']=='PAD_2_PHYSICAL_CONTACT');target=support['tr']@Vector(w['source_m']);assert support['tree'].find_nearest(target)[3]<2e-4
 eye=Vector(PLAN['views']['privacy_'+state+'_arrival']['source_eye_m']);delta=target-eye;blocked=part['tree'].ray_cast(eye,delta.normalized(),delta.length)[0] is not None;assert blocked==(state=='closed');privacy_checks.append({'state':state,'name':'actual_middle_pad_surface_from_arrival','target_source_m':list(target),'blocked_by_privacy_component':blocked,'passed':True,'scope':'Only this actual support-surface witness, not a patient silhouette or whole platform guarantee'})
# Positive actual-solid controls plus finite clear approach lines in both states.
route_checks=[]
for state in states:
 keys=['wash','support','trolley','privacy' if state=='closed' else 'privacy_open'];points=[];triangles=[]
 for key in keys:
  off=len(points);points+=parts[key]['points'];triangles += [tuple(off+i for i in t) for t in parts[key]['triangles']]
 tree=BVHTree.FromPolygons(points,triangles,all_triangles=True)
 for x in [1.55,1.9,2.25]:
  for z in [.1,1.19,1.65,2.6]:
   a=Vector((x,-.05,z));b=Vector((x,3.7,z));delta=b-a;assert tree.ray_cast(a,delta.normalized(),delta.length)[0] is None;(route_checks.append({'state':state,'source_x':x,'source_z':z,'clear':True}))
 for key in ['wash','support','trolley']:
  p=parts[key];pts,t=p['points'],p['triangles'];t=max(t,key=lambda q:(pts[q[1]]-pts[q[0]]).cross(pts[q[2]]-pts[q[0]]).length);a,b,c=[pts[i] for i in t];normal=(b-a).cross(c-a).normalized();centre=(a+b+c)/3;assert p['tree'].ray_cast(centre+normal*.03,-normal,.061)[0] is not None
scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=48;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15
scene.world=bpy.data.worlds.new('QA_ONLY_neutral_world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.29,.30,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
mat=bpy.data.materials.new('QA_ONLY_inspection_floor');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.3,.31,.32,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=45,location=(0,1,-.004));bpy.context.object.name='QA_ONLY_floor_not_original_support';bpy.context.object.data.materials.append(mat)
for name,pos,target,energy,size in [('front',[-3,-4,6],[0,1,1.2],1600,6),('care_fill',[4,4,5],[.5,2,.8],1100,5),('rear',[-4,5,4],[0,2,1],700,4)]:
 data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=pos;data.energy=energy;data.shape='DISK';data.size=size;aim(o,target)
cd=bpy.data.cameras.new('QA_ONLY_camera');camera=bpy.data.objects.new(cd.name,cd);bpy.context.collection.objects.link(camera);scene.camera=camera;cd.clip_start=.015;cd.clip_end=100
report={'scope':PLAN['scope'],'executed_script_sha256':SCRIPT_SHA,'plan_sha256':PLAN_SHA,'items':records,'state_derivative':state_record,'privacy_checks':privacy_checks,'finite_approach_checks':route_checks,'positive_solid_controls_passed':True,'original_host_or_actor_fit':False,'source_capacity_effect':0,'views':{}}
path=RUN/('preflight.json' if PREFLIGHT else 'render_evidence.json');assert not path.exists(),'Preserve prior evidence and select a new revision tag'
for name,view in PLAN['views'].items():
 for state,part in states.items():
  for obj in part['objects']:obj.hide_render=state!=view['state'];obj.hide_viewport=state!=view['state']
 camera.location=view['source_eye_m'];aim(camera,view['source_target_m']);cd.lens=view['lens_mm'];scene.render.resolution_x=640;scene.render.resolution_y=360;bpy.context.view_layer.update();focus=[]
 for key in view['keys']:
  part=states[view['state']] if key=='privacy' else parts[key];focus+=part['objects']
 framing=frame.frame_report(scene,camera,focus,.04);assert not view['full_component_frame'] or framing['passes'],(name,framing)
 rec={**view,'framing':framing,'camera_matrix_world':[list(row) for row in camera.matrix_world],'resolution':[640,360],'executed_script_sha256':SCRIPT_SHA,'source_scope':{row['catalogue_id']:row['hashes']['path'] for row in records},'open_export_sha256':state_record['open_sha256']}
 if not PREFLIGHT:
  image=RUN/(name+'.png');assert not image.exists();scene.render.filepath=str(image);scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);rec['image_sha256']=sha(image)
 report['views'][name]=rec;report['execution_complete']=False;path.write_text(json.dumps(report,indent=2)+'\n')
assert all(sha(ROOT/p)==h for p,h in frozen),'Source changed during inspection';assert sha(Path(__file__))==SCRIPT_SHA and sha(OUT/'plan.json')==PLAN_SHA
report['inputs_unchanged_during_execution']=True;report['execution_complete']=True;path.write_text(json.dumps(report,indent=2)+'\n');print('CLINICAL_ASSEMBLY_PREFLIGHT_PASS' if PREFLIGHT else 'CLINICAL_ASSEMBLY_RENDER_PASS')
