"""Independent export triangles, plan sections, real floor and ownership evidence."""
from pathlib import Path
import hashlib,json,math
import numpy as np
import shapely
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from native_glb_subset import GLB
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok,**data):
 checks.append(dict(name=name,pass_check=bool(ok),**data));assert ok,name
contract=json.load(open(HERE/'source/PRECINCT_CONTRACT.json'))
for f,h in contract['source_pins'].items():check('retained_input_'+f,sha(ROOT/f)==h)
first=json.load(open(HERE/'qa/FIRST_EXPORT_SHA256.json'))
counts={};models={}
for f,h in first.items():
 g=GLB(HERE/'exports'/f);models[f]=g;meshcount=0;triangles=0
 check('runtime_copy_'+f,sha(g.path)==sha(ROOT/'Game/assets/models/group3_completion_20261011'/f)==h)
 for name,q in g.by_name.items():
  if'mesh'not in q:continue
  meshcount+=1;vs,fs,uv,extra=g.geometry(name);v=np.asarray(vs);face=np.asarray(fs);triangles+=len(face)
  check('finite_'+f+'_'+name,np.isfinite(v).all()and np.isfinite(uv).all())
  t=v[face];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2
  check('nondegenerate_'+f+'_'+name,(area>1e-12).all(),minimum_triangle_area_m2=float(area.min()))
  # No reversed duplicate faces in compact material batches.
  oriented={tuple(sorted(tuple(np.round(v[k],6))for k in face_row)):[]for face_row in face}
  for i,row in enumerate(face):oriented[tuple(sorted(tuple(np.round(v[k],6))for k in row))].append(cross[i])
  opposed=sum(any(np.dot(a,b)<-1e-14 for a in norms for b in norms)for norms in oriented.values()if len(norms)>1)
  check('no_opposed_duplicate_faces_'+f+'_'+name,opposed==0)
 counts[f]=dict(meshes=meshcount,triangles=triangles,bytes=g.path.stat().st_size)

# Actual exported slab sections. Top triangles, not the JSON plan, supply support.
floor=models['AST-STF-G3-027.glb'];tops=[]
for name,q in floor.by_name.items():
 if'mesh'not in q:continue
 v,f,_,_=floor.geometry(name)
 for indices in f:
  t=[v[i]for i in indices]
  if max(abs(p[1]-12)for p in t)<.0001:
   cross=np.cross(np.asarray(t[1])-t[0],np.asarray(t[2])-t[0])
   check('actual_floor_top_faces_outward_'+str(len(tops)),cross[1]>0)
   tops.append(Polygon([(p[0],p[2])for p in t]))
exported_floor=unary_union(tops)
spec=json.load(open(HERE/'source/MISSING_ONLY_FLOOR_PATCH.json'))
planned_floor=unary_union([Polygon(p['boundary'],p['holes'])for p in spec['parts']])
check('actual_export_top_area_matches_plan',exported_floor.symmetric_difference(planned_floor).area<.008,
 float32_symmetric_difference_m2=exported_floor.symmetric_difference(planned_floor).area)
struct=json.load(open(ROOT/'Game/data/generated/structural_meshes.json'));add=json.load(open(ROOT/'Game/data/generated/received_structural_meshes.json'))
actual=unary_union([Polygon(t)for q in struct['regions']+add['regions']if q['deck']=='D03'for t in q['triangles']])
check('no_existing_floor_duplicate_at_1mm_precision',exported_floor.intersection(actual.buffer(-.001)).area<1e-7)
support=exported_floor.union(actual)
points=[]
for side in [-1,1]:
 for z in range(-40,41,2):points.append([-102 if side==-1 else 103,12,z])
 for z in [-40,40]:
  for x in range(57,104,2):points.append([side*x,12,z])
 for x in np.linspace(97,102 if side==-1 else 103,25):points.append([side*float(x),12,0])
for z in np.linspace(420.4,435.3,32):points.append([57,12,float(z)])
for x in np.linspace(52.8,57,25):points.append([float(x),12,432])
for index,p in enumerate(points):
 missing=Point(p[0],p[2]).buffer(.3).difference(support).area
 check('exported_floor_worker_footprint_'+str(index),missing<1e-7,point=p,outside_floor_m2=missing)

# Original selected street source minus exactly the disclosed cuts, compared in horizontal sections.
selection=json.load(open(HERE/'source/SELECTED_STREET_PRECINCTS.json'))
source=json.load(open(HERE.parent.parent/'source/CREW_STREETS.json'))
old=[p for p in source['parts']if p['name']in selection['selected_original_semantic_parts']]
cuts=unary_union([Polygon(p)for p in selection['explicit_portal_cuts']])
columns=unary_union([box(q['bounds'][0],q['bounds'][4],q['bounds'][1],q['bounds'][5])for q in selection['protected_column_notches']])
area=unary_union([box(-105.7,-42.7,-53.4,42.7),box(53.4,-42.7,105.7,42.7),box(54.9,420,59.1,432.14)])
for y in [12.31,13.01,13.04,14.8,15.19,15.27]:
 for role in ['staff_bluegrey_paint','staff_white_paint']:
  before=unary_union([Polygon(p['boundary'],p['holes']).intersection(area).difference(cuts if p['category']=='screen_wall'else Polygon()).difference(columns)for p in old if p['role']==role and p['y'][0]<y<p['y'][1]])
  after=unary_union([Polygon(p['boundary'],p['holes'])for p in selection['parts']if'boundary'in p and p['role']==role and p['y'][0]<y<p['y'][1]])
  err=before.symmetric_difference(after).area;check('selected_street_source_section_'+str(y)+'_'+role,err<1e-8,error_m2=err)

report=dict(status='PASS',checks=len(checks),mesh_counts=counts,source_pins=len(contract['source_pins']),
 actual_export_worker_floor_footprints=len(points),new_floor_m2=exported_floor.area,
 scope='Exact retained inputs, finite native triangle geometry, disclosed source-section cuts and actual export floor support. No primary engineering, sterile-flow, driven-cart, species or complete-group acceptance.',details=checks)
(HERE/'qa/EXPORT_GEOMETRY_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k]for k in ['status','checks','mesh_counts','actual_export_worker_floor_footprints','new_floor_m2']}))
