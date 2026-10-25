"""Conservative source-space screening, not an installed physics acceptance."""
from pathlib import Path
import json,struct,hashlib
R=Path(__file__).resolve().parents[2];D=R/'Game/foremid_orchard_receiver_20261025'
c=json.loads((D/'RECEIVER_r003.json').read_text(encoding='utf-8'))
def glb(path,offset=(0,0,0)):
 with path.open('rb') as f:
  h=f.read(20);j=json.loads(f.read(struct.unpack_from('<I',h,12)[0]))
 rows=[]
 for n in j['nodes']:
  if 'mesh' not in n:continue
  assert not any(k in n for k in ['matrix','translation','rotation','scale']), 'This screening requires source-baked mesh transforms'
  bounds=[]
  for p in j['meshes'][n['mesh']]['primitives']:
   a=j['accessors'][p['attributes']['POSITION']];bounds.append((a['min'],a['max']))
  lo=[min(v[0][i] for v in bounds)+offset[i] for i in range(3)];hi=[max(v[1][i] for v in bounds)+offset[i] for i in range(3)]
  rows.append({'name':n.get('name',''),'lo':lo,'hi':hi})
 return rows
def overlap(a,b):return all(a['lo'][i]<b['hi'][i]-1e-5 and a['hi'][i]>b['lo'][i]+1e-5 for i in range(3))
model=glb(D/'ForemidOrchardReceiver_r003.glb')
assert len(model)==len(c['parts'])==90
names={p['name'] for p in c['parts']};assert names=={p['name'] for p in model}
for p,h in c['source_pins'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
box_checks=0
for p in c['parts']:
 if 'lo' not in p:continue
 q=next(q for q in model if q['name']==p['name'])
 assert max(abs(q[k][i]-p[k][i]) for k in ['lo','hi'] for i in range(3))<.00004,p['name']
 box_checks+=1
vehicle=glb(R/'Game/source_derivatives/group4_boarding_safety_20261011/AST-TRM-G4-024_powered_portal_body_r001.glb',(-5.6,56.1,-241))
vehicle_box={'lo':[min(p['lo'][i] for p in vehicle) for i in range(3)],'hi':[max(p['hi'][i] for p in vehicle) for i in range(3)]}
over_vehicle=[p['name'] for p in model if overlap(p,vehicle_box)]
station=glb(R/'Game/source_derivatives/group4_completion_20261011/AST-TRM-G4-020_foremid_north_candidate.glb')
court=glb(R/'Game/assets/models/AST-RTL-009.glb',(4,52.5,-250))
interfaces=[]
for p in model:
 for source,q in [('station',q) for q in station]+[('court',q) for q in court]:
  if overlap(p,q):interfaces.append({'candidate':p['name'],'source':source,'member':q['name']})
bridge=next(p for p in model if p['name']=='MissingOnlyOverRailReceiving')
receipt={'candidate_only':True,'checks':{'named_parts':len(model),'exact_box_bounds':box_checks,'source_pins':len(c['source_pins']),'riser_sum_m':28*.175,'tread_run_each_m':14*.28},'stationary_vehicle_full_source_aabb':vehicle_box,'candidate_overlaps_full_vehicle_aabb':over_vehicle,'bridge_underside_above_source_vehicle_top_m':bridge['lo'][1]-vehicle_box['hi'][1],'conservative_static_interface_overlaps':interfaces,'limits':'Baked GLB accessor AABBs only. No triangle sweep, gate/door poses, player/cart test, structural receiver proof, whole-world or scenic acceptance. Candidate is unselected; overlaps are retained for exact fitting, not filtered away.'}
out=D/'SOURCE_FIT_SCREEN_r003.json';assert not out.exists();out.write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in receipt.items() if k!='conservative_static_interface_overlaps'}));print('Conservative static interfaces:',len(interfaces))
