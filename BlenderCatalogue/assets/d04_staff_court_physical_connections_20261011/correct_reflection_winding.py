from pathlib import Path
import json
W=Path(__file__).resolve().parent;P=json.load(open(W/'RUNTIME_PLAN.json'));assert P['revision']=='r008'
P['revision']='r009';P['previous_native_export_records']=P['native_export_records']
members={n for g in P['gates'] if g.get('hinge_relocated_away_from_middle_planter') for n in g['members']}
for part in P['parts']:
 if part['name'] in members:part['faces']=[list(reversed(f))for f in part['faces']]
P['reflection_winding_corrected']=True
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n')
