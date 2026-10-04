import bpy,json,pathlib
from mathutils import Vector
root=pathlib.Path(__file__).resolve().parents[1];records=[]
for fam,aid in [('garden_overlook','AST-GAR-003'),('canopy_terrace','AST-GAR-004'),('botanical_portico','AST-GAR-005'),('residential_suite','AST-SUI-001'),('guest_privacy_door','AST-DOR-001'),('guest_wash','AST-SAN-001'),('guest_wash','AST-SAN-002'),('guest_wash','AST-SAN-003'),('guest_entry_door','AST-DOR-002'),('residential_arrival','AST-ARR-001')]:
 path=root/'assets'/fam/'source'/(aid+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path));coords=[];tri=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  coords.extend(o.matrix_world@Vector(p) for p in o.bound_box);o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
 lo=[min(p[i] for p in coords) for i in range(3)];hi=[max(p[i] for p in coords) for i in range(3)]
 record={'id':aid,'source_bounds_min':lo,'source_bounds_max':hi,'source_triangles':tri,'source_reopened':True}
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(root/'assets'/fam/'exports'/(aid+'.glb')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box];elo=[min(p[i] for p in coords) for i in range(3)];ehi=[max(p[i] for p in coords) for i in range(3)]
 assert max(abs(lo[i]-elo[i]) for i in range(3))<.002;assert max(abs(hi[i]-ehi[i]) for i in range(3))<.002
 record['glb_roundtrip_bounds_match']=True;records.append(record)
(root/'garden_overlook_geometry_checks.json').write_text(json.dumps(records,indent=2)+'\n');print(records)
