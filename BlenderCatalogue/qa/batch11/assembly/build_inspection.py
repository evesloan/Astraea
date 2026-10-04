"""Frozen actual-GLB landing arrangement checks and ordinary-height QA captures."""
from pathlib import Path
import bpy,json,math,hashlib,sys,importlib.util
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT/'plan.json').read_text());PREFLIGHT='--preflight' in sys.argv
TAG=sys.argv[sys.argv.index('--tag')+1] if '--tag' in sys.argv else 'r01'
assert TAG.isalnum() or TAG.replace('_','').isalnum()
RUN=OUT/TAG;RUN.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SCRIPT_SHA=sha(Path(__file__));PLAN_SHA=sha(OUT/'plan.json')
spec=importlib.util.spec_from_file_location('qa_frame',ROOT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def transform(p,a):return Matrix.Translation(Vector(p))@Matrix.Rotation(math.radians(a),4,'Z')
def ship(p):return Vector((p.x-44,p.z,-p.y-378))
def source(p):return Vector((p[0]+44,-p[2]-378,p[1]))
def imp(path,key,tr):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/path));objects=[o for o in bpy.context.scene.objects if o not in before]
 root=bpy.data.objects.new('QA_PLACEMENT_'+key,None);bpy.context.collection.objects.link(root)
 for o in objects:
  if o.parent is None:o.parent=root
 root.matrix_world=tr;bpy.context.view_layer.update();return [o for o in objects if o.type=='MESH']
def geometry(objects):
 pts=[];tri=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in objects:
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();off=len(pts);pts.extend(o.matrix_world@v.co for v in m.vertices);tri.extend(tuple(off+i for i in t.vertices) for t in m.loop_triangles);ev.to_mesh_clear()
 assert pts and tri;return pts,tri
def bounds(pts):
 w=[ship(p) for p in pts];return {'min':[min(p[i] for p in w) for i in range(3)],'max':[max(p[i] for p in w) for i in range(3)]}
def overlaps(b,z):return min(b['max'][0],z['ship_x'][1])-max(b['min'][0],z['ship_x'][0])>1e-5 and min(b['max'][2],z['ship_z'][1])-max(b['min'][2],z['ship_z'][0])>1e-5
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC'
assert len(PLAN['items'])==4 and len(PLAN['context'])==2,'Final proposed assembly requires four components and two disclosed reused fixtures'
parts={};records=[];contexts=[];allp=[];allt=[];frozen=[]
for entry in PLAN['author_interface_inputs']:
 assert sha(ROOT/entry['path'])==entry['sha256'],'Author interface changed; refresh before a new preflight'
 frozen.append((entry['path'],entry['sha256']))
frozen.append(('standards/qa_frame.py',sha(ROOT/'standards/qa_frame.py')))
for row in PLAN['items']:
 hashes={k:sha(ROOT/row[k]) for k in ['path','source_path','manifest_path']};tr=transform(row['inspection_source_origin_m'],row['source_z_rotation_deg']);obs=imp(row['path'],row['key'],tr);pts,tri=geometry(obs);b=bounds(pts);expected=row['candidate_ship_bounds_m']
 assert all(b['min'][i]>=expected['min'][i]-1e-4 and b['max'][i]<=expected['max'][i]+1e-4 for i in range(3)),(row['key'],b,expected)
 for zone in PLAN['empty_plan_reservations']:assert not overlaps(b,zone),(row['key'],zone['name'])
 off=len(allp);allp+=pts;allt += [tuple(off+i for i in t) for t in tri]
 parts[row['key']]={'tr':tr,'objects':obs,'points':pts,'triangles':tri,'tree':BVHTree.FromPolygons(pts,tri,all_triangles=True),'record':row}
 records.append({**row,'hashes':hashes,'actual_ship_bounds_m':b,'triangles':len(tri),'actual_source_transform':[list(r) for r in tr]});frozen += [(row[k],v) for k,v in hashes.items()]
for row in PLAN['context']:
 parent=parts[row['parent']];tr=parent['tr']@Matrix(row['parent_local_source_matrix']);obs=imp(row['path'],row['key'],tr);pts,tri=geometry(obs);b=bounds(pts);expected=parent['record']['candidate_ship_bounds_m'];h=sha(ROOT/row['path'])
 assert all(b['min'][i]>=expected['min'][i]-1e-4 and b['max'][i]<=expected['max'][i]+1e-4 for i in range(3)),('fixture housing outside component envelope',row['key'],b,expected)
 for zone in PLAN['empty_plan_reservations']:assert not overlaps(b,zone),(row['key'],zone['name'])
 parts[row['key']]={'objects':obs};off=len(allp);allp+=pts;allt += [tuple(off+i for i in t) for t in tri];contexts.append({**row,'sha256':h,'actual_ship_bounds_m':b,'triangles':len(tri),'new_design':False});frozen.append((row['path'],h))
world=BVHTree.FromPolygons(allp,allt,all_triangles=True);checks=[]
def ray(name,a,b,expected):
 a=source(a);b=source(b);delta=b-a;hit=world.ray_cast(a,delta.normalized(),delta.length)[0];passed=(hit is not None)==expected;checks.append({'name':name,'expected_hit':expected,'actual_hit':hit is not None,'passed':passed});assert passed,name
for x in [-38.3,-37,-35.7]:
 for y in [.2,1.19,1.65,2.65]:ray('guest_empty_%s_%s'%(x,y),(x,y,-374.1),(x,y,-377.9),False)
for z in [-377.8,-376,-374.2]:
 for y in [.2,1.19,1.65,2.65]:ray('staff_side_entry_%s_%s'%(z,y),(-53.9,y,z),(-49.3,y,z),False)
for key in ['guest_directory','guest_waiting','staff_return','staff_stow']:
 part=parts[key];pts,tri=part['points'],part['triangles'];t=max(tri,key=lambda t:(pts[t[1]]-pts[t[0]]).cross(pts[t[2]]-pts[t[0]]).length);a,b,c=[pts[i] for i in t];normal=(b-a).cross(c-a).normalized();centre=(a+b+c)/3;start=centre+normal*.03;end=centre-normal*.03;hit=part['tree'].ray_cast(start,(end-start).normalized(),.061)[0];assert hit is not None;checks.append({'name':key+'_actual_solid_control','passed':True})
assert overlaps({'min':[-37.1,0,-376.1],'max':[-36.9,1,-375.9]},PLAN['empty_plan_reservations'][0]),'Injected zone blocker must be detected'
scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=48;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15
scene.world=bpy.data.worlds.new('QA_ONLY_neutral_world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.29,.30,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
mat=bpy.data.materials.new('QA_ONLY_inspection_floor');mat.diffuse_color=(.3,.31,.32,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.3,.31,.32,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9
bpy.ops.mesh.primitive_plane_add(size=50,location=(0,-1,-.004));bpy.context.object.name='QA_ONLY_floor_not_recovered_support';bpy.context.object.data.materials.append(mat)
for name,pos,target,energy,size in [('guest_key',[5,-5,6],[7,-.6,1.3],1500,6),('guest_fill',[10,2,5],[7,-.6,1.4],900,5),('staff_key',[-10,-3,6],[-4.5,-1.9,1.2],1400,6),('staff_fill',[-1,2,4],[-4.5,-1.9,1.2],700,4)]:
 d=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(d.name,d);bpy.context.collection.objects.link(o);o.location=pos;d.energy=energy;d.shape='DISK';d.size=size;aim(o,target)
cd=bpy.data.cameras.new('QA_ONLY_camera');camera=bpy.data.objects.new(cd.name,cd);bpy.context.collection.objects.link(camera);scene.camera=camera;cd.clip_start=.015;cd.clip_end=100
report={'scope':'Actual imported component arrangement; original core/doors/support/headroom and actor/cart acceptance unknown','plan_sha256':PLAN_SHA,'executed_script_sha256':SCRIPT_SHA,'items':records,'context':contexts,'finite_clear_and_blocked_checks':checks,'source_geometry_triangles':len(allt),'views':{},'fixture_emission_is_not_room_lighting_acceptance':True}
path=RUN/('preflight.json' if PREFLIGHT else 'render_evidence.json');assert not path.exists(),'Preserve existing reports; choose a fresh version tag'
for name,v in PLAN['views'].items():
 camera.location=v['source_eye_m'];aim(camera,v['source_target_m']);cd.lens=v['lens_mm'];scene.render.resolution_x=640;scene.render.resolution_y=360;bpy.context.view_layer.update();focus=[o for key in v['keys'] for o in parts[key]['objects']];fr=frame.frame_report(scene,camera,focus,margin=.04)
 rec={**v,'framing':fr,'camera_matrix_world':[list(r) for r in camera.matrix_world],'resolution':[640,360],'executed_script_sha256':SCRIPT_SHA,'source_scope':{r['catalogue_id']:r['hashes']['path'] for r in records}}
 if v['full_component_frame']:assert fr['passes'],(name,fr)
 if not PREFLIGHT:
  image=RUN/(name+'.png');assert not image.exists();scene.render.filepath=str(image);scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);rec['image_sha256']=sha(image)
 report['views'][name]=rec;report['execution_complete']=False;path.write_text(json.dumps(report,indent=2)+'\n')
assert all(sha(ROOT/p)==h for p,h in frozen),'Source changed during inspection';assert sha(Path(__file__))==SCRIPT_SHA and sha(OUT/'plan.json')==PLAN_SHA
report['inputs_unchanged_during_execution']=True;report['execution_complete']=True;path.write_text(json.dumps(report,indent=2)+'\n');print('LANDING_ASSEMBLY_PREFLIGHT_PASS' if PREFLIGHT else 'LANDING_ASSEMBLY_RENDER_PASS')
