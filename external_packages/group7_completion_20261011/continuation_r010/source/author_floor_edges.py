"""First-pass closed guards with contained clamps; no original floor changes."""
import bpy, bmesh, json, hashlib
from pathlib import Path
from mathutils import Vector

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
plan = json.loads((P/'docs/GUARD_PLAN.json').read_text())
native = P/'source/natives'/plan['native_filename']; assert not native.exists()
for name, want in plan['source_pins'].items(): assert hashlib.sha256((R/name).read_bytes()).hexdigest() == want
material_native = R/plan['material_native']
assert hashlib.sha256(material_native.read_bytes()).hexdigest() == plan['material_native_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(material_native), link=False) as (available, selected):
    selected.materials = ['G7C3_metal', 'G7C3_glass']
for row in plan['parts']:
    name = row['name']; me = bpy.data.meshes.new(name)
    me.from_pydata([(x, -z, y) for x, y, z in row['vertices_world_xyz']], [], row['faces']); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges) and bm.calc_volume() > 1e-9, name
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    me.materials.append(bpy.data.materials['G7C3_'+row['role']]); uv = me.uv_layers.new(name='MetreScaled')
    for face in me.polygons:
        n = face.normal; u = Vector((0, 1, 0)) if abs(n.x) > .8 else Vector((1, 0, 0)); w = n.cross(u)
        for k in face.loop_indices:
            point = me.vertices[me.loops[k].vertex_index].co; uv.data[k].uv = (point.dot(u), point.dot(w))
    ob['group7_cell'] = row['cell']; ob['contact_category'] = row['category']
    ob['interface_function'] = row['function']; ob['engineering_capacity_accepted'] = False
    ob['immutable_originals_preserved'] = True
bpy.context.scene.unit_settings.system = 'METRIC'; bpy.context.scene.unit_settings.scale_length = 1
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
for name, want in plan['source_pins'].items(): assert hashlib.sha256((R/name).read_bytes()).hexdigest() == want
assert hashlib.sha256(material_native.read_bytes()).hexdigest() == plan['material_native_sha256']
report = {'status': 'SOURCE_AUTHORED_ORIGINALS_UNCHANGED', 'native': native.relative_to(P).as_posix(),
          'native_sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
          'source_pins': plan['source_pins'], 'parts': plan['parts'], 'export_cells': plan['export_cells'],
          'new_original_floor_owners_or_room_ids': 0, 'capacity_delta': 0,
          'primary_guard_or_floor_connection_capacity_accepted': False}
(P/'docs/AUTHORED_GUARDS.json').write_text(json.dumps(report, separators=(',', ':'))+'\n')
print('G7_R010_SOURCE', len(plan['parts']), 'closed parts', report['native_sha256'])
