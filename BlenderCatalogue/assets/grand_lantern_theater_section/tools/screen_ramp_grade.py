import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];objects=json.load(open(R/'source/geometry.json'))['objects'];out=[]
for o in objects:
 if not o.get('ramp_part_kind'):continue
 vs=o['vertices_world']
 for f in o['faces'][:2]:
  a,b,c=[vs[j] for j in f];det=(b[0]-a[0])*(c[2]-a[2])-(c[0]-a[0])*(b[2]-a[2]);ax=((b[1]-a[1])*(c[2]-a[2])-(c[1]-a[1])*(b[2]-a[2]))/det;az=((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]))/det
  out.append(dict(object=o['name'],part=o['ramp_part_kind'],triangle=f,gradient_x=ax,gradient_z=az,total_gradient=math.hypot(ax,az)))
(R/'qa/rear_ramp_grade_screen.json').write_text(json.dumps(dict(triangle_count=len(out),maximum_grade=max(v['total_gradient'] for v in out),above_1in12=[v for v in out if v['total_gradient']>1/12+1e-7],triangles=out,scope='Pure source top-triangle gradients; no species/cart/runtime certification'),indent=2)+'\n')
print('Maximum rear-ramp grade',max(v['total_gradient'] for v in out))
