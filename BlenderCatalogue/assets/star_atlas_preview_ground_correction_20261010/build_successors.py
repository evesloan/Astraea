from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PREIMAGE_SURVEY.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
for r in P['rooms']:
 original=R/r['original_native'];assert sha(original)==r['original_native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(original));remove=[o for o in bpy.data.objects if '__Preview_Ground'in o.name];assert len(remove)==len(r['preview_planes'])
 before={o.name:{'matrix_world':[list(row)for row in o.matrix_world],'vertices':len(o.data.vertices)if o.type=='MESH'else None,'polygons':len(o.data.polygons)if o.type=='MESH'else None}for o in bpy.data.objects if o not in remove}
 removed=[{'name':o.name,'runtime_collision':o.get('runtime_collision',False),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)}for o in remove]
 for o in remove:assert o.type=='MESH'and o.get('runtime_collision',False);bpy.data.objects.remove(o,do_unlink=True)
 after={o.name:{'matrix_world':[list(row)for row in o.matrix_world],'vertices':len(o.data.vertices)if o.type=='MESH'else None,'polygons':len(o.data.polygons)if o.type=='MESH'else None}for o in bpy.data.objects};assert before==after
 native=W/r['successor_native'];out=W/r['successor_runtime'];bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True);first=sha(out);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True);assert sha(out)==first and sha(original)==r['original_native_sha256'];records.append({**r,'successor_native_sha256':sha(native),'successor_runtime_sha256':sha(out),'removed_objects':removed,'retained_native_objects_unchanged':True,'fresh_native_repeat_identical':True,'mesh_count':sum(o.type=='MESH'for o in bpy.data.objects)})
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'rooms':records,'original_editable_history_unchanged':True},indent=2)+'\n')
