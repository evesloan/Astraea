"""Make additive, missing-only private floor proposals against actual triangles.

Never edit spatial_layout.json or the compiler output. The integration owner
must fit bearing/support and adopt these interfaces through the real compiler.
"""
import hashlib, json, pathlib
from shapely import constrained_delaunay_triangles
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text())

def polygons(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    return [p for part in g.geoms for p in polygons(part)]

def main():
    actual_path = ROOT / 'Game/data/generated/structural_meshes.json'
    actual = read(actual_path)
    floors = read(P / 'prior_handoff/ALL81_FLOOR_PROPOSALS.json')['units']
    levels = read(P / 'prior_handoff/PRIVATE_MULTILEVEL_FLOOR_ADDENDUM.json')['entries']
    inventory = read(P / 'prior_handoff/LUXURY_81_INVENTORY.json')
    by_index = {r['identity']['source_envelope_index']: r for r in inventory['records']}
    existing = {}
    for r in actual['regions']:
        existing.setdefault(float(r['floor_y']), []).extend(Polygon(t) for t in r['triangles'])
    existing = {y: unary_union(parts) for y, parts in existing.items()}
    rows = []
    summary = []

    def add(key, owner, y, boundary, holes=(), preview=False):
        wanted = Polygon(boundary)
        assert wanted.is_valid and wanted.area > 0
        holes_geometry = unary_union([Polygon(h) for h in holes])
        wanted = wanted.difference(holes_geometry)
        retained = existing.get(float(y), Polygon())
        missing = wanted.difference(retained)
        triangles = []
        for part in polygons(missing):
            triangles.extend([list(t.exterior.coords)[:3] for t in constrained_delaunay_triangles(part).geoms])
        area = sum(Polygon(t).area for t in triangles)
        assert abs(area - missing.area) < 1e-6
        assert missing.intersection(retained).area < 1e-7
        assert missing.intersection(holes_geometry).area < 1e-7
        for number, part in enumerate(polygons(missing)):
            rows.append({'id': f'GROUP2_{key}_{number:02d}', 'source_owner': owner,
                         'deck': 'D17' if y == 102 else 'D18', 'floor_y': y,
                         'thickness': .24, 'boundary': list(part.exterior.coords)[:-1],
                         'holes': [list(r.coords)[:-1] for r in part.interiors],
                         'triangles': [t for t in triangles if part.covers(Polygon(t))],
                         'status': 'HELD_PRIVATE_SAME_UNIT_FLOOR_INTERFACE; support/adoption required',
                         'new_unit': False, 'new_deck': False, 'priority': -1})
        summary.append({'key': key, 'source_owner': owner, 'floor_y': y,
                        'wanted_m2': wanted.area, 'already_supported_floor_m2': wanted.intersection(retained).area,
                        'missing_floor_m2': missing.area, 'holes_m2': holes_geometry.area,
                        'retained_overlap_m2': missing.intersection(retained).area})

    for floor in floors:
        index = floor['source_envelope_index']
        if index == 790:
            continue
        add(f'{index}_lower', str(index), 102.0, floor['boundary_xz'])
    for level in levels:
        index = level['source_index']
        assert index != 790
        add(f'{index}_upper', str(index), 106.5, level['effective_upper_proposal_boundary_world_xz'],
            [level['stair_void_world_xz'], level['rigid_lift_void_world_xz']])
    adjuncts = read(P / 'prior_handoff/EXCLUSIVE_FACILITIES_CROSSWALK.json')['source_proposals']
    for adjunct in adjuncts:
        add(adjunct['house'] + '_adjunct', adjunct['house'], 102.0, adjunct['source_proposal_boundary'])
    # Proposals must never duplicate one another at the same absolute elevation.
    for i, a in enumerate(rows):
        pa = Polygon(a['boundary'], a['holes'])
        for b in rows[i+1:]:
            if a['floor_y'] == b['floor_y']:
                assert pa.intersection(Polygon(b['boundary'], b['holes'])).area < 1e-7, (a['id'], b['id'])
    output = {'schema': 'astraea.group2_missing_only_private_floor_interface.v1',
              'baseline': 'affc5c807087ff87da29f3642c2d6e418241b896',
              'structural_preimage_sha256': hashlib.sha256(actual_path.read_bytes()).hexdigest(),
              'production_adoption': False, 'root_owner': True,
              '790_excluded': True, 'new_units': 0, 'new_decks': 0,
              'upper_level_policy': 'Same existing private unit at106.5; D18 is compiler datum only',
              'required_holds': ['Bearing/support and lower-room section fitting',
                                 'Upper private lift pit/slab interfaces and operating cabin',
                                 'External receiving, egress, frontage and service links',
                                 'Actual actor/body/cart routes and final game visuals'],
              'rows': rows, 'summary': summary,
              'missing_m2': sum(s['missing_floor_m2'] for s in summary),
              'retained_overlap_m2': 0.0, 'proposal_overlap_m2': 0.0}
    target = ROOT / 'Game/data/group2_completion/FLOOR_INTERFACE.json'
    target.write_text(json.dumps(output, indent=2) + '\n')
    (P / 'evidence/FLOOR_INTERFACE_VERIFICATION.json').write_text(json.dumps({
        'pass': True, 'regions': len(rows), 'owners': len(summary),
        'missing_m2': output['missing_m2'], 'retained_overlap_m2': 0,
        'proposal_overlap_m2': 0, '790_excluded': True,
        'source_sha256': output['structural_preimage_sha256'],
        'accepted_scope': 'Additive polygon/triangle fit only; unadopted support/physics/engineering'}, indent=2) + '\n')
    print('PASS missing-only interfaces', len(rows), 'regions', output['missing_m2'], 'm2')

if __name__ == '__main__':
    main()
