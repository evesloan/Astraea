from pathlib import Path
import sys,json,gzip,hashlib,numpy as np
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(S/'pool-opposite-gallery-proposal001/reference_programme001'));import check_programme as q
from shapely.geometry import Polygon
from shapely import union_all
with gzip.open(S/'pool-connected-gallery-curved001/source_build001/qa/BUILD_EVALUATED_NEW_PROGRAMME.json.gz','rt')as f:old=json.load(f)
with gzip.open(B/'source_build001/qa/BUILD_EVALUATED_STOCK.json.gz','rt')as f:actual=json.load(f)
furn=q.cache([q.record(p['name'],p['vertices_xyz'],[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']],instance=p['instance'])for p in old if p['instance']in ['CG_MarketCounter','CG_ServiceWorkbench']]);plan=q.read(B/'STOCK_PLAN.json');issues=[];records=[];placed=[]
for row in plan['placements']:
 objects=[p for p in actual if p['instance']==row['name']];assert objects
 vs=[v for p in objects for v in p['vertices_xyz']];tri=[[p['vertices_xyz'][i]for i in t]for p in objects for t in p['evaluated_triangles']];rec=q.record(row['name'],vs,tri,open_surface=True);q.cache([rec]);placed.append(rec);y=row['position_xyz'][1]
 feet=[t for t in tri if max(abs(v[1]-y)for v in t)<q.TOL];foot=union_all([Polygon([(v[0],v[2])for v in t])for t in feet if Polygon([(v[0],v[2])for v in t]).area>1e-12]);supports=[]
 for part in furn:
  if part['instance']!=row['support_instance']:continue
  for t in part['triangles']:
   if max(abs(v[1]-y)for v in t)<q.TOL:
    poly=Polygon([(v[0],v[2])for v in t])
    if poly.area>1e-12:supports.append(poly)
 outside=foot.difference(union_all(supports).buffer(q.TOL)).area
 if outside>1e-8 or foot.area<1e-5:issues.append({'kind':'unsupported_actual_base','name':row['name'],'outside_m2':outside})
 collisions=[]
 for part in furn:
  if not q.overlap(rec['bounds'],part['bounds'],q.TOL):continue
  hit=q.actual_contact(rec,part)
  if hit['penetration']:collisions.append({'part':part['name'],**hit})
 if collisions:issues.append({'kind':'actual_stock_furniture_penetration','name':row['name'],'hits':collisions})
 records.append({'name':row['name'],'source_meshes':len(objects),'actual_triangles':len(tri),'base_area_m2':foot.area,'unsupported_area_m2':outside,'world_bounds':rec['bounds'],'support':row['support_instance'],'original_scale':True})
for i,a in enumerate(placed):
 for b in placed[i+1:]:
  if not q.overlap(a['bounds'],b['bounds'],q.TOL):continue
  hit=q.actual_contact(a,b)
  if hit['penetration']:issues.append({'kind':'actual_stock_intersection','a':a['name'],'b':b['name'],**hit})
report={'status':'PASS_ACTUAL_SAVED_STOCK_CONTACTS'if not issues else'CORRECTION_REQUIRED','source_sha256':q.read(B/'source_build001/qa/BUILD_RECEIPT.json')['sha256'],'source_reopen_sha256':q.sha(B/'source_build001/qa/INDEPENDENT_REOPEN.json'),'instances':records,'issues':issues,'native_acceptance':False};(B/'ACTUAL_STOCK_CONTACTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'instances':len(records),'issues':issues},indent=2),flush=True)
