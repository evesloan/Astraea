import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/Astraea');path=R/'Game/assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb';bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));o=bpy.data.objects['QG_Batch_14'];o.data.calc_loop_triangles();lo=[19.38,89.55,-482.36];hi=[42.2,89.62,-482.2];rows=[]
for t in o.data.loop_triangles:
 vs=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];vs=[[v.x,v.z,-v.y]for v in vs]
 if all(min(v[i]for v in vs)<hi[i] and max(v[i]for v in vs)>lo[i]for i in range(3)):rows.append(vs)
vs=[o.matrix_world@v.co for v in o.data.vertices];vs=[[v.x,v.z,-v.y]for v in vs];out={'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mesh':o.name,'materials':[m.name for m in o.data.materials],'mesh_bounds':[[min(v[i]for v in vs)for i in range(3)],[max(v[i]for v in vs)for i in range(3)]],'candidate_box':[lo,hi],'overlap_triangles':rows};(Path('/workspace/quiet-d14-integration/TRIM_CONTACT.json')).write_text(json.dumps(out,indent=2)+'\n');print(out)
