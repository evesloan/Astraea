"""Correct only declared Group7 objects; retain immutable source revisions."""
import bpy, bmesh, json, hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
plan = json.loads((P / 'docs/THEATER_SEAM_PLAN.json').read_text())
base = R / plan['base_native']; native = P / 'source/natives' / plan['native_filename']
assert not native.exists(), 'Never overwrite a retained native'
assert hashlib.sha256(base.read_bytes()).hexdigest() == plan['base_native_sha256']
for name, want in plan['source_pins'].items():
    assert hashlib.sha256((R / name).read_bytes()).hexdigest() == want
bpy.ops.wm.open_mainfile(filepath=str(base))

def signature(ob):
    h = hashlib.sha256(); h.update(np.array(ob.matrix_world).tobytes()); h.update(ob.type.encode())
    if ob.type == 'MESH':
        h.update(np.array([q.co[:] for q in ob.data.vertices], dtype='<f4').tobytes())
        h.update(json.dumps([list(f.vertices) for f in ob.data.polygons]).encode())
        for uv in ob.data.uv_layers:
            h.update(np.array([q.uv[:] for q in uv.data], dtype='<f4').tobytes())
        h.update(json.dumps([m.name if m else None for m in ob.data.materials]).encode())
    return h.hexdigest()

original = {ob.name: signature(ob) for ob in bpy.context.scene.objects}
corrected = {q['name'] for q in plan['corrected_owned_parts']}
assert corrected <= original.keys()
preimage_signatures = {name: original[name] for name in corrected}
for row in plan['corrected_owned_parts'] + plan['added_parts']:
    name = row['name']
    if name in corrected:
        old = bpy.data.objects[name]
        assert old.get('group7_cell') == row['cell']
        old_mesh = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
    else:
        assert name not in bpy.data.objects
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x, -z, y) for x, y, z in row['vertices_world_xyz']], [], row['faces']); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges) and bm.calc_volume() > 1e-9, name
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    me.materials.append(bpy.data.materials['G7C3_'+row['role']])
    uv = me.uv_layers.new(name='MetreScaled')
    for face in me.polygons:
        n = face.normal; u = Vector((0, 1, 0)) if abs(n.x) > .8 else Vector((1, 0, 0)); w = n.cross(u)
        for k in face.loop_indices:
            q = me.vertices[me.loops[k].vertex_index].co; uv.data[k].uv = (q.dot(u), q.dot(w))
    ob['group7_cell'] = row['cell']; ob['contact_category'] = row['category']
    ob['interface_function'] = row['function']; ob['engineering_capacity_accepted'] = False
    ob['original_source_edited'] = False
for name, want in original.items():
    if name not in corrected:
        assert signature(bpy.data.objects[name]) == want, name
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
assert hashlib.sha256(base.read_bytes()).hexdigest() == plan['base_native_sha256']
report = {'status': 'SOURCE_AUTHORED_UNDECLARED_OBJECTS_EXACT',
          'native': native.relative_to(P).as_posix(), 'native_sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
          'retained_base_native': plan['base_native'], 'retained_base_native_sha256': plan['base_native_sha256'],
          'original_object_signatures': {k: v for k, v in original.items() if k not in corrected},
          'declared_owned_object_preimage_signatures': preimage_signatures,
          'corrected_owned_parts': plan['corrected_owned_parts'], 'added_parts': plan['added_parts'],
          'unchanged_original_objects': len(original)-len(corrected), 'export_cells': plan['export_cells'],
          'source_originals_overwritten': False, 'primary_capacity_or_whole_group_accepted': False}
(P / 'docs/AUTHORED_THEATER_SUCCESSOR.json').write_text(json.dumps(report, separators=(',', ':'))+'\n')
print('G7_R008_SOURCE', len(corrected), 'owned corrections', len(plan['added_parts']), 'additions', report['unchanged_original_objects'], 'objects exact', report['native_sha256'])
