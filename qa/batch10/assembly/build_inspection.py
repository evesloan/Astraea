"""Actual-GLB connected component QA; no original host, game or room recovery."""
from pathlib import Path
import bpy,json,math,hashlib,sys,importlib.util
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT/'plan.json').read_text());PREFLIGHT='--preflight' in sys.argv
ONLY=sys.argv[sys.argv.index('--only')+1] if '--only' in sys.argv else None
spec=importlib.util.spec_from_file_location('frame_tools',ROOT/'standards/qa_frame.py');frame=importlib.util.module_from_spec(spec);spec.loader.exec_module(frame)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
EXECUTED_SCRIPT_SHA=sha(Path(__file__))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def matrix(p,angle):return Matrix.Translation(Vector(p))@Matrix.Rotation(math.radians(angle),4,'Z')
def import_part(path,key,transform):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/path));obs=[o for o in bpy.context.scene.objects if o not in before]
 wrapper=bpy.data.objects.new('QA_PLACEMENT_'+key,None);bpy.context.collection.objects.link(wrapper)
 for o in obs:
  if o.parent is None:o.parent=wrapper
 wrapper.matrix_world=transform;bpy.context.view_layer.update()
 return wrapper,[o for o in obs if o.type=='MESH']
def mesh_geometry(obs):
 points=[];polys=[];dg=bpy.context.evaluated_depsgraph_get()
 for ob in obs:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();base=len(points);points.extend([ob.matrix_world@v.co for v in me.vertices]);polys.extend([tuple(base+i for i in t.vertices) for t in me.loop_triangles]);ev.to_mesh_clear()
 assert points and polys
 return points,polys
def bounds(points):
 lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 return {'min_inspection_source_m':lo,'max_inspection_source_m':hi,'min_ship_m':[lo[0]+52,lo[2],-hi[1]],'max_ship_m':[hi[0]+52,hi[2],-lo[1]]}
def material(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.9;return m
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC'
parts={};records=[];context=[];geometry={};all_points=[];all_polys=[]
for item in PLAN['items']:
 before_hashes={k:sha(ROOT/item[k]) for k in ('path','source_path','manifest_path')};tr=matrix(item['inspection_source_origin_m'],item['source_z_rotation_deg']);wrapper,obs=import_part(item['path'],item['key'],tr);pts,tris=mesh_geometry(obs);tree=BVHTree.FromPolygons(pts,tris,all_triangles=True)
 assert all(sha(ROOT/item[k])==v for k,v in before_hashes.items()),'Source changed during import'
 parts[item['key']]={'transform':tr,'objects':obs,'tree':tree,'wrapper':wrapper};geometry[item['key']]=(pts,tris)
 base=len(all_points);all_points.extend(pts);all_polys.extend([tuple(base+i for i in t) for t in tris])
 records.append({**item,'source_sha256':sha(ROOT/item['source_path']),'glb_sha256':sha(ROOT/item['path']),'manifest_sha256':sha(ROOT/item['manifest_path']),'actual_triangle_count':len(tris),'actual_bounds':bounds(pts),'source_transform_matrix':[list(row) for row in tr]})
# Old catalogue props are inspection/use context, not new production dependencies.
contexts=[('quiet_book_left','quiet','qa/batch10/assembly/quiet_books_left.glb',[-2.775,1.12,.96],0),('quiet_book_right','quiet','qa/batch10/assembly/quiet_books_right.glb',[2.775,1.12,.96],0),('court_understory','planted','assets/botanical_understory/exports/AST-BOT-002.glb',[.43,1.18,.62],0),('court_rosette','planted','assets/botanical_understory/exports/AST-BOT-003.glb',[-.84,1.18,.62],0)]
context_fit=[]
for key,parent,path,pos,angle in contexts:
 tr=parts[parent]['transform']@matrix(pos,angle);wrapper,obs=import_part(path,key,tr);pts,tris=mesh_geometry(obs);parts[key]={'objects':obs,'transform':tr,'wrapper':wrapper};context.append({'key':key,'parent_component':parent,'path':path,'sha256':sha(ROOT/path),'local_source_translation_m':pos,'actual_bounds':bounds(pts),'triangles':len(tris),'new_design':False,'production_dependency':False})
# Measure actual shelf free planes and support in the imported quiet mesh.
for key,xcentre in [('quiet_book_left',-2.775),('quiet_book_right',2.775)]:
 qpart=parts['quiet'];origin=qpart['transform']@Vector((xcentre,1.12,1.10));limits={}
 for name,direction in [('left',(-1,0,0)),('right',(1,0,0)),('bottom',(0,0,-1)),('top',(0,0,1)),('back',(0,1,0))]:
  hit=qpart['tree'].ray_cast(origin,qpart['transform'].to_3x3()@Vector(direction),4);assert hit[0] is not None,(key,name)
  local=qpart['transform'].inverted()@hit[0];limits[name]=list(local)
 pts,_=mesh_geometry(parts[key]['objects']);lp=[qpart['transform'].inverted()@p for p in pts];lo=[min(p[i] for p in lp) for i in range(3)];hi=[max(p[i] for p in lp) for i in range(3)]
 bottoms=[p for p in pts if abs(p.z-.96)<2e-6];assert bottoms
 support=max(qpart['tree'].find_nearest(p)[3] for p in bottoms)
 margins={'left_m':lo[0]-limits['left'][0],'right_m':limits['right'][0]-hi[0],'top_m':limits['top'][2]-hi[2],'back_m':limits['back'][1]-hi[1]}
 assert min(margins.values())>0 and support<2e-4,(key,margins,support)
 assert hi[0]+.1>limits['right'][0], 'Shifted-stock negative control must reject'
 context_fit.append({'key':key,'actual_parent_local_min_m':lo,'actual_parent_local_max_m':hi,'native_measured_shelf_planes':limits,'clear_margins':margins,'actual_base_vertex_support_max_error_m':support,'tested_base_vertices':len(bottoms),'shifted_100mm_row_rejected':True,'scope':'Actual unscaled existing-book subsets; bounded straight shelf-space and base-contact checks only','derivation_receipt':'qa/batch10/assembly/book_context_receipt.json'})
world_tree=BVHTree.FromPolygons(all_points,all_polys,all_triangles=True)
checks=[]
for j in PLAN['joins']:
 a,b=parts[j['a']],parts[j['b']];pa=a['transform']@Vector(j['a_local_m']);pb=b['transform']@Vector(j['b_local_m']);na=a['transform'].to_3x3()@Vector(j['a_normal']);nb=b['transform'].to_3x3()@Vector(j['b_normal']);da=a['tree'].find_nearest(pa)[3];db=b['tree'].find_nearest(pb)[3]
 row={'name':j['name'],'point_gap_m':(pa-pb).length,'normal_dot':na.dot(nb),'actual_surface_distance_a_m':da,'actual_surface_distance_b_m':db};row['passed']=row['point_gap_m']<2e-6 and row['normal_dot']<-.9999 and da<2e-4 and db<2e-4;checks.append(row)
# Finite new-component rays only. The historical moving doors/host are unmodeled.
rays=[]
def ray(name,start,end,expect_hit):
 delta=Vector(end)-Vector(start);hit=world_tree.ray_cast(Vector(start),delta.normalized(),delta.length);blocked=hit[0] is not None;r={'name':name,'start_inspection_source_m':start,'end_inspection_source_m':end,'blocked':blocked,'expected_blocked':expect_hit,'passed':blocked==expect_hit};rays.append(r)
for y in [-1.75,0,1.75]:
 for z in [.20,1.19,1.65,2.65]:ray('new_component_strip_%s_%s'%(y,z),[-6,y,z],[46,y,z],False)
ray('known_clear_portal_control',[-6,0,1],[-1,0,1],False)
ray('known_blocked_portal_jamb',[-6,-2.4,1],[-1,-2.4,1],True)
ray('known_blocked_quiet_back',[11.6,2,1.2],[11.6,6,1.2],True)
# Explicit containment from actual imported vertices, not room allocation boxes.
qpoints=geometry['quiet'][0]+geometry['cove'][0];qb=bounds(qpoints);containment={'quiet_actual_bounds':qb,'inside_proposed_zone':qb['min_ship_m'][0]>=60-1e-5 and qb['max_ship_m'][0]<=67.2+1e-5 and qb['min_ship_m'][2]>=-7.4-1e-5 and qb['max_ship_m'][2]<=-2+1e-5 and qb['max_ship_m'][1]<=3.8+1e-5,'new_components_outside_tram_band':all(r['actual_bounds']['min_ship_m'][0]>=45-1e-5 for r in records),'host_polygon_verified':False,'host_doors_or_floor_support_verified':False}
assert all(x['passed'] for x in checks),checks
assert all(x['passed'] for x in rays),rays
assert containment['inside_proposed_zone'] and containment['new_components_outside_tram_band'],containment
scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=48;scene.render.threads_mode='FIXED';scene.render.threads=3;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.15
scene.world=bpy.data.worlds.new('QA_ONLY_neutral_world');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.27,.29,.30,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
bpy.ops.mesh.primitive_plane_add(size=160,location=(18,0,-.004));bpy.context.object.name='QA_ONLY_inspection_ground_not_host_floor';bpy.context.object.data.materials.append(material('QA_ONLY_neutral_ground',(.30,.31,.32)))
for name,loc,target,energy,size in [('arrival',[-5,-5,7],[-3,0,1.5],1800,7),('court',[8,-6,8],[11.6,1,1.5],2600,8),('quiet',[12,4,6],[11.6,3,1.6],1400,5),('service',[43,-6,6],[43,-3,1],1300,5)]:
 data=bpy.data.lights.new('QA_ONLY_'+name,'AREA');o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=loc;data.energy=energy;data.shape='DISK';data.size=size;aim(o,target)
cd=bpy.data.cameras.new('QA_ONLY_camera');cam=bpy.data.objects.new(cd.name,cd);bpy.context.collection.objects.link(cam);scene.camera=cam;cd.clip_start=.015;cd.clip_end=160
views={'portal_join_standing':{'position':[-5.8,-9,1.65],'target':[-3.8,-1.8,1.40],'lens':22,'keys':['portal','terminal'],'full':True,'meaning':'Proposed architectural portal/edge terminal join at historical X48 interface; moving door X52 and floor support remain unmodeled'},'quiet_court_approach':{'position':[2.5,0,1.65],'target':[11.6,0,1.85],'lens':18,'keys':['cove','quiet','planted','quiet_book_left','quiet_book_right','court_understory','court_rosette'],'full':True,'meaning':'Ordinary-height view of proposed quiet and low planted sections across4m study strip; no completed host room'},'quiet_seated_return':{'position':[11.6,4.2,1.19],'target':[-3,-.6,1.35],'lens':24,'keys':['quiet','cove'],'full':False,'meaning':'Proposed seated view toward arrival; partial overhead framing intentional, actual species/actor use unverified'},'service_end_standing':{'position':[45.7,-8.5,1.65],'target':[43.6,-3.4,1.18],'lens':28,'keys':['service'],'full':True,'meaning':'Separate rear service-interface candidate; intervening host route and rear moving door X98 unmodeled'}}
views.pop('quiet_court_approach');views.pop('quiet_seated_return')
views.update({'quiet_pair_standing':{'position':[7,-1,1.65],'target':[11.6,1.5,1.7],'lens':18,'keys':['quiet','cove','planted','quiet_book_left','quiet_book_right','court_understory','court_rosette'],'full':False,'meaning':'Standing view from proposed through strip toward the quiet mouth and neighboring low planted edge; ordinary partial-context framing, not a whole-room view'},'quiet_forward_court':{'position':[11.6,4.08,1.19],'target':[10.8,-2.8,.9],'lens':30,'keys':['planted','court_understory','court_rosette'],'full':True,'meaning':'Seated quiet-bay view through its actual open front toward planted court; lateral arrival remains screened by end storage'},'quiet_from_planted_seat':{'position':[12.6,-2.34,1.19],'target':[11.6,4,1.8],'lens':17.5,'keys':['quiet','cove','quiet_book_left','quiet_book_right'],'full':True,'meaning':'Opposing proposed planted-seat eye position looking into joined quiet section; inspection posture only, not actor or species validation'}})
report={'scope':'Actual imported-GLB component arrangement and finite geometry screen. No recovered host, complete guard, actor/cart traversal, operating doors or runtime lighting.','plan_sha256':sha(OUT/'plan.json'),'script_sha256':EXECUTED_SCRIPT_SHA,'items':records,'context':context,'physical_joins':checks,'context_fit':context_fit,'book_context_derivation_sha256':sha(OUT/'book_context_receipt.json'),'finite_new_component_ray_checks':rays,'geometry_triangle_count':len(all_polys),'containment':containment,'inspection_floor_and_lights_are_qa_only':True,'views':{}}
output=OUT/('camera_preflight_v2.json' if PREFLIGHT else'render_evidence_v2.json')
if output.exists():report['views']=json.loads(output.read_text()).get('views',{})
elif not PREFLIGHT:
 old=json.loads((OUT/'render_evidence.json').read_text())
 for name in ('portal_join_standing','service_end_standing'):
  rec=old['views'][name];assert rec['source_scope']=={x['catalogue_id']:x['glb_sha256'] for x in records};rec['executed_script_sha256']=old['script_sha256'];rec['retained_from_unchanged_input_capture']=True;report['views'][name]=rec
report['superseded_camera_evidence']='qa/batch10/assembly/first_camera_evidence/interpretation.json'
for name,v in views.items():
 if ONLY and ONLY!=name:continue
 if not PREFLIGHT and not ONLY and name in report['views']:continue
 cam.location=v['position'];aim(cam,v['target']);cd.lens=v['lens'];scene.render.resolution_x=640;scene.render.resolution_y=360;bpy.context.view_layer.update();focus=[o for key in v['keys'] for o in parts[key]['objects']];fr=frame.frame_report(scene,cam,focus,margin=.045)
 if v['full']:assert fr['passes'],(name,fr)
 rec={**v,'executed_script_sha256':EXECUTED_SCRIPT_SHA,'framing':fr,'resolution':[640,360],'camera_matrix_world':[list(row) for row in cam.matrix_world],'source_scope':{x['catalogue_id']:x['glb_sha256'] for x in records}}
 if not PREFLIGHT:
  path=OUT/(name+'.png');scene.render.filepath=str(path);scene.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True);rec['raw_image_sha256']=sha(path)
 report['views'][name]=rec
 if not PREFLIGHT:
  report['execution_complete']=False;output.write_text(json.dumps(report,indent=2)+'\n')
for rec in records:
 assert sha(ROOT/rec['path'])==rec['glb_sha256'] and sha(ROOT/rec['source_path'])==rec['source_sha256'] and sha(ROOT/rec['manifest_path'])==rec['manifest_sha256'],'Source changed during inspection'
for rec in context:assert sha(ROOT/rec['path'])==rec['sha256'],'Context changed during inspection'
assert sha(Path(__file__))==EXECUTED_SCRIPT_SHA,'Inspection script changed during execution'
report['inputs_unchanged_during_execution']=True
report['all_final_views_present']=set(report['views'])==set(views)
report['execution_complete']=True
output.write_text(json.dumps(report,indent=2)+'\n');print('ASSEMBLY_PREFLIGHT_PASS' if PREFLIGHT else'ASSEMBLY_RENDER_PASS')
