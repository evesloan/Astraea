"""Actual new joinery meshes against the inherited asymmetric curved perimeter."""
from pathlib import Path
import json,sys,argparse
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
ap=argparse.ArgumentParser();ap.add_argument('--revision',default='source_r004');a=ap.parse_args()
left=[(-3.50,.12),(-3.50,4.0),(-3.40,4.8),(-3.0,5.5),(-2.85,6.3),(-3.15,7.2),(-3.50,7.8),(-3.50,12.75)]
right=[(3.50,.12),(3.50,2.8),(3.35,3.5),(2.95,4.2),(2.75,5.1),(2.90,6.2),(3.35,7.25),(3.50,8),(3.50,12.75)]
# Eight centimetres is the actual fixed trim zone; projections beyond it are
# not a legitimate bearing contact and must be fitted to the inherited profile.
outer=Polygon(left+list(reversed(right))).buffer(.08)
rows=[]
for path in sorted((R/'outputs'/a.revision).glob('*/EVALUATED_GEOMETRY.json')):
 checks=[]
 for o in json.loads(path.read_text()):
  if not o['name'].startswith('NG_'):continue
  v=o['vertices'];polys=[]
  for tri in o['triangles']:
   p=Polygon([v[i][:2]for i in tri])
   if p.area>1e-9:polys.append(p)
  if not polys:continue
  footprint=unary_union(polys);area=footprint.difference(outer).area;dist=max(Point(q[:2]).distance(outer)for q in v)
  checks.append({'part':o['name'],'outside_authored_perimeter_area_m2':area,'maximum_vertex_outside_distance_m':dist,'pass':area<1e-7 and dist<1e-5})
 rows.append({'prototype':path.parent.name,'checks':checks,'pass':all(c['pass']for c in checks)})
report={'revision':a.revision,'source_geometry_not_runtime_collision':True,'profile':{'left':left,'right':right,'retained_trim_zone_m':.08},'shared_families':len(rows),'all_pass':len(rows)==8 and all(r['pass']for r in rows),'records':rows}
(R/'qa'/('CURVED_PERIMETER_'+a.revision+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print('CURVED_PERIMETER',a.revision,report['all_pass'],sum(not c['pass']for r in rows for c in r['checks']))
if a.revision!='source_r002':assert report['all_pass']
