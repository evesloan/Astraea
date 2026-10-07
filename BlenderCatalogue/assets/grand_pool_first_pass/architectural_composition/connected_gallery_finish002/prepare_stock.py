from pathlib import Path
import sys,json,gzip,math,hashlib,numpy as np
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(S/'pool-opposite-gallery-proposal001/reference_programme001'));import check_programme as q
from shapely.geometry import Polygon
from shapely import union_all
C=q.C;sha=q.sha
assets={
 'AST-CUR-001':(C/'assets/curio_keepsakes/source/AST-CUR-001.blend',C/'assets/curio_keepsakes/exports/AST-CUR-001.glb'),
 'AST-CUR-002':(C/'assets/curio_keepsakes/source/AST-CUR-002.blend',C/'assets/curio_keepsakes/exports/AST-CUR-002.glb'),
 'AST-CUR-003':(C/'assets/curio_keepsakes/source/AST-CUR-003.blend',C/'assets/curio_keepsakes/exports/AST-CUR-003.glb'),
 'AST-RTL-004':(C/'assets/retail_work/source/AST-RTL-004.blend',C/'assets/retail_work/exports/AST-RTL-004.glb'),
 'AST-LIB-006':(C/'assets/library_contents/AST-LIB-006_upright_book_group.blend',C/'assets/library_contents/AST-LIB-006_upright_book_group.glb'),
 'AST-LIB-007':(C/'assets/library_contents/AST-LIB-007_open_folio_stack.blend',C/'assets/library_contents/AST-LIB-007_open_folio_stack.glb')}
placements=[
 ('FIN_Orbit_West','AST-CUR-001',[-10.22,53.45000076293945,-440.2],0,'CG_MarketCounter'),
 ('FIN_Stellar_West','AST-CUR-003',[-10.62,53.45000076293945,-439.6],.2,'CG_MarketCounter'),
 ('FIN_Ceramic_East','AST-CUR-002',[-10.62,53.45000076293945,-437.8],.4,'CG_MarketCounter'),
 ('FIN_Stellar_East','AST-CUR-003',[-10.20,53.45000076293945,-437.25],-.3,'CG_MarketCounter'),
 ('FIN_Catalogue_Books','AST-LIB-006',[-10.52,53.2400016784668,-438.89],math.pi/2,'CG_MarketCounter'),
 ('FIN_Guest_Folio','AST-LIB-007',[-10.64,53.2400016784668,-438.39],-math.pi/2,'CG_MarketCounter'),
 ('FIN_Case_LowerShelf','AST-RTL-004',[-10.60,52.67499923706055,-443.55],0,'CG_ServiceWorkbench'),
 ('FIN_Case_UpperShelf','AST-RTL-004',[-10.60,53.05500030517578,-443.55],0,'CG_ServiceWorkbench')]
with gzip.open(S/'pool-connected-gallery-curved001/source_build001/qa/BUILD_EVALUATED_NEW_PROGRAMME.json.gz','rt')as f:old=json.load(f)
furn=q.cache([q.record(p['name'],p['vertices_xyz'],[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']],instance=p['instance'])for p in old if p['instance']in ['CG_MarketCounter','CG_ServiceWorkbench']]);loaded={k:q.read_glb(v[1])for k,v in assets.items()};issues=[];records=[];placed=[]
for name,asset,origin,yaw,instance in placements:
 raw=loaded[asset];vs=[q.transform(v,origin,yaw)for v in raw['vertices']];tri=[[q.transform(v,origin,yaw)for v in t]for t in raw['triangles']];rec=q.record(name,vs,tri,open_surface=True);q.cache([rec]);placed.append(rec)
 base=[t for t in tri if max(abs(v[1]-origin[1])for v in t)<q.TOL];foot=union_all([Polygon([(v[0],v[2])for v in t])for t in base if Polygon([(v[0],v[2])for v in t]).area>1e-12]);supports=[]
 for p in furn:
  if p['instance']!=instance:continue
  for t in p['triangles']:
   if max(abs(v[1]-origin[1])for v in t)<q.TOL:
    poly=Polygon([(v[0],v[2])for v in t])
    if poly.area>1e-12:supports.append(poly)
 surface=union_all(supports);outside=foot.difference(surface.buffer(q.TOL)).area
 if outside>1e-8 or foot.area<1e-5:issues.append({'kind':'unsupported_base','name':name,'outside_m2':outside,'foot_area_m2':foot.area})
 interference=[]
 for p in furn:
  if not q.overlap(rec['bounds'],p['bounds'],q.TOL):continue
  hit=q.actual_contact(rec,p)
  if hit['penetration']:interference.append({'part':p['name'],**hit})
 if interference:issues.append({'kind':'furniture_interference','name':name,'hits':interference})
 records.append({'name':name,'asset':asset,'source':str(assets[asset][0]),'source_sha256':sha(assets[asset][0]),'export':str(assets[asset][1]),'export_sha256':sha(assets[asset][1]),'position_xyz':origin,'yaw_radians':yaw,'scale_xyz':[1,1,1],'support_instance':instance,'actual_bounds_xyz':rec['bounds'],'actual_base_area_m2':foot.area,'unsupported_base_m2':outside,'triangles':len(tri),'unscaled':True})
for i,a in enumerate(placed):
 for b in placed[i+1:]:
  if not q.overlap(a['bounds'],b['bounds'],q.TOL):continue
  hit=q.actual_contact(a,b)
  if hit['penetration']:issues.append({'kind':'stock_interference','a':a['name'],'b':b['name'],**hit})
# Preserve the broad wrapping worktop and parcel-rest working rectangle.
worktops=[p for p in furn if p['name']in ['CG_ServiceWorkbench__clear_wrapping_worktop','CG_ServiceWorkbench__guest_parcel_rest']]
for p in placed:
 for t in worktops:
  if q.overlap(p['bounds'],[t['bounds'][0],[t['bounds'][1][0],t['bounds'][1][1]+.6,t['bounds'][1][2]]],q.TOL):issues.append({'kind':'occupied_work_patch','stock':p['name'],'patch':t['name']})
plan={'status':'PASS_SUPPORTED_RETAINED_RECEIVING_STOCK'if not issues else'CORRECTION_REQUIRED','placements':records,'instance_count':len(records),'max_authorized_instances':12,'issues':issues,'floor_or_route_changes':False,'retained_counter_and_workbench_unchanged':True,'wrapping_and_guest_parcel_worktops_clear':not any(x['kind']=='occupied_work_patch'for x in issues),'gameplay_or_sales_inventory_implemented':False,'native_visual_acceptance':False};(B/'STOCK_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
with gzip.open(B/'STOCK_GEOMETRY.json.gz','wt')as f:json.dump([{'name':p['name'],'vertices_xyz':p['vertices'],'triangles':p['triangles'],'bounds':p['bounds']}for p in placed],f,separators=(',',':'))
print(json.dumps({'status':plan['status'],'instances':len(records),'issues':issues},indent=2),flush=True)
