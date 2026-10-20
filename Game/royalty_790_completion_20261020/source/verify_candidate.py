"""Independent reopen + source/export triangle-equivalence, never production adoption."""
from pathlib import Path
import bpy,bmesh,json,hashlib,collections
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/ROYALTY790_upper_candidate_r002.blend'))
def triangles():
 out=collections.Counter()
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render:continue
  o.data.calc_loop_triangles()
  for tri in o.data.loop_triangles:
   vv=[o.matrix_world@o.data.vertices[i].co for i in tri.vertices]
   key=tuple(sorted(tuple(round(x,4)for x in(v.x,v.z,-v.y))for v in vv))
   out[key]+=1
 return out
native=triangles();mesh_rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('RG_'):continue
 bm=bmesh.new();bm.from_mesh(o.data);mesh_rows.append({'name':o.name,'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(R/'exports/ROYALTY790_upper_candidate_r002.glb'))
export=triangles();missing=native-export;extra=export-native
result={'status':'PASS'if not missing and not extra and all(x['volume']>0 and x['nonmanifold_edges']==0 for x in mesh_rows)else'FAIL','native_triangles':sum(native.values()),'export_triangles':sum(export.values()),'missing_triangles':sum(missing.values()),'extra_triangles':sum(extra.values()),'new_meshes':mesh_rows,'rounded_world_precision_m':.0001,'scope':'Saved native reopen and actual GLB import; not runtime/main integration','sample_missing':[str(k) for k in list(missing)[:3]],'sample_extra':[str(k) for k in list(extra)[:3]]}
(R/'evidence/NATIVE_EXPORT_EQUIVALENCE.json').write_text(json.dumps(result,indent=2)+'\n');print('ROYALTY_EQUIVALENCE',result['status'],result['native_triangles'],result['missing_triangles'],result['extra_triangles'])
assert result['status']=='PASS'
