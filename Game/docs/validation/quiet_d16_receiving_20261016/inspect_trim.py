import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/Astraea');E=Path('/workspace/quiet-d16-integration');p=json.loads((R/'BlenderCatalogue/assets/quiet_d16_staff_receiving_20261016/RECEIPT.json').read_text());part=next(r for r in p['parts']if r['name']=='Q16_Edge1_Reveal');lo,hi=part['min'],part['max'];path=R/'Game/assets/models/QUIET_GROVE_ARCHITECTURE_lift_r003.glb';bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();hit=[]
 for t in o.data.loop_triangles:
  vs=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];vs=[[v.x,v.z,-v.y]for v in vs]
  if all(min(v[i]for v in vs)<=hi[i] and max(v[i]for v in vs)>=lo[i]for i in range(3)):hit.append(vs)
 if hit:rows.append({'mesh':o.name,'materials':[m.name for m in o.data.materials],'triangles':hit})
(E/'TRIM_CONTACT.json').write_text(json.dumps({'source':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'part':part,'contacts':rows},indent=2)+'\n');print([(r['mesh'],len(r['triangles']))for r in rows])
