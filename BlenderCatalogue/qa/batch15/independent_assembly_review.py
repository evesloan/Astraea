"""Actual-native relative paired inspection and cross-family mounting. No cabin adoption."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch15';sys.path.insert(0,str(OUT));from independent_collision_adapters import expand,Hull
from independent_contact_graph import normal_witness
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask,hull_box_overlap
from independent_collision_geometry import nearest_distances,inside_mesh
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
pp=OUT/'assembly/plan.json';plan=json.loads(pp.read_text());states={};bindings=[];sweeps=[]
def rot(item):
 a=np.radians(item['source_z_rotation_deg']);return np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
def loadcol(mp,m):
 d=json.loads((mp.parent/m['collision_proposal_file']).read_text());return d.get('assets',d)[m['catalogue_id']]
for state in ['closed','open','privacy','all_open']:
 triangles=[];names=[];hulls=[];bounds=[]
 for item in plan['items']:
  ident=item['asset_id'];mp=ROOT/item['manifest_path'];m=json.loads(mp.read_text());alt=('curtain'in item['key']and(state in ['open','all_open']or(state=='privacy'and item['key'].startswith('right'))))or('storage'in item['key']and state in ['privacy','all_open']);gp=ROOT/(item['alternative_export']if alt else item['path']);g=Native(gp);R=rot(item);off=np.array(item['source_origin_m']);t=g.tris@C@R.T+off;triangles.extend(t);names.extend([item['key']]*len(t));bounds.append({'key':item['key'],'min_m':t.min((0,1)).tolist(),'max_m':t.max((0,1)).tolist()});c=loadcol(mp,m)
  for rec in c['shapes']:
   for h in expand(rec,1 if alt and'ident'not in rec and ident.endswith('002')else 0):
    delta=np.array([0,-.24,0])if alt and ident.endswith('003')and rec.get('movement_group')=='drawer'else np.zeros(3);hulls.append(Hull((h.points+delta)@R.T+off,{**h.record,'key':item['key']}))
  if state=='closed':bindings.append({'key':item['key'],'files':{k:bind(p)for k,p in [('source',ROOT/item['source_path']),('export',gp),('manifest',mp),('collision',mp.parent/m['collision_proposal_file'])]}})
 triangles=np.asarray(triangles);names=np.asarray(names);boxes=[]
 for box in plan['proposed_empty_regions']:
  lo=np.array(box['min_source_m'])+.0002;hi=np.array(box['max_source_m'])-.0002;mask=triangle_box_mask(triangles,lo,hi);over=[h.record['key']+':'+h.record['name']for h in hulls if hull_box_overlap(h,lo,hi)['overlaps']];boxes.append({'name':box['id'],'source_box_m':[lo.tolist(),hi.tolist()],'actual_native_intrusions':sorted(set(str(x)for x in names[mask])),'collision_intrusions':over,'pass':not mask.any()and not over})
 pairs=[]
 for a,b in itertools.combinations(bounds,2):
  alo,ahi=np.array(a['min_m']),np.array(a['max_m']);blo,bhi=np.array(b['min_m']),np.array(b['max_m']);gap=np.maximum(np.maximum(alo-bhi,blo-ahi),0);mount_pair={a['key'].split('_',1)[1],b['key'].split('_',1)[1]}=={'rest','light'}and a['key'].split('_')[0]==b['key'].split('_')[0];pairs.append({'keys':[a['key'],b['key']],'separating_axis_gaps_m':gap.tolist(),'intentional_mount_pair':mount_pair,'pass':mount_pair or bool((gap>.0002).any())})
 states[state]={'bounds':bounds,'complete_empty_region_checks':boxes,'component_pair_bounds':pairs,'passed':all(x['pass']for x in boxes+pairs)}
for item in plan['items']:
 boxes=[next(b for b in s['bounds']if b['key']==item['key'])for s in states.values()];lo=np.min([b['min_m']for b in boxes],axis=0);hi=np.max([b['max_m']for b in boxes],axis=0)
 if item['asset_id'].endswith('002'):
  env=json.loads((ROOT/'assets/crew_rest/interface_api.json').read_text())['assets']['AST-CRW-002']['continuous_geometric_envelope'];p=np.array(list(itertools.product(*zip(env['min_source_m'],env['max_source_m']))))@rot(item).T+np.array(item['source_origin_m']);lo=np.minimum(lo,p.min(0));hi=np.maximum(hi,p.max(0))
 checks=[{'name':b['id'],'pass':bool(((hi<=np.array(b['min_source_m']))|(lo>=np.array(b['max_source_m']))).any())}for b in plan['proposed_empty_regions']];sweeps.append({'key':item['key'],'full_static_or_authored_swept_bounds_source_m':[lo.tolist(),hi.tolist()],'checks':checks,'pass':all(x['pass']for x in checks)})
# Independent mating surfaces, with all module geometry placed into the actual frame datum.
arrays={};sources={}
for ident in ['AST-CRW-001','AST-CRW-004']:
 s=json.loads((OUT/f'independent_source_{ident}.json').read_text());assert sha(ROOT/s['path'])==s['sha256'];sources[ident]=s;arrays[ident]=np.load(ROOT/s['geometry_cache'])
a,b=arrays.values();off=np.array([-.26,2.14,.88]);t1=a['triangles'];t4=b['triangles']+off;head=t1[a['object_names']=='001_flat_headboard'];plate=t4[b['object_names']=='headboard_mount_backplate'];ng1=Native(ROOT/'assets/crew_rest/exports/AST-CRW-001.glb');ng4=Native(ROOT/'assets/crew_personal/exports/AST-CRW-004.glb');mounts=[]
for x,z in itertools.product([-.37,-.15],[.76,1.0]):
 p=np.array([x,2.14,z]);d1=float(nearest_distances([p],head)[0]);d4=float(nearest_distances([p],plate)[0]);n1=normal_witness(p,head,[0,-1,0]);n4=normal_witness(p,plate,[0,1,0]);nd1=ng1.nearest(C@p,role='ASTRAEA_staff_white_paint')['distance_m'];nd4=ng4.nearest(C@(p-off),role='ASTRAEA_staff_white_paint')['distance_m'];mounts.append({'point_source_frame_m':p.tolist(),'frame_surface_distance_m':d1,'module_surface_distance_m':d4,'native_frame_distance_m':nd1,'native_module_distance_m':nd4,'frame_outward_normal':n1,'module_opposing_normal':n4,'pass':max(d1,d4,nd1,nd4)<.00002 and n1['pass']and n4['pass']})
penetrations=[]
for source,labels,target,targetlabels,direction in [(t1,a['object_names'],t4,b['object_names'],'frame_into_module'),(t4,b['object_names'],t1,a['object_names'],'module_into_frame')]:
 for name in np.unique(labels):
  tt=source[labels==name];v=np.concatenate([tt.reshape(-1,3),tt.mean(1)])
  for other in np.unique(targetlabels):
   ot=target[targetlabels==other]
   if((v.max(0)<ot.min((0,1)))|(v.min(0)>ot.max((0,1)))).any():continue
   inside=inside_mesh(v,ot)&(nearest_distances(v,ot)>.00002)
   if inside.any():penetrations.append({'direction':direction,'source_part':str(name),'target_part':str(other),'contained_samples':int(inside.sum())})
pillow=t1[a['object_names']=='001_shaped_head_pillow'];shelf=t4[b['object_names']=='clipped_personal_shelf'];gap=float(shelf[:,:,2].min()-pillow[:,:,2].max());central_lo=np.array([-.4,.30,.565]);central_hi=np.array([.4,1.52,1.1]);central=triangle_box_mask(t4,central_lo,central_hi)
mount={'witnesses':mounts,'deep_containment_screen':penetrations,'actual_shelf_to_pillow_vertical_gap_m':gap,'module_intrudes_central_rest_use':bool(central.any()),'physical_support_dependency':'004 backplate is explicitly mated to actual001 headboard; not free-standing or attached to an invented wall','pass':all(x['pass']for x in mounts)and not penetrations and gap>.0779 and not central.any()}
r={'passed':all(x['passed']for x in states.values())and all(x['pass']for x in sweeps)and mount['pass'],'bindings':bindings,'plan':bind(pp),'states':states,'whole_motion_bounds_clearance':sweeps,'cross_family_mount':mount,'scope':'Two reused frame/curtain/storage/light sets in a relative studio fixture. Eight displayed instances remain four designs and zero registered berths. Central1.4m strip and foot approach boxes are proposals, not a certified cabin or body/cart route.','executed_script_sha256':sha(Path(__file__))};(OUT/'independent_assembly_geometry_review.json').write_text(json.dumps(r,indent=2)+'\n');print('ASSEMBLY',r['passed'],[(k,v['passed'])for k,v in states.items()],'mount',mount['pass'],'sweep_failures',[x['key']for x in sweeps if not x['pass']],flush=True)
