from pathlib import Path
import json,hashlib,numpy as np
from scipy.spatial import ConvexHull
R=Path(__file__).resolve().parent;P=R.parent;C=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section/contracts/END_RETURN_MITER_RESERVATION.json');A=P/'ARCHITECTURE_ADDITIONS_GEOMETRY.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=json.loads(C.read_text());a=json.loads(A.read_text());outer=np.array(h['outer_vertices_world']);inner=np.array(h['inner_vertices_world']);volumes=[]
for i,ids in enumerate(h['triangles']):
 v=np.concatenate([outer[ids],inner[ids]]);volumes.append((v,ConvexHull(v)))
fail=[];candidates=[];exclusions=0
for o in a['objects']:
 q=np.array(o['vertices_world'])
 for i,(v,hull)in enumerate(volumes):
  if not np.all(q.max(0)>=v.min(0)-1e-9)or not np.all(v.max(0)>=q.min(0)-1e-9):exclusions+=1;continue
  separated=[{'plane':j,'margin_m':float(np.min(q@eq[:3]+eq[3]))}for j,eq in enumerate(hull.equations)if np.min(q@eq[:3]+eq[3])>1e-8];row={'object':o['name'],'reservation_facet':i}
  if not separated:fail.append(row)
  else:row['separating_plane']=max(separated,key=lambda x:x['margin_m'])
  candidates.append(row)
d={'status':'NEW_SOURCE_PROPOSAL_CLEAR_OF_18_MITER_BANDS'if not fail else'UNRESOLVED_NEW_SOURCE_MITER_CONTACT','architecture_sha256':sha(A),'miter_contract_sha256':sha(C),'source_shell_contract_sha256':h['source_contract_sha256'],'proposed_object_count':len(a['objects']),'proposed_vertices':sum(len(o['vertices_world'])for o in a['objects']),'normal_reservation_m':h['normal_reserve_m'],'facets':len(volumes),'broad_phase_separations':exclusions,'actual_vertex_separating_plane_checks':candidates,'unresolved':fail,'method':'Identical six-point outer-to-inner convex facet bands and separating-plane threshold (>1e-8 m) to screen_shell_and_floor_readiness.py. All actual proposed vertices, hence their connected faces/edges, lie on the separating side; no center-only or AABB-overlap acceptance.','maximum_new_top_y':max(v[1]for o in a['objects']for v in o['vertices_world']),'limits':['The reservation is an unbuilt 0.8m normal-pressure-shell proposal. This proves absence of geometric intrusion, not structural or pressure certification.','Covers the 145 current new architecture objects, not absent optical head derivative bodies or future edits.']};(R/'CURRENT_NEW_ARCHITECTURE_MITER_SCREEN.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
