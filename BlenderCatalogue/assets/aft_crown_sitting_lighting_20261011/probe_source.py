import bpy,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/hospitality_lantern/source/AST-LGT-001.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  v=[o.matrix_world@Vector(c)for c in o.bound_box];rows.append({'name':o.name,'lo':[min(c[i]for c in v)for i in range(3)],'hi':[max(c[i]for c in v)for i in range(3)],'materials':[m.name for m in o.data.materials],'vertices':len(o.data.vertices)})
 else:rows.append({'name':o.name,'type':o.type,'at':list(o.location),'props':dict(o.items())})
(W/'SOURCE_FIXTURE_PROBE.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
