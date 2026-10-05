"""Conservative full-height footprint guard; not structural or route acceptance."""
import argparse
import hashlib
import json
from pathlib import Path

FAMILY = Path(__file__).resolve().parents[1]
FILES = {
    'guest': 'data/reference/historical_guest_census.json',
    'crew': 'data/reference/D03_crew_envelopes.json',
    'retail': 'data/reference/historical_atlas_allocations.json',
    'programme': 'data/programme_ledger.json',
}


def overlaps(a, b):
    return all(min(a[k][1], b[k][1]) > max(a[k][0], b[k][0]) for k in ('x', 'z'))


def footprint(spec):
    x, z = spec['centre_xz']
    w, d = spec['size_xz']
    assert w > 0 and d > 0
    return {'x': [x-w/2, x+w/2], 'z': [z-d/2, z+d/2]}


def run(root):
    raw = {k: json.loads((root / p).read_text()) for k, p in FILES.items()}
    groups = {
        'guest': raw['guest']['guest_envelopes'],
        'crew': raw['crew']['records'],
        'retail': [r for r in raw['retail'] if r['kind'] == 'unlabelled_shop_allocation'],
        'programme': [dict(r['historical_envelope'], programme_key=r['programme_key'])
                      for r in raw['programme']['destinations']],
    }
    assert {k: len(v) for k, v in groups.items()} == {'guest': 1000, 'crew': 200, 'retail': 100, 'programme': 161}

    def hits(spec):
        rect = footprint(spec)
        return {k: [{'source_index': i, 'drawing_index': r.get('drawing_index'),
                     'programme_key': r.get('programme_key')}
                    for i, r in enumerate(rows) if overlaps(rect, r)]
                for k, rows in groups.items()}

    # A guest-only check previously missed these lower crew-bank conflicts.
    rejected = []
    for z, drawing in [(-71.4, 414), (-48.6, 418), (50.4, 420), (71.6, 424)]:
        result = hits({'centre_xz': [100, z], 'size_xz': [.8, 1.2]})
        assert any(r['drawing_index'] == drawing for r in result['crew']), (z, drawing)
        rejected.append({'centre_xz': [100, z], 'required_crew_drawing': drawing, 'detected': True})
    assert not overlaps({'x': [0, 1], 'z': [0, 1]}, {'x': [1, 2], 'z': [0, 1]})
    assert overlaps({'x': [0, 1.01], 'z': [0, 1]}, {'x': [1, 2], 'z': [0, 1]})

    contract_path = FAMILY / 'source/section_contract.json'
    contract = json.loads(contract_path.read_text())
    specs = list(contract['footing_specs'])
    for key in ['royalty_frame_candidate', 'transverse_frame_candidate', 'aft_cross_frame_candidate']:
        if not contract.get(key):
            continue
        b = contract[key]['bounds']
        specs.append({'centre_xz': [(b['x'][0]+b['x'][1])/2, (b['z'][0]+b['z'][1])/2],
                      'size_xz': [b['x'][1]-b['x'][0], b['z'][1]-b['z'][0]]})
    specs.extend(contract.get('outer_frame_candidate', {}).get('strips', []))
    rows = [{'centre_xz': s['centre_xz'], 'bounds': footprint(s), 'hits': hits(s)} for s in specs]
    passed = all(not matches for row in rows for matches in row['hits'].values())
    report = {'pass': passed,
              'scope': 'Conservative full-height support footprint allocation screen. No mesh, loading, circulation or runtime acceptance.',
              'allocation_counts': {k: len(v) for k, v in groups.items()},
              'rows': rows, 'rejected_crew_regressions': rejected,
              'source_sha256': {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in FILES.values()},
              'contract_sha256': hashlib.sha256(contract_path.read_bytes()).hexdigest()}
    (FAMILY / 'qa/allocation_footprint_regression.json').write_text(json.dumps(report, indent=2)+'\n')
    assert passed, 'Candidate footprint overlaps protected allocation; inspect receipt'
    print(json.dumps({'pass': passed, 'candidate_footprints': len(rows), 'crew_regressions': len(rejected)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('godot_root', type=Path)
    run(parser.parse_args().godot_root)
