"""Scope a corrected owned foot and finite weatherline over the retained shoulder.

Neither the original theatre skin nor its room/floor/capacity source is changed.
The skin-cap contact is weather construction, not an accepted primary bearing.
"""
from pathlib import Path
import json, hashlib, copy
import numpy as np

P = Path(__file__).resolve().parents[1]
C = P.parent
R = C.parents[1]
for directory in ['docs', 'qa', 'exports', 'source/natives']:
    (P / directory).mkdir(parents=True, exist_ok=True)
base = C / 'continuation_r005/source/natives/G7_BodyEnclosure_r005b.blend'
assert hashlib.sha256(base.read_bytes()).hexdigest() == 'c44d92f922628ad6b88e6c678d2dbbd7aa1fc2f18c8adef4f3248495b3a5fee0'
eligibility = json.loads((P / 'docs/THEATER_OWN_FOOT_CORRECTION_ELIGIBILITY.json').read_text())
assert not eligibility['actual_source_aabb_overlap_candidates']
assert not eligibility['historical_guest_reservation_overlap_candidates']
group8 = json.loads((P / 'qa/group8_readonly/Game_docs_group8/THEATER_RECEIVING_CONTRACT.json').read_text())
pins = {name: row['sha256'] for name, row in group8['source_pins'].items()
        if name != 'Game/scripts/ship.gd'}
pins['Game/assets/models/AST-HUL-002.glb'] = hashlib.sha256((R / 'Game/assets/models/AST-HUL-002.glb').read_bytes()).hexdigest()
for name, want in pins.items():
    assert hashlib.sha256((R / name).read_bytes()).hexdigest() == want, name
panels = [q for q in json.loads((C / 'docs/PLAN.json').read_text())['panels']
          if q['side'] == -1 and q['y'] == [93, 97.5]
          and q['z'][0] >= -275 and q['z'][1] <= -105]
assert len(panels) == 31 and sum(q['z'][1] - q['z'][0] for q in panels) == 170
faces = [[2, 1, 0], [3, 4, 5], [0, 1, 4, 3], [1, 2, 5, 4], [2, 0, 3, 5]]
box_faces = [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]

def field(q, u0, u1, v0, v1):
    q = np.array(q, dtype=float)
    def at(u, v):
        return ((q[0] * (1-u) + q[1] * u) * (1-v)
                + (q[3] * (1-u) + q[2] * u) * v).tolist()
    return [at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)]

def facets(name, q, a, b, role, category, cell, function):
    result = []
    for suffix, indices in [('a', [0, 1, 2]), ('b', [0, 2, 3])]:
        t = np.array(q)[indices]
        n = np.cross(t[1]-t[0], t[2]-t[0]); n /= np.linalg.norm(n)
        if n.dot([-t[:, 0].mean(), 0, -t[:, 2].mean()]) < 0:
            n = -n
        h = n * [1, 0, 1]
        delta = h / h.dot(h)
        result.append({'name': name+'_'+suffix, 'cell': cell, 'role': role,
                       'category': category, 'vertices_world_xyz': np.concatenate([t+delta*a, t+delta*b]).tolist(),
                       'faces': faces, 'inward_normal': n.tolist(),
                       'normal_interval_m': [a, b], 'function': function})
    return result

corrections = []; additions = []; panel_rows = []
for old in panels:
    panel = copy.deepcopy(old)
    for point in panel['quad'][:2]:
        point[0] = -109.2
    cell = 'Body_-1_' + str(int((old['z'][0]+510)//120)).zfill(2)
    dy = .18 / 4.5
    if panel['quad'] != old['quad']:
        for suffix, sub, role in [('Sill', field(panel['quad'], 0, 1, 0, dy), 'shell'),
                                  ('Pier', field(panel['quad'], 0, .03, dy, 1), 'metal'),
                                  ('Glass', field(panel['quad'], .03, 1, dy, 1), 'glass')]:
            corrections += facets(old['id']+'_'+suffix, sub, 0, .18, role, 'solid_skin', cell, 'OWNED_CANONICAL_FOOT_CORRECTION')
        for suffix, sub in [('Sill', field(panel['quad'], 0, 1, 0, dy)), ('Pier', field(panel['quad'], 0, .03, dy, 1))]:
            corrections += facets(old['id']+'_'+suffix+'_Receiver', sub, .18, .4, 'metal', 'solid_frame', cell, 'OWNED_CANONICAL_FOOT_CORRECTION')
    za, zb = old['z']
    q = [[-109.6, 92, za], [-109.6, 92, zb], [-109.2, 93, zb], [-109.2, 93, za]]
    name = 'G7C8_TheaterWeather_' + old['id'].rsplit('_', 1)[1]
    for suffix, sub, role in [('Sill', field(q, 0, 1, 0, .18), 'metal'),
                              ('Pier', field(q, 0, .03, .18, 1), 'metal'),
                              ('Glass', field(q, .03, 1, .18, 1), 'glass')]:
        additions += facets(name+'_'+suffix, sub, 0, .18, role, 'solid_skin', cell, 'NONPRIMARY_FINITE_WEATHERLINE')
    # The 140mm gasket lies inside the exact original cap even at both narrow ends.
    # It contacts the original source deliberately; no structural rating is assigned.
    poly = [(-109.58, za), (-109.44, za), (-109.44, zb), (-109.58, zb)]
    additions.append({'name': name+'_CapGasket', 'cell': cell, 'role': 'metal', 'category': 'solid_skin',
                      'vertices_world_xyz': [[x, y, z] for y in [91.99, 92.03] for x, z in poly],
                      'faces': box_faces, 'function': 'NONPRIMARY_RETAINED_CAP_WEATHER_CONTACT',
                      'permitted_original_contact_node': 'HUL2_FullShoulderSkin'})
    panel_rows.append({'id': old['id'], 'cell': cell, 'previous_quad': old['quad'],
                       'successor_quad': panel['quad'], 'weather_quad': q, 'z': old['z'],
                       'owned_foot_changed': panel['quad'] != old['quad']})
assert len(corrections) == 270 and len(additions) == 217
for row in corrections + additions:
    assert min(v[0] for v in row['vertices_world_xyz']) >= -109.601
    assert max(v[0] for v in row['vertices_world_xyz']) < -106.9
plan = {'schema': 'astraea.group7.theater_weatherline.r008', 'status': 'OWNED_SOURCE_PLAN',
        'base_native': base.relative_to(R).as_posix(), 'base_native_sha256': hashlib.sha256(base.read_bytes()).hexdigest(),
        'native_filename': 'G7_TheaterWeatherline_r008.blend', 'source_pins': pins,
        'original_theater_skin_node': 'HUL2_FullShoulderSkin',
        'corrected_owned_parts': corrections, 'added_parts': additions, 'panels': panel_rows,
        'export_cells': ['Body_-1_01', 'Body_-1_02', 'Body_-1_03'],
        'finite_join': {'z': [-275, -105], 'y': [92, 93], 'outer_lower_x': -109.6, 'outer_upper_x': -109.2,
                        'skin_true_normal_depth_m': .18, 'length_m': 170,
                        'original_cap_gasket_x': [-109.58, -109.44], 'gasket_y': [91.99, 92.03]},
        'capacity_delta': 0, 'new_room_ids': 0, 'original_sources_changed': False,
        'protected_routes_roofs_or_floor_owners_changed': False,
        'primary_bearing_acceptance': 'HELD: weather contact on source skin cap supplies no primary load rating; frame-head graph, member seats, sections and load cases require Group1/Group8 receiver contract.',
        'criteria': 'Original 0.8m width reservation retained separately; this correction resolves own unsupported adjacent-height bulge only.',
        'group8_readonly_commit': '688a18417b6b17cfdcf527f26c8973ed4fd1142a',
        'group8_source_geometry_pins_exact': 24,
        'shared_ship_root': 'Expected source-root drift only; local ship.gd remains immutable baseline and is not edited.'}
(P / 'docs/THEATER_SEAM_PLAN.json').write_text(json.dumps(plan, indent=2)+'\n')
preimage = P / 'docs/PREIMAGE_GROUP7_COMPLETION.json'
assert not preimage.exists()
preimage.write_bytes((R / 'Game/data/architecture/GROUP7_COMPLETION.json').read_bytes())
print('G7_R008_PLAN', len(corrections), 'owned corrections', len(additions), 'finite additions', '170m join')
