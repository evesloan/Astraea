from pathlib import Path
import bpy,json,hashlib,math,struct,shutil
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=R/'Game/sunset_specialty_bank_20261022';plan=json.loads((W/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
def topology():
 h=hashlib.sha256()
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  if o.type!='MESH':continue
  h.update(o.name.encode())
  for v in o.data.vertices:h.update(struct.pack('<fff',*v.co))
  for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
for row in plan['rooms']:
 assert shutil.disk_usage(R).free>700*1024**2,'Preserve700MiB durable reserve'
 src=R/row['source_native'];assert sha(src)==row['source_native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(src));before=topology();dz=row['placement']['translation'][2];transform=Matrix.Translation(Vector((0,-dz,0)))@Matrix.Rotation(math.pi,4,'Z')
 roots=[o for o in bpy.data.objects if o.parent is None]
 for o in roots:o.matrix_world=transform@o.matrix_world
 for o in bpy.data.objects:
  if 'reserved_rest_slot_id'in o:o['reserved_rest_slot_id']=str(o['reserved_rest_slot_id']).replace(row['source_room_identity'],row['allocation']['proposed_runtime_id'])
 bpy.context.scene['sunset_allocation']=row['allocation']['source_envelope_index'];bpy.context.scene['receiving_verified']=False;bpy.context.scene['visual_accepted']=False
 assert topology()==before
 out=W/f"SunsetSpecialty_{row['allocation']['source_envelope_index']}_r001.blend";assert not out.exists();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
 records.append({'allocation':row['allocation']['source_envelope_index'],'native':str(out.relative_to(R)),'sha256':sha(out),'source_sha256':sha(src),'unchanged_local_mesh_topology_sha256':before,'rigid_transform':row['placement'],'objects':len(bpy.data.objects)});print('SUNSET_NATIVE',row['allocation']['source_envelope_index'],flush=True)
(P/'evidence/NATIVE.json').write_text(json.dumps({'status':'PASS','rooms':records,'main_integrated':False,'source_pins_unchanged':all(sha(R/p)==v for p,v in plan['pins'].items())},indent=2)+'\n')
