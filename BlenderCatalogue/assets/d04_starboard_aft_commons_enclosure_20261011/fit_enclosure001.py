from pathlib import Path
import json
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;P=json.loads((W/'PLAN.json').read_text());over=json.loads((W/'SOURCE_CLOSURE_OVERLAPS.json').read_text())
assert not P['parts'];sites=[]
for s in P['closure_sites']:sites.append(dict(s,site_id=s['source_name']))
for s in P['ceiling_edge_sites']:sites.append(dict(s,site_id=s['name'],source_name=s['material_source'],source_root=P['source_root'],material_native=P['source_native'],role='staff_panel',category='ceiling_edge_closure',bottom=s['bounds'][0][1],top=s['bounds'][1][1]))
# The north edge owns the shared corner; west strip begins at its south edge.
sites[2]['bounds'][0][2]=sites[3]['bounds'][1][2]
proof=[];coverage=[]
for i,site in enumerate(sites):
 lo,hi=site['bounds'];foot=box(lo[0],lo[2],hi[0],hi[2]);solids=[]
 for row in over:
  if row['site']!=site['site_id']:continue
  s=row['source'];vs=s['world_vertices'];a,b=s['bounds'];poly=MultiPoint([(v[0],v[2])for v in vs]).convex_hull
  if poly.intersection(foot).area<1e-8:continue
  assert all(min(abs(v[1]-a[1]),abs(v[1]-b[1]))<5e-5 for v in vs),s['name']
  bottom=MultiPoint([(v[0],v[2])for v in vs if abs(v[1]-a[1])<5e-5]).convex_hull;top=MultiPoint([(v[0],v[2])for v in vs if abs(v[1]-b[1])<5e-5]).convex_hull
  assert bottom.symmetric_difference(top).area<1e-6 and poly.equals(bottom),s['name']
  solids.append((s['name'],poly,a[1],b[1]));proof.append({'site':site['site_id'],'retained_owner':s['name'],'exact_plan_polygon':list(poly.exterior.coords),'bottom':a[1],'top':b[1],'source_geometry_unmodified':True})
 bands=sorted({lo[1],hi[1]}|{max(lo[1],min(hi[1],v))for _,_,a,b in solids for v in[a,b]});n=0
 for y,Y in zip(bands,bands[1:]):
  if Y-y<1e-5:continue
  occupied=unary_union([p for _,p,a,b in solids if a<(y+Y)/2<b]);free=foot.difference(occupied);polygons=[free]if isinstance(free,Polygon)else list(free.geoms);newpolys=[]
  for poly in polygons:
   if poly.area<1e-8:continue
   for tri in constrained_delaunay_triangles(poly).geoms:
    pts=list(tri.exterior.coords)[:-1];verts=[[x,h,z]for h in[y,Y]for x,z in pts];name=f'SAE_Fitted_{i}_{n}';n+=1
    P['parts'].append({'name':name,'verts':verts,'faces':[[2,1,0],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],'role':site['role'],'category':site['category'],'runtime_collision':True,'source_name':site['source_name'],'source_root':site['source_root'],'site_id':site['site_id'],'site_bottom':lo[1],'site_top':hi[1],'bottom':y,'top':Y,'expected_bounds':[[min(v[k]for v in verts)for k in range(3)],[max(v[k]for v in verts)for k in range(3)]],'material_native':site['material_native'],'source_materials_exact':True});newpolys.append(tri)
  union=unary_union(newpolys);gap=foot.difference(union.union(occupied)).area;excess=union.difference(foot).area;overlap=union.intersection(occupied).area
  assert max(gap,excess,overlap)<1e-6,(site['site_id'],gap,excess,overlap)
  assert abs(sum(q.area for q in newpolys)-union.area)<1e-6
  coverage.append({'site':site['site_id'],'bottom':y,'top':Y,'gap_m2':gap,'excess_m2':excess,'retained_overlap_m2':overlap})
# No duplicate volume between any added sites, including the north/west corner.
for i,a in enumerate(P['parts']):
 for b in P['parts'][i+1:]:
  if min(a['top'],b['top'])-max(a['bottom'],b['bottom'])>1e-5:
   assert Polygon([(v[0],v[2])for v in a['verts'][:3]]).intersection(Polygon([(v[0],v[2])for v in b['verts'][:3]])).area<1e-6,(a['name'],b['name'])
P['fit_sites']=sites;P['retained_members_exact_fit']=proof
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'EXACT_FIT_AND_COVERAGE001.json').write_text(json.dumps({'status':'PASS','source_contacts':proof,'sites':len(sites),'fitted_triangular_prisms':len(P['parts']),'bands':coverage,'original_members_moved':0,'unexplained_gap_or_overlap':0,'new_floor_m2':0},indent=2)+'\n');print('PASS',len(sites),'sites',len(P['parts']),'prisms',len(coverage),'bands')
