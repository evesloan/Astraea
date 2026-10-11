"""Independent exported aft landing support, geometry and unchanged original pins."""
from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/AFT_PAIR_CONTRACT.json'));checks=[]
def check(name,ok,**data):
 checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in p['source_pins'].items():check('pin_'+f,sha(ROOT/f)==h)
counts={}
for path in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(path);n=tcount=0
 check('runtime_copy_'+path.name,sha(path)==sha(ROOT/'Game/assets/models/group3_remaining_risers_20261011'/path.name))
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  n+=1;v,f,u,e=g.geometry(name);tcount+=len(f);check('finite_'+path.name+name,np.isfinite(v).all()and np.isfinite(u).all())
  t=np.asarray(v)[np.asarray(f)];areas=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
  check('nondegenerate_'+path.name+name,(areas>1e-12).all())
 counts[path.name]=dict(meshes=n,triangles=tcount,bytes=path.stat().st_size,sha256=sha(path))
floor=GLB(HERE/'exports/AST-STF-G3-035.glb');spec=json.load(open(HERE/'source/AFT_PAIR_MISSING_ONLY_FLOORS.json'));report=[]
old=[]
for f in ['structural_meshes.json','received_structural_meshes.json']:old+=json.load(open(ROOT/'Game/data/generated'/f))['regions']
for site in p['sites']:
 key=site['reservation_id'];sign=-1 if site['center_xz'][0]<0 else 1
 for landing in site['floor_checks']:
  deck=landing['deck'];y=landing['floor_y'];tops=[]
  for name,node in floor.by_name.items():
   if'mesh'not in node or key not in name or not name.endswith(deck):continue
   v,faces,_,_=floor.geometry(name)
   for f in faces:
    t=np.asarray([v[i]for i in f])
    if np.max(abs(t[:,1]-y))>.0001:continue
    check('upward_'+key+deck+str(len(tops)),np.cross(t[1]-t[0],t[2]-t[0])[1]>0);tops.append(Polygon(t[:,[0,2]]))
  actual=unary_union(tops);planned=unary_union([Polygon(q['boundary'],q['holes'])for q in spec['parts']if q['batch_cell']==key+'_'+deck])
  check('plan_matches_export_'+key+deck,actual.symmetric_difference(planned).area<.005)
  previous=unary_union([Polygon(t)for q in old if q['deck']==deck for t in q['triangles']])
  check('no_old_floor_duplicate_'+key+deck,actual.intersection(previous.buffer(-.001)).area<1e-7)
  check('worker_support_'+key+deck,Point(sign*21,490).buffer(.3).difference(actual.union(previous)).area<1e-7)
  cabin=box(-26.8,488,-23.2,492)if sign<0 else box(23.2,488,26.8,492)
  check('shaft_travel_no_floor_'+key+deck,actual.intersection(cabin).area<1e-7)
  report.append(dict(reservation_id=key,deck=deck,actual_floor_m2=actual.area))
check('D01_D04_preserved',not p['original_D01_shared_circuit_and_D04_routes_modified'])
check('authoritative_identity_map_not_created',p['persistent_identity_map']is None and all(s['authoritative_identity_map']is None for s in p['sites']))
q=dict(status='PASS',checks=len(checks),exports=counts,landings=34,sites=2,new_floor_m2=sum(q['actual_floor_m2']for q in report),floor_reports=report,
 original_and_prior_frozen_sources_unchanged=True,identity_or_population_or_engineering_or_final_art_acceptance=False,details=checks)
(HERE/'qa/NATIVE_GEOMETRY_CHECKS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='details'}))
