from pathlib import Path
import json,copy
W=Path(__file__).resolve().parent;P=json.load(open(W/'AUDIT_INPUT_PLAN.json'));S=json.load(open(W/'SITE_PREFLIGHT001.json'));(W/'SITE_ATTEMPT002_PLANTER_STANCE_HOLD.json').write_text(json.dumps({'status':'HOLD','blocked_court_stances':[q for q in S['stances']if q['blockers']],'routes_roof_and_ledger_failures':[q for q in S['roof_rows']if q['blockers']],'note':'Long court interfaces shift to source gaps; two short court centre planter groups translate inward within their original allocations. No source planter removed.'},indent=2)+'\n');(W/'RETAINED_INPUT_PLAN_ATTEMPT001.json').write_text(json.dumps(P,indent=2)+'\n');(W/'RETAINED_SITE_ATTEMPT002.json').write_text(json.dumps(S,indent=2)+'\n')
for i in [0,1,3,5,7]:
 g=P['gates'][i];old=g['z'];new=old+2.3 if old>0 else old-2.3;dz=new-old;g['z']=new
 for key in ['pivot','closed_center','court_stance','sweep_min','sweep_max']:g[key][2]+=dz
 for q in P['cuts']:
  if q['name'].startswith(g['court_prefix']):
   for b in q['boxes']:b['min'][2]+=dz;b['max'][2]+=dz
 q=next(q for q in P['floor_rectangles']if q['name']=='Collar'+str(i));q['lo'][1]+=dz;q['hi'][1]+=dz
for i,d in [(2,[1.3,0,0]),(6,[-1.2,0,0])]:
 g=P['gates'][i];g['court_stance'][0]=66.5 if i==2 else 101.6;model=P['source_models']['central']
 for q in model['parts']:
  if q['name'].startswith(g['court_prefix']+'_')and(q['name'].endswith('_Planter_1')or q['name'].endswith('_Soil_1')or'_LeafMass_1_'in q['name']):P['moves'].append({'source_root':model['root'],'source_model':model['model'],'source_native':model['native'],'name':q['name'],'preimage':q,'delta':d})
assert len(P['moves'])==10;(W/'AUDIT_INPUT_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print('Revised long-court gaps and ten original planter/soil/leaf meshes; originals preserved')
