"""Assemble source-backed records for the reviewed utility components."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--review-completed-utc', required=True)
args = parser.parse_args()
rows = []
for family in ('utility_machines', 'utility_console', 'utility_pipework'):
    base = ROOT / 'assets' / family
    for manifest_path in sorted(base.glob('AST-ENG-*.manifest.json')):
        manifest = json.loads(manifest_path.read_text())
        source = base / manifest.get('source', manifest.get('source_file', ''))
        export = base / manifest.get('exchange', manifest.get('export', manifest.get('export_file', '')))
        assert source.is_file() and export.is_file(), manifest_path
        dimensions = manifest.get('dimensions_blender_source_xyz_m', manifest.get('bounds_blender_z_up', {}).get('dimensions_m', manifest.get('bounds_blender_source', {}).get('dimensions_m')))
        triangles = manifest.get('triangles', manifest.get('evaluated_triangles', manifest.get('evaluated_source_triangles')))
        assert dimensions and triangles, manifest_path
        rows.append({
            'catalogue_id': manifest['catalogue_id'],
            'name': manifest.get('title', manifest.get('design')),
            'family': family,
            'source': str(source.relative_to(ROOT)),
            'export': str(export.relative_to(ROOT)),
            'manifest': str(manifest_path.relative_to(ROOT)),
            'dimensions_blender_xyz_m': dimensions,
            'evaluated_triangles': triangles,
            'batch': '06',
            'adopted_game_instances': 0,
            'source_sha256': sha(source),
            'export_sha256': sha(export),
        })
rows.sort(key=lambda row: row['catalogue_id'])
assert [row['catalogue_id'] for row in rows] == [f'AST-ENG-{i:03d}' for i in range(1, 7)]
manifest = {
    'batch': '06',
    'started_utc': '2026-10-02T13:13:00Z',
    'unique_authored_asset_count': 6,
    'assets': rows,
    'actual_game_adoptions': 0,
    'scope': 'Transfer pump, serviceable filter, wall control console, straight pipe, elbow and manual valve. Original script-assisted editable components, separate from the missing game.',
    'review_completed_utc': args.review_completed_utc,
    'review': 'qa/batch06/independent_final_review.json',
    'coordinate_contract': 'standards/COORDINATE_CONTRACT.md',
    'reference_manifest': 'batches/batch06/reference_manifest.json',
    'shared_materials': 'materials/staff/manifest.json',
    'local_graphics': 'assets/utility_console/textures/',
    'shared_port_contract': 'standards/utility_port_spec.json',
    'connected_component_evidence': 'qa/batch06/arrangement/evidence.json',
    'performance_followups': 'standards/PERFORMANCE_FOLLOWUPS.md',
    'limitations': [
        'Geometric mating and proposed control/service motion are component evidence only; no working fluid circuit or engineering certification',
        'Human-scale proposed controls and access require actual species, actor, room and route validation',
        'Proposed collisions are not imported or accepted engine physics',
        'Current 2328-triangle shared flanges are near inspection candidates; economical repeated/distant exports and actual runtime performance remain pending',
        'Neutral floor and local console wall are QA-only fixtures, not authored game rooms',
    ],
}
(ROOT / 'batches/batch06/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
path = ROOT / 'catalogue_manifest.json'
catalogue = json.loads(path.read_text())
catalogue['assets'] = [row for row in catalogue['assets'] if row.get('batch') != '06'] + rows
catalogue['unique_authored_asset_count'] = len(catalogue['assets'])
assert catalogue['unique_authored_asset_count'] == 39
catalogue['batch'] = '01–06'
catalogue['version'] = 6
catalogue['current_batch'] = '06'
catalogue['component_review_completed_utc'] = args.review_completed_utc
catalogue['status']['independent_component_visual_review'] = 'batches01_to06_passed_for_components_only'
if 'batches/batch06/manifest.json' not in catalogue['batches']:
    catalogue['batches'].append('batches/batch06/manifest.json')
if 'qa/batch06/independent_final_review.json' not in catalogue['reviews']:
    catalogue['reviews'].append('qa/batch06/independent_final_review.json')
path.write_text(json.dumps(catalogue, indent=2) + '\n')
print(json.dumps({'new_designs': len(rows), 'total_unique': len(catalogue['assets']), 'new_triangles': sum(row['evaluated_triangles'] for row in rows)}, indent=2))
