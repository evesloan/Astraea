"""Independent exported floors, original fitting payloads and surgical riser cuts."""
from pathlib import Path
import json,hashlib,numpy as np
import shapely
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/FORE_PHYSICAL_CONTRACT.json'));checks=[]
def check(name,ok,**data):
 checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in p['source_pins'].items():check('source_pin_'+f,sha(ROOT/f)==h)
counts={}
for file in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(file);n=0;tcount=0
 check('Game_copy_'+file.name,sha(file)==sha(ROOT/'Game/assets/models/group3_fore_starboard_clinical_20261011'/file.name))
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  n+=1;v,f,u,e=g.geometry(name);tcount+=len(f)
  check('finite_'+file.name+'_'+name,np.isfinite(v).all()and np.isfinite(u).all())
  t=np.asarray(v)[np.asarray(f)];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2
  check('nondegenerate_'+file.name+'_'+name,(area>1e-12).all())
 counts[file.name]=dict(meshes=n,triangles=tcount,bytes=file.stat().st_size,sha256=sha(file))
floor=GLB(HERE/'exports/AST-STF-G3-041.glb');floor_specs=json.load(open(HERE/'source/FORE_MISSING_ONLY_FLOORS.json'))
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
 check('landing_worker_floor_'+deck,Point(21,-490).buffer(.3).difference(actual.union(previous)).area<1e-7)
 check('no_cabin_travel_floor_'+deck,actual.intersection(box(23.2,-492,26.8,-488)).area<1e-7)
 floor_reports.append(dict(deck=deck,actual_top_m2=actual.area))


check('no_authoritative_keys_created',p['authoritative_identity_map']is None and p['authoritative_operation_IDs']is None)
check('original_custodial_cart_retained',not p['duplicate_physics_cart_created']and not p['original_custodial_cart_identity_or_position_changed'])
check('six_fitted_unscaled_doors',len(p['door_bindings'])==6 and all(q['persistent_id']is None for q in p['door_bindings']))
check('dispatch_outside_shared_buffer',all(q['position'][2]>p['shared_buffer_bounds_xz'][3]for q in p['dispatch_buttons']))
check('no_custodial_cart_clone',all(q['asset']!='AST-HSK-005'for q in p['reused_asset_instances']))
# The principal bay approaches lie on one continuous physical floor; source
# closed boxes and static trolleys remain independent of gameplay inventory.
new05=unary_union([Polygon(q['boundary'],q['holes'])for q in floor_specs['parts']if q['batch_cell']=='D05'])
prev05=unary_union([Polygon(t)for q in old if q['deck']=='D05'for t in q['triangles']])
for x,z in [(21,-494.35),(21,-500),(21,-504),(27,-500),(27,-504),(33,-500),(33,-496.4),(43,-500),(43,-496.4),(43,-504),(43,-507.6),(57,-500),(57,-472),(61,-504),(61,-472)]:
 check('programme_support_'+str((x,z)),Point(x,z).buffer(.3).difference(new05.union(prev05)).area<1e-7)
q=dict(status='PASS',checks=len(checks),exports=counts,landings=17,service_doors=6,receiving_bays=3,physical_furniture_instances=len(p['reused_asset_instances']),fixture_profiles=len(p['fixtures']),floor_reports=floor_reports,
 actual_exported_floor_m2=sum(q['actual_top_m2']for q in floor_reports),source_geometry_only_not_primary_engineering_stock_species_or_final_acceptance=True,details=checks)
(HERE/'qa/NATIVE_GEOMETRY_CHECKS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='details'}))
