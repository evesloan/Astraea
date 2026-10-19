import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/Astraea');cuts=[('fore','Game/assets/group2_central_receiving_20261013/CENTRAL_ADJUNCT_RECEIVING_FRAME_r004.glb',[60.05,102.001,-16.04],[62.95,103.2,-15.96]),('aft','Game/assets/models/AST-RES-006.glb',[78.2,102.001,14.5],[78.7,104,17.5])];rows=[]
for owner,path,lo,hi in cuts:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/path))
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();hit=0
  for t in o.data.loop_triangles:
   vs=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];vs=[(v.x,v.z,-v.y)for v in vs]
   if all(min(v[i]for v in vs)<hi[i] and max(v[i]for v in vs)>lo[i]for i in range(3)):hit+=1
  if hit:rows.append({'owner':owner,'path':path,'name':o.name,'potential_triangles':hit,'total_triangles':len(o.data.loop_triangles),'cut_min':lo,'cut_max':hi})
Path('/workspace/d17-starboard-integration/RUNTIME_PREIMAGES.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
