"""Read-only authored curtain pose capture; no source saving or rendering."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch15';p=ROOT/'assets/crew_rest/source/AST-CRW-002.blend';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);motion=bpy.data.objects['AST-CRW-002_CURTAIN_MOTION'];rows=[]
for ix,value in enumerate([0,.001,.125,.25,.5,.75,.875,.999,1]):
 motion['gather']=value;motion.update_tag();bpy.context.scene.frame_set(ix+2);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();tris=[];labels=[];roles=[];objects=[]
 for ob in bpy.context.scene.objects:
  row={'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'world_matrix':np.asarray(ob.matrix_world).tolist()}
  if ob.type=='MESH':
   ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=np.asarray([ob.matrix_world@v.co for v in me.vertices]);ts=np.asarray([t.vertices for t in me.loop_triangles]);tris.extend(vs[ts]);labels.extend([ob.name]*len(ts));roles.extend([me.materials[t.material_index].name for t in me.loop_triangles]);row.update(min_m=vs.min(0).tolist(),max_m=vs.max(0).tolist());ev.to_mesh_clear()
  objects.append(row)
 file=OUT/f'independent_curtain_pose_{ix:02}.npz';np.savez_compressed(file,triangles=np.asarray(tris),object_names=np.asarray(labels),material_names=np.asarray(roles));rows.append({'gather':value,'geometry_cache':str(file.relative_to(ROOT)),'geometry_sha256':sha(file),'objects':objects})
assert sha(p)==before
(OUT/'independent_curtain_pose_source.json').write_text(json.dumps({'passed':True,'source':str(p.relative_to(ROOT)),'source_sha256':before,'poses':rows,'source_bytes_unchanged':True,'executed_script_sha256':sha(Path(__file__)),'limits':'Read-only authored geometric parameter samples; source formula review is separate from the finite sample observations and from any real cloth behavior'},indent=2)+'\n')
