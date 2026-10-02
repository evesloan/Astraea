from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
from check_interfaces import equations_box,intersecting_triangles,inside
ROOT=Path(__file__).resolve().parents[1];data=json.loads((ROOT/'qa/proposal_geometry.json').read_text());report={}
for asset,shapes in data.items():
 manifests=json.loads((ROOT/f'{asset}.manifest.json').read_text());tris=np.concatenate([np.array(s['vertices'])[np.array(s['triangles'])] for s in shapes]);clear=[]
 for c in manifests['clear_volumes']:
  lo=np.array(c['min_m']);hi=np.array(c['max_m']);hits=intersecting_triangles(tris,equations_box(lo,hi),lo,hi)
  center=(lo+hi)/2;contained=[]
  for s in shapes:
   v=np.array(s['vertices'])
   if np.all(center>=v.min(0)) and np.all(center<=v.max(0)) and inside(v[np.array(s['triangles'])],center):contained.append(s['name'])
  clear.append({'name':c['name'],'whole_clear_volume_boundary_intrusions':len(hits),'center_contained_in_shapes':contained,'passed':not hits and not contained})
 p=tris[0];lo=p.min(0)-.001;hi=p.max(0)+.001;positive=intersecting_triangles(tris,equations_box(lo,hi),lo,hi)
 row={'proposal_shape_count':len(shapes),'whole_clear_volumes':clear,'positive_solid_boundary_hits':len(positive),'passed':all(x['passed'] for x in clear) and bool(positive)}
 if asset=='AST-AQU-008':
  fixed=np.concatenate([np.array(s['vertices'])[np.array(s['triangles'])] for s in shapes if s['motion_group']=='fixed']);sweeps=[]
  for s in shapes:
   if s['motion_group']!='container':continue
   v=np.array(s['vertices']);v=np.vstack((v,v+[0,.92,0]));h=ConvexHull(v);hits=intersecting_triangles(fixed,h.equations,v.min(0),v.max(0));sweeps.append({'shape':s['name'],'fixed_proposal_triangle_intrusions':len(hits),'passed':not hits})
  row['continuous_proposal_sweeps']=sweeps;row['passed'] &= all(x['passed'] for x in sweeps)
  rad=.025;off=np.array([[x,y,z] for x in (-rad,rad) for y in (-rad,rad) for z in (-rad,rad)]);path=manifests['throat_path_proposal']['centres_blender_source_m'];segments=[]
  for i,(a,b) in enumerate(zip(path,path[1:])):
   v=np.vstack((np.array(a)+off,np.array(b)+off));h=ConvexHull(v);hits=intersecting_triangles(tris,h.equations,v.min(0),v.max(0));segments.append({'segment':i,'proposal_intrusions':len(hits),'passed':not hits})
  row['continuous_proposal_throat']=segments;row['passed'] &= all(x['passed'] for x in segments)
 row['limitations']='Declared geometric compounds, not engine physics. Boundaries tested against full volumes and continuous sweeps. Wheel analytic cylinders conservatively enclosed in AABBs; the documented0.961mm floor overreach remains.'
 report[asset]=row
out={'assets':report,'all_passed':all(r['passed'] for r in report.values())};(ROOT/'qa/collision_proposal_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
