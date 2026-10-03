"""Publish four independently reviewed D09 retail component designs."""
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
review_path = ROOT / 'qa/batch18/independent_final_review.json'
assert json.loads(review_path.read_text())['passed'] is True
rows = []
for number in range(1, 5):
    asset_id = f'AST-RTL-{number:03d}'
    family = 'retail_display' if number < 3 else 'retail_work'
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
        'batch': '18',
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
    'batch': '18',
    'started_utc': '2026-10-03T03:55:35Z',
    'kind': 'D09_programme_guided_retail_display_work_components',
    'unique_authored_asset_count': 4,
    'assets': rows,
    'actual_game_adoptions': 0,
    'scope': 'Recessed fitted wall display, stepped display island, wrapping/service bench and one coordinated goods-container design. A partial source-level arrangement is tied to the historical R070 allocation without assigning actual shop slots or replacing the missing host.',
    'review_completed_utc': args.review_completed_utc,
    'review': 'qa/batch18/independent_final_review.json',
    'coordinate_contract': 'standards/COORDINATE_CONTRACT.md',
    'reference_manifest': 'batches/batch18/reference_manifest.json',
    'programme_handoff': 'references/retail/D09_retail_programme_reference_handoff.json',
    'contract': 'batches/batch18/CONTRACT.md',
    'arrangement': 'qa/batch18/assembly/plan.json',
    'category_coverage': 'CATEGORY_COVERAGE.json',
    'quality_baseline_user_message': 'Sentinel_1f1516ffa9a08191a5f37800301a001c',
    'limits': [
        'R070 Kind Curios /070 is a proven historical12×12m allocation with symbolic entrance; actual finished walls, door aperture/pockets/head, local support and slots remain unknown',
        'The100 small shop addresses and ten larger D09 destinations remain distinct; Orchard market is not moved beside the atrium',
        'The source-level empty regions and full nominal bounds are adjustable proposals, not certified actor/cart or six-species routes',
        'Component states, source/native markers and original inactive service graphics do not implement transactions, payment, inventory, merchant work or persistence',
        'Goods containers and packaging have no assigned contents, quantity, biological compatibility or load certification',
        'Component material/geometry counts and inspection lighting do not establish original-engine appearance or target-PC performance',
        'The original game remains absent; no room, store, capacity or game adoption is added',
    ],
}
(ROOT / 'batches/batch18/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
path = ROOT / 'catalogue_manifest.json'
catalogue = json.loads(path.read_text())
old = [row for row in catalogue['assets'] if row.get('batch') != '18']
assert len(old) == 85
catalogue.update(assets=old + rows, unique_authored_asset_count=89,
                 batch='01–18', current_batch='18', version=18,
                 component_review_completed_utc=args.review_completed_utc)
catalogue['status']['independent_component_visual_review'] = 'batches01_to07_09_to18_passed_for_components_only_with_batch08_readiness'
for key, value in [('batches', 'batches/batch18/manifest.json'),
                   ('reviews', 'qa/batch18/independent_final_review.json')]:
    if value not in catalogue[key]:
        catalogue[key].append(value)
path.write_text(json.dumps(catalogue, indent=2) + '\n')
print(json.dumps({'published_designs': 4, 'catalogue_total': 89,
                  'triangles': sum(row['evaluated_triangles'] for row in rows),
                  'adoptions': 0}, indent=2))
