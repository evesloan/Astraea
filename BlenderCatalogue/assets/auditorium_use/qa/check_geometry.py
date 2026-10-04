"""Double-precision whole-convex-solid tests; continuous rotation enclosed in 0.5deg arc boxes.
Endpoint hulls enlarged in Y/Z by r*(1-cos(dtheta/2)) bound every vertex arc.
X remains exact for actual X hinges; do not artificially expand bearing end faces.
"""
from pathlib import Path
import json,itertools,hashlib,math
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[1];doc=json.loads((BASE/'qa/evaluated_source_geometry.json').read_text());coll=json.loads((BASE/'collision_proposals.json').read_text())
def hull(v):
 v=np.asarray(v,dtype=float);h=ConvexHull(v);return {'v':v,'eq':h.equations,'lo':v.min(0),'hi':v.max(0),'volume':h.volume,'simplices':h.simplices}
def box(lo,hi):return hull(list(itertools.product(*zip(lo,hi))))
def intersect(a,b,tol=2e-7):
 if np.any(np.minimum(a['hi'],b['hi'])-np.maximum(a['lo'],b['lo'])<=tol):return False,0.
 eq=np.concatenate((a['eq'],b['eq']));r=linprog([0,0,0,-1],A_ub=np.column_stack((eq[:,:3],np.ones(len(eq)))),b_ub=-eq[:,3],bounds=[(None,None)]*4,method='highs')
 radius=float(r.x[3])if r.success else -1.;return radius>tol,radius
def rotate(v,p,a):
 v=np.array(v)-p;c=math.cos(a);s=math.sin(a);m=np.array([[1,0,0],[0,c,-s],[0,s,c]]);return v@m.T+p
def sweep_bounds(part,motion):
 vs=np.array(part['vertices']);travel=motion['travel'];p=np.array(motion['pivot_source_m'])
 if motion['kind']=='translation':yield 0.,hull(np.concatenate((vs,vs+[0,travel,0]))),0.;return
 ns=math.ceil(abs(travel)/.5);rad=np.max(np.linalg.norm((vs-p)[:,1:],axis=1));step=math.radians(travel/ns);eps=rad*(1-math.cos(abs(step)/2))+2e-10
 for k in range(ns):
  points=np.concatenate((rotate(vs,p,k*step),rotate(vs,p,(k+1)*step)))
  clouds=np.concatenate([points+[0,a*eps,b*eps]for a,b in itertools.product((-1,1),repeat=2)])
  yield k*travel/ns,hull(clouds),eps
rows=[]
for ident,data in doc.items():
 rec=json.loads((BASE/f'{ident}.manifest.json').read_text());parts={p['name']:p for p in data['parts']};shapes={n:hull(p['vertices'])for n,p in parts.items()};joins=[];markers=[]
 for j in data['joins']:
  p=np.array(j['probe_source_m']);values=[float(np.max(shapes[n]['eq'][:,:3]@p+shapes[n]['eq'][:,3]))for n in j['parts']];dots=[]
  if 'normal_a_source'in j:
   for n,key in zip(j['parts'],('normal_a_source','normal_b_source')):
    eq=shapes[n]['eq'];active=eq[np.abs(eq[:,:3]@p+eq[:,3])<2e-6];dots.append(float(np.max(active[:,:3]@j[key]))if len(active)else-1)
  joins.append({'name':j['name'],'maximum_signed_planes_m':values,'boundary_normal_dots':dots,'passes':max(values)<2e-6 and (not dots or min(dots)>.999)})
 for m in data['markers']:
  if not m['physical_part']:continue
  eq=shapes[m['physical_part']]['eq'];p=np.array(m['source_m']);values=eq[:,:3]@p+eq[:,3];distance=float(np.max(values));active=eq[np.abs(values)<2e-6];dot=float(np.max(active[:,:3]@m['direction_source']))if 'direction_source'in m and len(active)else 1
  markers.append({'name':m['name'],'maximum_signed_surface_distance_m':distance,'normal_dot':dot,'passes':abs(distance)<2e-6 and dot>.999})
 voids=[]
 for v in data['voids']:
  scope=v['state'];geometry=shapes
  if scope=='folded':
   motion=next(m for m in rec['motion_records']if m['root']=='PAN_HINGE_X');geometry={n:hull(rotate(p['vertices'],np.array(motion['pivot_source_m']),math.radians(motion['travel'])))if p['movement_group']==motion['root']else shapes[n]for n,p in parts.items()}
  h=box(v['min_source_m'],v['max_source_m']);hits=[]
  for name,g in geometry.items():
   yes,rad=intersect(h,g)
   if yes:hits.append({'part':name,'penetration_insphere_radius_m':rad})
  motion_hits=[]
  if scope=='all':
   for motion in rec['motion_records']:
    for part in parts.values():
     if part['movement_group']!=motion['root']:continue
     for angle,sh,eps in sweep_bounds(part,motion):
      yes,rad=intersect(h,sh)
      if yes:motion_hits.append({'part':part['name'],'motion_root':motion['root'],'interval_start':angle,'radius_m':rad})
  if scope=='cover_local':
   mh=hull(np.concatenate((h['v'],h['v']+[0,.22,0])))
   for name,g in shapes.items():
    if parts[name]['movement_group']=='REAR_COVER_REMOVE':continue
    yes,rad=intersect(mh,g)
    if yes:motion_hits.append({'part':name,'moving_void':'complete cover-local translation','radius_m':rad})
  voids.append({'name':v['name'],'state':scope,'complete_volume_against_every_solid':True,'all_state_void_against_complete_motion_envelopes':scope=='all','parent_local_void_against_fixed_complete_relative_motion':scope=='cover_local','penetrations':hits,'motion_penetrations':motion_hits,'passes':not hits and not motion_hits})
 sweeps=[]
 for motion in rec['motion_records']:
  moving=[p for p in parts.values()if p['movement_group']==motion['root']];fixed=[p for p in parts.values()if p['movement_group']!=motion['root']];hits=[];extra=[];maxeps=0.;bounds=[];tested=0
  for part in moving:
   for angle,sh,eps in sweep_bounds(part,motion):
    maxeps=max(maxeps,eps);bounds.extend((sh['lo'],sh['hi']))
    for fp in fixed:
     yes,rad=intersect(sh,shapes[fp['name']]);tested+=1
     if yes:hits.append({'moving':part['name'],'fixed':fp['name'],'interval_start_degrees_or_m':angle,'intersection_radius_m':rad})
    if ident=='AST-CUL-003':
     for fp in parts.values():
      ng=hull(shapes[fp['name']]['v']+[.74,0,0]);yes,rad=intersect(sh,ng)
      if yes:extra.append({'moving':part['name'],'adjacent':fp['name'],'interval_start':angle,'radius_m':rad})
  b=np.array(bounds);sweeps.append({'root':motion['root'],'initial_state_exactly_zero':True,'kind':motion['kind'],'travel':motion['travel'],'moving_parts':[p['name']for p in moving],'fixed_part_tests':tested,'conservative_arc_enclosure_yz_error_max_m':maxeps,'complete_motion_bounds_source':{'min_m':b.min(0).tolist(),'max_m':b.max(0).tolist()},'penetrations':hits,'adjacent_QA_only_penetrations':extra,'passes':not hits and not extra})
 graph={n:set()for n in shapes}
 for j in data['joins']:
  a,b=j['parts'];graph[a].add(b);graph[b].add(a)
 roots={m['physical_part']for m in data['markers']if m['kind']=='physical_floor_contact'};seen=set(roots);queue=list(roots)
 while queue:
  n=queue.pop()
  for nxt in graph[n]-seen:seen.add(nxt);queue.append(nxt)
 profiles=[]
 for co in coll[ident]['shapes']:
  h=hull(co['points_source_m']);visual=np.concatenate([shapes[n]['v']for n in co['covered_parts']]);outside=float(np.max(visual@h['eq'][:,:3].T+h['eq'][:,3]));planes=[shapes[n]['eq']for n in co['covered_parts']];samples=np.concatenate((h['v'],h['v'][h['simplices']].mean(1)))
  excess=max(min(max(0,float(np.max(eq[:,:3]@p+eq[:,3])))for eq in planes)for p in samples)
  exact=len(planes)==1 and abs(h['volume']-shapes[co['covered_parts'][0]]['volume'])<1e-10
  profiles.append({'name':co['name'],'covered_parts':co['covered_parts'],'source_vertex_outside_max_m':outside,'sampled_profile_plane_excess_m':excess,'volume_difference_m3':h['volume']-sum(shapes[n]['volume']for n in co['covered_parts']),'exact_single_convex_source_hull':exact,'allowance_m':co['allowed_inflation_m'],'omission_allowance_m':co['allowed_omission_m'],'passes':outside<2e-6 and excess<2e-6 and exact})
 overlaps=[];joined={frozenset(j['parts'])for j in data['joins']}
 for a,b in itertools.combinations(shapes,2):
  yes,rad=intersect(shapes[a],shapes[b])
  if yes:overlaps.append({'parts':[a,b],'radius_m':rad,'declared_joint':frozenset((a,b))in joined})
 row={'catalogue_id':ident,'source_sha256':rec['source_sha256'],'joins':joins,'physical_marker_planes':markers,'whole_volume_void_checks':voids,'continuous_movement':sweeps,'support_graph':{'physical_floor_roots':sorted(roots),'all_parts':len(shapes),'reachable_parts':len(seen),'unconnected_parts':sorted(set(shapes)-seen),'passes':len(seen)==len(shapes)},'collision_profiles':profiles,'source_overlap_screen':overlaps}
 row['passes']=all(x['passes']for x in joins+markers+voids+sweeps+profiles)and row['support_graph']['passes'];rows.append(row)
h=box([0,0,0],[1,1,1]);yes,r=intersect(h,box([.99,.99,.99],[1.01,1.01,1.01]));boundary,_=intersect(h,box([1,0,0],[2,1,1]));ctrl={'10mm_corner_penetration_detected':yes,'boundary_contact_not_penetration':not boundary,'detected_insphere_radius_m':r,'wrong_axis_control':'Native marker validator separately tests incorrect basis'}
report={'method':'Entire convex evaluated solids; positive controls; continuous arc enclosure including initial zero; complete translation hull; exact visual convex collision comparison','tolerance_m':2e-7,'limits':'Finite piecewise authored convex geometry only; no anatomical fit, mechanics, host scene, runtime collision, load or performance acceptance','assets':rows,'positive_controls':ctrl,'all_passed':all(r['passes']for r in rows)and yes and not boundary};(BASE/'qa/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'all_passed':report['all_passed'],'assets':[{'id':r['catalogue_id'],'passes':r['passes'],'bad_joins':[x for x in r['joins']if not x['passes']],'bad_markers':[x for x in r['physical_marker_planes']if not x['passes']],'bad_voids':[x for x in r['whole_volume_void_checks']if not x['passes']],'bad_sweeps':[{'root':x['root'],'hits':x['penetrations'][:12]}for x in r['continuous_movement']if not x['passes']],'unsupported':r['support_graph']['unconnected_parts'],'undeclared_overlap':[x for x in r['source_overlap_screen']if not x['declared_joint']]}for r in rows]},indent=2))
