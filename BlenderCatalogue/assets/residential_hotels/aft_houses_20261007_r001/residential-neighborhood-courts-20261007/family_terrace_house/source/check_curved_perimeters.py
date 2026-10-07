"""Use each evaluated recipe's exact selected sidewalls; no template guessing."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parents[1]/'geometry-deps'))
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
rows=[]
for p in sorted((R/'outputs/interiors_r003').glob('*/SOURCE_RECEIPT.json')):
 rec=json.loads(p.read_text());profile=rec['actual_shell_profile'];outer=Polygon(profile['left']+list(reversed(profile['right']))).buffer(.08);checks=[]
 for ob in json.loads((p.parent/'EVALUATED_GEOMETRY.json').read_text()):
  if not ob['name'].startswith('FT_'):continue
  polys=[];v=ob['vertices']
  for f in ob['triangles']:
   q=Polygon([v[i][:2]for i in f])
   if q.area>1e-9:polys.append(q)
  if not polys:continue
  q=unary_union(polys);area=q.difference(outer).area;dist=max(Point(a[:2]).distance(outer)for a in v);checks.append({'part':ob['name'],'outside_area_m2':area,'max_outside_distance_m':dist,'pass':area<1e-7 and dist<1e-5})
 rows.append({'prototype':rec['prototype'],'actual_selected_profile':profile,'checks':checks,'pass':all(x['pass']for x in checks)})
out={'shared_recipes':len(rows),'all_pass':len(rows)==8 and all(r['pass']for r in rows),'records':rows,'scope':'Exact evaluated new joinery projected against source-selected curved profile with0.08m trim zone. Runtime collision remains untested.'};(R/'qa/EXACT_SELECTED_CURVED_PERIMETERS.json').write_text(json.dumps(out,indent=2)+'\n');print('SELECTED_PERIMETERS',out['all_pass'],[(r['prototype'],[c['part']for c in r['checks']if not c['pass']])for r in rows if not r['pass']]);assert out['all_pass']
