import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path('/workspace/scratch/375c2e438292/laundry_receiving_20261008');src=r/'incoming/WP08_housekeeping_laundry.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='e84c36b516e24be2f78a627dcd764c6aed1822a77cbb91b2d4d7c775a0ce4072'
objects=list(bpy.data.objects);images=[i for i in bpy.data.images if i.users>0];fonts=[o.name for o in objects if o.type=='FONT'];preview=[o.name for o in objects if 'PREVIEW' in o.name.upper()]
mesh=[o for o in objects if o.type=='MESH' and o.name not in preview];bounds=[]
for o in mesh:
 for c in o.bound_box:
  v=o.matrix_world@Vector(c);bounds.append([v.x,v.z,-v.y])
lo=[min(v[a]for v in bounds)for a in range(3)];hi=[max(v[a]for v in bounds)for a in range(3)]
report={'scope':'Read-only native inspection; no rebuild/save or runtime acceptance','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'mesh_objects_excluding_preview':len(mesh),'world_bounds':[lo,hi],'authored_fonts':fonts,'preview_objects':preview,'used_images':len(images),'unpacked_file_images':[i.name for i in images if i.source=='FILE' and not i.packed_file],'lights':len([o for o in objects if o.type=='LIGHT'])}
(r/'NATIVE_INTAKE.json').write_text(json.dumps(report,indent=2)+'\n');print('LAUNDRY_NATIVE_INTAKE',json.dumps(report))
