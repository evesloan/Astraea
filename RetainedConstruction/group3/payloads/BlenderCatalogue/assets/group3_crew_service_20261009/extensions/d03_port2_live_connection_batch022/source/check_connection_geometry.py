"""Independent native topology, fitting travel, support and protected source audit."""
from pathlib import Path
import json,hashlib,numpy as np,math
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/D03_PORT2_CONNECTION_CONTRACT.json'));checks=[]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def check(name,ok,**data):checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
for f,h in p['source_pins'].items():check('source_pin_'+f,sha(ROOT/f)==h)
counts={}
for path in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(path);n=tris=0;check('runtime_copy_'+path.name,sha(path)==sha(ROOT/'Game/assets/models/group3_d03_port2_20261011'/path.name))
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  v,f,u,e=g.geometry(name);n+=1;tris+=len(f);check('finite_'+path.name+name,np.isfinite(v).all()and np.isfinite(u).all());t=np.asarray(v)[np.asarray(f)];a=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2;check('nondegenerate_'+path.name+name,(a>1e-12).all())
 counts[path.name]=dict(meshes=n,triangles=tris,bytes=path.stat().st_size,sha256=sha(path))
g=GLB(HERE/'exports/AST-STF-G3-054.glb');top=[]
for name,node in g.by_name.items():
 if'mesh'not in node:continue
 v,f,u,e=g.geometry(name)
 for i,face in enumerate(f):
  t=np.asarray([v[k]for k in face])
  if abs(t[:,1]-12).max()>.000001:continue
  check('outward_floor_'+name+str(i),np.cross(t[1]-t[0],t[2]-t[0])[1]>0);top.append(Polygon(t[:,[0,2]]))
actual=unary_union(top);spec=json.load(open(HERE/'source/D03_PORT2_MISSING_FLOOR.json'));planned=unary_union([Polygon(q['boundary'],q['holes'])for q in spec['parts']])
# Expected boundary uses IEEE float32 export coordinates; this preserves an
# exact topology comparison without inventing a large-area tolerance.
def f32(r):return [[float(np.float32(x)),float(np.float32(z))]for x,z in r]
quantized=unary_union([Polygon(f32(q['boundary']),[f32(r)for r in q['holes']])for q in spec['parts']]);check('exact_float32_floor_topology',actual.symmetric_difference(quantized).area<1e-7)

old=[]
for f in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/REMAINING_BATCH_FLOORS.json']:old+=json.load(open(ROOT/f))['regions']
previous=unary_union([Polygon(t)for q in old if q['deck']=='D03'for t in q['triangles']]);check('no_old_floor_overlay',actual.intersection(previous.buffer(-.001)).area<1e-7)

prior=[]
for folder,file in [('d03_remaining_receivers_batch013','MISSING_ONLY_FLOOR_PATCH.json'),('port2_clinical_physical_batch016','PORT2_MISSING_ONLY_FLOORS.json'),('d03_service_receivers_physical_batch021','D03_SERVICE_MISSING_FLOOR.json')]:
 for q in json.load(open(HERE.parent/folder/'source'/file))['parts']:
  y=q['y']if'y'in q else q['aabb'][2:4]
  if y[1]==12:prior.append(Polygon(q['boundary'],q['holes'])if'boundary'in q else box(q['aabb'][0],q['aabb'][4],q['aabb'][1],q['aabb'][5]))
prior=unary_union(prior);check('no_prior_Group3_floor_overlay',actual.intersection(prior.buffer(-.001)).area<1e-7)
for x,z in [(-57,-293),(-56.5,-293),(-54.7,-293),(-52.5,-293),(-45,-293),(-33,-293),(-21,-293),(-21,-291.4),(-21,-289.5),(-21,-286.8)]:check('worker_branch_support_'+str((x,z)),Point(x,z).buffer(.3).difference(actual.union(previous).union(prior)).area<1e-7)
# Cross-rays compare the actual exported current derivative, including the
# protected upper wall/roof and both sides outside the disclosed aperture.
oldg=GLB(ROOT/p['current_spine_source']);newg=GLB(HERE/'exports/AST-STF-G3-052.glb')
check('exact_current_replacement_names',{n for n,q in newg.by_name.items()if'mesh'in q}==set(p['exact_current_meshes_to_replace']))
def triangles(g):
 out=[]
 for name in p['exact_current_meshes_to_replace']:
  v,f,_,_=g.geometry(name);out.extend(np.asarray(v)[np.asarray(f)])
 return np.asarray(out)
a=triangles(oldg);b=triangles(newg)
def cross_hit(t,y,z):
 o=np.array([-55.6,y,z]);d=np.array([.6,0,0]);e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);den=(e1*h).sum(axis=1);valid=abs(den)>1e-10;inv=np.zeros_like(den);inv[valid]=1/den[valid];s=o-t[:,0];u=inv*(s*h).sum(axis=1);q=np.cross(s,e1);v=inv*(np.broadcast_to(d,q.shape)*q).sum(axis=1);f=inv*(e2*q).sum(axis=1)
 return bool(np.any(valid&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1.0000001)&(f>=0)&(f<=1)))
for y in [12.1,12.7,13.1,14.5,14.9,15.1,15.3]:
 for z in [-299,-296,-295,-294.7,-293.5,-293,-291.3,-291,-288,-281]:
  before=cross_hit(a,y,z);after=cross_hit(b,y,z);cut=y<14.852 and -294.8<z<-291.2
  check('current_native_cross_section_'+str((y,z)),not after if cut else after==before)
check('two_unassigned_operation_IDs',len(p['door_bindings'])==2 and all(q['persistent_id']is None for q in p['door_bindings']))
check('no_person_or_berth_mapping',p['authoritative_identity_map']is None and p['registered_berths_added']==0)
q=dict(status='PASS',checks=len(checks),exports=counts,new_floor_m2=actual.area,planned_floor_m2=planned.area,current_composite_cells_replaced=len(p['exact_current_meshes_to_replace']),other_current_composite_native_cells_preserved=288-len(p['exact_current_meshes_to_replace']),fixture_profiles=len(p['fixtures']),source_originals_and_previous_slices_unchanged=True,whole_group_species_loaded_cart_primary_structure_graphical_or_400_assigned_berth_acceptance=False,details=checks)
(HERE/'qa/NATIVE_GEOMETRY_CHECKS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='details'}))
