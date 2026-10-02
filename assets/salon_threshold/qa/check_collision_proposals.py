"""Finite clear/blocked probes of proposed separate convex collision hulls."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
BASE=Path(__file__).resolve().parents[1]
data=json.loads((BASE/'collision_proposals.json').read_text());eq={};counts={}
for ident,a in data['assets'].items():
 hs=[]
 for h in a['hulls']:
  p=np.array(h['points_m']);assert np.isfinite(p).all();ch=ConvexHull(p);assert ch.volume>0;hs.append(ch.equations)
 eq[ident]=hs;counts[ident]=len(hs)
def hit(ident,p):return any(np.max(h[:,:3]@np.array(p)+h[:,3])<=1e-7 for h in eq[ident])
def hits(p,ids):
 for ident in ids:
  q=list(p)
  if ident=='AST-SAL-002' and 'AST-SAL-003' in ids:q[0]+=3.1
  if hit(ident,q):return True
 return False
probes=[]
def probe(name,p,want,ids):
 actual=hits(p,ids);probes.append({'name':name,'point_source_m':p,'asset_ids':ids,'expected_blocked':want,'actual_blocked':actual,'pass':actual==want})
for x in(-2.10,0,2.10):
 for y in(.08,.64,1.20):
  for z in(.03,1.65,3.05):probe('portal_clear_'+str((x,y,z)),[x,y,z],False,['AST-SAL-001'])
for x in(-2.42,2.42):probe('jamb_blocked_'+str(x),[x,.64,1.0],True,['AST-SAL-001'])
probe('header_blocked',[0,.64,3.40],True,['AST-SAL-001'])
for x in(-2.3,0,2.3):
 for y in(.24,.80,1.40):
  for z in(.06,1.65,2.60):probe('quiet_approach_'+str((x,y,z)),[x,y,z],False,['AST-SAL-003','AST-SAL-002'])
for x in(-1.6,0,1.6):probe('quiet_seat_blocked_'+str(x),[x,2.08,.42],True,['AST-SAL-003','AST-SAL-002'])
for p in([0,3.10,1.5],[-2.0,.64,3.4],[1.0,.64,3.5],[-3.02,.08,1.2]):probe('quiet_structure_blocked_'+str(p),p,True,['AST-SAL-003','AST-SAL-002'])
probe('left_shelf_void',[-2.775,1.8,.75],False,['AST-SAL-003','AST-SAL-002'])
probe('left_shelf_board',[-2.775,1.8,.53],True,['AST-SAL-003','AST-SAL-002'])
for ident,a in data['assets'].items():
 for v in a['preserved_voids']:
  lo=np.array(v['min_source_m']);hi=np.array(v['max_source_m']);mid=(lo+hi)/2
  for axis in range(3):
   for i,t in enumerate(np.linspace(0,1,33)):
    p=mid.copy();p[axis]=lo[axis]+t*(hi[axis]-lo[axis]);probe(v['name']+'_finite_axis_'+str(axis)+'_'+str(i),p.tolist(),False,[ident])
report={'status':'PASS' if all(p['pass'] for p in probes) else'FAIL','schema':data['schema'],'hull_counts':counts,'probes':probes,'scope':'Finite source-coordinate component collision proposal screens only; no swept volumes, actor/cart fit, runtime or actual host placement proof'}
(BASE/'qa/collision_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'hulls':counts,'checks':len(probes),'failed':[p for p in probes if not p['pass']]},indent=2));assert report['status']=='PASS'
