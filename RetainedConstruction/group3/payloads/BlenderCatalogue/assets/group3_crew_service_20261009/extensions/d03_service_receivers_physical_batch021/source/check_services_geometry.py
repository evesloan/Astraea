"""Independent native topology, fitting travel, support and protected source audit."""
from pathlib import Path
import json,hashlib,numpy as np,math
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/D03_SERVICE_CONTRACT.json'));checks=[]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def check(name,ok,**data):checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
for f,h in p['source_pins'].items():check('source_pin_'+f,sha(ROOT/f)==h)
counts={}
for path in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(path);n=tris=0;check('runtime_copy_'+path.name,sha(path)==sha(ROOT/'Game/assets/models/group3_d03_services_20261011'/path.name))
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  v,f,u,e=g.geometry(name);n+=1;tris+=len(f);check('finite_'+path.name+name,np.isfinite(v).all()and np.isfinite(u).all());t=np.asarray(v)[np.asarray(f)];a=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2;check('nondegenerate_'+path.name+name,(a>1e-12).all())
 counts[path.name]=dict(meshes=n,triangles=tris,bytes=path.stat().st_size,sha256=sha(path))
g=GLB(HERE/'exports/AST-STF-G3-050.glb');top=[]
for name,node in g.by_name.items():
 if'mesh'not in node:continue
 v,f,u,e=g.geometry(name)
 for i,face in enumerate(f):
  t=np.asarray([v[k]for k in face])
  if abs(t[:,1]-12).max()>.000001:continue
  check('outward_floor_'+name+str(i),np.cross(t[1]-t[0],t[2]-t[0])[1]>0);top.append(Polygon(t[:,[0,2]]))
actual=unary_union(top);spec=json.load(open(HERE/'source/D03_SERVICE_MISSING_FLOOR.json'));planned=unary_union([Polygon(q['boundary'],q['holes'])for q in spec['parts']])
# Expected boundary uses IEEE float32 export coordinates; this preserves an
# exact topology comparison without inventing a large-area tolerance.
def f32(r):return [[float(np.float32(x)),float(np.float32(z))]for x,z in r]
quantized=unary_union([Polygon(f32(q['boundary']),[f32(r)for r in q['holes']])for q in spec['parts']]);check('exact_float32_floor_topology',actual.symmetric_difference(quantized).area<1e-7)

old=[]
for f in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/data/architecture/REMAINING_BATCH_FLOORS.json']:old+=json.load(open(ROOT/f))['regions']
previous=unary_union([Polygon(t)for q in old if q['deck']=='D03'for t in q['triangles']]);check('no_old_floor_overlay',actual.intersection(previous.buffer(-.001)).area<1e-7)
prior=[]
for folder,file in [('d03_remaining_receivers_batch013','MISSING_ONLY_FLOOR_PATCH.json'),('labelled_crew_bank_batch014','BANK_MISSING_ONLY_FLOOR.json'),('fore_starboard_clinical_batch018','FORE_MISSING_ONLY_FLOORS.json'),('port2_clinical_physical_batch016','PORT2_MISSING_ONLY_FLOORS.json'),('starboard3_private_landings_batch019','STARBOARD3_MISSING_FLOORS.json')]:
 for q in json.load(open(HERE.parent/folder/'source'/file))['parts']:
  y=q['y']if'y'in q else q['aabb'][2:4]
  if y[1]==12:prior.append(Polygon(q['boundary'],q['holes'])if'boundary'in q else box(q['aabb'][0],q['aabb'][4],q['aabb'][1],q['aabb'][5]))
prior=unary_union(prior);check('no_prior_Group3_floor_overlay',actual.intersection(prior.buffer(-.001)).area<1e-7)
for name,z,sign in [('breakroom',-420,1),('dining',-216,1),('care',422,-1),('recreation',216,-1),('briefing',216,1)]:
 for x in[sign*57,sign*56,sign*54.5,sign*52.2]:check('supported_approach_'+name+str(x),Point(x,z).buffer(.3).difference(actual.union(previous).union(prior)).area<1e-7)
# Original custom care roof/wall vertices and topology are rigidly retained.
original=json.load(open(HERE.parent/'care_dogleg_batch010/source/CARE_DOGLEG.json'));new=json.load(open(HERE/'source/D03_SERVICE_ARCHITECTURE.json'));byname={q['name']:q for q in new['parts']}
for q in original['parts']:
 if'vertices_godot'in q:check('original_custom_care_'+q['name'],q==byname[q['name']])
check('five_unassigned_fitting_IDs',len(p['door_bindings'])==5 and all(q['persistent_id']is None for q in p['door_bindings']))
check('original_headers_preserved',all(q['original_room_or_header_modified']is False for q in p['door_bindings']))
check('no_person_or_berth_mapping',p['authoritative_identity_map']is None and p['registered_berths_added']==0)
q=dict(status='PASS',checks=len(checks),exports=counts,new_floor_m2=actual.area,planned_floor_m2=planned.area,receivers=5,fixture_profiles=len(p['fixtures']),source_originals_and_previous_slices_unchanged=True,whole_group_species_loaded_cart_primary_structure_graphical_or_400_assigned_berth_acceptance=False,details=checks)
(HERE/'qa/NATIVE_GEOMETRY_CHECKS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='details'}))
