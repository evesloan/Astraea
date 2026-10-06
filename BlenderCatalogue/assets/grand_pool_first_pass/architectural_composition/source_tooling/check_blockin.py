"""Read-only exact planned-geometry screen before any block-in source build."""
import sys,ast,json,math,hashlib,collections,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/workspace/scratch/375c2e438292/geometry-deps')
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon,Point
from shapely import constrained_delaunay_triangles
S=Path(__file__).resolve().parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');G=Path('/workspace/shared/astraea-godot-production-20261003');P=C/'assets/grand_pool_first_pass';TOL=5e-5
path=P/'finish_envelope/stock/geometry.py';sp=importlib.util.spec_from_file_location('retained_geometry',path);geo=importlib.util.module_from_spec(sp);sp.loader.exec_module(geo)
for name in dir(geo):
 if not name.startswith('_'):globals()[name]=getattr(geo,name)
helper=P/'finish_envelope/qa/pure_geometry/review_finish.py';tree=ast.parse(helper.read_text());wanted={'record','triang_face','rayhits','surface_points','on_surface','strict_inside','contact_pair'};functions=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))and node.name in wanted];assert len(functions)==len(wanted);exec(compile(ast.Module(body=functions,type_ignores=[]),str(helper),'exec'))
plan=json.loads((S/'BLOCKIN_PLAN.json').read_text());section=json.loads((G/'data/architecture/GRAND_POOL_SECTION_RUNTIME.json').read_text());finish=json.loads((P/'finish_envelope/source/finish_contract.json').read_text());first=json.loads((G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json').read_text());runtime=json.loads((G/'data/architecture/GRAND_POOL_FINISH_RUNTIME.json').read_text())
NEW=[record(p['name'],p['vertices_xyz'],[t for f in p['faces']for t in triang_face(p['vertices_xyz'],f)],meta=p)for p in plan['parts']]
def mapped_parts(glb,parts,coord='world_vertices'):
 data=geo.read_glb(glb);tri=np.array(data['triangles']);uv=np.unique(tri.reshape(-1,3),axis=0);tree=cKDTree(uv);members=collections.defaultdict(set)
 for p in parts:
  if p.get('export_excluded'):continue
  distances,ix=tree.query(p[coord]);assert max(distances)<TOL,(p['name'],max(distances))
  for i in ix:members[int(i)].add(p['name'])
 mapping=collections.defaultdict(list)
 for t,indices in zip(tri,tree.query(tri.reshape(-1,3))[1].reshape(-1,3)):
  names=set.intersection(*(members[int(i)]for i in indices));assert names,'Unmapped retained triangle'
  for name in names:mapping[name].append(t.tolist())
 return[record(p['name'],p[coord],mapping[p['name']],meta=p)for p in parts if not p.get('export_excluded')]
OLD=mapped_parts(C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb',section['source_parts'])
FIN=mapped_parts(P/'finish_envelope/exports_r002/AST-AQU-016_finish_envelope.glb',finish['parts'])
# Other checked world assemblies, including all mounted screens/signs, are genuine
# retained mesh geometry; botanical renders remain relevant to view constraints.
for key in ['wayfinding','media']:
 data=geo.read_glb(C/runtime['models'][key]['source_path'])
 for mesh in data['meshes']:FIN.append(record(key+'::'+mesh['name'],mesh['vertices'],mesh['triangles']))
FURN=[];cache={}
for p in first['placements']+runtime['placements']:
 path=C/p['retained_export']
 if path not in cache:cache[path]=geo.read_glb(path)
 data=cache[path];pos=p['position_xyz'];yaw=p['yaw_radians']
 FURN.append(record(p['name'],[transform(v,pos,yaw)for v in data['vertices']],[tuple(transform(v,pos,yaw)for v in t)for t in data['triangles']],meta=p))
for p in NEW+OLD+FIN+FURN:
 p['ta']=np.asarray(p['triangles']);p['tmin']=p['ta'].min(axis=1);p['tmax']=p['ta'].max(axis=1)
issues=[];collisions=[];allowed=[]
for new in NEW:
 for old in OLD+FIN+FURN:
  if not overlap(new['bounds'],old['bounds'],TOL):continue
  result=contact_pair(new,old)
  if not result['penetration']:continue
  row=dict(new=new['name'],retained=old['name'],**result)
  if old['name']in new['meta'].get('intentional_anchor_through',[]):allowed.append(row)
  else:collisions.append(row)
print('Retained-interference screen',len(collisions),'unexpected,',len(allowed),'named anchor-through-finish joints',flush=True)
# Source exits and physical receivers stay precise, including the 20mm-free-space
# runtime sample. No endpoint/contact tolerance is widened.
light_issues=[]
for fixture in section['fixtures']+runtime['fixtures']:
 d=fixture.get('direction_xyz',fixture.get('direction'));start=fixture['position_xyz'];hits=rayhits(start,add(start,mul(d,.06)),NEW)
 if hits:light_issues.append(dict(name=fixture['name'],kind='source_exit',hits=hits))
 if 'receiver_xyz'in fixture:
  hits=rayhits(start,fixture.get('visibility_sample_xyz',fixture['receiver_xyz']),NEW)
  if hits:light_issues.append(dict(name=fixture['name'],kind='physical_receiver',hits=hits))
view_issues=[]
for media in runtime['media_candidates']:
 for probe in media['sampled_current_triangle_sightlines']:
  hits=rayhits(probe['eye_xyz'],probe['target_xyz'],NEW)
  if hits:view_issues.append(dict(display=media['name'],eye=probe['eye_xyz'],hits=hits))
# Preserved supported user routes are continuous capsule corridors. This is a
# conservative broad phase (fail closed), not an engine walking substitute.
route_hits=[]
paths=[dict(name=p['item'],points=p['points'],r=.30,h=1.80)for p in first['approach_paths']]
paths += [dict(name='wet_main',points=[[-45.9,46.2,-458],[-45.9,46.2,-405]],r=.5,h=2.0)]
paths += [dict(name='dry_market',points=[[x,52.5,z]for x,z in section['market']['adopted_dry_loop_centreline_xz']],r=.5,h=2.0)]
paths += [dict(name='stock_'+p['display'],points=p['points_xyz'],r=.3,h=1.8)for p in runtime['stock_approach_paths']]
paths += [dict(name='ramp',points=section['accessible_ramp']['route_xyz'],r=.5,h=2.0)]
paths += [dict(name='lower_lift',points=section['wet_market_link']['lift']['lower_approach_xyz'],r=.5,h=2.0)]
for path in paths:
 found=set()
 for a,b in zip(path['points'],path['points'][1:]):
  delta=sub(b,a);steps=max(1,math.ceil(length(delta)/.08))
  for i in range(steps+1):
   q=add(a,mul(delta,i/steps));lo=[q[0]-path['r'],q[1]+.02,q[2]-path['r']];hi=[q[0]+path['r'],q[1]+path['h'],q[2]+path['r']]
   for p in NEW:
    if overlap([lo,hi],p['bounds'],TOL):found.add(p['name'])
 if found:route_hits.append(dict(path=path['name'],parts=sorted(found)))
report=dict(status='PURE_PREFLIGHT_PASS'if not(collisions or light_issues or view_issues or route_hits)else'BLOCKIN_REQUIRES_CORRECTION',plan_sha256=hashlib.sha256((S/'BLOCKIN_PLAN.json').read_bytes()).hexdigest(),planned_parts=len(NEW),unexpected_retained_penetrations=collisions,named_finish_anchor_penetrations=allowed,preserved_fixture_issues=light_issues,preserved_media_view_issues=view_issues,preserved_route_broad_phase_hits=route_hits,limits=['Planned geometry only; actual saved source reopen, exact support graph, new/new contacts and visual review remain required','No new source build/export/renderer/runtime change performed'])
(S/'BLOCKIN_PREFLIGHT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='named_finish_anchor_penetrations'},indent=2));assert report['status']=='PURE_PREFLIGHT_PASS'
