from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;p=json.load(open(W/'EXACT_RETAINED_MEDICAL_BAY_RECOVERY.json'));native=Path(p['native']);assert hashlib.sha256(native.read_bytes()).hexdigest()==p['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(native));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in bpy.context.scene.objects:
 if ob.type not in['MESH','FONT','CURVE']:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];v=[(q.x,q.z,-q.y)for q in vs]
 if v:rows.append({'name':ob.name,'world_aabb':[min(q[0]for q in v),max(q[0]for q in v),min(q[1]for q in v),max(q[1]for q in v),min(q[2]for q in v),max(q[2]for q in v)],'triangles':sum(len(f.vertices)-2 for f in me.polygons)})
 ev.to_mesh_clear()
(W/'ACTUAL_MEDICAL_BAY_NATIVE_BOUNDS.json').write_text(json.dumps(rows,indent=2)+'\n');print('MEDICAL BAY ACTUAL SOURCE',len(rows),'bounds',flush=True)
for r in rows:
 if r['name'].startswith(('Surgery1_portal','Bed1_light','Surgery1_task')):print(r)
assert hashlib.sha256(native.read_bytes()).hexdigest()==p['native_sha256']
