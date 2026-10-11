from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));rows=[]
for q in P['survey_inputs']:
 assert hashlib.sha256((R/q['native']).read_bytes()).hexdigest()==P['source_pins'][q['native']];bpy.ops.wm.open_mainfile(filepath=str(R/q['native']));bpy.context.view_layer.update();objects=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  vs=[o.matrix_world*v.co for v in o.data.vertices];vertices=[[v.x,v.z,-v.y]for v in vs];objects.append({'name':o.name,'bounds':[[min(v[k]for v in vertices)for k in range(3)],[max(v[k]for v in vertices)for k in range(3)]],'world_vertices':vertices,'role':o.get('role',''),'category':o.get('category','')})
 rows.append(dict(q,objects=objects))
(W/'SOURCE_NATIVE_GEOMETRY.json').write_text(json.dumps(rows,indent=2)+'\n');print('SURVEY',[(q['district'],len(q['objects']))for q in rows])
