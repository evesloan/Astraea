import bpy,json,pathlib,hashlib,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/crossing_r001';build=json.loads((D/'BUILD.json').read_text())
for path,row in build['outputs'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==row['sha256']
native=next(R/p for p in build['outputs'] if p.endswith('.blend'))
bpy.ops.wm.open_mainfile(filepath=str(native))
source={o.name:{'vertices':[tuple(o.matrix_world@v.co) for v in o.data.vertices],'material':[m.name for m in o.data.materials],'uv':len(o.data.uv_layers.active.data) if o.data.uv_layers.active else 0} for o in bpy.data.objects if o.type=='MESH'}
assert len(source)==16 and all(v['uv']>0 for v in source.values())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(D/'ForwardCrossing.glb'))
runtime={o.name:o for o in bpy.data.objects if o.type=='MESH'};assert set(runtime)==set(source)
max_error=0.;tested=0
for name,row in source.items():
 o=runtime[name];points=[o.matrix_world@v.co for v in o.data.vertices]
 assert o.data.uv_layers.active and len(o.data.uv_layers.active.data)>0
 for p in points:
  distance=min((p-Vector(q)).length for q in row['vertices']);max_error=max(max_error,distance);tested+=1
 for p in row['vertices']:assert min((Vector(p)-q).length for q in points)<.0001
 assert [m.name.split('.')[0] for m in o.data.materials]==[m.split('.')[0] for m in row['material']]
assert max_error<.0001
receipt={'passed':True,'objects':len(source),'runtime_vertices_checked':tested,'maximum_coordinate_error_m':max_error,'uv_layers_present':True,'material_roles_preserved':True,'scope':'Independent native reopen and runtime GLB import; no visual or installed-route acceptance','outputs':build['outputs']}
(D/'NATIVE_RUNTIME_CHECK.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
