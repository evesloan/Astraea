from pathlib import Path
import bpy,bmesh,json,math
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-HUL-001.blend'))
source={};rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),o.name
 assert bm.calc_volume(signed=True)>0,o.name
 assert all(f.calc_area()>1e-8 for f in bm.faces),o.name
 assert o.data.uv_layers and all(math.isfinite(v)for uv in o.data.uv_layers.active.data for v in uv.uv)
 source[o.name]=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'closed_manifold':True,'positive_volume':True,'metric_uvs_finite':True});bm.free()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'exports/AST-HUL-001.glb'))
max_error=0;degenerate=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 assert o.name in source,o.name
 tree=KDTree(len(source[o.name]))
 for i,v in enumerate(source[o.name]):tree.insert(v,i)
 tree.balance()
 for v in o.data.vertices:max_error=max(max_error,tree.find(o.matrix_world@v.co)[2])
 for f in o.data.polygons:
  if f.area<1e-8:degenerate+=1
assert max_error<.002,max_error
assert degenerate==0,degenerate
out={'meshes':rows,'export_to_source_vertex_max_error_m':max_error,'degenerate_export_faces':degenerate,'scope':'Structural mesh validity and source/export checks; no final art, aperture or structural-load acceptance'}
(R/'qa/lower_hull_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
