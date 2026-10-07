from pathlib import Path
import sys,json,gzip,importlib.util,collections,math,hashlib
sys.dont_write_bytecode=True;S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;sys.path.insert(0,str(S/'pool-opposite-gallery-proposal001/reference_programme001'))
import check_programme as q
import numpy as np
from shapely.geometry import Polygon,Point
from shapely import union_all
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();plan=json.loads((B/'CORE_PLAN.json').read_text());actual=json.loads((B/'source_build001/qa/BUILD_EVALUATED_CORE.json').read_text());assert json.loads((B/'source_build001/qa/INDEPENDENT_REOPEN.json').read_text())['status']=='PASS_EXACT_COMPLETE_SOURCE_REOPEN'
core=q.cache([q.record(p['name'],p['vertices_xyz'],[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']],meta=p)for p in actual['parts']]);cm={p['name']:p for p in core}
with gzip.open(B/'source_build001/qa/BUILD_EVALUATED_NEW_PROGRAMME.json.gz','rt')as f:data=json.load(f)
parts=q.cache([q.record(p['name'],p['vertices_xyz'],[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']],meta=p,instance=p['instance'],source_part=p['source_name'],open_surface='AST-BOT-'in p['source'])for p in data])
issues=[];roots=[]
for a in q.source_inventory(dict(plan,plant_reservations=plan['additional_plants'])):
 name='CG_'+a['instance_name'];r=a['reservation'];soil=cm[r['soil_object']];y=53.02;poly=union_all([Polygon([(v[0],v[2])for v in t])for t in soil['triangles']if max(abs(v[1]-y)for v in t)<q.TOL]);ps=[p for p in parts if p['instance']==name];rp=[p for p in ps if p['source_part']in a['asset']['root_parts']];assert{p['source_part']for p in rp}==set(a['asset']['root_parts']);vs=[v for p in rp for v in p['vertices']if v[1]<=min(t[1]for t in p['vertices'])+1e-7];gap=max(abs(v[1]-y)for v in vs);bad=[v for v in vs if not poly.buffer(q.TOL).covers(Point(v[0],v[2]))];row={'instance':name,'soil':soil['name'],'actual_root_vertices':len(vs),'max_gap_m':gap,'unsupported':bad,'unscaled':True};roots.append(row)
 if bad or gap>q.TOL:issues.append({'kind':'soil_contact','row':row})
intersections=[]
for p in parts:
 for r in core:
  if not q.overlap(p['bounds'],r['bounds'],-q.TOL if p['open_surface']else q.TOL):continue
  # Root penetration into its own finite soil is intentional planting; only leaf/root supports and the actual rim are separate gates.
  if p['open_surface']and r['meta']['material_role']=='botanical_soil':continue
  result=q.actual_contact(p,r)
  if result['penetration']:intersections.append({'new':p['name'],'other':r['name'],**result})
if intersections:issues.append({'kind':'solid_interference','rows':intersections})
protected=q.read(S/'pool-opposite-gallery-proposal001/geometry/PROTECTED_RESERVATIONS.json');routes=[]
for r in protected['routes']:
 region=union_all([Polygon(p)for p in r['plan_polygon_union_xz']]);hits=[]
 for p in parts:
  if min(p['bounds'][1][1],r['y_m'][1])-max(p['bounds'][0][1],r['y_m'][0])<=q.TOL:continue
  if q.footprint(p).intersection(region).area>1e-8:hits.append(p['name'])
 routes.append({'name':r['id'],'hits':hits})
 if hits:issues.append({'kind':'route','row':routes[-1]})
# Exact source furniture bounds, whole group floor-bearing and side-correct placement.
fit=q.read(S/'pool-east-gallery-surrounding-diagnosis001/independent_geometry/FULL_SCALE_SERVICE_FIT.json')
footprintrows=[]
floor=next(f for f in q.read(S/'pool-opposite-gallery-proposal001/geometry/FLOOR_POLYGONS.json')['floor_regions']if f['id']=='D09_orchard_market_gallery');fp=union_all([Polygon(t)for t in floor['triangles']])
for r in plan['retained_furniture']:
 ps=[p for p in parts if p['instance']==r['name']];vv=[v for p in ps for v in p['vertices']];bounds=q.bounds(vv);base=union_all([Polygon([(v[0],v[2])for v in t])for p in ps for t in p['triangles']if max(abs(v[1]-52.5)for v in t)<q.TOL]);outside=base.difference(fp).area;row={'instance':r['name'],'bounds':bounds,'floor_bearing_m2':base.area,'outside_m2':outside,'original_scale':True};footprintrows.append(row)
 if outside>1e-7 or base.area<1e-5:issues.append({'kind':'furniture_floor','row':row})
result={'status':'PASS_ACTUAL_NEW_PROGRAMME_FIT'if not issues else'CORRECTION_REQUIRED','source_sha256':q.read(B/'source_build001/qa/BUILD_RECEIPT.json')['sha256'],'issues':issues,'soil_root_contacts':roots,'routes':routes,'furniture':footprintrows,'notes':['Retained botanical self-overlap is unchanged. Natural overhang above soil is permitted; actual closed planter/rim interference is checked.','Source-only fit. Native walking/cart and visual acceptance remain pending.']}
(B/'ACTUAL_NEW_PROGRAMME_FIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'issues':issues,'roots':roots,'furniture':footprintrows},indent=2),flush=True)
