import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[4];p=r/'BlenderCatalogue/assets/aquatic_float/source/AST-AQU-006.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='7a146947251756fef403b87f6b6eebfc6f6216dfe9606d2113b0569c9c933f03'
bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(q) for q in o.bound_box];b=[[min(v[j] for v in pts),max(v[j] for v in pts)] for j in range(3)];rows.append({'name':o.name,'bounds_xyz':[b[0],b[2],[-b[1][1],-b[1][0]]],'vertices':len(o.data.vertices),'faces':len(o.data.polygons)})
print(json.dumps(rows,indent=2))
(r/'BlenderCatalogue/assets/group6_completion_20261011/float_physics/ORIGINAL_ASSET_BOUNDS.json').write_text(json.dumps(rows,indent=2)+'\n')
