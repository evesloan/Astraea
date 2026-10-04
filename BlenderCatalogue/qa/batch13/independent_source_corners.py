"""Read-only evaluated triangle corner attributes for post-consolidation verification."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for family in ['botanical_cluster','botanical_transition']:
 for p in sorted((ROOT/'assets'/family/'source').glob('AST-*.blend')):
  before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);dg=bpy.context.evaluated_depsgraph_get();records=[];expected=[];roles=[];repairs=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();nm=ob.matrix_world.to_3x3().inverted().transposed();uv=me.uv_layers.active
   repair=set()
   for t in me.loop_triangles:
    a,b,c=[uv.data[li].uv for li in t.loops]
    if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:repair.add(t.polygon_index)
   if repair:repairs.append({'part':ob.name,'collapsed_uv_polygons':sorted(repair),'material':me.materials[0].name})
   for t in me.loop_triangles:
    for vi,li in zip(t.vertices,t.loops):
     point=ob.matrix_world@me.vertices[vi].co;normal=(nm@me.corner_normals[li].vector).normalized();tex=uv.data[li].uv;records.append(list(point)+list(normal)+list(tex));expected_tex=list(tex)
     if t.polygon_index in repair:
      face=me.polygons[t.polygon_index];axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis];v=me.vertices[vi].co;sc=tuple(me.materials[t.material_index].get('meters_per_tile_uv',[1,1]));expected_tex=[v[axes[0]]/sc[0],v[axes[1]]/sc[1]]
     expected.append(list(point)+list(normal)+expected_tex);roles.append(me.materials[t.material_index].name)
   ev.to_mesh_clear()
  cache=OUT/f'independent_source_corners_{p.stem}.npz';np.savez_compressed(cache,corners=np.asarray(records),export_expected_corners=np.asarray(expected),roles=np.asarray(roles));assert before==sha(p)
  (OUT/f'independent_source_corners_{p.stem}.json').write_text(json.dumps({'source':str(p.relative_to(ROOT)),'source_sha256':before,'corner_cache':str(cache.relative_to(ROOT)),'corner_cache_sha256':sha(cache),'corners':len(records),'export_only_degenerate_uv_projection_repairs':repairs,'executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
