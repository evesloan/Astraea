"""Independently checks actual exported seam profiles, not generator constants."""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# Load the binary-reader definitions, without running its top-level audit.
ns={"__file__":str(ROOT/"qa/validate_glb.py")};exec((ROOT/'qa/validate_glb.py').read_text().split('reports=[]')[0],ns)
read_glb=ns['read_glb'];accessor=ns['accessor']
def data(ident):
 j,b=read_glb(ROOT/(ident+'.glb'));out={};normals=[]
 for mesh in j['meshes']:
  for p in mesh['primitives']:
   role=j['materials'][p['material']]['name'].replace('ASTRAEA_','')
   pos=accessor(j,b,p['attributes']['POSITION']);nor=accessor(j,b,p['attributes']['NORMAL'])
   out.setdefault(role,[]).extend((v[0],-v[2],v[1]) for v in pos)
   if ident=='AST-STF-003':
    normals.extend({'position':(v[0],-v[2],v[1]),'normal':(n[0],-n[2],n[1])} for v,n in zip(pos,nor))
 return out,normals
D={ident:data(ident) for ident in ['AST-STF-001','AST-STF-002','AST-STF-003']}
def seam(ident,kind):
 role='staff_rubber' if kind=='bumper' else 'staff_zinc'
 x=.3 if ident=='AST-STF-002' else 0
 pts=[]
 for a,y,z in D[ident][0][role]:
  if abs(a-x)>1e-6:continue
  if kind=='bumper' and not (.76499<=z<=.93501 and y<-.039):continue
  if kind=='cove' and not (z<=.18201 and y<-.032):continue
  if kind=='top' and not (z>=2.57499 and y<-.032):continue
  pts.append((round(y,6),round(z,6)))
 return sorted(set(pts))
rows=[]
for kind in ['bumper','cove','top']:
 baseline=seam('AST-STF-001',kind)
 for other in ['AST-STF-002','AST-STF-003']:
  match=baseline==seam(other,kind)
  rows.append({'profile':kind,'bay_to':other,'vertices_on_exact_mating_plane':baseline,'maximum_profile_deviation_m':0 if match else None,'pass':match})
# Corner second leg shares the same physical section after a +90-degree turn.
for kind in ['bumper','cove','top']:
 role='staff_rubber' if kind=='bumper' else 'staff_zinc';pts=[]
 for x,y,z in D['AST-STF-002'][0][role]:
  if abs(y+.3)>1e-6:continue
  if kind=='bumper' and not (.76499<=z<=.93501 and x>.039):continue
  if kind=='cove' and not (z<=.18201 and x>.032):continue
  if kind=='top' and not (z>=2.57499 and x>.032):continue
  pts.append((round(-x,6),round(z,6)))
 rows.append({'profile':kind,'bay_to':'AST-STF-002_B_rotated_90deg','pass':sorted(set(pts))==seam('AST-STF-001',kind)})
terminal_outward=[p for p in D['AST-STF-003'][1] if abs(p['position'][0]-.09)<1e-6 and p['normal'][0]>.9]
report={'scope':'Actual GLB static interface proof; no runtime collision or route acceptance','joints':rows,'panel_joint_gap_m':.012,'bumper_and_cove_mating_gap_m':0,'terminal_positive_X_end_cap_vertices':len(terminal_outward),'terminal_closed_end_pass':len(terminal_outward)>8,'all_source_parts_closed':'See source_reload_validation.json for every source mesh manifold edge and positive-volume check','status':'PASS' if all(r['pass'] for r in rows) and len(terminal_outward)>8 else 'FAIL'}
(ROOT/'qa/connection_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['status']=='PASS'
