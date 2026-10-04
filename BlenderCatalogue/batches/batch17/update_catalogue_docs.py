"""Publish reviewed workplace coverage and its complete source package group."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
assert json.loads((ROOT / 'qa/batch17/independent_final_review.json').read_text())['passed']
path = ROOT / 'CATEGORY_COVERAGE.json'
coverage = json.loads(path.read_text())
coverage['families'] = [row for row in coverage['families'] if row['family'] != 'housekeeping_laundry']
coverage['families'].append({
    'family': 'housekeeping_laundry',
    'title': 'Housekeeping / laundry',
    'primary_category_asset_ids': {
        'equipment': ['AST-HSK-001', 'AST-HSK-002', 'AST-HSK-004'],
        'furnishings': ['AST-HSK-003'],
    },
    'next_useful_coverage': 'Recovered-host clean/used routes, supported utility and storage transitions, actual carrier and six-species work fitting; no fixed player chore loop',
})
for row in coverage['families']:
    row['primary_category_counts'] = {key: len(row['primary_category_asset_ids'].get(key, [])) for key in coverage['category_totals']}
    row['unique_designs'] = sum(row['primary_category_counts'].values())
coverage['category_totals'] = {key: sum(row['primary_category_counts'][key] for row in coverage['families']) for key in coverage['category_totals']}
coverage['total_unique_artistic_designs'] = sum(coverage['category_totals'].values())
assert coverage['total_unique_artistic_designs'] == 85
path.write_text(json.dumps(coverage, indent=2) + '\n')

path = ROOT / 'CATEGORY_COVERAGE.md'
text = path.read_text().replace('Each of the 81 designs', 'Each of the 85 designs')
text = text.replace('| Total | 31 | 20 | 7 | 15 | 8 | 81 |', '| Housekeeping / laundry | 0 | 1 | 0 | 3 | 0 | 4 |\n| Total | 31 | 21 | 7 | 18 | 8 | 85 |')
if '- **Housekeeping / laundry:**' not in text:
    text = text.replace('These directions support district-specific needs', '- **Housekeeping / laundry:** Recovered-host clean/used routes, supported utility and storage transitions, actual carrier and six-species work fitting; no fixed player chore loop.\n\nThese directions support district-specific needs')
path.write_text(text)

path = ROOT / 'standards/source_package_groups.json'
groups = json.loads(path.read_text())
groups['revision'] = 'source-family-delivery-10'
groups['groups'] = [row for row in groups['groups'] if row['name'] != 'Housekeeping_Operations']
groups['groups'].append({'name': 'Housekeeping_Operations', 'asset_directories': ['housekeeping_equipment', 'housekeeping_handling']})
path.write_text(json.dumps(groups, indent=2) + '\n')

art_paths = [
    'assets/housekeeping_equipment/source/cloth_controls.png',
    'assets/housekeeping_equipment/source/rack_controls.png',
    'assets/housekeeping_handling/textures/handling_canvas.png',
    'assets/housekeeping_handling/textures/handling_linen.png',
    'assets/housekeeping_handling/textures/clean.png',
    'assets/housekeeping_handling/textures/used.png',
]
art = {'scope': 'Original inactive control graphics, handling glyphs and low-contrast textile roles; shared staff materials remain unchanged and no new design count is added',
       'textures': [{'path': rel, 'sha256': hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()} for rel in art_paths],
       'source_generators': ['assets/housekeeping_equipment/source/draw_controls.py', 'assets/housekeeping_handling/textures/draw_handling_art.py']}
(ROOT / 'batches/batch17/local_material_sources.json').write_text(json.dumps(art, indent=2) + '\n')
path = ROOT / 'catalogue_manifest.json'
catalogue = json.loads(path.read_text())
record = {'path': 'batches/batch17/local_material_sources.json', 'scope': 'Original fictional appliance controls and clean/used textile-handling materials'}
if not any(row['path'] == record['path'] for row in catalogue['material_libraries']):
    catalogue['material_libraries'].append(record)
path.write_text(json.dumps(catalogue, indent=2) + '\n')

path = ROOT / 'README.md'
text = path.read_text().replace('contains 81 unique authored component designs', 'contains 85 unique authored component designs')
text = text.replace('Batch16 adds four auditorium arrival, audience and backstage components.', 'Batch17 adds four housekeeping and laundry workplace components.')
if '## Batch17 housekeeping and laundry' not in text:
    text += '''
## Batch17 housekeeping and laundry

Four original designs add a fictional cloth-treatment appliance, open conditioning rack, sorting/folding bench and a distinct bulk-linen carrier. Useful chambers, work surfaces, retained moving parts, source/native interfaces and collision proposals are reviewed at component scale. The actual exported components are shown in separate equipment and handling examples under inspection lighting.

The historical D01 laundry and custodial depot remain separate allocations, 648 m apart longitudinally. These examples do not invent their connector or establish a mandatory end-of-shift loop. Live cleaning, heat, utilities, hygiene and species compatibility are unimplemented. The carrier does not replace the original player cart. See batches/batch17/STATUS.md and the independent source/export review.
'''
path.write_text(text)
print('Coverage85 and complete housekeeping source family updated')
