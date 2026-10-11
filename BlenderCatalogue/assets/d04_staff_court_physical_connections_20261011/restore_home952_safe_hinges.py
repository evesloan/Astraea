from pathlib import Path
import json
W=Path(__file__).resolve().parent;P=json.load(open(W/'RUNTIME_PLAN.json'));assert P['revision']=='r009';old=json.load(open(W/'attempt12_r007_contact_diagnostic/RUNTIME_PLAN.json'));restore={'D04PC_Hatch_952_1','D04PC_ToolPane_952_1'};members={n for g in old['gates'] if g['name'] in restore for n in g['members']}
P['gates']=[next(q for q in old['gates'] if q['name']==g['name']) if g['name'] in restore else g for g in P['gates']]
P['parts']=[next(q for q in old['parts'] if q['name']==part['name']) if part['name'] in members else part for part in P['parts']]
P['revision']='r010';P['previous_native_export_records']=P['native_export_records'];P['maintenance_method']['home952_safe_hinges_preserve_cocoon_clearance']=True
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n')
