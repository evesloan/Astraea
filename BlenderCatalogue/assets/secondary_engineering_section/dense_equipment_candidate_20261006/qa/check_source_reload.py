"""Read-only independent source reopen; report only in scratch QA folder."""
from pathlib import Path
import bpy,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];S=json.loads((R/'qa/source_build.json').read_text());p=R/'source/AST-ENG-008_dense_bays.blend';before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();errors=[];triangles=[];part_ids=[];material_ids=[];part_names=[];material_names=[]
for row in S['parts']:
 ob=bpy.data.objects.get(row['name']);assert ob is not None;eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();v=[ob.matrix_world@p.co for p in me.vertices];v=[(p.x,p.z,-p.y) for p in v];bounds=[min(p[i] for p in v) for i in range(3)]+[max(p[i] for p in v) for i in range(3)];errors.append(max(abs(a-b) for a,b in zip(bounds,row['bounds_xyz'])));assert len(me.loop_triangles)==row['triangles']
 part_index=len(part_names);part_names.append(row['name'])
 for tr in me.loop_triangles:
  triangles.append([v[i] for i in tr.vertices]);part_ids.append(part_index)
  material=me.materials[tr.material_index].name if me.materials else 'NONE'
  if material not in material_names:material_names.append(material)
  material_ids.append(material_names.index(material))
 eo.to_mesh_clear()
for row in S['markers']:assert bpy.data.objects.get(row['name']) is not None
np.savez_compressed(R/'qa/reopened_source_triangles.npz',triangles=np.array(triangles,dtype=np.float64),part_ids=np.array(part_ids,dtype=np.int32),material_ids=np.array(material_ids,dtype=np.int16),part_names=np.array(part_names),material_names=np.array(material_names),source_sha256=np.array(before),coordinate_system=np.array('world Godot XYZ metres'))
report={'passed':max(errors)<1e-7 and hashlib.sha256(p.read_bytes()).hexdigest()==before,'source_sha256':before,'source_parts':len(errors),'markers':len(S['markers']),'max_bounds_error_m':max(errors),'source_unchanged':True,'evaluated_triangle_dump':'reopened_source_triangles.npz','triangle_dump_sha256':hashlib.sha256((R/'qa/reopened_source_triangles.npz').read_bytes()).hexdigest(),'scope':'Actual saved editable Blender source reopen; no visual/runtime acceptance'};(R/'qa/source_reload.json').write_text(json.dumps(report,indent=2)+'\n');print(report);assert report['passed']

import resource
print('PROCESS_PEAK_RSS_KIB',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
