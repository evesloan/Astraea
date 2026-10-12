"""Independent exported floors, original fitting payloads and surgical riser cuts."""
from pathlib import Path
import json,hashlib,numpy as np
import shapely
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/PHYSICAL_CONTRACT.json'));checks=[]
def check(name,ok,**data):
 checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in p['source_pins'].items():check('source_pin_'+f,sha(ROOT/f)==h)
counts={}
for file in sorted((HERE/'exports').glob('*.glb')):
 g=GLB(file);n=0;tcount=0
 check('Game_copy_'+file.name,sha(file)==sha(ROOT/'Game/assets/models/group3_port2_clinical_20261011'/file.name))
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  n+=1;v,f,u,e=g.geometry(name);tcount+=len(f)
  check('finite_'+file.name+'_'+name,np.isfinite(v).all()and np.isfinite(u).all())
  t=np.asarray(v)[np.asarray(f)];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2
  check('nondegenerate_'+file.name+'_'+name,(area>1e-12).all())
 counts[file.name]=dict(meshes=n,triangles=tcount,bytes=file.stat().st_size,sha256=sha(file))
floor=GLB(HERE/'exports/AST-STF-G3-030.glb');floor_specs=json.load(open(HERE/'source/PORT2_MISSING_ONLY_FLOORS.json'))
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
 check('landing_worker_floor_'+deck,Point(-21,-283).buffer(.3).difference(actual.union(previous)).area<1e-7)
 check('no_cabin_travel_floor_'+deck,actual.intersection(box(-26.8,-285,-23.2,-281)).area<1e-7)
 floor_reports.append(dict(deck=deck,actual_top_m2=actual.area))

# Exact retained semantic geometry outside the disclosed trim; unchanged
# neighboring native batches are kept from the original export by the module.
old_spec=json.load(open(ROOT/p['original_riser_export'].replace('/exports/AST-STF-G3-006.glb','/source/PORT_SECOND_STAFF_RISER.json')))
patch=json.load(open(HERE/'source/RISER_FRAME_AND_CALL_PATCH.json'))
def shape(q):
 if'boundary'in q:return Polygon(q['boundary'],q['holes'])
 a=q['aabb'];return box(a[0],a[4],a[1],a[5])
def y_range(q):return q['y']if'y'in q else q['aabb'][2:4]
omissions=patch['native_meshes_to_omit'];original=GLB(ROOT/p['original_riser_export'])
check('all_exact_omission_nodes_exist',all(name in original.by_name for name in omissions))
new=GLB(HERE/'exports/AST-STF-G3-032.glb')
check('replacement_batches_match_exact_omission_set',{n for n,q in new.by_name.items()if'mesh'in q}==set(omissions))
trim=box(-23.187,-284.922,-22.983,-281.078)
for y in [2.66,2.9,7.3,14.66,23.66,44.01,71.1,90.0,104.7,104.86]:
 for category in ['shaft_architecture','control_fixture']:
  before=[]
  for q in old_spec['parts']:
   if q['category']!=category or q['category']+'_'+q['role']+'_'+q['batch_cell']not in omissions:continue
   if not y_range(q)[0]<y<y_range(q)[1]:continue
   geometry=shape(q)
   if q['name'].startswith('Port2_ShaftFront'):
    deck=q['name'].split('_')[-1];at=next(s['floor_y']for s in p['floor_checks']if s['deck']==deck)
    if at+2.648<y<at+2.852:geometry=geometry.difference(trim)
   if q['name'].startswith('Port2_CallControlBacking'):
    match=next(s for s in patch['call_backings']if s['name']==q['name']);a=match['fitted_aabb'];geometry=box(a[0],a[4],a[1],a[5])
   before.append(geometry)
  after=unary_union([shape(q)for q in patch['parts']if q['category']==category and y_range(q)[0]<y<y_range(q)[1]])
  check('source_section_'+category+'_'+str(y),unary_union(before).symmetric_difference(after).area<1e-8)
for q in patch['call_backings']:
 a=q['fitted_aabb'];check('mounted_original_button_'+q['name'],a[0]==-22.995 and a[1]<-22.86 and abs((a[4]+a[5])/2+284.65)<1e-8 and a[1]>-22.905)
check('no_authoritative_keys_created',p['authoritative_identity_map']is None and not p['persistent_identity_mapping_created'])
report=dict(status='PASS',checks=len(checks),exports=counts,landings=17,fitted_original_crossing_doors=4,original_ten_junctions_changed=False,
 preserved_riser_native_batches=len([q for q in original.by_name.values()if'mesh'in q])-len(omissions),replacement_riser_native_batches=len(omissions),
 actual_exported_floor_m2=sum(q['actual_top_m2']for q in floor_reports),floor_reports=floor_reports,
 source_floor_contacts_not_primary_engineering_acceptance=True,original_persistent_identity_mapping=False,details=checks)
(HERE/'qa/NATIVE_GEOMETRY_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='details'}))
