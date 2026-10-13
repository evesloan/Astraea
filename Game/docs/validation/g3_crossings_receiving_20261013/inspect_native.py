import bpy,json
from pathlib import Path
out=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 mesh=o.data;rows=[]
 for face in mesh.polygons:
  if face.normal.z>.99:
   rows.append({'verts':[[round(float(x),7)for x in mesh.vertices[mesh.loops[i].vertex_index].co]for i in face.loop_indices],'uv':[[float(x)for x in mesh.uv_layers.active.data[i].uv]for i in face.loop_indices]if mesh.uv_layers.active else None})
 out.append({'name':o.name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'matrix':[[float(v)for v in row]for row in o.matrix_world],'materials':[m.name for m in mesh.materials],'top_samples':rows[:3]})
Path('/workspace/astraea-integration-cutoff-20261013/crossing_threshold_successor/ORIGINAL_NATIVE_INSPECTION.json').write_text(json.dumps(out,indent=2)+'\n')
print('NATIVE_INSPECTION_PASS',[(q['name'],q['vertices'],q['faces'])for q in out])
