from pathlib import Path
import bpy,json,hashlib
from mathutils import Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'EXACT_RETAINED_SOURCE_RECOVERY.json'));assert hashlib.sha256(Path(p['native']).read_bytes()).hexdigest()==p['native_sha256']
bpy.ops.wm.open_mainfile(filepath=p['native']);dg=bpy.context.evaluated_depsgraph_get();root=Matrix.Translation((-28,446,21));rows=[]
for ob in bpy.context.scene.objects:
 if ob.type not in ['MESH','FONT','CURVE']:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();vs=[root@ev.matrix_world@v.co for v in me.vertices];points=[(q.x,q.z,-q.y)for q in vs]
 if points:rows.append({'name':ob.name,'world_aabb':[min(v[0]for v in points),max(v[0]for v in points),min(v[1]for v in points),max(v[1]for v in points),min(v[2]for v in points),max(v[2]for v in points)],'vertices':len(points),'faces':len(me.polygons)})
 ev.to_mesh_clear()
(W/'ACTUAL_MEDICAL_NATIVE_BOUNDS.json').write_text(json.dumps(rows,indent=2)+'\n');print('ACTUAL MEDICAL SOURCE SURVEY',len(rows))
for row in rows:
 if row['name'].startswith('TRIAGE_01')and any(s in row['name']for s in ['privacy_leaf','leaf_left','portal_left','portal_right','front_service']):print(row)
