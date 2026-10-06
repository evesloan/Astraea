"""Actual reopened new/new contact diagnosis; no source/engine edits."""
import sys,ast,json,math,hashlib,collections,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from shapely.geometry import Polygon,Point
from shapely import constrained_delaunay_triangles
S=Path(__file__).resolve().parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');P=C/'assets/grand_pool_first_pass';TOL=5e-5
sp=importlib.util.spec_from_file_location('geometry',P/'finish_envelope/stock/geometry.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
for name in dir(g):
 if not name.startswith('_'):globals()[name]=getattr(g,name)
helper=P/'finish_envelope/qa/pure_geometry/review_finish.py';tree=ast.parse(helper.read_text());wanted={'record','triang_face','rayhits','surface_points','on_surface','strict_inside','contact_pair'};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in wanted],type_ignores=[]),str(helper),'exec'))
plan_path=P/'architectural_composition/source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json';plan=json.loads(plan_path.read_text());parts=[record(p['name'],p['vertices_xyz'],[t for f in p['faces']for t in triang_face(p['vertices_xyz'],f)],meta=p)for p in plan['parts']]
for p in parts:p['ta']=np.array(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1)
penetrations=[];touches=[];broad=0
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  if not overlap(a['bounds'],b['bounds'],-TOL):continue
  broad+=1;result=contact_pair(a,b)
  if result['penetration']:penetrations.append(dict(a=a['name'],b=b['name'],**result))
  elif result['touch']:touches.append([a['name'],b['name']])
meta={p['name']:p['meta']for p in parts};allowed=[r for r in penetrations if meta[r['a']].get('intentional_new_mechanical_joint')==r['b']or meta[r['b']].get('intentional_new_mechanical_joint')==r['a']];unexpected=[r for r in penetrations if r not in allowed];assert len(allowed)==4
report=dict(status='PASS_ACTUAL_NEW_NEW_WITH_FOUR_NAMED_MOUNTING_JOINTS'if not unexpected else'FAIL_UNCLASSIFIED_INTERSECTION',unexpected_intersections=unexpected,named_mechanical_joints=allowed,actual_plan_sha256=hashlib.sha256(plan_path.read_bytes()).hexdigest(),broad_pairs=broad,positive_volume_intersections=penetrations,surface_contacts=touches,scope='Intersections require exact intentional-joint classification or geometry correction; no blanket allowance.');(S/'ACTUAL_NEW_NEW_003.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'broad_pairs':broad,'penetrations':penetrations,'surface_contacts':len(touches)},indent=2))

assert not unexpected,unexpected
