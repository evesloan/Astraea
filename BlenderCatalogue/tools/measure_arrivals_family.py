from pathlib import Path
import bpy,json
from mathutils import Vector
r=Path(__file__).resolve().parents[1];records=[]
for family,aid in [('arrivals_fusion','AST-ARR-002'),('fusion_exhibit','AST-ENG-007')]:
 root=r/'assets'/family;bpy.ops.wm.open_mainfile(filepath=str(root/'source'/(aid+'.blend')));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(p)for o in meshes for p in o.bound_box];lo=[min(p[i]for p in coords)for i in range(3)];hi=[max(p[i]for p in coords)for i in range(3)];tri=0
 for o in meshes:
  assert o.data.uv_layers,'Missing UVs: '+o.name;o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 if aid=='AST-ARR-002':
  assert lo[0]>=-23.001 and hi[0]<=23.001,(lo,hi)
  assert lo[1]>=-34.001 and hi[1]<=34.001,(lo,hi)
  assert lo[2]>=-.241 and hi[2]<=11.761,(lo,hi)
 else:
  assert lo[0]>=-10 and hi[0]<=10 and lo[1]>=-3.5 and hi[1]<=3.5
  assert lo[2]+8.65>6.65 and hi[2]+8.65<=10.901,(lo,hi)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(root/'exports'/(aid+'.glb')));coords=[o.matrix_world@Vector(p)for o in bpy.context.scene.objects if o.type=='MESH'for p in o.bound_box];elo=[min(p[i]for p in coords)for i in range(3)];ehi=[max(p[i]for p in coords)for i in range(3)];assert max(abs(lo[i]-elo[i])for i in range(3))<.002 and max(abs(hi[i]-ehi[i])for i in range(3))<.002
 records.append({'id':aid,'source_bounds_min':lo,'source_bounds_max':hi,'source_triangles':tri,'source_reopened':True,'all_mesh_uvs':True,'glb_roundtrip_bounds_match':True,'scope':'Geometric envelope and UV coverage only; no engineering certification or final visual acceptance'})
(r/'arrivals_family_geometry_checks.json').write_text(json.dumps(records,indent=2)+'\n');print(records)
