"""Adopt the reviewed enclosure and bounded guard revision without changing floors."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = Path('/workspace/shared/astraea-catalogue-continuation-20261002')


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def author(enclosure_sha, platform_sha):
    manifest = json.loads((CATALOGUE / 'catalogue_manifest.json').read_text())
    for asset_id, family, expected in [('AST-CMD-003', 'bridge_platform', platform_sha),
                                       ('AST-CMD-004', 'bridge_enclosure', enclosure_sha)]:
        matches = [row for row in manifest['assets'] if row['catalogue_id'] == asset_id]
        assert len(matches) == 1 and matches[0]['family'] == family
        source = CATALOGUE / 'assets' / family / 'exports' / (asset_id + '.glb')
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
        assert matches[0]['export_sha256'] == expected

    source_dir = CATALOGUE / 'assets/bridge_enclosure'
    data = json.loads((source_dir / 'source/section_contract.json').read_text())
    assert data['catalogue_id'] == 'AST-CMD-004' and data['floor_y'] == 106.5
    assert {door['id'] for door in data['doors']} == {'aft', 'fore'}
    assert not data['light_markers']
    data['export_sha256'] = enclosure_sha
    data['runtime_status'] = 'Architectural integration awaiting runtime and visual acceptance'
    data['controlled_spine_subregion'] = {
        'retained_floor_owner': 'D18_fore_route',
        'boundary_xz': [[-4, -171.7], [4, -171.7], [4, -118.3], [-4, -118.3]],
        'scope': 'Door-bounded bridge segment only; no global owner reclassification or role enforcement'
    }
    data['public_route_with_bridge_doors_closed_xz'] = [
        [0, -520], [0, -177], [-44, -177], [-44, -77],
        [5.5, -77], [5.5, -111], [0, -111]
    ]
    write(ROOT / 'data/architecture/BRIDGE_ENCLOSURE_RUNTIME.json', data)
    platform = json.loads((CATALOGUE / 'assets/bridge_platform/source/section_contract.json').read_text())
    platform['export_sha256'] = platform_sha
    platform['runtime_status'] = 'Supported platform and bypass with bounded low-sill guards joined to bridge enclosure'
    write(ROOT / 'data/architecture/BRIDGE_PLATFORM_RUNTIME.json', platform)
    for asset_id, family in [('AST-CMD-003', 'bridge_platform'), ('AST-CMD-004', 'bridge_enclosure')]:
        shutil.copyfile(CATALOGUE / 'assets' / family / 'exports' / (asset_id + '.glb'),
                        ROOT / 'assets/models' / (asset_id + '.glb'))

    ledger = json.loads((ROOT / 'data/programme_ledger.json').read_text())
    row = next(row for row in ledger['destinations'] if row['programme_key'] == 'D18_directory_01')
    row['current_geometry_owner'] = 'scripts/bridge_enclosure.gd'
    row['current_boundary_xz'] = data['boundary_xz']
    row['current_boundary_authority'] = 'data/architecture/BRIDGE_ENCLOSURE_RUNTIME.json'
    row['current_status'] = 'Unfurnished bridge shell under integration; operational systems and acceptance unfinished'
    assert len(ledger['destinations']) == 161
    write(ROOT / 'data/programme_ledger.json', ledger)
    print(json.dumps({'enclosure_export': enclosure_sha, 'platform_export': platform_sha,
                      'floor_geometry_changed': False, 'runtime_acceptance': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--enclosure-sha', required=True)
    parser.add_argument('--platform-sha', required=True)
    args = parser.parse_args()
    author(args.enclosure_sha, args.platform_sha)
