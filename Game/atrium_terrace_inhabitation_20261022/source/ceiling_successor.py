"""Shallow only our added ceiling relief; preserve the structural cap and r001."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((G/'atrium_ceiling_completion_20261022/evidence/BUILD.json').read_text());assert sha(R/b['native'])==b['native_sha256'];parent=b['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(R/b['native']));bpy.context.preferences.filepaths.save_version=0
def raised(y):return 106.17+(y-106.17)*.35 if y<106.17 else y
before=[];after=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 assert o.matrix_world==Matrix.Identity(4)
 for v in o.data.vertices:before.append(v.co.z);v.co.z=raised(v.co.z);after.append(v.co.z)
 o.data.update()
bpy.context.view_layer.update();records=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(c)for c in o.bound_box];pts=[(v.x,v.z,-v.y)for v in pts]
 records.append({'name':o.name,'bounds':[[min(v[k]for v in pts)for k in range(3)],[max(v[k]for v in pts)for k in range(3)]],'material':o.data.materials[0].name})
for row in b['lights']:
 row['position'][1]=raised(row['position'][1]);row['anchor'][1]=raised(row['anchor'][1]);row['energy']=1.5;row['angle']=72
native=R/'BlenderCatalogue/assets/atrium_terrace_inhabitation_20261022/AtriumLanternCeiling_r002.blend';out=P/'runtime/AtriumLanternCeiling_r002.glb';assert not native.exists()and not out.exists()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
b.update(native=str(native.relative_to(R)),native_sha256=sha(native),runtime=str(out.relative_to(G)),runtime_sha256=sha(out),predecessor_native_sha256=parent,parts=records,minimum_added_clearance_before=min(before)-102,minimum_added_clearance_after=min(after)-102,protected_cap_changed=False)
(P/'evidence/CEILING_BUILD.json').write_text(json.dumps(b,indent=2)+'\n');print('CEILING_CLEARANCE',min(before)-102,min(after)-102)
