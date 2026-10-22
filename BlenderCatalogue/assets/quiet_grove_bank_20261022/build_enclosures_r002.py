from pathlib import Path
import bpy,json,hashlib,math,shutil
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=R/'Game/quiet_grove_bank_20261022';plan=json.loads((P/'ENCLOSURES_R002.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda a:Vector((a[0],-a[2],a[1]));records=[]
for room in plan['rooms']:
 source=W/room['source_native'];assert sha(source)==room['source_native_sha256'];target=W/room['native_successor'];export=P/'runtime'/room['runtime_delta'];assert not target.exists() and not export.exists();assert shutil.disk_usage(R).free>60*1024**2
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.ops.object.select_all(action='DESELECT');changed=[]
 for p in room['parts']:
  ob=bpy.data.objects[p['name']];delta=Matrix.Translation(B(p['target']))@Matrix.Rotation(p['yaw_delta'],4,'Z')@Matrix.Translation(-B(p['source']));ob.matrix_world=delta@ob.matrix_world;ob.select_set(True);changed.append(ob)
 bpy.context.view_layer.update()
 for p,ob in zip(room['parts'],changed):
  pts=[ob.matrix_world@v.co for v in ob.data.vertices];g=[(v.x,v.z,-v.y) for v in pts]
  assert max(abs(min(v[k] for v in g)-p['expected_min'][k]) for k in range(3))<.0001
  assert max(abs(max(v[k] for v in g)-p['expected_max'][k]) for k in range(3))<.0001
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True);bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True)
 assert sha(source)==room['source_native_sha256'];records.append(dict(index=room['index'],native=target.name,native_sha256=sha(target),delta_export=export.name,delta_sha256=sha(export),parts=len(changed),bounds_match=True));print('ENCLOSURE_SAVED',room['index'],flush=True)
(P/'evidence/ENCLOSURES_NATIVE_R002.json').write_text(json.dumps(dict(status='PASS',blender=bpy.app.version_string,rooms=records,native_saved_before_export=True),indent=2)+'\n')
