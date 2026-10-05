"""Dry-run D17 floor ownership planning. Never writes the live layout or mesh cache."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union

OWNER = 'd17_connected_house'


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def substrate(layout):
    result = copy.deepcopy(layout)
    result['regions'] = [row for row in result['regions'] if row.get('authoring_owner') != OWNER]
    return result


def plan(layout, contract, deck_elevations, expected_substrate_sha256):
    """Union desired footprints, subtract retained owners/voids, preserve old rows."""
    base = substrate(layout)
    assert digest(base) == expected_substrate_sha256, 'Reviewed substrate changed'
    assert deck_elevations['D17'] == 102
    candidates = contract['floor_regions']
    assert candidates and len({row['id'] for row in candidates}) == len(candidates)
    desired = []
    for row in candidates:
        assert row['floor_y'] == 102 and row['thickness'] == .24
        polygon = Polygon(row['boundary'], row.get('holes', []))
        assert polygon.is_valid and polygon.area > 0, row['id']
        desired.append(polygon)
    target = unary_union(desired)

    existing = []
    coplanar_priorities = []
    for row in base['regions']:
        if abs(deck_elevations[row['deck']] + row.get('offset_y', 0) - 102) > 1e-6:
            continue
        shape = Polygon(row['boundary'], row.get('holes', []))
        for void in base['voids']:
            if row['deck'] in void['decks'] and void['id'] not in row.get('void_exemptions', []):
                shape = shape.difference(Polygon(void['boundary']))
        existing.append(shape)
        coplanar_priorities.append(row.get('priority', 0))
    assert existing, 'Expected the retained D17 ship floor'
    old_floor = unary_union(existing)
    protected = unary_union([Polygon(row['boundary']) for row in base['voids'] if 'D17' in row['decks']])
    missing = target.difference(old_floor).difference(protected)
    assert missing.is_valid and missing.area > 1e-7
    assert missing.intersection(old_floor).area < 1e-7
    assert missing.intersection(protected).area < 1e-7
    components = [missing] if missing.geom_type == 'Polygon' else list(missing.geoms)
    assert all(p.geom_type == 'Polygon' for p in components)

    result = copy.deepcopy(base)
    # Lower than every retained owner: adding a touching region cannot retriangulate it.
    priority = min(coplanar_priorities) - 1
    for index, polygon in enumerate(sorted(components, key=lambda p: (p.centroid.x, p.centroid.y))):
        result['regions'].append({
            'id': f'D17_connected_house_floor_{index:02d}',
            'authoring_owner': OWNER,
            'deck': 'D17',
            'boundary': [list(p) for p in polygon.exterior.coords[:-1]],
            'holes': [[list(p) for p in ring.coords[:-1]] for ring in polygon.interiors],
            'priority': priority,
            'thickness': .24,
            'render_cell_m': 16,
            'material_role': 'guest_floor',
            'status': 'Candidate connected residential platform; source, route and visual acceptance separate',
        })
    assert result['regions'][:len(base['regions'])] == base['regions']
    assert result['voids'] == base['voids']
    assert len({row['id'] for row in result['regions']}) == len(result['regions']), 'Compiler ID collision'
    report = {
        'planning_pass': True,
        'live_adoption': False,
        'substrate_sha256': digest(base),
        'candidate_contract_sha256': digest(contract),
        'original_region_count': len(base['regions']),
        'added_region_count': len(components),
        'gross_candidate_sum_m2': sum(p.area for p in desired),
        'candidate_union_m2': target.area,
        'candidate_overlap_removed_m2': sum(p.area for p in desired) - target.area,
        'existing_floor_overlap_m2': target.intersection(old_floor).area,
        'protected_void_overlap_m2': target.difference(old_floor).intersection(protected).area,
        'new_floor_m2': missing.area,
        'new_priority': priority,
        'old_records_exact': True,
        'scope': 'Polygon ownership only; no support, architecture, cart, capacity or runtime acceptance',
    }
    return result, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--baseline-sha256', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    layout = json.loads((root / 'data/spatial_layout.json').read_text())
    datums = json.loads((root / 'data/design_contract.json').read_text())['deck_datums']
    _, report = plan(layout, json.loads(args.contract.read_text()),
                     {row['deck_id']: row['floor_elevation_m'] for row in datums}, args.baseline_sha256)
    print(json.dumps(report, indent=2))
