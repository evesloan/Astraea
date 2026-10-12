"""Independent native topology, fitting travel, support and protected source audit."""
from pathlib import Path
import json,hashlib,numpy as np,math
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/COMPLETE_CLINICAL_CONTRACT.json'));checks=[]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def check(name,ok,**data):checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
for f,h in p['source_pins'].items():check('source_pin_'+f,sha(ROOT/f)==h)
counts={}
for path in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(path);n=tris=0;check('runtime_copy_'+path.name,sha(path)==sha(ROOT/'Game/assets/models/group3_clinical_full_20261011'/path.name))
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  v,f,u,e=g.geometry(name);n+=1;tris+=len(f);check('finite_'+path.name+name,np.isfinite(v).all()and np.isfinite(u).all());t=np.asarray(v)[np.asarray(f)];a=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2;check('nondegenerate_'+path.name+name,(a>1e-12).all())
 counts[path.name]=dict(meshes=n,triangles=tris,bytes=path.stat().st_size,sha256=sha(path))
g=GLB(HERE/'exports/AST-MED-G3-008.glb');top=[]
for name,node in g.by_name.items():
 if'mesh'not in node:continue
 v,f,u,e=g.geometry(name)
 for i,face in enumerate(f):
  t=np.asarray([v[k]for k in face])
  if abs(t[:,1]-21).max()>.000001:continue
  check('outward_floor_'+name+str(i),np.cross(t[1]-t[0],t[2]-t[0])[1]>0);top.append(Polygon(t[:,[0,2]]))
actual=unary_union(top);spec=json.load(open(HERE/'source/CLINICAL_COMPLETE_MISSING_FLOOR.json'));planned=unary_union([Polygon(q['boundary'],q['holes'])for q in spec['parts']])
# Expected boundary uses IEEE float32 export coordinates; this preserves an
# exact topology comparison without inventing a large-area tolerance.
def f32(r):return [[float(np.float32(x)),float(np.float32(z))]for x,z in r]
quantized=unary_union([Polygon(f32(q['boundary']),[f32(r)for r in q['holes']])for q in spec['parts']]);check('exact_float32_floor_topology',actual.symmetric_difference(quantized).area<1e-7)
old=[]
for f in ['structural_meshes.json','received_structural_meshes.json']:old+=json.load(open(ROOT/'Game/data/generated'/f))['regions']
old+=json.load(open(ROOT/'Game/data/architecture/REMAINING_BATCH_FLOORS.json'))['regions']
previous=unary_union([Polygon(t)for q in old if q['deck']=='D05'for t in q['triangles']]);prior=[]
for folder,file in [('port2_clinical_physical_batch016','PORT2_MISSING_ONLY_FLOORS.json'),('fore_starboard_clinical_batch018','FORE_MISSING_ONLY_FLOORS.json')]:
 for q in json.load(open(HERE.parent/folder/'source'/file))['parts']:
  if q['batch_cell']=='D05':prior.append(Polygon(q['boundary'],q['holes']))
prior=unary_union(prior);check('no_old_compiled_floor_overlay',actual.intersection(previous.buffer(-.001)).area<1e-7);check('no_prior_Group3_floor_overlay',actual.intersection(prior.buffer(-.001)).area<1e-7)
for h in p['held_support_spans']:check('support_span_excluded_'+h['name'],actual.intersection(box(*h['bounds_xz']).buffer(-.001)).area<1e-7)
slider=json.load(open(HERE/'qa/SLIDING_NATIVE_ASSEMBLY.json'))
fixed=[q for q in slider['template_new_parts']if not q['name'].startswith(('LEFT_','RIGHT_'))]
leaves=[[q for q in slider['template_new_parts']if q['name'].startswith(side+'_')]for side in ['LEFT','RIGHT']]
def volume_overlap(a,b):return all(min(a[j+1],b[j+1])-max(a[j],b[j])>1e-8 for j in[0,2,4])
for step in range(41):
 f=step/40;poses=[]
 for i,parts in enumerate(leaves):
  d=(-1.9 if i==0 else 1.9)*(min(1,f/.85)if i==0 else max(0,min(1,(f-.15)/.85)));poses.append([[q['aabb'][0]+d,q['aabb'][1]+d,*q['aabb'][2:]]for q in parts])
  for q,a in zip(parts,poses[-1]):
   for r in fixed:check('source_slider_travel_'+str(step)+q['name']+r['name'],not volume_overlap(a,r['aabb']))
 for i,a in enumerate(poses[0]):
  for j,b in enumerate(poses[1]):check('opposed_source_leaves_'+str(step)+str(i)+'_'+str(j),not volume_overlap(a,b))
check('clear_source_aperture',slider['clear_aperture_m']==[3.6,2.4]and slider['travel_m']==1.9)
check('thirty_six_closed_source_gates',len(p['door_bindings'])==36 and all(q['persistent_id']is None for q in p['door_bindings']))
check('support_hold_disables_district06_return',not next(q for q in p['crossings']if q['programme_key']=='D05_directory_06')['sealed_return_available'])
check('no_person_or_room_keys_created',p['authoritative_identity_map']is None and p['authoritative_operation_IDs']is None and not p['original_D01_D04_or_medical_room_or_shared_root_modified'])
q=dict(status='PASS',checks=len(checks),exports=counts,new_floor_m2=actual.area,planned_floor_m2=planned.area,exact_float32_plan_topology=True,crossings=9,source_sliding_gates=36,held_crossings=1,fixture_profiles=len(p['fixtures']),native_slider_poses=41,held_cross_group_interfaces=3,originals_or_old_receivers_modified=False,full_group_or_medical_stock_sterility_species_loaded_cart_primary_structure_graphical_or_final_acceptance=False,details=checks)
(HERE/'qa/NATIVE_GEOMETRY_CHECKS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='details'}))
