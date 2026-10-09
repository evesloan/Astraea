from pathlib import Path
import json,copy,hashlib,sys
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[4];O=R/'BlenderCatalogue/assets/quiet_lift_receiving_20261009';(O/'source').mkdir(parents=True,exist_ok=True)
S=R/'BlenderCatalogue/assets/residential_hotels/quiet_grove_20261007_r001/residential-neighborhood-courts-20261007/outputs/sf_house_r002/PLAN.json'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); assert h(S)=='d0bf2e894aa2347ff50ea8580f0ff1d94c16754708732bb7ac94357f61a5775a'
p=json.loads(S.read_text());result=copy.deepcopy(p);added=[];removed=[];cuts=[]
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
pit=box(88.7,-357.2,93.3,-362.2);names=['QuietGrove_D13Commons_0']+[f'D{d}_CommonsIsland_0'for d in range(14,18)];parts=[]
for q in p['parts']:
 if q['name']not in names:parts.append(q);continue
 removed.append(q['name']);vs=q['verts'];lo=min(v[1]for v in vs);hi=max(v[1]for v in vs)
 top=unary_union([Polygon([(vs[i][0],vs[i][2])for i in f])for f in q['faces']if all(abs(vs[i][1]-hi)<1e-6 for i in f)])
 assert top.covers(pit);cut=top.difference(pit);assert abs(top.area-cut.area-23)<1e-5
 slab(q['name']+'_LiftRecess',cut,lo,hi,q['role'],q['category']);cuts.append({'part':q['name'],'top_y':hi,'removed_m2':top.area-cut.area})
assert len(removed)==5
slab('QG_LiftPitBase',pit,83.76,83.79,'warm_stone','support')
for z in [-357.4,-362.0]:
 slab('QG_LiftPitCrossbearer_'+str(z),box(88.5,z-.16,95.97,z+.16),83.25,83.76,'champagne_metal','support')
# Fully enclosed shaft, preserving the old cover and all original materials.
for name,poly in [('West',box(88.5,-357,88.7,-362.32)),('East',box(93.3,-357,93.5,-362.32)),('Rear',box(88.7,-357,93.3,-357.2))]:
 slab('QG_LiftShaft_'+name,poly,83.76,105.8,'glass','public_glass')
slab('QG_LiftShaftCap',box(88.5,-357,93.5,-362.32),105.8,105.96,'ivory_enamel','ceiling')
for d,y in zip(range(13,18),[84,88.5,93,97.5,102]):
 for suffix,x0,x1,lo,hi,role in [('Left',88.5,89.06,y,y+2.88,'ivory_enamel'),('Right',92.94,93.5,y,y+2.88,'ivory_enamel'),('Header',88.5,93.5,y+2.88,min(y+4.5,105.8),'warm_walnut')]:
  slab(f'QG_D{d}_LiftOuterFrame_{suffix}',box(x0,-362.16,x1,-362.32),lo,hi,role,'enclosure')
result['parts']=parts+added;result['status']='LIFT_SOURCE_DERIVATIVE_RUNTIME_PENDING';result['predecessor_plan_sha256']=h(S)
result['lift_successor']={'removed_source_parts':removed,'added_source_parts':[q['name']for q in added],'preserved_source_parts':len(parts),'root_ship_xyz':[91,0,-362.1],'root_yaw_degrees':-90,'gate_origin_xz':[0,0],'cabin_file':'AST-CIR-003_five_stop.glb','floor_heights':[84,88.5,93,97.5,102],'floor_cuts':cuts,'source_preservation':'All other geometry,83 homes,250 landscape placements,stairs and Library composite retained','limits':'Headless floor/gate checks pending; no visual or structural acceptance.'}
assert len({q['name']for q in result['parts']})==len(result['parts'])
(O/'LIFT_GEOMETRY_PLAN.json').write_text(json.dumps(result,indent=2)+'\n');(O/'PLAN_CHANGE_RECEIPT.json').write_text(json.dumps(result['lift_successor'],indent=2)+'\n')
print(json.dumps({'removed':removed,'added':len(added),'preserved':len(parts),'cut_area_m2':sum(c['removed_m2']for c in cuts)}))
