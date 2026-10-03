"""Expose reviewed optional body roles without changing prior precision records."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return json.loads((ROOT / path).read_text())


def binding(path):
    return {'path': path, 'sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}


review_path = 'qa/batch17/independent_final_review.json'
assert load(review_path)['passed']
path = ROOT / 'batches/batch17/body_proxy_candidates.json'
registry = {'schema': 'astraea_optional_body_proxy_registry_v1', 'status': 'Explicit optional body-role selections; no engine adoption', 'policy': 'Keep precise contacts and motion ownership for fine mechanisms, service and interaction. These literal subsets preserve actual useful voids; counts are not runtime performance evidence.', 'assets': [], 'game_adoptions': 0}
for number in range(1, 5):
    asset_id = f'AST-HSK-{number:03d}'
    family = 'housekeeping_equipment' if number < 3 else 'housekeeping_handling'
    precise_path = f'assets/{family}/collision_proposals.json'
    precise = load(precise_path)[asset_id]
    if number < 3:
        candidate_path = f'assets/{family}/actor_proxies/body_collision_subset.json'
        candidate = load(candidate_path)[asset_id]
        detailed_count = len(precise['shapes'])
        retained_count = len(candidate['shapes'])
        selector = f'/{asset_id}/shapes'
    else:
        candidate_path = precise_path
        candidate = precise['optional_body_candidate']
        detailed_count = len(precise['precise_reference'])
        retained_count = len(candidate['retained_shape_names'])
        selector = f'/{asset_id}/optional_body_candidate'
    assert 0 < retained_count <= detailed_count
    registry['assets'].append({
        'catalogue_id': asset_id,
        'detailed_shape_count': detailed_count,
        'body_shape_count': retained_count,
        'omitted_shape_count': detailed_count - retained_count,
        'candidate_source': binding(candidate_path),
        'candidate_json_pointer': selector,
        'precision_reference': binding(precise_path),
        'independent_review': binding(review_path),
        'scope': 'Literal original shape selection with primary physical contacts and useful voids retained; fine mechanism, service and target selection continue to use the detailed set',
        'engine_adoption': False,
    })
registry['record_resolution'] = 'Each record names its exact candidate source, JSON pointer, precision reference and independent review. The previous cultural registry remains unchanged at standards/body_proxy_candidates.json.'
path.write_text(json.dumps(registry, indent=2) + '\n')
registry_binding = binding('batches/batch17/body_proxy_candidates.json')
catalogue_path = ROOT / 'catalogue_manifest.json'
catalogue = json.loads(catalogue_path.read_text())
catalogue['additional_optional_body_proxy_registries'] = [row for row in catalogue.get('additional_optional_body_proxy_registries', []) if row['path'] != registry_binding['path']] + [registry_binding]
catalogue_path.write_text(json.dumps(catalogue, indent=2) + '\n')
batch_path = ROOT / 'batches/batch17/manifest.json'
batch = json.loads(batch_path.read_text())
batch['optional_body_proxy_registry'] = registry_binding
batch_path.write_text(json.dumps(batch, indent=2) + '\n')
print('Published four explicit optional housekeeping body-role entries')
