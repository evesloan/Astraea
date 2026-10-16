import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/Astraea');p=R/'BlenderCatalogue/assets/quiet_lift_receiving_20261009/source/architecture_lift_fit.blend';assert hashlib.sha256(p.read_bytes()).hexdigest()=='e5cdba761acf8a80c2844cc566f9d014cfb36571ea42f75ece8b5a44b48bf26b'
bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];vs=[(v.x,v.z,-v.y) for v in vs];lo=[min(v[i]for v in vs)for i in range(3)];hi=[max(v[i]for v in vs)for i in range(3)]
 if all(lo[i]<[46.2,101.0,-478][i] and hi[i]>[18.6,97.2,-484.1][i] for i in range(3)):rows.append({'name':o.name,'min':lo,'max':hi})
Path('/workspace/quiet-d16-integration/NATIVE_INTERFACE_SURVEY.json').write_text(json.dumps({'native':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nearby':rows},indent=2)+'\n');print('NATIVE_INTERFACE',len(rows))
