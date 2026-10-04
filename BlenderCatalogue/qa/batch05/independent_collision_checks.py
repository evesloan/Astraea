"""Independent numeric proposal screen, never engine collision acceptance."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05'
def in_box(p,s):
 q=s.get('rotation_quaternion_wxyz',[1,0,0,0]);r=Rotation.from_quat([q[1],q[2],q[3],q[0]]).as_matrix();v=r.T@(np.array(p)-s['center_m']);return bool((np.abs(v)<=np.array(s['size_m'])/2+1e-8).all())
def capsule_distance(p,a,b):
 p,a,b=map(np.array,[p,a,b]);v=b-a;f=np.clip((p-a)@v/(v@v),0,1);return float(np.linalg.norm(p-(a+f*v)))
rows=[]
for id in ['AST-AQU-001','AST-AQU-002']:
 p=ROOT/'assets/aquatic_lounge'/(id+'.collision_proposal.json');j=json.loads(p.read_text());samples=[(0,-.1,.2),(-.7,-.1,.5),(.7,-.1,.5)] if id.endswith('001') else [(0,0,.2)]
 rows.append({'asset':id,'proposal_shape_count':len(j['shapes']),'types':sorted({s['type'] for s in j['shapes']}),'all_finite_positive_boxes':all(np.isfinite(s['center_m']+s['size_m']+s['rotation_quaternion_wxyz']).all() and min(s['size_m'])>0 for s in j['shapes']),'void_samples':[{'point_m':p,'containing_shapes':[s['name'] for s in j['shapes'] if in_box(p,s)]} for p in samples],'drain_slots':'Thin seating/table contact surfaces intentionally bridge narrow drainage slots; no full-height hull.'})
j=json.loads((ROOT/'assets/aquatic_float/collision_proposals.json').read_text());wedges=j['body_proposal']['wedges'];points=[(0,-.06,.1),(-.12,-.06,.1),(.12,-.06,.1),(0,-.2,.1),(0,.15,.2)];hits=[]
for p in points:
 contain=[]
 for w in wedges:
  vs=np.array(w['convex_hull_input_points_m']);h=ConvexHull(vs)
  if ((h.equations[:,:3]@p+h.equations[:,3])<=1e-8).all():contain.append(w['index'])
 hits.append({'point_m':p,'containing_wedges':contain})
chains=j['grip_proposal']['capsule_chains'];gaps=[]
for c in chains:
 side=c['side'];p=[-.499381 if side=='left' else .499381,-.09,.27]
 gaps.append({'side':side,'under_grip_point_m':p,'minimum_clearance_to_capsule_surface_m':min(capsule_distance(p,s['a_m'],s['b_m'])-s['radius_m'] for s in c['capsules']),'chain_continuity_max_gap_m':max(np.linalg.norm(np.array(a['b_m'])-b['a_m']) for a,b in zip(c['capsules'],c['capsules'][1:]))})
surf=j['seat_proposal']['sampled_surface'];rows.append({'asset':'AST-AQU-006','separate_hull_wedges':len(wedges),'all_hull_points_finite':all(np.isfinite(w['convex_hull_input_points_m']).all() for w in wedges),'well_samples':hits,'grip_capsules':sum(len(c['capsules']) for c in chains),'grip_void_samples':gaps,'sampled_seat_surface_keys':list(surf),'sampled_seat_vertex_count':len(surf['vertices_m']),'scope':'Numeric proposal geometry only; reduced concave seat and segmented coaming need recovered-engine dynamic-body evaluation.'})
for id in ['AST-AQU-003','AST-AQU-004','AST-AQU-005']:
 j=json.loads((ROOT/'assets/aquatic_edges'/(id+'.collision_proposal.json')).read_text());r={'asset':id,'part_count':len(j['parts']),'types':sorted({s['shape'] for s in j['parts']}),'explicitly_disallows_whole_assembly_convex_hull':j['do_not_use_whole_assembly_convex_hull'],'preserve_openings':j['preserve_openings']}
 if id.endswith('005'):
  samples=[(0,-.3,.15),(0,.16,-.03),(0,.48,-.21),(0,.8,-.39),(0,1.22,-.57)];r['center_route_box_samples']=[{'point_m':p,'containing_boxes':[s['name'] for s in j['parts'] if s['shape']=='box' and (np.array(p)>=s['min_m']).all() and (np.array(p)<=s['max_m']).all()]} for p in samples]
 rows.append(r)
result={'scope':'Data-only numerical collision proposals. Finite sample checks cannot prove full swept actor access, game collision, solver support, fluid or buoyancy behavior.','rows':rows}
(OUT/'independent_collision_proposals.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
