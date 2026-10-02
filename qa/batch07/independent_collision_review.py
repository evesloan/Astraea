"""Numeric compound collision proposals: frame fidelity and sensitive opening probes."""
from pathlib import Path
import json,hashlib,itertools,numpy as np
from scipy.spatial import ConvexHull,cKDTree
from scipy.optimize import lsq_linear
from independent_geometry import C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch07';reports=[]
def corners(lo,hi):return np.asarray(list(itertools.product(*zip(lo,hi))),float)
def hit_shape(p,a,b):
 a=np.asarray(a);b=np.asarray(b);d=b-a
 if p['kind']=='hull':
  lo=0.;hi=1.
  for pl in p['planes']:
   v=pl[:3]@a+pl[3];w=pl[:3]@d
   if abs(w)<1e-12:
    if v>1e-9:return False
   elif w>0:hi=min(hi,-v/w)
   else:lo=max(lo,-v/w)
  return lo<=hi+1e-9 and hi>=0 and lo<=1
 pa=np.asarray(p['a']);pb=np.asarray(p['b']);r=p['radius'];e=pb-pa
 if (np.maximum(a,b)<np.minimum(pa,pb)-r).any() or (np.minimum(a,b)>np.maximum(pa,pb)+r).any():return False
 if p['kind']=='capsule':
  mat=np.stack([d,-e],axis=1);sol=lsq_linear(mat,pa-a,bounds=(0,1),tol=1e-10)
  return np.linalg.norm(mat@sol.x-(pa-a))<=r+1e-9
 L=np.linalg.norm(e);axis=e/L;v=a-pa;dv=d@axis;av=v@axis;low=0.;high=1.
 if abs(dv)<1e-12:
  if av<0 or av>L:return False
 else:
  t0,t1=sorted([-av/dv,(L-av)/dv]);low=max(low,t0);high=min(high,t1)
 if high<low:return False
 up=d-dv*axis;vp=v-av*axis;den=up@up;at=low if den<1e-20 else np.clip(-(up@vp)/den,low,high)
 return np.linalg.norm(vp+at*up)<=r+1e-9
for family in ['hospitality_counters','hospitality_stations','hospitality_serviceware']:
 path=ROOT/'assets'/family/'collision_proposals.json';j=json.loads(path.read_text());j=j.get('assets',j)
 for ident,r in j.items():
  if not ident.startswith('AST-HSP-'):continue
  parts=r.get('proposals',r.get('boxes',r.get('shapes',[])));assert parts,ident
  hs=[];errs=[]
  for p in parts:
   rec={'name':p.get('name',p.get('semantic_part')),'group':p.get('functional_group',p.get('group','static'))}
   if p['type']=='convex_hull_points':
    a=np.asarray(p['source_points_m']);b=np.asarray(p['glb_points_m']);rec.update(kind='hull',planes=ConvexHull(a).equations);errs.append(float(np.max(np.abs(a@C.T-b))))
   elif p['type']=='box':
    a=p.get('blender_z_up',{'min_m':p.get('min_source_m'),'max_m':p.get('max_source_m')});b=p.get('gltf_y_up',p.get('bounds_gltf_yup'));aa=corners(a['min_m'],a['max_m']);bb=corners(b['min_m'],b['max_m']);rec.update(kind='hull',planes=ConvexHull(aa).equations);errs.append(float(max(cKDTree(aa@C.T).query(bb)[0].max(),cKDTree(bb).query(aa@C.T)[0].max())))
   elif p['type'] in ['cylinder','capsule']:
    a=p['blender_z_up'];b=p['gltf_y_up'];rec.update(kind=p['type'],a=a['a_m'],b=a['b_m'],radius=a['radius_m']);assert a['radius_m']>0
    errs.extend([float(np.linalg.norm(C@a[k]-b[k])) for k in ['a_m','b_m']]);errs.append(abs(a['radius_m']-b['radius_m']))
   else:raise ValueError(p['type'])
   hs.append(rec)
  tests=[]
  def check(name,a,b,empty=True,exclude=None):
   hits=[p['name'] for p in hs if (exclude is None or p['group']!=exclude) and hit_shape(p,a,b)];tests.append({'name':name,'source_segment_m':[a,b],'hits':hits,'expected_empty':empty,'pass':not hits if empty else bool(hits)})
  if ident.endswith('001'):
   for x in [.4,1.2,2.0]:
    for z in [.30,.55]:check(f'staff_open_{x}_{z}',[x,.60,z],[x,-.24,z])
   check('drawer_cavity',[1.2,.25,.72],[1.2,-.20,.72]);check('blocked_fascia',[1.2,-.42,.55],[1.2,-.25,.55],False)
  if ident.endswith('002'):
   for t in [.2,.75,1.4]:
    for z in [.3,.55]:
     a=[(.62-.57)*np.sin(t),.62-(.62-.57)*np.cos(t),z];b=[(.62+.22)*np.sin(t),.62-(.62+.22)*np.cos(t),z];check('inner_service_'+str((t,z)),a,b)
   check('blocked_fascia',[.88/2**.5,.62-.88/2**.5,.55],[.99/2**.5,.62-.99/2**.5,.55],False)
  if ident.endswith('003'):
   for x in [-.18,-.14,-.10,.10,.14,.18]:
    for y in [-.14,-.095,-.04]:check('cup_vertical_'+str((x,y)),[x,y,.083],[x,y,.360])
   check('cup_front_approach',[-.14,-.35,.22],[-.14,-.08,.22]);check('blocked_rear',[-.14,-.08,.22],[-.14,.16,.22],False)
   check('drip_extraction',[0,-.10,.070],[0,-.51,.070],exclude='DRIP_TRAY')
  if ident.endswith('004'):
   for x in [-.30,0,.30]:
    for z in [.97,1.04,1.13]:check('tray_entry_'+str((x,z)),[x,-.44,z],[x,.27,z])
   check('caddy_removed_path',[0,.1,.89],[0,1.1,.89],exclude='RECEIVING_CADDY');check('blocked_floor',[0,.015,.88],[0,.015,.90],False)
  if ident.endswith('005'):
   for x in [-.41,-.22,-.03]:
    for z in [.27,.50,.73]:check('tray_stock_rear_'+str((x,z)),[x,-.08,z],[x,.95,z])
   for z in [.30,.58]:check('plate_approach_'+str(z),[.274,.7,z],[.274,.0,z])
   check('blocked_divider',[.052,.6,.4],[.052,-.1,.4],False)
  if ident.endswith('006'):
   for x in [-.18,0,.18]:
    for z in [.30,.5,.70]:check('tier_open_'+str((x,z)),[x,.5,z],[x,-.17,z])
    check('underhand_'+str(x),[x,.5,.86],[x,.29,.86])
   check('blocked_tier',[0,.5,.20],[0,0,.20],False)
  reports.append({'id':ident,'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'shape_count':len(parts),'maximum_frame_error_m':max(errs),'checks':tests,'pass':len(tests)>=3 and max(errs)<1e-7 and all(t['pass'] for t in tests)})
out={'pass':len(reports)==6 and all(r['pass'] for r in reports),'assets':reports,'shape_count':sum(r['shape_count'] for r in reports),'method':'Source/native-frame correspondence for every explicit shape, finite segment clipping against convex planes, finite cylinders, and exact closest-segment distance for capsules; nonempty blocked controls for every asset.','limits':['Offline compound proposals, not instantiated engine collisions.','263 pieces on the curved return alone require simplification/runtime budgeting before adoption; quantity is reported, not performance-certified.','Opening rays are bounded representative free-space evidence, not continuous actor-fit or mechanical certification.']}
(OUT/'independent_collision_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'shapes':out['shape_count'],'failures':[{'id':r['id'],'tests':[t for t in r['checks'] if not t['pass']]} for r in reports if not r['pass']]},indent=2))
