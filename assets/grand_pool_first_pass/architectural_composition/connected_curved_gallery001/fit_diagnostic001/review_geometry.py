"""Exact pure geometry fit before source authoring; no engine/shared write."""
from pathlib import Path
import json,math,hashlib,ast,sys,collections,importlib.util,time
sys.dont_write_bytecode=True;sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely import constrained_delaunay_triangles,union_all
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');TOL=5e-5
spec=importlib.util.spec_from_file_location('geo',C/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py');geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
for n in dir(geo):
 if not n.startswith('_'):globals()[n]=getattr(geo,n)
def definitions(path,names):
 tree=ast.parse(path.read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in names],type_ignores=[]),str(path),'exec'),globals())
definitions(C/'assets/grand_pool_first_pass/finish_envelope/qa/pure_geometry/review_finish.py',{'record','rayhits','surface_points','on_surface','strict_inside','contact_pair','topology'})
definitions(S/'pool-opposite-gallery-proposal001/source_blockin001/review_core.py',{'triang_face'})
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
plan=read(B/'CORE_PLAN.json');assert sha(plan['source_base'])==plan['source_base_sha256']
parts=[record(p['name'],p['vertices_xyz'],[t for f in p['faces']for t in triang_face(p['vertices_xyz'],f)],meta=p)for p in plan['parts']]
oldglb=read_glb(C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');old=[]
for p in read(S/'pool-opposite-gallery-proposal001/geometry/RETAINED_PART_BOUNDS.json')['parts']:
 ts=[oldglb['triangles'][i]for i in p['global_triangle_indices']];old.append(record(p['source_name'],[v for t in ts for v in t],ts,meta=p))
floor=next(p for p in read(S/'pool-opposite-gallery-proposal001/geometry/FLOOR_POLYGONS.json')['floor_regions']if p['id']=='D09_orchard_market_gallery');floorpoly=union_all([Polygon(t)for t in floor['triangles']]);fm=record('COMPILER_FLOOR_D09_orchard_market_gallery',[[x,52.5,z]for t in floor['triangles']for x,z in t],[[[x,52.5,z]for x,z in t]for t in floor['triangles']]);old.append(fm)
for p in parts+old:p['ta']=np.array(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1)
issues=[];tops=[topology(p)for p in parts]
for t in tops:
 if t['degenerate_triangles']or t['nonmanifold_edges']or t['inconsistent_winding_edges']:issues.append({'kind':'topology','row':t})
print('Topology',len(issues),flush=True)
new_names=set(plan['new_parts']);changed=set(plan['modified_existing_parts']);active=[p for p in parts if p['name']in new_names|changed];contacts=collections.defaultdict(list);penetrations=[]
for i,p in enumerate(parts):
 for q in parts[i+1:]:
  if not overlap(p['bounds'],q['bounds'],TOL):
   # Touching bounds are relevant to actual support contact.
   if any(p['bounds'][0][k]>q['bounds'][1][k]+TOL or q['bounds'][0][k]>p['bounds'][1][k]+TOL for k in range(3)):continue
  r=contact_pair(p,q)
  if r['penetration']:penetrations.append({'a':p['name'],'b':q['name'],'evidence':r})
  elif r['touch']:contacts[p['name']].append(q['name']);contacts[q['name']].append(p['name'])
 if i%40==0:print('Pair checks',i,len(penetrations),flush=True)
print('New pair terminal',len(penetrations),flush=True)
retained=[]
for p in active:
 for q in old:
  if any(p['bounds'][0][k]>q['bounds'][1][k]+TOL or q['bounds'][0][k]>p['bounds'][1][k]+TOL for k in range(3)):continue
  r=contact_pair(p,q)
  if r['penetration']:retained.append({'a':p['name'],'b':q['name'],'evidence':r})
  elif r['touch']:contacts[p['name']].append(q['name'])
issues += [{'kind':'new_part_overlap','rows':penetrations}]if penetrations else[]
issues += [{'kind':'retained_overlap','rows':retained}]if retained else[]
# All added/modified components need a real contact path to retained structure, no declared-name shortcut.
oldnames={p['name']for p in old};unchanged={p['name']for p in parts if p['name']not in new_names|changed}
def path(start):
 todo=collections.deque([(start,[start])]);seen=set()
 while todo:
  n,chain=todo.popleft()
  if n in oldnames|unchanged:return chain
  if n in seen:continue
  seen.add(n)
  for q in contacts[n]:todo.append((q,chain+[q]))
 return None
rooted={p['name']:path(p['name'])for p in active}
for n,p in rooted.items():
 if not p:issues.append({'kind':'no_actual_support_path','name':n})
protected=read(S/'pool-opposite-gallery-proposal001/geometry/PROTECTED_RESERVATIONS.json');routes=[]
for r in protected['routes']:
 poly=union_all([Polygon(v)for v in r['plan_polygon_union_xz']]);hits=[]
 for p in active:
  if min(p['bounds'][1][1],r['y_m'][1])-max(p['bounds'][0][1],r['y_m'][0])<=TOL:continue
  foot=union_all([Polygon([(v[0],v[2])for v in t])for t in p['triangles']if Polygon([(v[0],v[2])for v in t]).area>1e-12])
  if foot.intersection(poly).area>1e-8:hits.append(p['name'])
 routes.append({'name':r['id'],'hits':hits})
 if hits:issues.append({'kind':'protected_route','name':r['id'],'hits':hits})
floorrows=[]
for p in active:
 if abs(p['bounds'][0][1]-52.5)>TOL:continue
 base=union_all([Polygon([(v[0],v[2])for v in t])for t in p['triangles']if max(abs(v[1]-52.5)for v in t)<TOL]);outside=base.difference(floorpoly).area;floorrows.append({'name':p['name'],'area':base.area,'uncovered':outside})
 if outside>1e-7 or base.area<1e-7:issues.append({'kind':'floor_bearing','row':floorrows[-1]})
lightrows=[]
for f in plan['fixture_reservations']:
 hits=rayhits(f['position_xyz'],add(f['position_xyz'],mul(f['direction_xyz'],.06)),parts);lightrows.append({'name':f['name'],'hits':hits})
 if hits:issues.append({'kind':'fixture_exit','row':lightrows[-1]})
views=[]
for v in plan['seated_views']:
 for target in ['market_target_xyz','media_target_xyz']:
  hits=rayhits(v['eye_xyz'],v[target],[p for p in parts if p['name']!='EAST_Display_AngledReceiver']);views.append({'name':v['name'],'target':target,'hits':hits})
  if hits:issues.append({'kind':'seat_view','row':views[-1]})
r={'status':'PASS_PURE_CONNECTED_GALLERY_GEOMETRY'if not issues else'CORRECTION_REQUIRED','plan_sha256':sha(B/'CORE_PLAN.json'),'source_base_sha256':sha(plan['source_base']),'parts':len(parts),'active_parts':len(active),'issues':issues,'topology':tops,'actual_contact_graph':dict(contacts),'actual_support_paths':rooted,'routes':routes,'floor_bearing':floorrows,'fixture_exits':lightrows,'seated_views':views,'excluded':['actual retained new plants/furniture placement and root contacts','editable source UV/material/reopen','native lighting and visual acceptance'],'engine_run':False}
(B/'PURE_GEOMETRY_REVIEW.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'issues':issues},indent=2),flush=True)
