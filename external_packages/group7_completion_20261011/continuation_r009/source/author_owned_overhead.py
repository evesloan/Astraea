"""Lift owned overhead hardware; stretch only its existing high wall ends."""
import bpy, bmesh, json, hashlib, copy, math
import numpy as np
from pathlib import Path
from mathutils import Vector

P = Path(__file__).resolve().parents[1]; C = P.parent; R = C.parents[1]
plan = json.loads((P / 'docs/OWNED_NECK_PREIMAGE.json').read_text())
native = P / 'source/natives' / plan['native_filename']; assert not native.exists()
prior = json.loads((P / 'docs/PREIMAGE_GROUP7_COMPLETION.json').read_text())
assert prior == json.loads((R / 'Game/data/architecture/GROUP7_COMPLETION.json').read_text())
expected_images = set()
for source in plan['sources']:
    path = R / source['base_native']; assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
    bpy.ops.wm.open_mainfile(filepath=str(path))
    for im in bpy.data.images:
        if im.packed_file: expected_images.add(hashlib.sha256(bytes(im.packed_file.data)).hexdigest())
bpy.ops.wm.read_factory_settings(use_empty=True)
for source in plan['materials_to_append_exact']:
    with bpy.data.libraries.load(str(R / source['base_native']), link=False) as (available, selected):
        assert set(source['names']) <= set(available.materials)
        selected.materials = source['names']

def signature(ob):
    h = hashlib.sha256(); h.update(np.array(ob.matrix_world).tobytes()); h.update(ob.type.encode())
    h.update(np.array([v.co[:] for v in ob.data.vertices], dtype='<f4').tobytes())
    h.update(json.dumps([list(f.vertices) for f in ob.data.polygons]).encode())
    for uv in ob.data.uv_layers: h.update(np.array([q.uv[:] for q in uv.data], dtype='<f4').tobytes())
    h.update(json.dumps([m.name if m else None for m in ob.data.materials]).encode())
    return h.hexdigest()

changed = []; unchanged = {}; all_parts = []
for old in plan['parts']:
    row = copy.deepcopy(old); name = row['name']; points = row['vertices_world_xyz']
    if 'NeckLandingFoot_' in name:
        function = 'UNCHANGED_RETAINED_OWNED_LANDING_FOOT'
    elif '_RaisedNeck_' in name or '_RaisedEnd_' in name:
        assert min(v[1] for v in points) == 106.5 and max(v[1] for v in points) == 110.5
        for point in points:
            if point[1] > 110.49: point[1] += .4
        function = 'OWNED_WALL_TOP_EXTENDED_FOOT_FIXED'
    elif 'NeckLandingJamb_' in name:
        assert min(v[1] for v in points) == 106.5
        for point in points:
            if point[1] > 110.29: point[1] += .4
        function = 'OWNED_JAMB_HEAD_EXTENDED_FOOT_FIXED'
    else:
        assert min(v[1] for v in points) >= 110.099, name
        for point in points: point[1] += .4
        function = 'OWNED_OVERHEAD_TRANSLATED_0_4M'
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x, -z, y) for x, y, z in points], [], row['faces']); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges) and bm.calc_volume() > 1e-9, name
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    for material in row['material_names']: me.materials.append(bpy.data.materials[material])
    if function.startswith('UNCHANGED'):
        for old_uv in row['uv_layers']:
            uv = me.uv_layers.new(name=old_uv['name'])
            for entry, coordinate in zip(uv.data, old_uv['coordinates']): entry.uv = coordinate
        assert signature(ob) == old['original_signature'], name
        unchanged[name] = old['original_signature']
    else:
        uv = me.uv_layers.new(name='MetreScaled')
        for face in me.polygons:
            n = face.normal; u = Vector((0, 1, 0)) if abs(n.x) > .8 else Vector((1, 0, 0)); w = n.cross(u)
            for k in face.loop_indices:
                q = me.vertices[me.loops[k].vertex_index].co; uv.data[k].uv = (q.dot(u), q.dot(w))
        changed.append(row)
    for k, value in old['properties'].items(): ob[k] = value
    ob['group7_cell'] = row['cell']; ob['contact_category'] = row['category']; ob['interface_function'] = function
    ob['engineering_capacity_accepted'] = False; row['function'] = function
    all_parts.append(row)
lights = []
for old in prior['lights']:
    if old['id'] not in ['G7C3_Fore_Lamp_0', 'G7C3_Fore_Lamp_1', 'G7C3_Aft_Lamp_0', 'G7C3_Aft_Lamp_1']: continue
    row = copy.deepcopy(old); row['position'][1] += .4
    data = bpy.data.lights.new(row['id'], 'SPOT'); data.energy = 220; data.color = row['color']
    data.spot_size = math.radians(row['angle']*2); data.use_custom_distance = True; data.cutoff_distance = row['range']
    ob = bpy.data.objects.new(row['id'], data); bpy.context.collection.objects.link(ob)
    ob.location = (row['position'][0], -row['position'][2], row['position'][1]); ob['fixture_source'] = row['source_hardware']
    lights.append({'previous': old, 'successor': row})
assert len(lights) == 4 and len(unchanged) == 4
for image in bpy.data.images:
    if image.name in ['Render Result', 'Viewer Node']: continue
    assert image.packed_file and hashlib.sha256(bytes(image.packed_file.data)).hexdigest() in expected_images
bpy.context.scene.unit_settings.system = 'METRIC'; bpy.context.scene.unit_settings.scale_length = 1
bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
for source in plan['sources']: assert hashlib.sha256((R / source['base_native']).read_bytes()).hexdigest() == source['sha256']
report = {'status': 'SOURCE_AUTHORED_TWO_IMMUTABLE_NATIVES_UNCHANGED',
          'native': native.relative_to(P).as_posix(), 'native_sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
          'immutable_sources': plan['sources'], 'original_object_signatures': unchanged,
          'corrected_owned_parts': changed, 'added_parts': [], 'all_parts': all_parts,
          'export_cells': plan['export_cells'], 'original_packed_image_hashes': sorted(expected_images),
          'source_position_successors': lights, 'fixed_wall_foot_y': 106.5,
          'additional_air_height_m': 4.0, 'original_source_or_roof_changed': False,
          'primary_capacity_or_whole_group_accepted': False}
(P / 'docs/AUTHORED_D18_SUCCESSOR.json').write_text(json.dumps(report, separators=(',', ':'))+'\n')
print('G7_R009_SOURCE', len(changed), 'owned overhead/wall revisions', len(unchanged), 'feet exact', report['native_sha256'])
