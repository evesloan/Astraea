import bpy,json
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(B/'source/AST-CRW-001.blend'));o=bpy.data.objects['001_shaped_single_mattress'];m=o.data;rows=[]
for f in m.polygons:
 if len(f.vertices)!=4:continue
 p=[m.vertices[i].co for i in f.vertices]
 for i in range(4):
  a,b,c=[p[(i+j)%4]for j in range(3)];d=p[(i+3)%4];n=(b-a).cross(c-a).normalized();rows.append(abs((d-a).dot(n)))
print('MAX_QUAD_NONPLANAR_DISTANCE',max(rows))
