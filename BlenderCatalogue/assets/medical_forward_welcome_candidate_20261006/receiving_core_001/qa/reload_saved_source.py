from pathlib import Path
import ast,bpy,bmesh,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];report=json.loads((R/'qa/SOURCE_PRESERVATION.json').read_text());code=ast.parse((R/'source/build_receiving_core.py').read_text())
functions=[n for n in code.body if isinstance(n,ast.FunctionDef) and n.name in ['normal','object_record','material_record']]
exec(compile(ast.Module(body=functions,type_ignores=[]),'preservation_functions','exec'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(report['source']);bpy.ops.wm.open_mainfile(filepath=report['source'])
for name,h in report['unchanged_object_sha256'].items():assert name in bpy.data.objects and object_record(bpy.data.objects[name])==h,name
assert not set(report['removed'])&set(bpy.data.objects.keys())
assert all(name in bpy.data.objects for name in report['added'])
assert hashlib.sha256(json.dumps(material_record(),sort_keys=True,separators=(',',':')).encode()).hexdigest()==report['material_graphs_and_packed_images_sha256']
assert sha(report['source'])==before
out={'status':'PASS','source_sha256':before,'preserved_objects_reloaded':len(report['unchanged_object_sha256']),'added_objects_reloaded':len(report['added']),'old_nodes_removed':report['removed'],'material_graphs_and_packed_images_unchanged':True,'scope':'Saved editable source reload; no Game import or physical runtime claim.'}
(R/'qa/SAVED_SOURCE_RELOAD.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
