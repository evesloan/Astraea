"""Pinned, bounded D17 adoption. Default is dry-run; existing systems stay intact."""
import argparse
import hashlib
import json
from pathlib import Path
from plan_d17_connected_platform import plan, digest

ROOT = Path(__file__).resolve().parents[1]
BASE_LAYOUT = '57e92da7a449ba51af977cf51267fab2f20360e1aea6c24c34b9b277efa9257b'
OLD_COM = 'd2ebe0a3a980cb283a4dc8909d07609d112dcbca196d3edbbf7bf47f1fcc9125'
PINS = {
    'source/AST-RES-006.blend': '9af75155605ca3c8b0f17cd31c1f7455f1afb54579772d11d9fcae13685d7224',
    'exports/AST-RES-006.glb': '5375179c3d89b92a4f950b7fad0a0936aafdeca37797aa388264f9bdf6d8e664',
    'exports/AST-COM-003_aft_only.glb': '6b559b69c13d0ea2e5cb16e42791aec6af495c377fcfbf074ebfb36f7e57ff18',
    'source/connected_contract.json': '672c57eec7f06d886b6a0ce4975fa7400a8742c7490751decee4425f096dabac',
    'qa/source_export_verification.json': '688203e10a4604e7c5e4631c422dc901f6fec79c67b0cab3d0d33babafcf08e1',
    'qa/portal_return_verification.json': 'bf446aed5d47fc55db9a7495f7bfb81b60e853e0a06667fdd688c943acff7f14',
}


def prepare(catalogue):
    rows = json.loads((catalogue / 'catalogue_manifest.json').read_text())['assets']
    matches = [r for r in rows if r['catalogue_id'] == 'AST-RES-006']
    assert len(matches) == 1 and matches[0]['family'] == 'd17_connected_royalty'
    family = catalogue / 'assets/d17_connected_royalty'
    for name, expected in PINS.items():
        assert hashlib.sha256((family / name).read_bytes()).hexdigest() == expected, name
    qa = json.loads((family / 'qa/source_export_verification.json').read_text())
    guard = json.loads((family / 'qa/portal_return_verification.json').read_text())
    assert qa['pass'] and guard['pass'] and guard['actual_closed_mesh_side_rays'] == 120
    assert qa['exported_walkable_floor_meshes'] == 0
    contract = json.loads((family / 'source/connected_contract.json').read_text())
    assert len(contract['units_preserved']) == 16 and len(contract['fixtures']) == 9
    layout = json.loads((ROOT / 'data/spatial_layout.json').read_text())
    datums = json.loads((ROOT / 'data/design_contract.json').read_text())['deck_datums']
    candidate, report = plan(layout, contract, {r['deck_id']: r['floor_elevation_m'] for r in datums}, BASE_LAYOUT)
    assert abs(report['new_floor_m2'] - 605.2) < 1e-7
    assert report['original_region_count'] == 255 and report['added_region_count'] == 1
    contract['runtime_status'] = 'Installed candidate; physical route, visual and full regression acceptance pending'
    contract['source_pins'] = PINS
    return family, candidate, contract, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    family, layout, contract, report = prepare(args.catalogue)
    if args.apply:
        # Reject unknown existing work. Retained source and published history are never reset.
        target = ROOT / 'assets/models/AST-RES-006.glb'
        runtime = ROOT / 'data/architecture/D17_CONNECTED_HOUSE_RUNTIME.json'
        assert not target.exists() and not runtime.exists(), 'Review an existing adoption instead of overwriting it'
        old = ROOT / 'assets/models/AST-COM-003.glb'
        assert hashlib.sha256(old.read_bytes()).hexdigest() == OLD_COM
        before = json.loads((ROOT / 'data/generated/structural_meshes.json').read_text())
        baseline = {'count': len(before['regions']), 'record_sha256': {row['id']: digest(row) for row in before['regions']}, 'scope': 'Exact canonical record hashes; complete prior data remains in retained Git history'}
        (ROOT / 'docs/D17_CONNECTED_PRE_ADOPTION_MESHES.json').write_text(json.dumps(baseline, indent=2)+'\n')
        target.write_bytes((family / 'exports/AST-RES-006.glb').read_bytes())
        old.write_bytes((family / 'exports/AST-COM-003_aft_only.glb').read_bytes())
        runtime.write_text(json.dumps(contract, indent=2)+'\n')
        (ROOT / 'data/spatial_layout.json').write_text(json.dumps(layout, indent=2)+'\n')
        report['live_adoption'] = 'Candidate files only; compiler and runtime checks still pending'
        (ROOT / 'docs/D17_CONNECTED_ADOPTION.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
