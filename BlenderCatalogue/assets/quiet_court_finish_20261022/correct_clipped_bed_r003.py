from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=R/'Game/quiet_court_finish_20261022';fix=json.loads((P/'evidence/CLIPPED_BED_R003.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(W/'QuietGroveCourtPlanting_r002.blend'));bpy.ops.object.select_all(action='DESELECT')
for row in fix['placements']:
 o=bpy.data.objects[row['name']];p=row['after'];o.location=(p[0],-p[2],p[1]);o.scale=(row['scale'],)*3;o.select_set(True)
 for c in o.children_recursive:c.select_set(True)
bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;native=W/'QuietGroveCourtPlanting_r003.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);out=P/'runtime/QuietGroveClippedBed_r003.glb';bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(P/'evidence/NATIVE_R003.json').write_text(json.dumps(dict(native=native.name,native_sha256=sha(native),delta_export=out.name,delta_sha256=sha(out),corrected_complete_assemblies=1,predecessor_preserved=True),indent=2)+'\n');print('CLIPPED_BED_NATIVE_CORRECTED',flush=True)
