"""Bind archived fixture truth to unchanged current large-venue exports."""
from pathlib import Path
import hashlib, json, struct
import numpy as np

P = Path(__file__).resolve().parents[1]
ROOT = P.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def exported_bounds(path):
    data = path.read_bytes()
    jsize = struct.unpack_from('<I', data, 12)[0]
    gltf = json.loads(data[20:20 + jsize])
    binary = data[28 + jsize:]
    assert not any('KHR_lights_punctual' in n.get('extensions', {}) for n in gltf['nodes'])
    parents = {child: i for i, node in enumerate(gltf['nodes']) for child in node.get('children', [])}
    def matrix(i):
        node = gltf['nodes'][i]
        if 'matrix' in node:
            local = np.array(node['matrix']).reshape(4, 4).T
        else:
            local = np.eye(4)
            x, y, z, w = node.get('rotation', [0, 0, 0, 1])
            local[:3, :3] = np.array([
                [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]) @ np.diag(node.get('scale', [1, 1, 1]))
            local[:3, 3] = node.get('translation', [0, 0, 0])
        return matrix(parents[i]) @ local if i in parents else local
    found = {}
    for i, node in enumerate(gltf['nodes']):
        if 'mesh' not in node:
            continue
        vertices = []
        for primitive in gltf['meshes'][node['mesh']]['primitives']:
            a = gltf['accessors'][primitive['attributes']['POSITION']]
            v = gltf['bufferViews'][a['bufferView']]
            assert a['componentType'] == 5126 and a['type'] == 'VEC3'
            offset = v.get('byteOffset', 0) + a.get('byteOffset', 0)
            xyz = np.ndarray((a['count'], 3), dtype='<f4', buffer=binary, offset=offset,
                             strides=(v.get('byteStride', 12), 4)).astype(float)
            xyz = (matrix(i) @ np.c_[xyz, np.ones(len(xyz))].T).T[:, :3]
            vertices.append(xyz)
        xyz = np.concatenate(vertices)
        found[node['name']] = (xyz.min(axis=0), xyz.max(axis=0))
    return found

sections = json.loads((ROOT/'Game/data/architecture/received_sections.json').read_text())['sections']
recovery = json.loads((P/'qa/VENUE_SOURCE_RECOVERY.json').read_text())
recovered = {r['programme_key']: r for r in recovery['rows']}
clearance_path=P/'docs/VENUE_FIXTURE_CLEARANCE.json'
clearance={r['programme_key']:r for r in json.loads(clearance_path.read_text())['rows']} if clearance_path.exists() else {}
rows = []
checks = []
mechanical_contacts = []
for key in ['D09_directory_02', 'D09_directory_03', 'D09_directory_07', 'D09_directory_09', 'D09_directory_10']:
    section = next(r for r in sections if r['programme_key'] == key)
    archive = P/'source/retained_venue_recovery'/key
    metadata_path = next(archive.rglob('build_metadata.json'))
    objects_path = next(archive.rglob('objects.json'))
    metadata = json.loads(metadata_path.read_text())
    objects = {o['name']: o for o in json.loads(objects_path.read_text())}
    model_path = ROOT/'Game/assets/models'/section['model_file']
    assert recovered[key]['archived_export_matches_current_runtime']
    assert sha(model_path) == section['source_sha256'] == recovered[key]['current_runtime_sha256']
    geometry = exported_bounds(model_path)
    revised=clearance.get(key)
    revised_geometry=exported_bounds(ROOT/revised['export']) if revised else {}
    drops={r['fixture']:r['drop_m'] for r in revised['fixtures']} if revised else {}
    if revised:
        for changed in revised['fixtures']:
            name=changed['fixture']
            rod_lo,rod_hi=revised_geometry[name+'_suspension']
            housing_lo,housing_hi=revised_geometry[name+'_housing']
            original_rod_lo,original_rod_hi=geometry[name+'_suspension']
            beam_lo,_=geometry[changed['beam']]
            top_error=float(abs(rod_hi[1]-original_rod_hi[1]))
            bearing=float(housing_hi[1]-rod_lo[1])
            gap=float(beam_lo[1]-housing_hi[1])
            # Native bounds conservatively enclose beveled beam corners. Actual
            # exported corners can increase the gap; retain the minimum30mm rule.
            assert top_error<.00003 and bearing>.0399 and gap>.0299
            assert max(np.abs(rod_lo[[0,2]]-original_rod_lo[[0,2]]).max(),np.abs(rod_hi[[0,2]]-original_rod_hi[[0,2]]).max())<.00003
            mechanical_contacts.append({'programme_key':key,'fixture':name,'unchanged_exported_ceiling_contact_top_error_m':top_error,
                'rod_housing_positive_overlap_m':bearing,'actual_exported_beam_aabb_clearance_m':gap,
                'original_horizontal_footprint_unchanged':True,'passed':True})
    lights = []
    sign = metadata['section']['sign']
    for authored in metadata['lights']:
        name = authored['name']
        lens_name = name + '_lens'
        assert lens_name in geometry and lens_name in objects
        lo, hi = revised_geometry[lens_name] if name in drops else geometry[lens_name]
        b = objects[lens_name]['bounds_blender']
        expected_lo = np.array([b[0][0], b[2][0], -b[1][1]])
        expected_hi = np.array([b[0][1], b[2][1], -b[1][0]])
        if name in drops:
            expected_lo[1]-=drops[name]
            expected_hi[1]-=drops[name]
        bound_error = float(max(np.abs(lo-expected_lo).max(), np.abs(hi-expected_hi).max()))
        assert bound_error < .00003, (key, name, bound_error)
        u, h, v = authored['pos']
        point = np.array([sign*u, h, v], dtype=float)
        archived_point=point.copy()
        if name in drops:point[1]-=drops[name]
        gap = float(np.linalg.norm(point-np.minimum(hi, np.maximum(lo, point))))
        assert .005 < gap < .08 and lo[1] > point[1], (key, name, gap)
        close = ('lamp' in name.lower())
        task = name.startswith('Sort_') or name.startswith('Browse_')
        energy, reach = ((.9, 6.0) if task else (.85, 5.5) if close else (1.3, 14.0))
        native = P/recovered[key]['native']['recovered_path']
        lights.append({'name': name, 'lens_mesh': lens_name, 'local_xyz': point.tolist(),
                       'lens_bounds': [lo.tolist(), hi.tolist()], 'physical_lens_gap_m': gap,
                       'color': authored['color'], 'energy': energy, 'range_m': reach,
                       'shadow_mode': 'supported_cubemap', 'calibration': 'first_pass_unaccepted',
                       'archived_blender_power': authored['power'], 'blender_power_is_godot_energy': False})
        lights[-1]['original_archived_local_xyz']=archived_point.tolist()
        lights[-1]['fixture_drop_m']=drops.get(name,0)
        checks.append({'programme_key': key, 'fixture': name, 'actual_export_bound_error_m': bound_error,
                       'below_original_lens_gap_m': gap, 'passed': True})
    rows.append({'programme_key': key, 'name': section['name'], 'model_path': 'res://assets/models/'+section['model_file'],
                 'model_sha256': sha(model_path), 'translation_xyz': section['translation_xyz'], 'rotation_y': section['rotation_y'],
                 'native': str(native.relative_to(ROOT)), 'native_sha256': sha(native),
                 'archived_metadata': str(metadata_path.relative_to(ROOT)), 'metadata_sha256': sha(metadata_path),
                 'source_archive_sha256': recovered[key]['archive_sha256'], 'fixtures': lights})
    if revised:
        rows[-1]['fixture_clearance']={'model_path':revised['runtime_model_path'],'model_sha256':revised['export_sha256'],
            'native':revised['native'],'native_sha256':revised['native_sha256'],
            'replaced_mesh_names':[r['fixture']+suffix for r in revised['fixtures'] for suffix in ['_suspension','_housing','_lens']]}
definition = {'schema': 'astraea.group5.large_venue_lighting.v1', 'baseline_group5_commit': 'e18919def72b86eaa202932f76009f037e835a76',
              'venues': rows, 'venue_count': len(rows), 'fixture_count': sum(len(r['fixtures']) for r in rows),
              'global_budget': {'shadow_sources': 8, 'visibility_candidates': 32},
              'scope': 'First-pass lighting in five exact-source venues:97 original fixtures plus12 explicitly derived below-rib fixtures with extended original suspension rods;no floor,capacity,room ID,ambient or original export/native changes.',
              'whole_group_accepted': False, 'pixel_lighting_and_hardware_accepted': False}
assert definition['fixture_count'] == 109
(ROOT/'Game/data/architecture/group5/LARGE_VENUE_LIGHTING.json').write_text(json.dumps(definition, indent=2)+'\n')
(P/'qa/LARGE_VENUE_SOURCE_LIGHTING.json').write_text(json.dumps({'status': 'PASS', 'checks': len(checks), 'proof': checks,
    'derived_fixture_mechanical_contact_checks':len(mechanical_contacts),'mechanical_contact_proof':mechanical_contacts,
    'original_export_light_nodes': 0, 'exact_archived_current_models': 5, 'originals_unchanged': True,
    'source_derived_below_rib_fixtures':sum(len(r['fixtures']) for r in clearance.values()),
    'accepted_scope': 'Literal fixture ownership,source identity and emitter-to-lens geometry only;not pixel-lighting,energy calibration,performance or full-venue acceptance.'}, indent=2)+'\n')
print('GROUP5_LARGE_VENUE_SOURCE_LIGHTING', len(rows), definition['fixture_count'], 'PASS')
