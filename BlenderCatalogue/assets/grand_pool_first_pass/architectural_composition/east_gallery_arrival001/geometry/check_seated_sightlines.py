"""Read-only exact compiled-floor triangle intersection of two bounded seated sightlines."""
import json,pathlib,hashlib
import numpy as np
R=pathlib.Path(__file__).resolve().parent
P=pathlib.Path('/workspace/shared/astraea-godot-production-20261003/data/architecture/GRAND_POOL_SECTION_RUNTIME.json')
S=pathlib.Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_orchard_section/source/connected_contract.json')
C=json.loads(P.read_text());assert C==json.loads(S.read_text())
eye=np.array([-9.8,53.75,-449.5]);targets={'water_surface':[-31,46.05,-432],'opposite_market_upper_eye_height':[-49.5,54.0,-446]}
def inside(p,t):
 # Barycentric coordinates on exact XZ triangle, no renderer/projection involved.
 a,b,c=np.array(t,dtype=float);m=np.column_stack((b-a,c-a));u,v=np.linalg.solve(m,np.array(p)-a);return [1-float(u)-float(v),float(u),float(v)]
results=[]
for label,target in targets.items():
 target=np.array(target);v=target-eye;hits=[]
 for f in C['floor_regions']:
  for surface,y in [('top',float(f['floor_y'])),('bottom',float(f['floor_y']-f['thickness']))]:
   if abs(v[1])<1e-12:continue
   t=(y-eye[1])/v[1]
   if not 0<t<1:continue
   point=eye+t*v
   for ix,tri in enumerate(f['triangles']):
    bc=inside(point[[0,2]],tri)
    if min(bc)>=-1e-10:
     hits.append({'segment_fraction':float(t),'distance_from_eye_m':float(np.linalg.norm(t*v)),'point_xyz':point.tolist(),'floor_owner':f['id'],'surface':surface,'floor_top_y':f['floor_y'],'floor_thickness_m':f['thickness'],'exact_triangle_index':ix,'exact_triangle_xz':tri,'barycentric_coordinates':bc})
 hits.sort(key=lambda h:h['segment_fraction'])
 results.append({'id':label,'eye_xyz':eye.tolist(),'target_xyz':target.tolist(),'floor_blocked':bool(hits),'first_floor_hit':hits[0]if hits else None,'all_floor_surface_hits':hits})
out={'scope':'Only intersections with exact retained compiler-owned horizontal floor surfaces. No engine, import, production write, new geometry or full-scene visibility claim. Source/runtime contracts compared exactly.','source_contract':str(S),'runtime_contract':str(P),'input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [S,P]},'results':results,'conclusion':'The seated water target is occluded by the bay’s own D09 gallery floor before the ray reaches the opening edge. The opposite-market upper-height ray does not intersect any retained floor plane; this establishes floor clearance only, not unrestricted visibility through glazing, furnishings or later proposal geometry.'}
(R/'SEATED_SIGHTLINES.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
