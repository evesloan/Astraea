"""Publish four independently reviewed D01 workplace component designs."""
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
review_path = ROOT / 'qa/batch17/independent_final_review.json'
assert json.loads(review_path.read_text())['passed'] is True
rows = []
for number in range(1, 5):
    asset_id = f'AST-HSK-{number:03d}'
    family = 'housekeeping_equipment' if number < 3 else 'housekeeping_handling'
    base = ROOT / 'assets' / family
    manifest_path = base / (asset_id + '.manifest.json')
    manifest = json.loads(manifest_path.read_text())
    source = base / manifest['source']
    export = base / manifest['export']
    assert source.is_file() and export.is_file()
    row = {
        'catalogue_id': asset_id,
        'name': manifest['title'],
        'family': family,
        'source': str(source.relative_to(ROOT)),
        'export': str(export.relative_to(ROOT)),
        'manifest': str(manifest_path.relative_to(ROOT)),
        'dimensions_blender_xyz_m': manifest['bounds_blender_z_up']['dimensions_m'],
        'evaluated_triangles': manifest['evaluated_triangles'],
        'batch': '17',
        'adopted_game_instances': 0,
        'source_sha256': sha(source),
        'export_sha256': sha(export),
        'interface_record_id': asset_id,
    }
    for state in manifest.get('state_derivatives', []):
        path = base / state['export']
        assert path.is_file()
        row.setdefault('state_derivatives', []).append({
            'state': state.get('state', state.get('name')),
            'export': str(path.relative_to(ROOT)),
            'sha256': sha(path),
            'counts_as_new_design': False,
        })
    rows.append(row)

manifest = {
    'batch': '17',
    'started_utc': '2026-10-03T02:56:52Z',
    'kind': 'D01_programme_guided_housekeeping_laundry_components',
    'unique_authored_asset_count': 4,
    'assets': rows,
    'actual_game_adoptions': 0,
    'scope': 'Cloth-treatment appliance, open conditioning rack, sorting/folding bench and distinct bulk-linen carrier. Relative equipment and handling examples do not join the separate historical laundry and depot allocations.',
    'review_completed_utc': args.review_completed_utc,
    'review': 'qa/batch17/independent_final_review.json',
    'coordinate_contract': 'standards/COORDINATE_CONTRACT.md',
    'reference_manifest': 'batches/batch17/reference_manifest.json',
    'programme_handoff': 'references/housekeeping/D01_housekeeping_programme_handoff.json',
    'contract': 'batches/batch17/CONTRACT.md',
    'arrangement': 'qa/batch17/assembly/plan.json',
    'category_coverage': 'CATEGORY_COVERAGE.json',
    'quality_baseline_user_message': 'Sentinel_1f1516ffa9a08191a5f37800301a001c',
    'limits': [
        'Laundry and custodial depot remain separate historical allocations, 648 m apart longitudinally; their finished polygons and actual connector are unknown',
        'The historical staff-only flags and arrival access conflict remain recorded without changing access rules',
        'Adjustable dimensions, movement states and source/native markers do not establish actual operator, six-species, room, carrier or door fit',
        'The linen carrier is a distinct component; it does not replace the player cart or implement rolling, load dynamics or inventory',
        'Clean/used markings communicate handling intent only; no hygiene, material compatibility, cleaning efficacy, heat, fluids, wiring or certification is implemented',
        'The suggested end-of-shift sequence remains an idea; these components establish no mandatory chores, staffing or throughput',
        'The original engine is absent and actual game adoption remains zero',
    ],
}
(ROOT / 'batches/batch17/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
path = ROOT / 'catalogue_manifest.json'
catalogue = json.loads(path.read_text())
old = [row for row in catalogue['assets'] if row.get('batch') != '17']
assert len(old) == 81
catalogue.update(assets=old + rows, unique_authored_asset_count=85,
                 batch='01–17', current_batch='17', version=17,
                 component_review_completed_utc=args.review_completed_utc)
catalogue['status']['independent_component_visual_review'] = 'batches01_to07_09_to17_passed_for_components_only_with_batch08_readiness'
for key, value in [('batches', 'batches/batch17/manifest.json'),
                   ('reviews', 'qa/batch17/independent_final_review.json')]:
    if value not in catalogue[key]:
        catalogue[key].append(value)
path.write_text(json.dumps(catalogue, indent=2) + '\n')
print(json.dumps({'published_designs': 4, 'catalogue_total': 85,
                  'triangles': sum(row['evaluated_triangles'] for row in rows),
                  'adoptions': 0}, indent=2))
