"""Imported aquatic arrival/use components; separate QA examples, no recovered room."""
from pathlib import Path
import bpy,json,math,hashlib,sys,importlib.util,shutil
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT/'plan.json').read_text());PREFLIGHT='--preflight' in sys.argv
TAG=sys.argv[sys.argv.index('--tag')+1] if '--tag' in sys.argv else 'r01'
assert TAG.replace('_','').isalnum();RUN=OUT/TAG;RUN.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SCRIPT_SHA=sha(Path(__file__));PLAN_SHA=sha(OUT/'plan.json')
spec=importlib.util.spec_from_file_location('qa_frame',ROOT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def imp(row):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/row['path']));objects=[o for o in bpy.context.scene.objects if o not in before]
 root=bpy.data.objects.new('QA_PLACEMENT_'+row['key'],None);bpy.context.collection.objects.link(root)
 for o in objects:
  if o.parent is None:o.parent=root
 tr=Matrix.Translation(Vector(row['source_origin_m']))@Matrix.Rotation(math.radians(row['source_z_rotation_deg']),4,'Z');root.matrix_world=tr;bpy.context.view_layer.update()
 return [o for o in objects if o.type=='MESH'],tr
def geometry(obs):
 points=[];tri=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in obs:
  ev=o.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles();off=len(points);points.extend(o.matrix_world@v.co for v in mesh.vertices);tri.extend(tuple(off+i for i in t.vertices) for t in mesh.loop_triangles);ev.to_mesh_clear()
 assert points and tri;return points,tri
def bounds(p):return {'min':[min(x[i] for x in p) for i in range(3)],'max':[max(x[i] for x in p) for i in range(3)]}
def clip(poly,axis,value,sign):
 if not poly:return []
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-value)*sign;db=(b[axis]-value)*sign;ina=da>=0;inb=db>=0
  if ina:result.append(a)
  if ina!=inb:result.append(a+(b-a)*(da/(da-db)))
 return result
def triangle_in_box(points,tri,box):
 lo=Vector(box['min_source_m'])+Vector((1e-5,)*3);hi=Vector(box['max_source_m'])-Vector((1e-5,)*3)
 if any(max(points[i][a] for i in tri)<lo[a] or min(points[i][a] for i in tri)>hi[a] for a in range(3)):return False
 poly=[points[i] for i in tri]
 for axis in range(3):poly=clip(poly,axis,lo[axis],1);poly=clip(poly,axis,hi[axis],-1)
 return len(poly)>=3 and sum((poly[i]-poly[0]).cross(poly[i+1]-poly[0]).length for i in range(1,len(poly)-1))>1e-10
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC'
parts={};records=[];frozen=[('standards/qa_frame.py',sha(ROOT/'standards/qa_frame.py'))]
snap=RUN/('preflight_manifests' if PREFLIGHT else 'captured_manifests');snap.mkdir(exist_ok=True)
assert len(PLAN['items'])==4
for row in PLAN['items']:
 hashes={k:sha(ROOT/row[k]) for k in ('path','source_path','manifest_path')};shutil.copy2(ROOT/row['manifest_path'],snap/(row['key']+'.json'));obs,tr=imp(row);points,tri=geometry(obs);b=bounds(points);assert b['min'][2]>=-1e-5 and abs(b['min'][2])<1e-4,(row['key'],'floor datum')
 parts[row['key']]={'objects':obs,'transform':tr,'points':points,'triangles':tri,'tree':BVHTree.FromPolygons(points,tri,all_triangles=True),'record':row,'bounds':b};records.append({**row,'hashes':hashes,'actual_source_bounds_m':b,'triangles':len(tri),'source_transform':[list(x) for x in tr]});frozen +=[(row[k],h) for k,h in hashes.items()]
used=parts['used'];openrow={**used['record'],'key':'used_withdrawn','path':PLAN['withdrawn_export']};obs,tr=imp(openrow);points,tri=geometry(obs);b=bounds(points);assert b['min'][2]>=-1e-5 and abs(b['min'][2])<1e-4
parts['used_withdrawn']={'objects':obs,'transform':tr,'points':points,'triangles':tri,'tree':BVHTree.FromPolygons(points,tri,all_triangles=True),'record':openrow,'bounds':b};frozen.append((PLAN['withdrawn_export'],sha(ROOT/PLAN['withdrawn_export'])))
state_record={'export':PLAN['withdrawn_export'],'sha256':sha(ROOT/PLAN['withdrawn_export']),'actual_source_bounds_m':b,'triangles':len(tri),'counts_as_new_design':False}
space_checks=[]
for state in ['closed','withdrawn']:
 keys=['clean','refreshment','rinse','used' if state=='closed' else 'used_withdrawn']
 for box in PLAN['proposed_empty_regions']:
  hits=[]
  for key in keys:
   part=parts[key]
   for t in part['triangles']:
    if triangle_in_box(part['points'],t,box):hits.append({'part':key,'triangle_source_m':[list(part['points'][i]) for i in t]});break
  if hits:(RUN/'failed_empty_space.json').write_text(json.dumps({'state':state,'box':box,'hits':hits,'plan_sha256':PLAN_SHA,'executed_script_sha256':SCRIPT_SHA},indent=2)+'\n')
  assert not hits,(state,box['id'],hits)
  space_checks.append({'state':state,'region':box['id'],'passed':True,'method':'All imported mesh triangles clipped against the strict interior of the declared box; no actor, species or cart inference'})
controls=[]
for key,part in parts.items():
 p=part['points'];t=max(part['triangles'],key=lambda q:(p[q[1]]-p[q[0]]).cross(p[q[2]]-p[q[0]]).length);a,b,c=[p[i] for i in t];n=(b-a).cross(c-a).normalized();centre=(a+b+c)/3
 assert part['tree'].ray_cast(centre+n*.03,-n,.061)[0] is not None;controls.append({'part':key,'actual_solid_control':True})
scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=48;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15
scene.world=bpy.data.worlds.new('QA_ONLY_neutral_world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.29,.30,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
mat=bpy.data.materials.new('QA_ONLY_floor');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.30,.31,.32,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=45,location=(0,0,-.004));bpy.context.object.name='QA_ONLY_floor_not_original_support';bpy.context.object.data.materials.append(mat)
for name,pos,target,energy,size in [('front',[-3,-4,6],[.5,.5,1],1600,6),('fill',[4,4,5],[.5,.5,1],1100,5),('rear',[-4,5,4],[.5,.5,1.4],700,4)]:
 data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=pos;data.energy=energy;data.shape='DISK';data.size=size;aim(o,target)
cd=bpy.data.cameras.new('QA_ONLY_camera');camera=bpy.data.objects.new(cd.name,cd);bpy.context.collection.objects.link(camera);scene.camera=camera;cd.clip_start=.015;cd.clip_end=100
report={'scope':PLAN['scope'],'executed_script_sha256':SCRIPT_SHA,'plan_sha256':PLAN_SHA,'items':records,'withdrawn_state':state_record,'empty_space_checks':space_checks,'positive_controls':controls,'original_host_or_actor_fit':False,'source_capacity_effect':0,'views':{}}
path=RUN/('preflight.json' if PREFLIGHT else 'render_evidence.json');assert not path.exists(),'Preserve previous evidence using a fresh tag'
for name,view in PLAN['views'].items():
 for key in ['used','used_withdrawn']:
  visible=(key=='used')==(view['state']=='closed')
  for o in parts[key]['objects']:o.hide_render=not visible;o.hide_viewport=not visible
 camera.location=view['source_eye_m'];aim(camera,view['source_target_m']);cd.lens=view['lens_mm'];scene.render.resolution_x=640;scene.render.resolution_y=360;bpy.context.view_layer.update()
 keys=[('used_withdrawn' if x=='used' and view['state']=='withdrawn' else x) for x in view['keys']];focus=[o for key in keys for o in parts[key]['objects']];framing=frame.frame_report(scene,camera,focus,.04);assert not view['full_component_frame'] or framing['passes'],(name,framing)
 rec={**view,'framing':framing,'camera_matrix_world':[list(row) for row in camera.matrix_world],'resolution':[640,360],'executed_script_sha256':SCRIPT_SHA,'source_scope':{row['key']:row['hashes']['path'] for row in records},'withdrawn_export_sha256':state_record['sha256']}
 if not PREFLIGHT:
  image=RUN/(name+'.png');assert not image.exists();scene.render.filepath=str(image);scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);rec['image_sha256']=sha(image)
 report['views'][name]=rec;report['execution_complete']=False;path.write_text(json.dumps(report,indent=2)+'\n')
assert all(sha(ROOT/p)==h for p,h in frozen),'Input changed during inspection';assert sha(Path(__file__))==SCRIPT_SHA and sha(OUT/'plan.json')==PLAN_SHA
report['inputs_unchanged_during_execution']=True;report['execution_complete']=True;path.write_text(json.dumps(report,indent=2)+'\n');print('AQUATIC_USE_PREFLIGHT_PASS' if PREFLIGHT else 'AQUATIC_USE_RENDER_PASS')
