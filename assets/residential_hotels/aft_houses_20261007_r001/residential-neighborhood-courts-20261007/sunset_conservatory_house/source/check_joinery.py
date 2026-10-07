"""Direct evaluated Sunset joinery/wall/roof fit. No inherited A/B assumption."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];W=R.parents[1];sys.path.insert(0,str(W/'geometry-deps'))
from shapely.geometry import MultiPoint
from shapely.ops import unary_union
P=json.loads((R/'SUNSET_83_PLACEMENT_MAP.json').read_text());rev=sys.argv[1]if len(sys.argv)>1 else'interiors_r001';checks=[];issues=[]
for cfg in P['prototypes']:
 obs=json.loads((R/'outputs'/rev/cfg['address']/'EVALUATED_GEOMETRY.json').read_text());walls=[o for o in obs if o['name'].startswith('SC_Enclosure_')]
 assert len(walls)==12
 for o in obs:
  if not o['name'].startswith(('SC_QuietAlcove','SC_ThirdAlcove','SC_SharedLuggage','SC_Luggage','SC_RecessedWriting','SC_WritingUpright','SC_WritingBook')):continue
  q=MultiPoint([v[:2]for v in o['vertices']]).convex_hull;worst=0
  for wall in walls:
   a,b=wall['bounds'];lo,hi=o['bounds']
   if min(b[2],hi[2])-max(a[2],lo[2])<.0001:continue
   p=MultiPoint([v[:2]for v in wall['vertices']]).convex_hull;overlap=q.intersection(p).area
   # Screen ends intentionally meet the wall; allow a 25mm mounting overlap.
   allowed=.004 if o['name'].startswith(('SC_QuietAlcove','SC_ThirdAlcove'))else .00005
   worst=max(worst,overlap)
   if overlap>allowed:issues.append({'prototype':cfg['address'],'joinery':o['name'],'wall':wall['name'],'overlap_m2':overlap,'allowance_m2':allowed})
  checks.append({'prototype':cfg['address'],'part':o['name'],'max_wall_overlap_m2':worst})
report={'status':'PASS'if not issues else'FAIL','actual_selected_profile':'Sunset-owned SC_Enclosure left/right profiles from evaluated geometry; retained A walls removed','prototype_count':len(P['prototypes']),'checks':len(checks),'issues':issues,'details':checks,'scope':'Purpose-authored built-ins against actual wall meshes; mounting contacts explicitly bounded. No runtime acceptance.'}
(R/'qa'/('JOINERY_WALL_FIT_'+rev+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(checks),len(issues));assert not issues
