"""Independent native rest-face witnesses and exported floor orientation, including source batch015."""
from pathlib import Path
import sys,json,hashlib,numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
checks=[]
def check(name,ok,**data):
 checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
def face_height(g,prefix,point):
 x,y,z=point;hits=[]
 for name,node in g.by_name.items():
  if'mesh'not in node or not name.startswith(prefix):continue
  # Blender truncates long anonymous allocation object names to 63 bytes.
  # Material identifiers remain intact and identify the actual original cloth.
  materials=[g.doc['materials'][p['material']]['name']for p in g.doc['meshes'][node['mesh']]['primitives']if'material'in p]
  if not any(s in m for m in materials for s in ['crew_ecru_sheet','crew_terracotta_blank']):continue
  v,faces,_,_=g.geometry(name)
  for f in faces:
   t=np.asarray([v[i]for i in f]);cross=np.cross(t[1]-t[0],t[2]-t[0])
   if cross[1]<1e-10:continue
   try:w=np.linalg.solve(np.vstack((t[:,[0,2]].T,np.ones(3))),[x,z,1])
   except np.linalg.LinAlgError:continue
   if w.min()>-1e-6:hits.append(float(w@t[:,1]))
 return max(hits)if hits else None
counts={}
for folder,contract,asset in [(HERE,'LABELLED_BANK_CONTRACT.json','AST-CRW-G3-002'),(HERE.parent/'remaining_crew_bank_source_batch015','REMAINING_BANK_CONTRACT.json','AST-CRW-G3-003')]:
 p=json.load(open(folder/'source'/contract));g=GLB(folder/'exports'/f'{asset}.glb')
 for f,h in p['source_pins'].items():check('retained_pin_'+asset+'_'+f,hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h)
 count=0;triangles=0
 for name,node in g.by_name.items():
  if'mesh'not in node:continue
  count+=1;v,t,u,e=g.geometry(name);triangles+=len(t)
  check('finite_'+asset+'_'+name,np.isfinite(v).all()and np.isfinite(u).all())
 for s in p['rest_surfaces']:
  prefix=s['reference_room_id']+'__Rest'+s['place']+'__Frame__';height=face_height(g,prefix,s['surface'])
  check('actual_upward_rest_face_'+asset+'_'+s['reference_room_id']+s['place'],height is not None and abs(height-s['surface'][1])<.00003,
   recorded_surface=s['surface'],actual_export_face_y=height)
 check('no_registered_berths_'+asset,p['new_registered_berths']==0 and not p['C036_migration_applied'])
 counts[asset]=dict(meshes=count,triangles=triangles,rest_faces=len(p['rest_surfaces']),bytes=g.path.stat().st_size)
floor=GLB(HERE/'exports/AST-STF-G3-029.glb');tops=[]
for name,node in floor.by_name.items():
 if'mesh'not in node:continue
 v,faces,_,_=floor.geometry(name)
 for f in faces:
  t=np.asarray([v[i]for i in f])
  if np.max(np.abs(t[:,1]-12))>.0001:continue
  check('actual_floor_upward_'+str(len(tops)),np.cross(t[1]-t[0],t[2]-t[0])[1]>0)
  tops.append(Polygon(t[:,[0,2]]))
actual_floor=unary_union(tops);planned=json.load(open(HERE/'source/BANK_MISSING_ONLY_FLOOR.json'))
plan=unary_union([Polygon(q['boundary'],q['holes'])for q in planned['parts']])
check('exported_floor_matches_plan',actual_floor.symmetric_difference(plan).area<.01)
old=[]
for f in ['structural_meshes.json','received_structural_meshes.json']:
 old.extend(Polygon(t)for q in json.load(open(ROOT/'Game/data/generated'/f))['regions']if q['deck']=='D03'for t in q['triangles'])
old.extend(Polygon(q['boundary'],q['holes'])for q in json.load(open(HERE.parent/'d03_remaining_receivers_batch013/source/MISSING_ONLY_FLOOR_PATCH.json'))['parts'])
prior=unary_union(old);check('no_existing_floor_overlap_at_1mm',actual_floor.intersection(prior.buffer(-.001)).area<1e-7)
support=prior.union(actual_floor)
for z in np.linspace(-141,-43.1,120):check('protected_column_clear_worker_lane_'+str(z),Point(87,z).buffer(.3).difference(support).area<1e-7)
report=dict(status='PASS',checks=len(checks),native_exports=counts,unassigned_actual_source_rest_faces=398,new_bank_floor_m2=actual_floor.area,
 baseline_shared_home_rests_retained=2,registered_berths_added=0,
 scope='Source physical rests and selected floor support only. Batch015 is uninstalled; no original 400-key, species, engineering or final-game acceptance.',details=checks)
(HERE/'qa/EXPORT_BANK_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='details'}))
