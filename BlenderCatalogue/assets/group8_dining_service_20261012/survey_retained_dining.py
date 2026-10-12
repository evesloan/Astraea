from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;rec=json.load(open(W/'EXACT_RETAINED_DINING_RECOVERY.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();reports=[]
for row in rec['families']:
 file=Path(row['native']);assert sha(file)==row['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(file));dg=bpy.context.evaluated_depsgraph_get();bounds=[]
 for ob in bpy.context.scene.objects:
  if ob.type not in ['MESH','FONT','CURVE']:continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];p=[(v.x,v.z,-v.y)for v in vs]
  if p:bounds.append({'name':ob.name,'world_aabb':[min(v[0]for v in p),max(v[0]for v in p),min(v[1]for v in p),max(v[1]for v in p),min(v[2]for v in p),max(v[2]for v in p)],'triangles':sum(len(f.vertices)-2 for f in me.polygons)})
  ev.to_mesh_clear()
 reports.append({'programme_key':row['programme_key'],'native_sha256':row['native_sha256'],'bounds':bounds});assert sha(file)==row['native_sha256'];print(row['programme_key'],len(bounds),'actual native source bounds',flush=True)
(W/'ACTUAL_DINING_NATIVE_BOUNDS.json').write_text(json.dumps(reports,indent=2)+'\n')
