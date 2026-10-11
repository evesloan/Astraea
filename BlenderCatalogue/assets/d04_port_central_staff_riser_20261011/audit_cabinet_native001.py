from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();P=json.load(open(W/'PLAN.json'));source=R/'BlenderCatalogue/assets/staff_workbay/AST-STF-007_supply_work_cabinet.blend';before=sha(source);native=W/'D04PortCentralStaffStructure_r001.blend';pin=sha(native)
def payload(ob):
 return {'verts':[list(v.co)for v in ob.data.vertices],'faces':[list(p.vertices)for p in ob.data.polygons],'uvs':[[list(q.uv)for q in layer.data]for layer in ob.data.uv_layers],'materials':[m.name for m in ob.data.materials]}
bpy.ops.wm.open_mainfile(filepath=str(source));expected={o.name:{'data':payload(o),'world':[list(o.matrix_world@v.co+Vector((-60.4,38.2,16.5)))for v in o.data.vertices]}for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(native));count=0;max_error=0
for name,record in expected.items():
 ob=bpy.data.objects.get('PCS_CleanCabinet_'+name);assert ob,name;assert payload(ob)==record['data'],name
 for v,e in zip(ob.data.vertices,record['world']):max_error=max(max_error,(ob.matrix_world@v.co-Vector(e)).length)
 count+=1
assert max_error<.00002,max_error
assert sha(source)==before and sha(native)==pin
(W/'EXACT_CABINET_NATIVE_AUDIT.json').write_text(json.dumps({'status':'PASS','mesh_count':count,'original_vertices_faces_materials_UVs_exact':True,'translation_only_max_world_error_m':max_error,'source_native_sha256':before,'new_native_sha256':pin,'source_and_new_native_bytes_unchanged':True,'cupboard_closed_staging_geometry_only_no_stock_provider_claim':True},indent=2)+'\n');print('Cabinet exact source audit',count,max_error)
