"""Read-only actual evaluated source corner attributes; no presumed exporter repair."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch18';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else []
for family in args or ['retail_display','retail_work']:
 for p in sorted((ROOT/'assets'/family/'source').glob('AST-*.blend')):
  before=sha(p);bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);dg=bpy.context.evaluated_depsgraph_get();records=[];expected=[];roles=[];collapsed=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();nm=ob.matrix_world.to_3x3().inverted().transposed();uv=me.uv_layers.active
   assert uv,ob.name+' missing UV'
   for t in me.loop_triangles:
    a,b,c=[uv.data[li].uv for li in t.loops]
    if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:collapsed.append({'part':ob.name,'polygon':t.polygon_index})
    for vi,li in zip(t.vertices,t.loops):
     point=ob.matrix_world@me.vertices[vi].co;normal=(nm@me.corner_normals[li].vector).normalized();tex=uv.data[li].uv;records.append(list(point)+list(normal)+list(tex));target_uv=list(tex)
     if family=='retail_work':
      face=me.polygons[t.polygon_index];axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3)if k!=axis];v=me.vertices[vi].co;scale=me.materials[t.material_index]['meters_per_tile_uv'];target_uv=[v[axes[0]]/scale[0],v[axes[1]]/scale[1]]
     expected.append(list(point)+list(normal)+target_uv);roles.append(me.materials[t.material_index].name)
   ev.to_mesh_clear()
  cache=OUT/f'independent_source_corners_{p.stem}.npz';np.savez_compressed(cache,corners=np.asarray(records),export_expected_corners=np.asarray(expected),roles=np.asarray(roles));assert before==sha(p)
  (OUT/f'independent_source_corners_{p.stem}.json').write_text(json.dumps({'source':str(p.relative_to(ROOT)),'source_sha256':before,'corner_cache':str(cache.relative_to(ROOT)),'corner_cache_sha256':sha(cache),'corners':len(records),'collapsed_uv_triangles':collapsed,'export_only_degenerate_uv_projection_repairs':[],'export_uv_policy':('Every evaluated retail_work face is metric-reprojected by dominant actual evaluated face normal before runtime material/ownership grouping; direct modifier-interpolated editable source UVs are retained separately and can differ on bevel faces' if family=='retail_work'else'Direct evaluated source UV unchanged'),'expected_uv_projection_differs_from_direct_source':bool(not np.array_equal(np.asarray(records)[:,6:],np.asarray(expected)[:,6:])),'executed_script_sha256':sha(Path(__file__))},indent=2)+'\n')
