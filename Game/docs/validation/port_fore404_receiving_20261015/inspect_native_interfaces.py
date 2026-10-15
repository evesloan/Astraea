from pathlib import Path
import bpy,json,hashlib
D=Path(__file__).resolve().parent;rows=[]
for r in json.loads((D/'EXACT_NATIVE_INPUTS.json').read_text()):
 p=D/'retained_source'/r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];bpy.ops.wm.open_mainfile(filepath=str(p))
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  ps=[o.matrix_world@v.co for v in o.data.vertices];ps=[(v.x,v.z,-v.y)for v in ps];lo=[min(v[i]for v in ps)for i in range(3)];hi=[max(v[i]for v in ps)for i in range(3)]
  if all(hi[i]>[-54.1,52.49,-406][i]and lo[i]<[-52,56.4,-397][i]for i in range(3)):rows.append({'file':Path(r['path']).name,'name':o.name,'bounds':[lo,hi],'materials':[m.name for m in o.data.materials if m]})
(D/'EXACT_NATIVE_NEIGHBOR_PARTS.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
