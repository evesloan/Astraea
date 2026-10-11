from pathlib import Path
import json
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;P=json.load(open(W/'PLAN.json'));old=json.load(open(W/'RETAINED_INPUT_R003.json'));rows=[]
for site in P['closure_sites']:
 q=next(q for q in old['parts']if q['source_name']==site['source_name']);lo,hi=q['expected_bounds'];foot=box(lo[0],lo[2],hi[0],hi[2]);caps=[q for q in P['parts']if q['source_name']==site['source_name']];fixed=[q for q in P['retained_members_exact_fit']if q['site']==site['source_name']];levels=sorted({lo[1],hi[1]}|{q[k]for q in caps for k in ['bottom','top']}|{max(lo[1],min(hi[1],q[k]))for q in fixed for k in ['bottom','top']});worst=0;checks=0
 for y,Y in zip(levels,levels[1:]):
  if Y-y<.00001:continue
  mid=(y+Y)/2;new=[Polygon([(v[0],v[2])for v in q['verts'][:3]])for q in caps if q['bottom']<mid<q['top']];retained=[Polygon(q['exact_plan_polygon'])for q in fixed if q['bottom']<mid<q['top']];coverage=unary_union(new+retained);gap=foot.difference(coverage).area;excess=unary_union(new).difference(foot).area;overlap=unary_union(new).intersection(unary_union(retained)).area;assert max(gap,excess,overlap)<.000001,(site['source_name'],mid,gap,excess,overlap);worst=max(worst,gap);checks+=1
 rows.append({'source_wall':site['source_name'],'vertical_bands_verified':checks,'unfilled_plan_area_m2':worst})
report={'status':'PASS_COMPLETE_CLOSURE_WITH_ORIGINAL_MEMBERS','original_wall_sites':len(rows),'source_wall_to_selected_ceiling_span_covered':True,'unexplained_gaps_or_duplicate_retained_volumes':0,'sites':rows};(W/'COMPLETE_CLOSURE_COVERAGE.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows))
