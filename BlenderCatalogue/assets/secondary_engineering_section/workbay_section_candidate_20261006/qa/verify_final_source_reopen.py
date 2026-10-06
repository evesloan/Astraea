"""Independent read-only reopen of the final editable section source."""
from pathlib import Path
import bpy,json,hashlib,numpy as np,resource
R=Path(__file__).resolve().parents[1];p=R/'source/AST-ENG-008_workbay_section_final.blend';sha=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest();before=sha(p);S=json.loads((R/'qa/section_export_build.json').read_text());assert before==S['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();errors=[];triangles=[];pids=[];mids=[];names=[];materials=[]
for row in S['parts']:
 ob=bpy.data.objects.get(row['name']);assert ob is not None,row['name'];eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];vs=[(v.x,v.z,-v.y) for v in vs];b=[min(v[i] for v in vs) for i in range(3)]+[max(v[i] for v in vs) for i in range(3)];errors.append(max(abs(a-z) for a,z in zip(b,row['bounds_xyz'])));assert len(me.loop_triangles)==row['triangles'];pid=len(names);names.append(ob.name)
 for t in me.loop_triangles:
  name=me.materials[t.material_index].name
  if name not in materials:materials.append(name)
  triangles.append([vs[i] for i in t.vertices]);pids.append(pid);mids.append(materials.index(name))
 eo.to_mesh_clear()
np.savez_compressed(R/'qa/reopened_final_source_triangles.npz',triangles=np.array(triangles),part_ids=np.array(pids),material_ids=np.array(mids),part_names=np.array(names),material_names=np.array(materials),source_sha256=np.array(before),coordinate_system=np.array('world Godot XYZ metres'))
report={'passed':max(errors)<1e-7 and sha(p)==before,'source_sha256':before,'export_sha256':S['export_sha256'],'source_parts':len(names),'triangles':len(triangles),'max_bounds_error_m':max(errors),'source_unchanged':True,'triangle_dump_sha256':sha(R/'qa/reopened_final_source_triangles.npz'),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss};(R/'qa/final_source_reopen.json').write_text(json.dumps(report,indent=2)+'\n');print('FINAL_SOURCE_REOPEN',report);assert report['passed']
