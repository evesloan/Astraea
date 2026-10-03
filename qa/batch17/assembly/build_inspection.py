"""Actual housekeeping components in separate equipment and handling QA examples."""
from pathlib import Path
import bpy,json,math,hashlib,sys,importlib.util,shutil
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT/'plan.json').read_text());PREFLIGHT='--preflight' in sys.argv
TAG=sys.argv[sys.argv.index('--tag')+1] if '--tag' in sys.argv else 'r01'
GROUPS=set(sys.argv[sys.argv.index('--groups')+1].split(',')) if '--groups' in sys.argv else {'equipment','handling'}
assert GROUPS and GROUPS.issubset({'equipment','handling'})
ITEMS=[r for r in PLAN['items'] if r['group'] in GROUPS]
KEYS={r['key'] for r in ITEMS}
assert TAG.replace('_','').isalnum();RUN=OUT/TAG;RUN.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SCRIPT_SHA=sha(Path(__file__));PLAN_SHA=sha(OUT/'plan.json')
spec=importlib.util.spec_from_file_location('qa_frame',ROOT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def imp(row,path):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/path));objects=[o for o in bpy.context.scene.objects if o not in before]
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
assert ITEMS
for row in ITEMS:
 hashes={k:sha(ROOT/row[k]) for k in ('source_path','manifest_path')};shutil.copy2(ROOT/row['manifest_path'],snap/(row['key']+'.json'));frozen +=[(row[k],h) for k,h in hashes.items()]
 for state,path in row['variants'].items():
  obs,tr=imp(row,path);points,tri=geometry(obs);b=bounds(points);assert abs(b['min'][2])<1e-4,(row['key'],'floor datum')
  key=row['key']+'@'+state;parts[key]={'objects':obs,'transform':tr,'points':points,'triangles':tri,'tree':BVHTree.FromPolygons(points,tri,all_triangles=True),'record':row,'bounds':b};records.append({'key':key,'row_key':row['key'],'state':state,'group':row['group'],'export':path,'export_sha256':sha(ROOT/path),'base_hashes':hashes,'actual_source_bounds_m':b,'triangles':len(tri),'source_transform':[list(x) for x in tr]});frozen.append((path,sha(ROOT/path)))
space_checks=[]
for box in PLAN['proposed_empty_regions']:
 if box['group'] not in GROUPS:continue
 for key,part in parts.items():
  if part['record']['group']!=box['group']:continue
  hits=[]
  for t in part['triangles']:
   if triangle_in_box(part['points'],t,box):hits.append([list(part['points'][i]) for i in t]);break
  if hits:(RUN/'failed_empty_space.json').write_text(json.dumps({'part':key,'box':box,'hits':hits,'plan_sha256':PLAN_SHA},indent=2)+'\n')
  assert not hits,(box['id'],key,hits)
  space_checks.append({'part_state':key,'region':box['id'],'passed':True,'method':'All actual imported mesh triangles against strict box interior; no actor/cart/species inference'})
controls=[]
for key,part in parts.items():
 p=part['points'];t=max(part['triangles'],key=lambda q:(p[q[1]]-p[q[0]]).cross(p[q[2]]-p[q[0]]).length);a,b,c=[p[i] for i in t];n=(b-a).cross(c-a).normalized();centre=(a+b+c)/3
 assert part['tree'].ray_cast(centre+n*.03,-n,.061)[0] is not None;controls.append({'part_state':key,'actual_solid_control':True})
scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=48;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15
scene.world=bpy.data.worlds.new('QA_ONLY_neutral_world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.29,.30,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
mat=bpy.data.materials.new('QA_ONLY_floor');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.30,.31,.32,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=45,location=(0,0,-.004));bpy.context.object.name='QA_ONLY_floor_not_original_support';bpy.context.object.data.materials.append(mat)
for name,pos,target,energy,size in [('front',[-3,-4,6],[0,1,1],1600,6),('fill',[4,4,5],[0,1,1],1100,5),('rear',[-4,5,4],[0,1,1.4],700,4)]:
 data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=pos;data.energy=energy;data.shape='DISK';data.size=size;aim(o,target)
cd=bpy.data.cameras.new('QA_ONLY_camera');camera=bpy.data.objects.new(cd.name,cd);bpy.context.collection.objects.link(camera);scene.camera=camera;cd.clip_start=.015;cd.clip_end=100
report={'scope':PLAN['scope'],'captured_groups':sorted(GROUPS),'input_scope':'Only the displayed component groups are imported and hash-frozen; other catalogue work is outside this capture scope','executed_script_sha256':SCRIPT_SHA,'plan_sha256':PLAN_SHA,'items':records,'empty_space_checks':space_checks,'positive_controls':controls,'original_host_or_actor_fit':False,'source_capacity_effect':0,'contexts_are_not_connected_rooms':True,'views':{}}
path=RUN/('preflight.json' if PREFLIGHT else 'render_evidence.json');assert not path.exists(),'Use fresh tag, retain prior evidence'
for name,view in PLAN['views'].items():
 if not set(view['states']).issubset(KEYS):continue
 selected=[key+'@'+state for key,state in view['states'].items()]
 for key,part in parts.items():
  for o in part['objects']:o.hide_render=key not in selected;o.hide_viewport=key not in selected
 camera.location=view['source_eye_m'];aim(camera,view['source_target_m']);cd.lens=view['lens_mm'];scene.render.resolution_x=640;scene.render.resolution_y=360;bpy.context.view_layer.update()
 focus=[o for key in selected for o in parts[key]['objects']];framing=frame.frame_report(scene,camera,focus,.04);assert framing['passes'],(name,framing)
 rec={**view,'framing':framing,'selected_part_states':selected,'camera_matrix_world':[list(row) for row in camera.matrix_world],'resolution':[640,360],'executed_script_sha256':SCRIPT_SHA}
 if not PREFLIGHT:
  image=RUN/(name+'.png');assert not image.exists();scene.render.filepath=str(image);scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);rec['image_sha256']=sha(image)
 report['views'][name]=rec;report['execution_complete']=False;path.write_text(json.dumps(report,indent=2)+'\n')
assert all(sha(ROOT/p)==h for p,h in frozen),'Input changed during inspection';assert sha(Path(__file__))==SCRIPT_SHA and sha(OUT/'plan.json')==PLAN_SHA
report['inputs_unchanged_during_execution']=True;report['execution_complete']=True;path.write_text(json.dumps(report,indent=2)+'\n');print('HOUSEKEEPING_EXAMPLES_PREFLIGHT_PASS' if PREFLIGHT else 'HOUSEKEEPING_EXAMPLES_RENDER_PASS')
