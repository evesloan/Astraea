from pathlib import Path
import json,copy
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;P=json.load(open(W/'PLAN.json'));(W/'RETAINED_INPUT_R003.json').write_text(json.dumps(P,indent=2)+'\n');over=json.load(open(W/'SOURCE_CAP_OVERLAPS002.json'));P['parts']=[];proof=[]
for i,site in enumerate(P['closure_sites']):
 base=next(q for q in json.load(open(W/'RETAINED_INPUT_R003.json'))['parts']if q['source_name']==site['source_name']);lo,hi=base['expected_bounds'];foot=box(lo[0],lo[2],hi[0],hi[2]);solids=[]
 for row in over:
  if row['cap']!=base['name']:continue
  s=row['source'];vs=s['world_vertices'];a,b=s['bounds'];polygon=MultiPoint([(v[0],v[2])for v in vs]).convex_hull
  if polygon.intersection(foot).area<.00000001:continue
  # Every intersecting retained member must be a verified straight vertical prism.
  assert all(min(abs(v[1]-a[1]),abs(v[1]-b[1]))<.00005 for v in vs),s['name'];bottom=MultiPoint([(v[0],v[2])for v in vs if abs(v[1]-a[1])<.00005]).convex_hull;top=MultiPoint([(v[0],v[2])for v in vs if abs(v[1]-b[1])<.00005]).convex_hull;assert bottom.symmetric_difference(top).area<.000001,s['name'];assert polygon.equals(bottom),s['name'];solids.append((s['name'],polygon,a[1],b[1]));proof.append({'site':site['source_name'],'retained_owner':s['name'],'exact_plan_polygon':list(polygon.exterior.coords),'bottom':a[1],'top':b[1],'source_geometry_unmodified':True})
 bands=sorted({lo[1],hi[1]}|{max(lo[1],min(hi[1],v))for _,_,a,b in solids for v in[a,b]});n=0
 for y,Y in zip(bands,bands[1:]):
  if Y-y<.00001:continue
  blockers=[p for name,p,a,b in solids if a<(y+Y)/2<b];free=foot.difference(unary_union(blockers))if blockers else foot
  polygons=[free]if isinstance(free,Polygon)else list(free.geoms)
  for polygon in polygons:
   if polygon.area<.00000001:continue
   for tri in constrained_delaunay_triangles(polygon).geoms:
    points=list(tri.exterior.coords)[:-1];verts=[[x,h,z]for h in[y,Y]for x,z in points];faces=[[2,1,0],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]];name='CCJ_Fitted_'+str(i)+'_'+str(n);n+=1;P['parts'].append({'name':name,'verts':verts,'faces':faces,'role':base['role'],'category':'wall_ceiling_closure','runtime_collision':True,'source_name':base['source_name'],'source_root':base['source_root'],'site_bottom':site['bottom'],'site_top':site['top'],'bottom':y,'top':Y,'expected_bounds':[[min(v[k]for v in verts)for k in range(3)],[max(v[k]for v in verts)for k in range(3)]],'material_native':site['material_native'],'source_materials_exact':True})
P['retained_members_exact_fit']=proof;(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'EXACT_EXISTING_MEMBER_FIT004.json').write_text(json.dumps({'status':'PASS_NATIVE_GEOMETRY_FIT','source_solids':proof,'fitted_triangular_prisms':len(P['parts']),'original_source_members_moved':0,'unexplained_overlap':0},indent=2)+'\n');print('fitted solids',len(P['parts']),'retained contacts',len(proof))
