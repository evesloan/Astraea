import bpy,json,pathlib,hashlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parent;I=R/'inputs';C=I/'BlenderCatalogue'
manifest=json.loads((C/'catalogue_manifest.json').read_text(encoding='utf-8'))
ids={'AST-SLP-002','AST-FUR-001','AST-FUR-002','AST-FUR-003','AST-GST-003','AST-HSP-001','AST-HSP-003','AST-SAN-001','AST-SAN-002','AST-SAN-003','AST-DOR-001','AST-DOR-002','AST-BOT-002','AST-LGT-001','AST-RES-006'}
out=[]
for item in manifest['assets']:
 if item['catalogue_id'] not in ids:continue
 p=C/item['source'];assert p.exists(),p
 raw=p.read_bytes();pin=hashlib.sha256(raw).hexdigest()
 if item.get('source_sha256'):assert pin==item['source_sha256'],item['catalogue_id']
 bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();parts=[];verts=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();vv=[ev.matrix_world@v.co for v in me.vertices];me.calc_loop_triangles();verts.extend(vv)
  parts.append({'name':ob.name,'bounds_source':[[min(v[k] for v in vv) for k in range(3)],[max(v[k] for v in vv) for k in range(3)]],'vertices':len(vv),'triangles':len(me.loop_triangles),'materials':[m.name for m in me.materials if m],'uv_layers':[u.name for u in me.uv_layers],'props':{k:str(v) for k,v in ob.items()}});ev.to_mesh_clear()
 out.append({'id':item['catalogue_id'],'source_sha256':pin,'mesh_parts':len(parts),'bounds_source':[[min(v[k] for v in verts) for k in range(3)],[max(v[k] for v in verts) for k in range(3)]],'parts':parts,'packed_images':[{'name':x.name,'packed':bool(x.packed_file),'path':x.filepath} for x in bpy.data.images if x.type!='RENDER_RESULT']})
 print('INSPECTED',item['catalogue_id'],len(parts),'parts',flush=True)
(R/'NATIVE_INPUT_INSPECTION.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
