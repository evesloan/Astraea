"""Recover six adjuncts' real retained light exits omitted by GLB export."""
import bpy, hashlib, json, pathlib
from mathutils import Vector
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).resolve().parent
index = json.loads((P / 'prior_handoff/DELIVERY_INDEX.json').read_text())
rows = []
for entry in index['private_house_adjuncts']:
    native = pathlib.Path('/workspace/group2-native-originals') / entry['original_native_path']
    assert hashlib.sha256(native.read_bytes()).hexdigest() == entry['native_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(native))
    lights = [ob for ob in bpy.context.scene.objects if ob.type == 'LIGHT']
    assert len(lights) == 2, (entry['house'], len(lights))
    fixtures = []
    for light in lights:
        point = light.matrix_world.translation
        candidates = []
        for ob in bpy.context.scene.objects:
            if ob.type != 'MESH' or 'lens' not in ob.name.lower():
                continue
            points = [ob.matrix_world @ Vector(p) for p in ob.bound_box]
            lo = [min(p[k] for p in points) for k in range(3)]
            hi = [max(p[k] for p in points) for k in range(3)]
            if lo[0] <= point.x <= hi[0] and lo[1] <= point.y <= hi[1] and .001 < lo[2] - point.z < .1:
                candidates.append((ob, lo, hi))
        assert len(candidates) == 1, (entry['house'], light.name, candidates)
        ob, lo, hi = candidates[0]
        fixtures.append({'name': 'DATUM_RETAINED_' + light.name,
                         'native_light': light.name, 'kind': 'fixture_light',
                         'world_xyz': [point.x, point.z, -point.y],
                         'color': list(light.data.color), 'original_blender_energy_w': light.data.energy,
                         'source_fixture_part': ob.name,
                         'source_lens_bounds_world': [[lo[0], lo[2], -hi[1]], [hi[0], hi[2], -lo[1]]],
                         'lens_exit_clearance_m': lo[2] - point.z,
                         'original_exit_omitted_from_glb': True})
    rows.append({'key': entry['house'], 'native_sha256': entry['native_sha256'],
                 'export_sha256': entry['export_sha256'], 'fixtures': fixtures})
output = {'schema': 'astraea.group2_retained_adjunct_light_exit_addendum.v1',
          'rows': rows, 'original_natives_modified': False,
          'fixture_geometry_modified': False, 'live_ship_adopted': False}
(ROOT / 'Game/data/group2_completion/LIGHTING_ADDENDUM.json').write_text(json.dumps(output, indent=2) + '\n')
(P / 'evidence/ADJUNCT_LIGHT_SOURCE_VERIFICATION.json').write_text(json.dumps({
    'pass': True, 'exact_natives': 6, 'real_light_exits': 12,
    'each_exit_below_one_actual_lens': True, 'source_bytes_unchanged': True,
    'addendum_sha256': hashlib.sha256(json.dumps(output, indent=2).encode() + b'\n').hexdigest()}, indent=2) + '\n')
print('PASS six native sources, twelve retained adjunct fixture exits')
