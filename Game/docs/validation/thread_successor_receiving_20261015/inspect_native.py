from pathlib import Path
import bpy,json,hashlib
D=Path(__file__).resolve().parent;p=D/'retained_source/BlenderCatalogue/assets/group5_completion_20261011/source/thread_stock/thread_stock_repair_r004.blend';bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH'or not('Ceiling'in o.name or 'fixture'in o.name):continue
 pts=[o.matrix_world@v.co for v in o.data.vertices];gd=lambda v:[v.x,v.z,-v.y];ps=[gd(v)for v in pts];lo=[min(v[i]for v in ps)+[8,52.5,-216][i]for i in range(3)];hi=[max(v[i]for v in ps)+[8,52.5,-216][i]for i in range(3)];rows.append({'name':o.name,'bounds':[lo,hi]})
(D/'NATIVE_CEILING_FIXTURE_BOUNDS.json').write_text(json.dumps(rows,indent=2)+'\n');print('READONLY_NATIVE',len(rows),hashlib.sha256(p.read_bytes()).hexdigest())
