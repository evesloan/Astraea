import bpy,json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
r={}
for i in ['02','03']:
 bpy.ops.wm.open_mainfile(filepath=str(p/f'RETAINED_D08_directory_{i}.blend'))
 r[i]=[]
 for o in bpy.data.objects:
  if o.type=='MESH':
   v=[o.matrix_world@Vector(x) for x in o.bound_box];a=[[min(q[j] for q in v),max(q[j] for q in v)] for j in range(3)];d={'name':o.name,'kind':o.get('kind'),'bounds_blender':a,'bounds_game':[[a[0][0],a[0][1]],[a[2][0],a[2][1]],[-a[1][1],-a[1][0]]]};r[i].append(d)
 (p/f'INVENTORY_{i}.json').write_text(json.dumps(r[i],indent=2)+'\n')
 print(i)
 for o in r[i]:
  if any(t in o['name'].lower() for t in ['basin','court_bottom','court_rim','entry','transfer','step','hoist','ramp','bath']):print(o)
