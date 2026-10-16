import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/Astraea');cuts=[('house','Game/assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb',[42.25,84.001,-482.4],[45.5,85.3,-482.0]),('lobby','Game/assets/models/group3_fore_starboard_clinical_20261011/AST-STF-G3-037.glb',[19.6,83.999,-484.2],[22.8,86.7,-483.8])];rows=[]
for owner,path,lo,hi in cuts:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/path))
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();hit=0
  for t in o.data.loop_triangles:
   vs=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];vs=[(v.x,v.z,-v.y)for v in vs]
   if all(min(v[i]for v in vs)<hi[i] and max(v[i]for v in vs)>lo[i]for i in range(3)):hit+=1
  if hit:rows.append({'owner':owner,'path':path,'name':o.name,'potential_triangles':hit,'total_triangles':len(o.data.loop_triangles),'cut_min':lo,'cut_max':hi})
Path('/workspace/quiet-d13-integration/SELECTED_PREIMAGES.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
