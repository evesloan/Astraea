"""Source-authored maximum-travel bounds against real exported triangles and clear prisms.
Conservative bounding-sphere enclosure for rotations covers the continuous travel, not snapshots.
"""
from pathlib import Path
import json,sys
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'qa'));from geometry_review import glb
s=json.loads((R/'qa/source_build.json').read_text());g=glb(R/'exports/AST-ENG-008_dense_bays.glb');rows=[]
for c in s['controls']:
 tris=np.concatenate([m['triangles'] for m in g['meshes'] if m['node']=='ACT_'+c['id']]);v=tris.reshape(-1,3);p=np.array(c['pivot_xyz']);axis=np.array(c['travel_axis_xyz'],float);axis/=np.linalg.norm(axis)
 if c['travel_type']=='translation':
  vv=np.concatenate([v+axis*t for t in c['travel_limits']]);lo=vv.min(0);hi=vv.max(0);mode='exact endpoint union for linear travel'
 else:
  d=v-p;ax=(d@axis)[:,None]*axis;perp=d-ax;rad=np.linalg.norm(perp,axis=1)
  # Each vertex's complete-axis circle contains the authored restricted arc.
  spread=rad[:,None]*np.sqrt(1-axis*axis);lo=(p+ax-spread).min(0);hi=(p+ax+spread).max(0);mode='conservative full-axis circular sweep contains entire bounded arc'
 hits=[n for n,b in s['prisms'].items() if np.all(np.minimum(hi,b[3:])-np.maximum(lo,b[:3])>1e-5)]
 rows.append({'id':c['id'],'swept_bounds_xyz':lo.tolist()+hi.tolist(),'method':mode,'prism_intrusions':hits})
report={'passed':all(not r['prism_intrusions'] for r in rows),'scope':'Conservative continuous motion envelope of actual exported actuator vertices only; no runtime animation, target, physical or repeated-use acceptance','actuator_count':len(rows),'rows':rows};(R/'qa/actuator_travel_check.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTINUOUS_ACTUATOR_TRAVEL_BOUNDS',report['passed'],len(rows));assert report['passed']
