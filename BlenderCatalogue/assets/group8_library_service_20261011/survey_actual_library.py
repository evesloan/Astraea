from pathlib import Path
import bpy,json,hashlib
from mathutils import Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];rec=json.load(open(W/'EXACT_RETAINED_LIBRARY_RECOVERY.json'));path=Path(rec['exact_native']);assert hashlib.sha256(path.read_bytes()).hexdigest()==rec['exact_native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(path));dg=bpy.context.evaluated_depsgraph_get();rows=[];pose=Matrix.Translation((8,466,78))
for ob in bpy.context.scene.objects:
 if ob.type not in ['MESH','FONT','CURVE'] or ob.name.startswith('PREVIEW'):continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();v=[pose@ev.matrix_world@a.co for a in me.vertices];vs=[(q.x,q.z,-q.y)for q in v]
 if vs:rows.append({'name':ob.name,'world_aabb':[min(q[0]for q in vs),max(q[0]for q in vs),min(q[1]for q in vs),max(q[1]for q in vs),min(q[2]for q in vs),max(q[2]for q in vs)],'vertices':len(vs),'faces':len(me.polygons)})
 ev.to_mesh_clear()
(W/'ACTUAL_INSTALLED_NATIVE_BOUNDS.json').write_text(json.dumps(rows,indent=2)+'\n');print('ORIGINAL LIBRARY SOURCE SURVEY',len(rows))
for row in rows:
 if row['name'].startswith(('CARE_','ARRIVAL_supported','ARRIVAL_vault','ROOT_roof')):print(row['name'],row['world_aabb'])
