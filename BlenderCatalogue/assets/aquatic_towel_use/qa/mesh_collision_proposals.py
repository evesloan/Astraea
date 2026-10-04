"""Triangulate declared collision profiles for independent whole-volume QA."""
from pathlib import Path
import bpy,bmesh,json,math
ROOT=Path(__file__).resolve().parents[1];out={}
for asset in ('AST-AQU-007','AST-AQU-008'):
 data=json.loads((ROOT/f'{asset}.collision_proposal.json').read_text());shapes=[]
 for shape in data['shapes']:
  s=shape;typ=s['type']
  if typ=='aabb':
   lo=s['min_m'];hi=s['max_m'];p=[(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])];a,b=lo[2],hi[2];axis='z'
  elif typ=='extruded_polygon':p=s['profile_2d_m'];a,b=s['interval_m'];axis=s['axis']
  elif typ=='cylinder':
   # A box conservatively contains the entire analytic wheel collider, so
   # finite polygon sampling cannot hide a true continuous-wheel intrusion.
   x,y,z=s['center_m'];r=s['radius_m'];p=[(y-r,z-r),(y+r,z-r),(y+r,z+r),(y-r,z+r)];a,b=x-s['depth_m']/2,x+s['depth_m']/2;axis='x'
  else:raise ValueError(typ)
  v=[(q,x,y) if axis=='x' else (x,q,y) if axis=='y' else (x,y,q) for q in (a,b) for x,y in p];n=len(p);f=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  me=bpy.data.meshes.new(s['name']);me.from_pydata(v,[],f);me.update();me.calc_loop_triangles()
  shapes.append({'name':s['name'],'motion_group':s['motion_group'],'vertices':v,'triangles':[list(t.vertices) for t in me.loop_triangles],'cylinder_bound':'Conservative exact analytic cylinder AABB' if typ=='cylinder' else None})
 out[asset]=shapes
(ROOT/'qa/proposal_geometry.json').write_text(json.dumps(out));print('COLLISION_PROPOSALS_TRIANGULATED')
