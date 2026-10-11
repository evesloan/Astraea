from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];source=R/'BlenderCatalogue/assets/primary_atrium_core/source/AST-CIR-005_spine_core.blend';bpy.ops.wm.open_mainfile(filepath=str(source));records={}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 v=[list(o.matrix_world*q.co)for q in o.data.vertices];faces=[list(q.vertices)for q in o.data.polygons];payload={'vertices':v,'faces':faces,'materials':[m.name for m in o.data.materials]};records[o.name]={'sha256':hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'world_min':[min(q[0]for q in v),min(q[2]for q in v),272-max(q[1]for q in v)],'world_max':[max(q[0]for q in v),max(q[2]for q in v),272-min(q[1]for q in v)]}
(W/'EXACT_NATIVE_MESH_AUDIT.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'meshes':records},indent=2)+'\n')
for name in ['CORE_OuterWall_03_-1','CORE_WallDado_03_-1']:print(name,records[name])
print('Audited meshes',len(records))
