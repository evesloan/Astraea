"""Read checked retained source; export new GLB without saving editable source."""
import bpy,json,hashlib
from pathlib import Path
M=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/comfort_greenery/media')
S=Path('/workspace/scratch/375c2e438292/pool-finish-runtime-adoption')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=M/'source/AST-LIB-010_pool_leisure_displays.blend'; approval=S/'media_source_retention.json';a=json.loads(approval.read_text());assert a['source_sha256']==sha(source)==a['committed_blob_sha256'] and a['independently_retained'] and a['parent_export_approved']
q=Path(a['source_qa_report']);assert sha(q)==a['source_qa_report_sha256'];r=json.loads(q.read_text());assert r['status']=='PASS_INDEPENDENT_REOPEN_GEOMETRY_MATERIAL_UV_CONTENT_SUPPORT' and r['actual_eye_to_image_probe_total']==120
out=M/'exports/AST-LIB-010_pool_leisure_displays.glb';report=M/'qa/EXPORT_001.json';assert not out.exists() and not report.exists()
bpy.ops.wm.open_mainfile(filepath=str(source));assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==99;assert len([o for o in bpy.context.scene.objects if o.type=='EMPTY'])==4;assert all(o.type in ['MESH','EMPTY'] for o in bpy.context.scene.objects)
source_hash=sha(source);out.parent.mkdir(exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
assert sha(source)==source_hash
report.write_text(json.dumps({'status':'EXPORTED_PENDING_INDEPENDENT_EQUIVALENCE','source_sha256':source_hash,'export_sha256':sha(out),'approval_sha256':sha(approval),'script_sha256':sha(Path(__file__)),'source_meshes':99,'display_roots':4,'source_saved':False,'runtime_changed':False},indent=2)+'\n')
print('New display export created; pending source/export equivalence',sha(out))
