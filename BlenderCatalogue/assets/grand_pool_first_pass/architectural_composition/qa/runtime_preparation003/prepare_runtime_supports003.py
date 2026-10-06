"""Derive actual retained surface witnesses; no Game or source writes."""
import json,hashlib,sys,importlib.util,ast
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles
S=Path(__file__).resolve().parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');G=Path('/workspace/shared/astraea-godot-production-20261003');P=C/'assets/grand_pool_first_pass';A=P/'architectural_composition';TOL=5e-5
sp=importlib.util.spec_from_file_location('geo',P/'finish_envelope/stock/geometry.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
for n in dir(g):
 if not n.startswith('_'):globals()[n]=getattr(g,n)
helper=P/'finish_envelope/qa/pure_geometry/review_finish.py';tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ['record','triang_face']],type_ignores=[]),str(helper),'exec'))
plan=json.loads((A/'source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json').read_text());roots=json.loads((A/'source_tooling003/ROOTED_SUPPORT_003.json').read_text());assert not roots['unrooted'];parts={p['name']:record(p['name'],p['vertices_xyz'],[t for f in p['faces']for t in triang_face(p['vertices_xyz'],f)],meta=p)for p in plan['parts']};section=json.loads((G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json').read_text());original=g.read_glb(C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');tri=np.array(original['triangles']);unique=np.unique(tri.reshape(-1,3),axis=0);tree=cKDTree(unique);ix=tree.query(tri.reshape(-1,3))[1].reshape(-1,3);ribs={}
for spec in section['source_parts']:
 if not spec['name'].startswith('GP_RoofRib_'):continue
 d,ids=tree.query(spec['world_vertices']);assert max(d)<TOL;mask=np.isin(ix,ids).all(axis=1);ribs[spec['name']]=record(spec['name'],spec['world_vertices'],tri[mask].tolist())
def witness(a,b):
 for t in a['triangles']:
  tr=np.array(t);n=np.cross(tr[1]-tr[0],tr[2]-tr[0]);length=np.linalg.norm(n)
  if length<1e-12:continue
  n/=length;axis=int(np.argmax(np.abs(n)));pa=Polygon(np.delete(tr,axis,axis=1))
  for other in b['triangles']:
   q=np.array(other)
   if np.max(np.abs((q-tr[0])@n))>TOL:continue
   nn=np.cross(q[1]-q[0],q[2]-q[0]);ll=np.linalg.norm(nn)
   if ll<1e-12 or abs(float(n@nn/ll))<.999999:continue
   polygon=pa.intersection(Polygon(np.delete(q,axis,axis=1)))
   if polygon.area<=1e-8:continue
   coords=list(polygon.representative_point().coords)[0];p=np.zeros(3);keep=[i for i in range(3)if i!=axis];p[keep]=coords;p[axis]=(np.dot(n,q[0])-sum(n[i]*p[i]for i in keep))/n[axis];return p.tolist()
 raise AssertionError((a['name'],b['name'],'no positive area witness'))
probes=[]
for name,owners in roots['roots'].items():
 owner=owners[0]['owner'];part=parts[name]
 if owner.startswith('GP_'):
  p=witness(part,ribs[owner]);z=float(owner.split('_')[-1]);direction=[0,0,1 if p[2]<z else -1];floor_owner=None
 else:
  y=46.2 if owner.startswith('D08')else 60.76;faces=[t for t in part['triangles']if max(abs(q[1]-y)for q in t)<TOL and abs(np.cross(np.array(t[1])-t[0],np.array(t[2])-t[0])[1])>1e-8];assert faces,name;p=np.mean(faces[0],axis=0).tolist();p[1]=y;direction=[0,-1,0]if owner.startswith('D08')else[0,1,0];floor_owner='D08_grand_pool_wet'if owner.startswith('D08')else'D10_shared_table_reserved_cap'
 probes.append(dict(part=name,owner=owner,floor_owner=floor_owner,position_xyz=p,into_support_xyz=direction))
assert len(probes)==114
# Bind retained source rib identities to the actual runtime export batches.
assert hashlib.sha256((G/'assets/models/AST-AQU-016.glb').read_bytes()).hexdigest()==hashlib.sha256((C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb').read_bytes()).hexdigest()
rib_batches={}
for name,part in ribs.items():
 matches=[]
 for mesh in original['meshes']:
  vertex_tree=cKDTree(np.array(mesh['vertices']));distance,_=vertex_tree.query(np.array(part['vertices']))
  if max(distance)<TOL:matches.append(mesh['name'])
 assert len(matches)==1,(name,matches);rib_batches[name]=matches[0]
for probe in probes:
 if probe['owner']in rib_batches:probe['expected_support_batch']=rib_batches[probe['owner']]
plant_probes=[]
for row in plan['plants']:
 path=P/'comfort_greenery/greenery/candidate_v001/exports_r002'/row['model_file'];d=g.read_glb(path);lowest=min(p[1]for p in d['vertices']);assert abs(lowest)<1e-10;vs=sorted(set(tuple(p)for p in d['vertices']if abs(p[1]-lowest)<1e-8));soil=parts[row['support']];radius=Polygon([(v[0],v[2])for v in soil['vertices'][28:]])
 for v in vs:
  p=g.transform(v,row['position_xyz'],row['yaw_radians']);assert radius.covers(__import__('shapely').geometry.Point(p[0],p[2])),(row['name'],v);plant_probes.append(dict(item=row['name'],support=row['support'],position_xyz=list(p)))
seat=[]
for label,z in [('Fore',-442.2),('Middle',-424.6),('Aft',-406.7)]:
 name='LOG_'+label+'_Seat_ClayPad_06';part=parts[name];y=max(v[1]for v in part['vertices']);f=[t for t in part['triangles']if all(abs(v[1]-y)<1e-8 for v in t)];assert f;seat.append(dict(part=name,position_xyz=np.mean(f[0],axis=0).tolist()))
records=json.loads((G/'data/generated/structural_meshes.json').read_text())['regions'];ids={r['id'] for r in section['floor_regions']};assert len(ids)==8;floors=[r for r in records if r['id']in ids];assert len(floors)==8
out={'retained_support_probes':probes,'plant_support_probes':plant_probes,'seat_surface_probes':seat,'retained_floor_records':floors,'source_plan_sha256':hashlib.sha256((A/'source_tooling003/BLOCKIN_ACTUAL_PLAN_003.json').read_bytes()).hexdigest()};(S/'RUNTIME_SUPPORTS_003.json').write_text(json.dumps(out,indent=2)+'\n');print(len(probes),'retained roots;',len(plant_probes),'actual botanical root vertices;3seat surfaces')
