from pathlib import Path
import bpy,json,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[1]
d=json.loads((P/'evidence/BOUNDED_BATCH_MEMBERSHIP.json').read_text());out=P/'source/OriginalBoundedBatches.glb';assert not out.exists()
def fingerprint(o):
 return hashlib.sha256(repr(([list(row)for row in o.matrix_world],[list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons],[m.name for m in o.data.materials],[[list(u.uv)for u in l.data]for l in o.data.uv_layers])).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/d17_connected_royalty/source/AST-RES-006.blend'))
before={n:fingerprint(bpy.data.objects[n])for n in d['unchanged_member_names']}
selected=[]
for key,names in d['membership_frozen_from_original_native'].items():
 bpy.ops.object.select_all(action='DESELECT')
 for n in names:bpy.data.objects[n].select_set(True)
 active=bpy.data.objects[names[0]];bpy.context.view_layer.objects.active=active;bpy.ops.object.join();active.name=key;selected.append(active)
bpy.ops.object.select_all(action='DESELECT')
for o in selected:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'Game/royalty_790_completion_20261020/source/ROYALTY790_upper_candidate_r002.blend'))
assert all(fingerprint(bpy.data.objects[n])==h for n,h in before.items())
(P/'evidence/UNCHANGED_MEMBERS.json').write_text(json.dumps({'verified_unchanged_members':len(before),'fingerprints':before,'original_bounded_export_sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n')
print('UNCHANGED_NATIVE_MEMBERS',len(before))
