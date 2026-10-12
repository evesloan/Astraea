from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;r=json.load(open(W/'EXACT_RETAINED_DINING_FIXTURE_RECOVERY.json'));output=[]
for row in r['families']:
 f=Path(row['native']);assert hashlib.sha256(f.read_bytes()).hexdigest()==row['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(f));dg=bpy.context.evaluated_depsgraph_get();meshes=[]
 for ob in bpy.context.scene.objects:
  if ob.type not in['MESH','FONT','CURVE']:continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];points=[(q.x,q.z,-q.y)for q in v]
  if points:meshes.append({'name':ob.name,'world_aabb':[min(q[0]for q in points),max(q[0]for q in points),min(q[1]for q in points),max(q[1]for q in points),min(q[2]for q in points),max(q[2]for q in points)]})
  ev.to_mesh_clear()
 output.append({'programme_key':row['programme_key'],'native_sha256':row['native_sha256'],'source_meshes':meshes});print(row['programme_key'],len(meshes),'exact native bounds',flush=True)
(W/'ACTUAL_DINING_FIXTURE_BOUNDS.json').write_text(json.dumps(output,indent=2)+'\n')
