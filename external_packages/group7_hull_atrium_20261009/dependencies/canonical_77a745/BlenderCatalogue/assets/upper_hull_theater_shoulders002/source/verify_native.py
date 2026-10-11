from pathlib import Path
import bpy,bmesh,json,hashlib,math
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'source/AST-HUL-002.blend'))
mesh=[o for o in bpy.data.objects if o.type=='MESH'];assert len(mesh)==74
for o in mesh:
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>0;bm.free();assert len(o.data.uv_layers)==1
 for loop in o.data.uv_layers.active.data:assert all(math.isfinite(x)for x in loop.uv)
 for v in o.data.vertices:
  p=o.matrix_world@v.co;x,y,z=p.x,p.z,-p.y
  assert -120.001<x<-109.19 and 60.999<y<92.001 and -275.001<z<-104.999
images=[i for i in bpy.data.images if i.type=='IMAGE'];assert len(images)==2 and all(i.packed_file for i in images)
out={'saved_native_reload':True,'closed_positive_meshes':len(mesh),'packed_images':len(images),'bounds_and_uvs_passed':True,'native_sha256':hashlib.sha256((R/'source/AST-HUL-002.blend').read_bytes()).hexdigest()};(R/'NATIVE_RELOAD_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
