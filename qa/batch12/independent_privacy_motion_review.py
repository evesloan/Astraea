"""Actual source-state/native hierarchy, continuous linear own-support and limited privacy checks."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
from scipy.spatial import cKDTree,ConvexHull
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch12';BASE=ROOT/'assets/clinical_architecture'
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,inside_mesh,segment_triangles
sys.path.insert(0,str(OUT));from independent_void_geometry import triangle_box_mask,hull_box_overlap
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def polygon_gap(a,b):
 def one(p,q):
  start=q;end=np.roll(q,-1,axis=0);edge=end-start;f=np.clip(np.einsum('pqi,qi->pq',p[:,None,:]-start,edge)/np.maximum(np.sum(edge*edge,axis=1),1e-30),0,1);near=start+f[:,:,None]*edge;return float(np.linalg.norm(p[:,None,:]-near,axis=2).min())
 return min(one(a,b),one(b,a))
mp=BASE/'AST-MED-001.manifest.json';m=json.loads(mp.read_text());rp=OUT/'independent_source_states_AST-MED-001.json';r=json.loads(rp.read_text());assert sha(BASE/m['source'])==r['source_sha256']==m['source_sha256'];cp=BASE/'collision_proposals.json';collision=json.loads(cp.read_text())['AST-MED-001'];fp=BASE/'privacy_test_field.json';field=json.loads(fp.read_text())
cache={s['frame']:np.load(ROOT/s['geometry_cache'])for s in r['states']};states={s['frame']:s for s in r['states']};first=min(cache);last=max(cache);initial=cache[first];lastg=cache[last];delta=np.asarray(m['details']['motion']['open_translation_source_m']);labels=initial['object_names'];tris=initial['triangles'];objects={o['name']:o for o in states[first]['objects']};moving={o['name']for o in states[first]['objects']if o['parent']=='SCREEN_TRANSLATION'and o['type']=='MESH'};fixed=set(labels)-moving
linearity=[]
for state in r['states']:
 g=cache[state['frame']];assert np.array_equal(labels,g['object_names']);fraction=(state['frame']-first)/(last-first);expected=tris.copy();expected[np.isin(labels,list(moving))]+=fraction*delta
 linearity.append({'frame':state['frame'],'actual_rigid_translation_error_m':float(np.max(abs(g['triangles']-expected)))})
channels=[c for a in r['actions']for c in a['channels']];linear_action=all(c['data_path']=='location'and all(k['interpolation']=='LINEAR'for k in c['keyframes'])and len(c['keyframes'])==2 for c in channels)and len(channels)==3
pairs=[]
for a in sorted(moving):
 av=tris[labels==a].reshape(-1,3);swept=np.vstack([av,av+delta]);alo,ahi=swept.min(0),swept.max(0)
 for b in sorted(fixed):
  bt=tris[labels==b];bv=bt.reshape(-1,3);blo,bhi=bv.min(0),bv.max(0);sep=np.maximum(blo-ahi,alo-bhi);gap=max(float(sep.max()),0.);row={'moving':a,'fixed':b,'swept_axis_separation_m':gap,'pass':gap>1e-7,'method':'Exact swept AABB separation for linear rigid translation'}
  if not row['pass']and 'annular_slider_sleeve'in a and b=='continuous_exposed_slider_rod':
   at=tris[labels==a];n=np.cross(at[:,1]-at[:,0],at[:,2]-at[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1),1e-30)[:,None];center=np.asarray([0,.095,2.29]);radial=at.mean(1)-center;radial[:,0]=0;inner=at[(n*radial).sum(1)<-1e-7];poly=ConvexHull(inner[:,:,1:].reshape(-1,2));rod=ConvexHull(bv[:,1:]);pv=poly.points[poly.vertices];rv=rod.points[rod.vertices];clearance=polygon_gap(pv,rv);contained=bool(np.max(rv@poly.equations[:,:2].T+poly.equations[:,2])<0);row.update(method='Actual sleeve inner polygon encloses actual rod polygon in invariant YZ section; x-only translation preserves radial gap for complete stroke',inner_section_contains_rod=bool(contained),actual_min_cross_section_clearance_m=clearance,clearance_pass=bool(contained and clearance>1e-6),sleeve_travel_x_m=[float(alo[0]),float(ahi[0])],rod_x_m=[float(blo[0]),float(bhi[0])])
  row['pass']=row.get('clearance_pass',row['pass']);pairs.append(row)
rows=[]
for state,meta in m['states'].items():
 frame=first if state=='closed'else last;g=cache[frame];st=states[frame];native=Native(BASE/meta['export']);nt=native.tris@C;v=g['triangles'].reshape(-1,3);nv=nt.reshape(-1,3);haus=float(max(cKDTree(v).query(nv)[0].max(),cKDTree(nv).query(v)[0].max()));assert sha(BASE/meta['export'])==meta['sha256'];ni={n.get('name'):i for i,n in enumerate(native.g.doc['nodes'])};marker_checks=[]
 for mark in m['physical_and_proposal_markers']:
  p=np.asarray(mark['open_source_m']if state=='open'and mark.get('moving_with_screen')else mark['source_m']);i=ni.get(mark['name']);err=float(np.linalg.norm(native.world[i][:3,3]-C@p))if i is not None else 1e9
  marker_checks.append({'name':mark['name'],'native_world_error_m':err,'pass':err<1e-6})
 hulls=[]
 for shape in collision['shapes']:
  points=np.asarray(list(itertools.product(*zip(shape['min_source_m'],shape['max_source_m']))))if shape['type']=='box'else np.asarray(shape['points_source_m']);points=points+(delta if state=='open'and shape.get('moving_with_screen')else 0);hulls.append(Hull(points,shape))
 voids=[]
 for void in collision['preserve_voids']:
  if void.get('state','all')not in ['all',state]:continue
  lo=np.asarray(void['min_source_m'])+.0002;hi=np.asarray(void['max_source_m'])-.0002;sm=triangle_box_mask(g['triangles'],lo,hi);gm=triangle_box_mask(nt,lo,hi);mid=(lo+hi)/2;solid=[str(n)for n in np.unique(labels)if inside_mesh([mid],g['triangles'][labels==n])[0]];over=[h.record['name']for h in hulls if hull_box_overlap(h,lo,hi)['overlaps']]
  voids.append({'name':void['name'],'source_intruding_parts':sorted(set(str(x)for x in labels[sm])),'native_intruding_triangles':int(gm.sum()),'midpoint_inside_parts':solid,'collision_overlaps':over,'pass':not sm.any()and not gm.any()and not solid and not over})
 rays=[]
 for ray in field['rays']:
  expected=ray['expected_'+state]=='blocked';a=np.asarray(ray['eye_source_m']);b=np.asarray(ray['target_source_m']);hits=native.segment_hits(C@a,C@b);source=bool(segment_triangles(a,b,g['triangles']));opaque=[]
  for hit in hits:
   material=next(x for x in native.g.doc['materials']if x.get('name')==hit['material']);pbr=material.get('pbrMetallicRoughness',{});opaque.append(material.get('alphaMode','OPAQUE')=='OPAQUE'and pbr.get('baseColorFactor',[1,1,1,1])[3]==1)
  rays.append({'name':ray['name'],'eye_source_m':a.tolist(),'target_source_m':b.tolist(),'expected_blocked':expected,'source_blocked':source,'native_hits':hits,'all_hit_materials_opaque':all(opaque),'pass':source==expected and bool(hits)==expected and all(opaque)})
 row={'state':state,'export':bind(BASE/meta['export']),'actual_native_frame_vertex_hausdorff_m':haus,'source_bounds_m':[v.min(0).tolist(),v.max(0).tolist()],'native_source_frame_bounds_m':[nv.min(0).tolist(),nv.max(0).tolist()],'declared_bounds_match':np.max(abs(v.min(0)-meta['bounds']['min_source_m']))<1e-6 and np.max(abs(v.max(0)-meta['bounds']['max_source_m']))<1e-6,'native_motion_node_translation_m':native.world[ni['SCREEN_TRANSLATION']][:3,3].tolist(),'markers':marker_checks,'whole_declared_voids':voids,'privacy_rays':rays,'native_animation_clips':len(native.g.doc.get('animations',[])),'pass':haus<1e-6 and all(x['pass']for x in marker_checks+voids+rays)};row['declared_bounds_match']=bool(row['declared_bounds_match']);rows.append(row)
res={'passed':linear_action and all(x['actual_rigid_translation_error_m']<1e-6 for x in linearity)and all(x['pass']for x in pairs+rows),'executed_script_sha256':sha(Path(__file__)),'bindings':[bind(p)for p in[mp,rp,cp,fp,BASE/m['source']]],'source_linear_location_action_verified':linear_action,'evaluated_state_translation_checks':linearity,'full_stroke_moving_vs_fixed_pairs':pairs,'states':rows,'limits':['The continuous geometric clearance proof covers the actual declared rigid prismatic translation and own visual supports only. It does not model loads, friction, bearings, latches, damping, external walls or body collision.','Native exports are static closed/open derivatives with retained marker/motion nodes; source has the editable action. Derivatives add no design.','Only eight declared care-field rays and two top/edge negative controls are privacy evidence. Opaque hits do not establish confidentiality outside the finite field.','Whole declared voids use 0.2mm surface tolerance; collision compounds are proposals, not moving engine solids.']}
(OUT/'independent_privacy_motion_review.json').write_text(json.dumps(res,indent=2)+'\n');print('privacy motion pass',res['passed'],'pair failures',[x for x in pairs if not x['pass']]);print('states',[(x['state'],x['pass'])for x in rows])
