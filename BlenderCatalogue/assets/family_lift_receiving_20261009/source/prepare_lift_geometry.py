from pathlib import Path
import json,copy,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,box,shape,mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parents[1]
S=R/'BlenderCatalogue/assets/residential_hotels/aft_houses_20261007_r001/residential-neighborhood-courts-20261007/family_terrace_house/outputs/house_r001/PLAN.json'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert h(S)=='227f25c59826687b0571d884d04a5674b3f46bd351ecab79476d86c892df798f'
p=json.loads(S.read_text());result=copy.deepcopy(p);added=[];removed=[];parts=[]
def slab(name,poly,lo,hi,role,category):
 assert poly.geom_type=='Polygon' and poly.is_valid
 poly=orient(poly,sign=1);vs=[];fs=[]
 for tri in constrained_delaunay_triangles(poly).geoms:
  q=list(orient(tri,sign=1).exterior.coords)[:3];k=len(vs)
  vs.extend([(x,lo,z)for x,z in q]+[(x,hi,z)for x,z in q]);fs.extend([(k,k+1,k+2),(k+5,k+4,k+3)])
 for ring in [poly.exterior,*poly.interiors]:
  for a,b in zip(ring.coords,list(ring.coords)[1:]):
   k=len(vs);vs.extend([(a[0],lo,a[1]),(a[0],hi,a[1]),(b[0],hi,b[1]),(b[0],lo,b[1])]);fs.append((k,k+1,k+2,k+3))
 added.append(dict(name=name,kind='mesh',verts=vs,faces=fs,role=role,category=category,owner=name,plan_area_m2=poly.area))
pit=box(88.0,377.4,92.6,382.5)
fronts={f'D{d}_{suffix}_0'for d in range(13,18)for suffix in ['LiftFront_88.0','LiftFront_91.4','LiftHeader','LiftClosedGate']}
guards=set()
for y,rim,segment in [('88.5',6,0),('93',2,0),('97.5',6,0),('102',2,3)]:
 for role in ['rail','infill']:guards.add(f'FT_PublicRim_{y}_{role}_{rim}_{segment}')
 for i in range(7):guards.add(f'FT_PublicRim_{y}_post_{rim}_{segment}_{i}')
assert fronts|guards <= {q['name']for q in p['parts']}
for q in p['parts']:
 if q['name']in fronts|guards:removed.append(q['name']);continue
 if q['name']=='FT_PrincipalTerraceCourtBase_0':
  removed.append(q['name']);vs=q['verts'];lo=min(v[1]for v in vs);hi=max(v[1]for v in vs)
  top=unary_union([Polygon([(vs[i][0],vs[i][2])for i in f])for f in q['faces']if all(abs(vs[i][1]-hi)<1e-6 for i in f)])
  assert top.covers(pit);cut=top.difference(pit);assert abs(top.area-cut.area-23.46)<1e-5
  slab('FT_PrincipalTerraceCourtBase_LiftRecess',cut,lo,hi,q['role'],q['category']);continue
 parts.append(q)
assert len(removed)==57
slab('FT_LiftPit_HeldReceivingInterface',pit,83.76,83.79,'warm_stone','architecture')
for d,y in zip(range(13,18),[84,88.5,93,97.5,102]):
 for suffix,x0,x1,lo,hi,role in [('Left',87.87,88.36,y,y+2.88,'ivory_enamel'),('Right',92.24,92.73,y,y+2.88,'ivory_enamel'),('Header',87.87,92.73,y+2.88,min(y+4.5,105.8),'warm_walnut')]:
  slab(f'FT_D{d}_LiftOuterFrame_{suffix}',box(x0,377.34,x1,377.46),lo,hi,role,'architecture')
# Close the bounded gaps between retained shaft stories and the held pit interface.
for q in p['parts']:
 if not any(t in q['name'] for t in ['_LiftJamb_','_LiftBack_']):continue
 vs=q['verts'];x0,x1=min(v[0]for v in vs),max(v[0]for v in vs);z0,z1=min(v[2]for v in vs),max(v[2]for v in vs);y0,y1=min(v[1]for v in vs),max(v[1]for v in vs)
 if y0<102:slab(q['name']+'_StoryInfill',box(x0,z0,x1,z1),y1,y0+4.5,q['role'],q['category'])
 if y0==84:slab(q['name']+'_PitInterface',box(x0,z0,x1,z1),83.79,84,q['role'],q['category'])
slab('FT_LiftShaftCap',box(87.87,377.34,92.73,382.6),105.8,105.96,'ivory_enamel','ceiling')
for region in result['floor_regions']:
 if region['name']=='FT_PrincipalTerraceCourtBase':region['geometry']=mapping(shape(region['geometry']).difference(pit))
result['parts']=parts+added;result['status']='LIFT_DERIVATIVE_FOUNDATION_STILL_HELD';result['predecessor_plan_sha256']=h(S)
result['lift_successor']={'removed_source_parts':removed,'added_source_parts':[q['name']for q in added],'preserved_source_parts':len(parts),'root_ship_xyz':[90.3,0,377.5],'root_yaw_degrees':-90,'gate_origin_xz':[0,0],'cabin_file':'AST-CIR-003_five_stop.glb','floor_heights':[84,88.5,93,97.5,102],'base_cut_m2':23.46,'existing_upper_apertures_retained':4,'open_construction_hold':'FT_BASE_RECEIVING_HOLD','source_preservation':'82 homes,157 landscape placements,stairs and protected Celestial lounge/Reading nooks retained','limits':'Operating lift candidate, runtime tests pending. Entire base/foundation hold remains Group1 work; no structural capacity or visual acceptance.'}
assert len({q['name']for q in result['parts']})==len(result['parts'])
(O/'LIFT_GEOMETRY_PLAN.json').write_text(json.dumps(result,indent=2)+'\n');(O/'PLAN_CHANGE_RECEIPT.json').write_text(json.dumps(result['lift_successor'],indent=2)+'\n')
print(json.dumps({'removed':len(removed),'added':len(added),'preserved':len(parts),'base_cut_m2':23.46,'receiving_hold':'OPEN'}))
