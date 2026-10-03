"""Complete finite-solid motion, useful void, bearing and body-subset checks.
Rotation intervals are enclosed by endpoint hulls with XY sagitta inflation; source Z is exact.
No sampled point proxies replace whole authored convex parts.
"""
from pathlib import Path
import json,math,itertools,hashlib
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hull(v):
 v=np.asarray(v);h=ConvexHull(v);return {'v':v,'eq':h.equations,'lo':v.min(0),'hi':v.max(0)}
def box(lo,hi):return hull(list(itertools.product(*zip(lo,hi))))
def overlap(a,b,tol=3e-6):
 if np.any(np.minimum(a['hi'],b['hi'])-np.maximum(a['lo'],b['lo'])<=tol):return False,0
 eq=np.concatenate((a['eq'],b['eq']));r=linprog([0,0,0,-1],A_ub=np.column_stack((eq[:,:3],np.ones(len(eq)))),b_ub=-eq[:,3],bounds=[(None,None)]*4,method='highs');rad=float(r.x[3])if r.success else -1;return rad>tol,rad

def transform(v,m,t):
 v=np.asarray(v);p=np.array(m['pivot_source_m']);axis=np.array(m['axis_source'])
 if m['kind']=='translation':return v+axis*t
 a=math.radians(t);c=math.cos(a);s=math.sin(a);R=np.array([[c,-s,0],[s,c,0],[0,0,1]]);return (v-p)@R.T+p

def sweeps(v,m):
 if m['kind']=='translation':yield hull(np.concatenate((v,transform(v,m,m['travel'])))),0.;return
 N=math.ceil(abs(m['travel'])/2);step=m['travel']/N;p=np.array(m['pivot_source_m']);rad=max(np.linalg.norm((v-p)[:,:2],axis=1));eps=rad*(1-math.cos(math.radians(step/2)))+2e-10
 for i in range(N):
  pts=np.concatenate((transform(v,m,i*step),transform(v,m,(i+1)*step)));yield hull(np.concatenate([pts+[x*eps,y*eps,0]for x,y in itertools.product((-1,1),repeat=2)])),eps

doc=json.loads((BASE/'qa/evaluated_source_geometry.json').read_text());rows=[]
for ident,data in doc.items():
 rec=json.loads((BASE/f'{ident}.manifest.json').read_text());ps={p['name']:p for p in data['parts']};hs={n:hull(p['vertices'])for n,p in ps.items()};motions={m['root']:m for m in data['motion_records']};motionrows=[];sweepcache={};allpts=[]
 for root,m in motions.items():
  moving=[p for p in ps.values()if p['parent']==root];fixed=[p for p in ps.values()if p['parent']!=root];hits=[];mins=[];maxs=[];maxeps=0
  for p in moving:
   blocks=list(sweeps(np.array(p['vertices']),m));sweepcache[p['name']]=blocks
   for sh,eps in blocks:
    mins.append(sh['lo']);maxs.append(sh['hi']);maxeps=max(maxeps,eps)
    for q in fixed:
     hit,rad=overlap(sh,hs[q['name']])
     if hit:hits.append({'moving':p['name'],'fixed':q['name'],'maximum_insphere_m':rad})
  lo=np.min(mins,axis=0);hi=np.max(maxs,axis=0);motionrows.append({'root':root,'full_interval':[0,m['travel']],'whole_moving_parts':len(moving),'method':'Full convex swept translation or2degree endpoint-hull rotation with sagitta padding','maximum_XY_arc_enclosure_m':maxeps,'occupied_sweep_min_source_m':lo.tolist(),'occupied_sweep_max_source_m':hi.tolist(),'interference_pairs':list({(r['moving'],r['fixed']):r for r in hits}.values()),'passes':not hits})
 voidrows=[]
 for v in data['voids']:
  vh=box(v['min_source_m'],v['max_source_m']);scope=v['state'];hits=[]
  localroot=scope[:-6]if scope.endswith('_local')else None
  terminalroot=scope[:-9]if scope.endswith('_terminal')else None
  for n,p in ps.items():
   shape=hs[n]
   if terminalroot and p['parent']==terminalroot:shape=hull(transform(shape['v'],motions[terminalroot],motions[terminalroot]['travel']))
   hit,rad=overlap(vh,shape)
   if hit:hits.append({'part':n,'scope':'declared_state','insphere_m':rad})
  if scope=='all':
   for n,blocks in sweepcache.items():
    if any(overlap(vh,b)[0]for b,e in blocks):hits.append({'part':n,'scope':'whole_movement'})
  if localroot:
   for swept,e in sweeps(vh['v'],motions[localroot]):
    for n,p in ps.items():
     if p['parent']!=localroot and overlap(swept,hs[n])[0]:hits.append({'part':n,'scope':'moving_void_vs_static'})
  voidrows.append({'name':v['name'],'scope':scope,'hits':hits,'passes':not hits})
 # Full octagonal chamber bore against every whole semantic solid, with an inserted-solid positive control.
 contain=[]
 if ident.endswith('001'):
  v=[[.35*math.cos(i*math.pi/4),y,1.03+.35*math.sin(i*math.pi/4)]for y in(-.430,.285)for i in range(8)];bore=hull(v);hits=[n for n,h in hs.items()if overlap(bore,h)[0]];positive=overlap(bore,box([-.05,-.1,.98],[.05,.1,1.08]))[0];contain.append({'name':'entire_octagonal_chamber_bore','whole_solid_intrusions':hits,'inserted_solid_positive_control_detected':positive,'passes':not hits and positive})
 else:
  # Hood inner usable volume tests every complete part, including frame/cover; outer skin is intentionally outside.
  inner=box([-.42,-.29,1.842],[.42,.375,1.930]);hits=[n for n,h in hs.items()if overlap(inner,h)[0]];contain.append({'name':'whole_unassigned_hood_service_volume','whole_solid_intrusions':hits,'passes':not hits})
 bearings=[]
 for b in rec['details']['bearing_records']:
  if 'pin'in b:
   ok=b['bore_inradius_m']>b['pin_circumradius_m'];bearings.append({'name':b['name'],'full_angle_radial_clearance_min_m':b['bore_inradius_m']-b['pin_circumradius_m'],'axial_faces_retained_at_all_angles':b['axial_retention_clearance_m']==0,'passes':ok})
  else:
   a0,a1=b['closed_runner_y'];f0,f1=b['fixed_bearing_y'];ov=min(a1-b['travel_m'],f1)-max(a0-b['travel_m'],f0);bearings.append({'name':b['name'],'linear_endpoint_minimum_overlap_m':ov,'retained_vertical_clearance_m':b['minimum_vertical_retaining_clearance_m'],'passes':ov>0 and abs(ov-b['terminal_overlap_m'])<1e-6})
 omissions=[]
 for p in ps.values():
  if p['body_candidate_keep']:continue
  prefix='lower'if p['name'].startswith('lower')else'upper';target=prefix+('_hatch_retaining_strap'if p['parent']=='LOADING_HATCH_Z'else'_fixed_hinge_bracket');v=np.array(p['vertices']);q=hs[target];distance=np.linalg.norm(np.maximum(np.maximum(q['lo']-v,v-q['hi']),0),axis=1);measured=float(max(distance));same=ps[target]['parent']==p['parent'];omissions.append({'part':p['name'],'retained_convex_box_witness':target,'same_motion_owner':same,'whole_part_max_distance_upper_bound_m':measured,'declared_omitted_detail_distance_m':p['body_omission_max_distance_m'],'all_motion_proof':'Distance to a convex box is convex: maximum over a convex polyhedron is bounded by its vertices; common rigid ownership preserves that bound for every state','passes':same and measured<=p['body_omission_max_distance_m']+2e-6})
 body=json.loads((BASE/'actor_proxies/body_collision_subset.json').read_text())[ident];precise=json.loads((BASE/'collision_proposals.json').read_text())[ident];lookup={s['name']:s for s in precise['shapes']};subset=all(s==lookup[s['name']]for s in body['shapes']);row={'catalogue_id':ident,'source_sha256':sha(BASE/rec['source']),'export_sha256':sha(BASE/rec['export']),'motion':motionrows,'voids':voidrows,'containment':contain,'bearings':bearings,'body_subset':{'literal_exact_subset':subset,'precise_shape_count':len(precise['shapes']),'body_shape_count':len(body['shapes']),'omitted_detail_count':len(body['omitted_parts']),'whole_omitted_part_distance_checks':omissions,'added_inflation_m':0,'void_preservation_reason':'Literal subset cannot add geometry to any previously empty void','passes':subset and all(o['passes']for o in omissions)},'all_passed':all(r['passes']for r in motionrows+voidrows+contain+bearings+omissions)and subset};rows.append(row)
 print(ident,row['all_passed'],[(r.get('root',r.get('name')),r.get('interference_pairs',r.get('hits',r.get('whole_solid_intrusions'))))for r in motionrows+voidrows+contain if not r['passes']])
(BASE/'qa/geometry_checks.json').write_text(json.dumps({'assets':rows,'all_passed':all(r['all_passed']for r in rows)},indent=2)+'\n')
