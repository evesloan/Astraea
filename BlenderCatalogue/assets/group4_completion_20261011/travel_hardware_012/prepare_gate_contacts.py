from pathlib import Path
import sys,json,hashlib,collections
import numpy as np
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());sys.path.insert(0,str(W.parent));from glb_geometry import triangles
source=R/'Game/assets/models/AST-DOR-003.glb';components={};checks=0;rows=[]
for name,t,e in triangles(source):
 if not name.startswith('LIFT_fixed_'):continue
 assert len(t)%12==0,name;parts=[]
 # Pinned source batches contain consecutive twelve-triangle closed boxes. Verify every component;
 # never infer a whole-frame convex hull, which would fill the original doorway.
 for start in range(0,len(t),12):
  tt=t[start:start+12];points=np.unique(np.round(tt.reshape(-1,3),6),axis=0);assert len(points)==8
  ids={tuple(p):i for i,p in enumerate(points)};edgecounts=collections.Counter()
  for tri in tt:
   f=[ids[tuple(np.round(p,6))] for p in tri]
   for a,b in zip(f,f[1:]+f[:1]):edgecounts[tuple(sorted([a,b]))]+=1
   n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);n/=np.linalg.norm(n);d=(points-tri[0])@n;assert not(d.min()<-2e-6 and d.max()>2e-6),name
  assert all(n==2 for n in edgecounts.values());checks+=14;parts.append(points.tolist())
 components[name]=parts;rows.append({'mesh':name,'source_triangles':len(t),'exact_closed_convex_components':len(parts),'all_source_faces_accounted':True})
out={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'exact_closed_convex_components':components,'checks':checks,'source_meshes':rows,'components_per_original_gate':sum(map(len,components.values())),'hollow_portal_filled':False,'scope':'Verified actual source closed components; shared faces/interfaces retained as original. No whole-frame hull or bounding box replaces the doorway.'}
(W/'GATE_FRAME_CONVEX_COMPONENTS.json').write_text(json.dumps(out,indent=2)+'\n');print('GATE_SOURCE_CONTACTS',out['components_per_original_gate'],'verified convex source solids per gate;',checks,'checks')
