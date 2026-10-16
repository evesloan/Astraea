import bpy,json,hashlib
from pathlib import Path
R=Path('/workspace/Astraea');D=R/'BlenderCatalogue/assets/quiet_d15_staff_receiving_20261016/r004';p=json.loads((D/'PLAN.json').read_text());f=next(f for f in p['source_pins']if f.endswith('AST-STF-G3-037.blend'));assert hashlib.sha256((R/f).read_bytes()).hexdigest()==p['source_pins'][f]
bpy.ops.wm.open_mainfile(filepath=str(R/f));rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];vs=[(v.x,v.z,-v.y)for v in vs];lo=[min(v[i]for v in vs)for i in range(3)];hi=[max(v[i]for v in vs)for i in range(3)]
 if not all(lo[i]<[22.8,91.2,-483.8][i]and hi[i]>[19.6,88.501,-484.2][i]for i in range(3)):continue
 rows.append({'name':o.name,'min':[min(v[i]for v in vs)for i in range(3)],'max':[max(v[i]for v in vs)for i in range(3)]})
assert len(rows)>=1
Path('/workspace/quiet-d14-integration/LOBBY_NATIVE_INSPECTION.json').write_text(json.dumps({'source':f,'sha256':p['source_pins'][f],'selected_wall':rows},indent=2)+'\n');print(rows)
