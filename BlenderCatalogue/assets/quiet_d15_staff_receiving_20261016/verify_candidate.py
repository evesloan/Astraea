from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
D=Path(__file__).resolve().parent;R=D.parents[2];p=json.loads((D/'PLAN.json').read_text());receipt=json.loads((D/'SOURCE_RECEIPT.json').read_text())
for f,h in p['source_pins'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h
bpy.ops.wm.open_mainfile(filepath=str(D/'QuietD15StaffReceiving_r001.blend'));native={};tops=[]
def signature(o):
 o.data.calc_loop_triangles();return sorted(tuple(sorted(tuple(round(float(c),4)for c in o.matrix_world@o.data.vertices[i].co)for i in t.vertices))for t in o.data.loop_triangles)
for o in bpy.data.objects:
 if o.type=='MESH':
  native[o.name]=signature(o)
  if o.name=='Q15_MissingFloor':
   for t in o.data.loop_triangles:
    vs=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
    if all(abs(v.z-93)<.0001 for v in vs):tops.append([[v.x,-v.y]for v in vs]);assert (vs[1]-vs[0]).cross(vs[2]-vs[0]).z>0
assert len(native)==44
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath='/workspace/quiet-d15-receiving/FRESH.glb',export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
assert Path('/workspace/quiet-d15-receiving/FRESH.glb').read_bytes()==(D/'QUIET_D15_STAFF_RECEIVING_r001.glb').read_bytes()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(D/'QUIET_D15_STAFF_RECEIVING_r001.glb'))
export={o.name:signature(o)for o in bpy.data.objects if o.type=='MESH'};assert native.keys()==export.keys()
assert all(native[n]==export[n]for n in native)
r={'status':'PASS_SOURCE_GEOMETRY_ONLY','native_meshes':44,'native_export_world_triangle_matches_at_100um':44,'fresh_export_byte_identical':True,'protected_file_hashes':len(p['source_pins']),'floor_top_triangles':tops,'runtime_installed':False,'route_support_engineering_or_visual_accepted':False}
(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS_NATIVE_CANDIDATE',len(native))
