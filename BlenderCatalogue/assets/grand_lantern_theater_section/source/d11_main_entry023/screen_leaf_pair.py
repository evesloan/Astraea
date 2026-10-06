from pathlib import Path
import sys,json,numpy as np,hashlib
R=Path(__file__).resolve().parent;G=Path('/workspace/shared/astraea-godot-production-20261003');P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from geometry_review import glb
source=(R/'screen_source_sweep.py').read_text();ns={'np':np};exec(source[source.index('def sat_times'):source.index('# Analytical witnesses')],ns);sat=ns['sat_times']
g=glb(G/'assets/models/AST-CUL-005_moving_003.glb');groups={key:[m for m in g['meshes']if m['extras'].get('source_owner')=='THEATER_D11_MAIN_LEAF_'+key]for key in ['LEFT','RIGHT']};rows=[]
def fraction(t,side):return np.clip(t/.85 if side=='LEFT'else(t-.15)/.85,0,1)
for t0,t1 in [(0,.15),(.15,.85),(.85,1)]:
 l0=-2.65*fraction(t0,'LEFT');r0=2.65*fraction(t0,'RIGHT');l1=-2.65*fraction(t1,'LEFT');r1=2.65*fraction(t1,'RIGHT');delta=np.array([0,0,(l1-l0)-(r1-r0)]);target=np.concatenate([m['triangles']+[0,0,r0]for m in groups['RIGHT']]);owners=np.concatenate([np.full(len(m['triangles']),i)for i,m in enumerate(groups['RIGHT'])]);lo=target.min(1);hi=target.max(1)
 for mesh in groups['LEFT']:
  for ai,a in enumerate(mesh['triangles']+[0,0,l0]):
   low=np.minimum(a.min(0),a.min(0)+delta)-1e-7;high=np.maximum(a.max(0),a.max(0)+delta)+1e-7;candidates=np.flatnonzero(np.all(hi>=low,1)&np.all(lo<=high,1))
   if not len(candidates):continue
   ix,enter,leave=sat(a,delta,target[candidates])
   for j in ix:
    ti=int(candidates[j]);rows.append({'open_fraction_phase':[t0,t1],'local_fraction_enter':float(enter[j]),'local_fraction_leave':float(leave[j]),'left_batch':mesh['node'],'left_triangle':ai,'right_batch':groups['RIGHT'][int(owners[ti])]['node'],'left_triangle_xyz':a.tolist(),'right_triangle_xyz':target[ti].tolist()})
p=R/'LEAF_PAIR_CONTINUOUS_CONTACTS.json';assert not p.exists();p.write_text(json.dumps({'status':'PAIR_CONTACTS_REPORTED'if rows else'PASS_NO_LEAF_PAIR_SURFACE_INTERSECTION','count':len(rows),'contacts':rows,'source_glb_sha256':g['sha256'],'sequence':'Exact existing first-open/last-close .85/.15 normalized family sequence at source2.65m stroke; allthree linear phases screened continuously. Actual imported margins pending.'},indent=2)+'\n');print('PAIR_CONTACTS',len(rows));print('max phase',max((r['open_fraction_phase'][0]+r['local_fraction_leave']*(r['open_fraction_phase'][1]-r['open_fraction_phase'][0])for r in rows),default=None))
