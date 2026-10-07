"""Check all new source joinery against the actual curved shell inner faces."""
from pathlib import Path
import json,sys,numpy as np
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import Polygon,MultiPoint,Point,box
from shapely.ops import unary_union
revision=sys.argv[1]if len(sys.argv)>1 else'source_r001';P=json.loads((R/'STAR_ATLAS_85_PLACEMENT_MAP.json').read_text());rows=[]
for cfg in P['prototypes']:
 obs=json.loads((R/'outputs'/revision/cfg['address']/'EVALUATED_GEOMETRY.json').read_text());walls=unary_union([MultiPoint(np.array(o['vertices'])[:,:2]).convex_hull for o in obs if o['name'].startswith(('SUI_Wall_L','SUI_Wall_R'))]);room=box(-3.5,.21,3.5,12.67).difference(walls);components=list(room.geoms)if hasattr(room,'geoms')else[room];inside=next(p for p in components if p.covers(Point(0,6)));objects=[]
 for o in obs:
  if not o['name'].startswith('SA_'):continue
  v=np.array(o['vertices']);tri=v[np.array(o['triangles'])];pieces=[Polygon(t[:,:2])for t in tri if Polygon(t[:,:2]).area>1e-9];p=unary_union(pieces);outside=p.difference(inside.buffer(.0001));a=outside.area
  mount=o['name'].startswith('SA_BedTaskBearing_')
  objects.append({'name':o['name'],'plan_outside_inner_shell_m2':a,'pass':a<1e-5 or mount,'exception':'Source-authored wall bearing intentionally spans the actual wall face'if mount else None})
 row={'prototype':cfg['address'],'new_joinery_count':len(objects),'all_pass':all(o['pass']for o in objects),'objects':objects};rows.append(row);print(cfg['address'],row['all_pass'],[(o['name'],round(o['plan_outside_inner_shell_m2'],4))for o in objects if not o['pass']])
report={'status':'PASS'if all(r['all_pass']for r in rows)else'FAIL_NEW_JOINERY_OUTSIDE_CURVED_INNER_SHELL','revision':revision,'actual_evaluated_perimeter_wall_geometry_used':True,'all_pass':all(r['all_pass']for r in rows),'rows':rows,'scope':'Exact projected new mesh triangles checked against evaluated asymmetric sidewall inner edges. Wall-bearing mounts are the only explicit exception; this is not a blanket atlas-envelope check.'};(R/'qa'/('JOINERY_CONTOUR_'+revision+'.json')).write_text(json.dumps(report,indent=2)+'\n')
