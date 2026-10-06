"""Positive-area contact graph on actual saved blockin002 vertices. Read-only source."""
import sys,ast,json,hashlib,collections,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon,Point
from shapely import constrained_delaunay_triangles
S=Path(__file__).resolve().parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');G=Path('/workspace/shared/astraea-godot-production-20261003');P=C/'assets/grand_pool_first_pass';A=P/'architectural_composition';TOL=5e-5
sp=importlib.util.spec_from_file_location('geometry',P/'finish_envelope/stock/geometry.py');geo=importlib.util.module_from_spec(sp);sp.loader.exec_module(geo)
for name in dir(geo):
 if not name.startswith('_'):globals()[name]=getattr(geo,name)
helper=P/'finish_envelope/qa/pure_geometry/review_finish.py';tree=ast.parse(helper.read_text());wanted={'record','triang_face'};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in wanted],type_ignores=[]),str(helper),'exec'))
planpath=A/'source_tooling002/BLOCKIN_ACTUAL_PLAN_002.json';plan=json.loads(planpath.read_text());parts={p['name']:record(p['name'],p['vertices_xyz'],[t for f in p['faces']for t in triang_face(p['vertices_xyz'],f)],meta=p)for p in plan['parts']};contacts=json.loads((A/'source_tooling002/ACTUAL_NEW_NEW_002.json').read_text());assert not contacts['unexpected_intersections']
section=json.loads((G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json').read_text());floor=next(f for f in section['floor_regions']if f['id']=='D08_grand_pool_wet');cap=next(f for f in json.loads((G/'data/generated/structural_meshes.json').read_text())['regions']if f['id']=='D10_shared_table_reserved_cap');floor_shape=Polygon(floor['boundary'],floor['holes']);cap_shape=Polygon(cap['rings'][0],cap['rings'][1:]);roots={};edges=[];adj=collections.defaultdict(set)
def contact_area(a,b):
 area=0.
 for t in a['triangles']:
  tr=np.asarray(t);n=np.cross(tr[1]-tr[0],tr[2]-tr[0]);length=np.linalg.norm(n)
  if length<1e-12:continue
  n/=length;axis=int(np.argmax(np.abs(n)));pa=Polygon(np.delete(tr,axis,axis=1))
  for other in b['triangles']:
   q=np.asarray(other)
   if np.max(np.abs((q-tr[0])@n))>TOL:continue
   nn=np.cross(q[1]-q[0],q[2]-q[0]);ll=np.linalg.norm(nn)
   if ll<1e-12 or abs(float(n@nn/ll))<.999999:continue
   pb=Polygon(np.delete(q,axis,axis=1));area+=pa.intersection(pb).area/abs(n[axis])
 return area
for a,b in contacts['surface_contacts']:
 area=contact_area(parts[a],parts[b])
 if area>1e-8:edges.append(dict(a=a,b=b,contact_area_m2=area));adj[a].add(b);adj[b].add(a)
for row in contacts['named_mechanical_joints']:
 a,b=row['a'],row['b'];edges.append(dict(a=a,b=b,kind='exact named finite mechanical hanger joint'));adj[a].add(b);adj[b].add(a)
for name,p in parts.items():
 for label,y,shape in [('D08_grand_pool_wet',46.2,floor_shape),('D10_shared_table_reserved_cap_underside',60.76,cap_shape)]:
  area=0
  for t in p['triangles']:
   if max(abs(q[1]-y)for q in t)>TOL:continue
   tri=Polygon([(q[0],q[2])for q in t])
   if tri.area<=1e-10:continue
   assert tri.difference(shape).area<1e-8,(name,'root leaves retained floor',label)
   area+=tri.area
  if area>1e-8:roots.setdefault(name,[]).append(dict(owner=label,contact_area_m2=area))
# Three retained roof-rib source solids are verified against their actual GLB.
old=geo.read_glb(C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');triangles=np.array(old['triangles']);unique=np.unique(triangles.reshape(-1,3),axis=0);tree=cKDTree(unique);ix=tree.query(triangles.reshape(-1,3))[1].reshape(-1,3)
for spec in [p for p in section['source_parts']if p['name'].startswith('GP_RoofRib_')]:
 delta,ids=tree.query(spec['world_vertices']);assert max(delta)<TOL;mask=np.isin(ix,ids).all(axis=1);r=record(spec['name'],spec['world_vertices'],triangles[mask].tolist());assert r['triangles']
 for name,p in parts.items():
  if not overlap(p['bounds'],r['bounds'],-TOL):continue
  area=contact_area(p,r)
  if area>1e-8:roots.setdefault(name,[]).append(dict(owner=spec['name'],contact_area_m2=area))
seen=set(roots);pending=list(roots)
while pending:
 n=pending.pop()
 for other in adj[n]:
  if other not in seen:seen.add(other);pending.append(other)
missing=sorted(set(parts)-seen);report=dict(status='PASS_POSITIVE_AREA_ROOTED_CONTACT_GRAPH'if not missing else'FAIL_UNROOTED_PARTS',actual_plan_sha256=hashlib.sha256(planpath.read_bytes()).hexdigest(),parts=len(parts),direct_root_parts=len(roots),positive_area_connections=len(edges)-4,exact_named_mechanical_joints=4,roots=roots,connections=edges,unrooted=missing,scoped_floor_record_sha256={floor['id']:hashlib.sha256(json.dumps(floor,sort_keys=True).encode()).hexdigest(),cap['id']:hashlib.sha256(json.dumps(cap,sort_keys=True).encode()).hexdigest()},scope='Actual saved geometry contact graph; no real-world structural certification, final art, export or runtime acceptance.');(S/'ROOTED_SUPPORT_002.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['roots','connections']},indent=2));assert not missing
