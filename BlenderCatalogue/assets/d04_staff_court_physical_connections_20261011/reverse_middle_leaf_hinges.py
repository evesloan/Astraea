from pathlib import Path
import json
W=Path(__file__).resolve().parent
P=json.load(open(W/'RUNTIME_PLAN.json'))
assert P['revision']=='r007'
P['revision']='r008';P['previous_native_export_records']=P['native_export_records']
for g in P['gates']:
 if g['name'] not in ['D04PC_Hatch_928_0','D04PC_Hatch_952_1','D04PC_ToolPane_928_0','D04PC_ToolPane_952_1']:continue
 lo,hi=g['leaf_min'][2],g['leaf_max'][2]
 for part in P['parts']:
  if part['name'] in g['members']:
   for v in part['verts']:v[2]=lo+hi-v[2]
 g['candidate_open_degrees']=-g['candidate_open_degrees'];g['pivot'][2]=hi if g['candidate_open_degrees']<0 else lo
 g['hinge_relocated_away_from_middle_planter']=True
P['maintenance_method']['open_middle_leaves_park_away_from_oblique_approach']=True
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n')
