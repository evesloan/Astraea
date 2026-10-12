"""Independent exported floors, original fitting payloads and surgical riser cuts."""
from pathlib import Path
import json,hashlib,numpy as np
import shapely
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/PRIVATE_LANDING_CONTRACT.json'));checks=[]
def check(name,ok,**data):
 checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in p['source_pins'].items():check('source_pin_'+f,sha(ROOT/f)==h)
counts={}
for file in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(file);n=0;tcount=0
 check('Game_copy_'+file.name,sha(file)==sha(ROOT/'Game/assets/models/group3_starboard3_private_20261011'/file.name))
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  n+=1;v,f,u,e=g.geometry(name);tcount+=len(f)
  check('finite_'+file.name+'_'+name,np.isfinite(v).all()and np.isfinite(u).all())
  t=np.asarray(v)[np.asarray(f)];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2
  check('nondegenerate_'+file.name+'_'+name,(area>1e-12).all())
 counts[file.name]=dict(meshes=n,triangles=tcount,bytes=file.stat().st_size,sha256=sha(file))
floor=GLB(HERE/'exports/AST-STF-G3-045.glb');floor_specs=json.load(open(HERE/'source/STARBOARD3_MISSING_FLOORS.json'))
old=[]
for f in ['structural_meshes.json','received_structural_meshes.json']:old+=json.load(open(ROOT/'Game/data/generated'/f))['regions']
floor_reports=[]
for landing in p['floor_checks']:
 deck=landing['deck'];y=landing['floor_y'];top=[]
 for name,node in floor.by_name.items():
  if'mesh'not in node:continue
  v,faces,_,_=floor.geometry(name)
  for f in faces:
   t=np.asarray([v[i]for i in f])
   if np.max(abs(t[:,1]-y))>.0001:continue
   check('outward_'+deck+'_'+str(len(top)),np.cross(t[1]-t[0],t[2]-t[0])[1]>0)
   top.append(Polygon(t[:,[0,2]]))
 actual=unary_union(top);planned=unary_union([Polygon(q['boundary'],q['holes'])for q in floor_specs['parts']if q['batch_cell']==deck])
 check('export_floor_plan_'+deck,actual.symmetric_difference(planned).area<.005)
 previous=unary_union([Polygon(t)for q in old if q['deck']==deck for t in q['triangles']])
 check('no_previous_floor_duplicate_'+deck,actual.intersection(previous.buffer(-.001)).area<1e-7)
 check('landing_worker_floor_'+deck,Point(21,-86).buffer(.3).difference(actual.union(previous)).area<1e-7)
 check('no_cabin_travel_floor_'+deck,actual.intersection(box(23.2,-88,26.8,-84)).area<1e-7)
 floor_reports.append(dict(deck=deck,actual_top_m2=actual.area))



check('no_authoritative_keys_created',p['authoritative_identity_map']is None and p['persistent_identity_map']is None)
check('seventeen_private_gates',len(p['door_bindings'])==17 and all(q['persistent_id']is None for q in p['door_bindings']))
source=json.load(open(HERE/'source/STARBOARD3_FITTED_SOURCE.json'))
allowed=box(18.8,-91.8,27.4,-80.2)
for q in source['parts']:
 g=Polygon(q['boundary'],q['holes'])if'boundary'in q else box(q['aabb'][0],q['aabb'][4],q['aabb'][1],q['aabb'][5])
 check('exact_reservation_'+q['name'],g.difference(allowed).area<1e-8)
for l in p['floor_checks']:
 deck=l['deck'];new=unary_union([Polygon(q['boundary'],q['holes'])for q in floor_specs['parts']if q['batch_cell']==deck]);prev=unary_union([Polygon(t)for q in old if q['deck']==deck for t in q['triangles']])
 for z in [-86,-82.3,-80.1,-79.5]:check('arrival_floor_'+deck+str(z),Point(21,z).buffer(.3).difference(new.union(prev)).area<1e-7)
q=dict(status='PASS',checks=len(checks),exports=counts,landings=17,private_arrival_doors=17,fixture_profiles=17,actual_exported_floor_m2=sum(q['actual_top_m2']for q in floor_reports),floor_reports=floor_reports,source_geometry_only_not_species_identity_loaded_cart_primary_structure_or_final_acceptance=True,details=checks)
(HERE/'qa/NATIVE_GEOMETRY_CHECKS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='details'}))
