from pathlib import Path
import sys,json,gzip,math,hashlib,numpy as np
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(S/'pool-opposite-gallery-proposal001/reference_programme001'));import check_programme as q
from shapely.geometry import Polygon
from shapely import union_all
plan=q.read(B/'CORE_PLAN.json');parts=q.cache([q.record(p['name'],p['vertices_xyz'],[t for f in p['faces']for t in q.triang_face(p['vertices_xyz'],f)],meta=p)for p in plan['parts']]);cm={p['name']:p for p in parts}
old=q.read_glb(q.C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');shell=q.cache([q.record(p['source_name'],[v for i in p['global_triangle_indices']for v in old['triangles'][i]],[old['triangles'][i]for i in p['global_triangle_indices']])for p in q.read(S/'pool-opposite-gallery-proposal001/geometry/RETAINED_PART_BOUNDS.json')['parts']]);sm={p['name']:p for p in shell}
with gzip.open(S/'pool-connected-gallery-curved001/source_build001/qa/BUILD_EVALUATED_NEW_PROGRAMME.json.gz','rt')as f:programme=json.load(f)
furn=q.cache([q.record(p['name'],p['vertices_xyz'],[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']])for p in programme if p['instance']in ['CG_MarketCounter','CG_ServiceWorkbench']]);allparts=parts+shell+furn
issues=[];rows=[]
for f in plan['fixture_reservations']:
 pos=np.array(f['position_xyz']);axis=q.unit(f['direction_xyz']);right=q.unit(np.cross(axis,[0,1,0])if abs(axis[1])<.999 else np.cross(axis,[0,0,1]));up=np.cross(right,axis);clear=[]
 for theta in [0,25,55]:
  for az in ([0]if theta==0 else range(0,360,30)):
   th=math.radians(theta);aa=math.radians(az);v=np.array(axis)*math.cos(th)+(np.array(right)*math.cos(aa)+np.array(up)*math.sin(aa))*math.sin(th);hit=q.rayhits(pos,pos+v*.06,allparts)
   if hit:clear.append({'theta':theta,'az':az,'hits':hit[:2]})
 if clear:issues.append({'kind':'aperture_obstruction','fixture':f['name'],'hits':clear})
 receiver=[]
 if f.get('mounting')=='cross_crown':
  target=np.array(f['intended_receiver_xyz']);targets=[target+np.array(d)for d in [[0,0,0],[.35,0,0],[-.35,0,0],[0,0,.7],[0,0,-.7]]]
  for t in targets:
   dv=t-pos;dv/=np.linalg.norm(dv);hits=q.rayhits(pos,pos+dv*10,allparts);first=hits[0]if hits else{};receiver.append(dict(first,angle_degrees=math.degrees(math.acos(float(np.clip(np.dot(dv,axis),-1,1))))))
   if not first or not first['part'].startswith(('CG_UpperCrown','GP_RoofRib','GP_LongCeiling','FIN_LongReturn','CG_Pier4')):issues.append({'kind':'crown_receiver','fixture':f['name'],'target':t.tolist(),'hits':hits[:2]})
 else:
  # Preserve the source's proven intended use surfaces, while checking current
  # furniture as real occluders. No hidden floor below a countertop is selected.
  previous=next(x for x in q.read(S/'pool-connected-gallery-curved001/lighting_revision002/RECEIVER_PROOF.json')['fixtures']if x['name']==f['name'])
  for rr in previous['receivers']:
   dv=np.array(rr['point_xyz'])-pos;dv/=np.linalg.norm(dv);hits=q.rayhits(pos,pos+dv*9,allparts)
   if hits:receiver.append(dict(hits[0],angle_degrees=math.degrees(math.acos(float(np.clip(np.dot(dv,axis),-1,1))))))
 if not receiver:issues.append({'kind':'no_receiver','fixture':f['name']})
 distance=max([r['distance_m']for r in receiver if'distance_m'in r],default=0);f['proposed_range_m']=math.ceil((distance+.35)*10)/10
 rows.append({'name':f['name'],'position_xyz':f['position_xyz'],'direction_xyz':list(axis),'physical_housing':f['housing'],'physical_lens':f['physical_lens'],'clear_first60mm_sampled_cone':not clear,'receivers':receiver,'measured_max_receiver_distance_m':distance,'proposed_range_m':f['proposed_range_m'],'proposed_energy':f['proposed_energy'],'half_angle_degrees':55})
# Actual source attachment of ceiling-seat top and source cup back.
contacts=[]
for label in ['Bay','Fore','Market']:
 p=cm[f'FIN_{label}_CeilingSeat'];top=max(v[1]for v in p['vertices']);vs=[v for v in p['vertices']if abs(v[1]-top)<1e-6];support=cm[p['meta']['support'][0]];missing=[v for v in vs if not q.on_surface(v,support)];contacts.append({'part':p['name'],'support':support['name'],'contact_vertices':len(vs),'missing':missing})
 if missing:issues.append({'kind':'ceiling_seat_gap','part':p['name'],'missing':missing})
for f in plan['fixture_reservations']:
 if f.get('mounting')!='cross_crown':continue
 p=cm[f['housing']];plate=cm[p['meta']['support'][0]];back=p['vertices'][:20];missing=[v for v in back if not q.on_surface(v,plate)];contacts.append({'part':p['name'],'support':plate['name'],'contact_vertices':len(back),'missing':missing})
 if missing:issues.append({'kind':'cup_rear_gap','fixture':f['name'],'missing':missing})
# Newly added outside skins may touch their support but must not carve into the
# original column/return. Closed actual triangles are used, not only AABBs.
cladding=[]
for p in parts:
 if not p['name'].startswith(('FIN_Pier3_','FIN_LongReturn_')):continue
 for oldpart in shell:
  if not q.overlap(p['bounds'],oldpart['bounds'],q.TOL):continue
  hit=q.actual_contact(p,oldpart)
  if hit['penetration']:cladding.append({'new':p['name'],'retained':oldpart['name'],**hit})
if cladding:issues.append({'kind':'cladding_solid_interference','rows':cladding})
protected=q.read(S/'pool-opposite-gallery-proposal001/geometry/PROTECTED_RESERVATIONS.json');route_rows=[]
for r in protected['routes']:
 poly=union_all([Polygon(p)for p in r['plan_polygon_union_xz']]);hits=[]
 for name in plan['new_parts']:
  p=cm[name]
  if min(p['bounds'][1][1],r['y_m'][1])-max(p['bounds'][0][1],r['y_m'][0])<=q.TOL:continue
  if q.footprint(p).intersection(poly).area>1e-8:hits.append(name)
 route_rows.append({'name':r['id'],'hits':hits})
 if hits:issues.append({'kind':'protected_route','row':route_rows[-1]})
# Store deterministic face triangulation for only changed/new mesh geometry.
tris={}
for p in plan['parts']:
 if p['name']not in set(plan['new_parts'])|{f[k]for f in plan['fixture_reservations']if f.get('mounting')=='cross_crown'for k in ['housing','physical_lens']}:continue
 vertices=np.array(p['vertices_xyz']);indices=[]
 for tri in cm[p['name']]['triangles']:
  row=[]
  for v in tri:
   dist=np.linalg.norm(vertices-v,axis=1);i=int(np.argmin(dist));assert dist[i]<1e-7;row.append(i)
  indices.append(row)
 tris[p['name']]=indices
(B/'CORE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();(B/'SOURCE_TRIANGLES.json').write_text(json.dumps({'plan_sha256':sha(B/'CORE_PLAN.json'),'parts':tris},indent=2)+'\n')
report={'status':'PASS_PURE_FIXTURE_AND_FINISH_FIT'if not issues else'CORRECTION_REQUIRED','issues':issues,'fixtures':rows,'mount_contacts':contacts,'routes':route_rows,'native_selection_accepted':False,'all_current_furniture_in_ray_test':True,'plan_sha256':sha(B/'CORE_PLAN.json')};(B/'FIXTURE_FIT_REVIEW.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'issues':issues,'ranges':{r['name']:r['proposed_range_m']for r in rows}},indent=2),flush=True)
