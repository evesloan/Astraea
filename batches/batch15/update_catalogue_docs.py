"""Update balanced coverage and complete source-family packaging after review."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];assert json.loads((R/'qa/batch15/independent_final_review.json').read_text())['passed']
p=R/'CATEGORY_COVERAGE.json';j=json.loads(p.read_text());f=next(x for x in j['families'] if x['family']=='staff_service')
for category,ids in [('architecture_transitions',['AST-CRW-002']),('furnishings',['AST-CRW-001','AST-CRW-003']),('fixtures',['AST-CRW-004'])]:
 for aid in ids:
  if aid not in f['primary_category_asset_ids'].setdefault(category,[]):f['primary_category_asset_ids'][category].append(aid)
for family in j['families']:
 family['primary_category_counts']={key:len(family['primary_category_asset_ids'].get(key,[])) for key in j['category_totals']};family['unique_designs']=sum(family['primary_category_counts'].values())
f['next_useful_coverage']='Actual crew-home body/environment fitting, supported stack variants where eligible, and personal/work storage matched to recovered host dimensions'
j['category_totals']={key:sum(x['primary_category_counts'][key] for x in j['families']) for key in j['category_totals']};j['total_unique_artistic_designs']=sum(j['category_totals'].values());assert j['total_unique_artistic_designs']==77;p.write_text(json.dumps(j,indent=2)+'\n')
p=R/'CATEGORY_COVERAGE.md';s=p.read_text().replace('Each of the 73 designs','Each of the 77 designs').replace('| Staff / service | 4 | 2 | 1 | 2 | 0 | 9 |','| Staff / service | 5 | 4 | 2 | 2 | 0 | 13 |').replace('| Total | 29 | 16 | 6 | 14 | 8 | 73 |','| Total | 30 | 18 | 7 | 14 | 8 | 77 |').replace('Workplace storage/use details and alternative practical fixture mounts.','Actual crew-home body/environment fitting, supported stack variants where eligible, and personal/work storage matched to recovered host dimensions.');p.write_text(s)
p=R/'standards/source_package_groups.json';j=json.loads(p.read_text());j['revision']='source-family-delivery-08';g=next(x for x in j['groups'] if x['name']=='Staff_Service')
for folder in ['crew_rest','crew_personal']:
 if folder not in g['asset_directories']:g['asset_directories'].append(folder)
p.write_text(json.dumps(j,indent=2)+'\n')
p=R/'README.md';s=p.read_text().replace('The catalogue now contains 73 unique authored component designs','Batch15 adds four shared-crew rest/privacy designs. The catalogue now contains 77 unique authored component designs')
s='\n'.join(('The catalogue now contains 77 unique authored component designs, with zero adopted game instances. Batch15 adds the four shared-crew rest/privacy components. Exact IDs, source/export paths, review status and limits are in catalogue_manifest.json and the per-batch manifests.\n\nThe collection covers guest day-use, libraries, staff/service, botanical edges, aquatic leisure, engineering utilities, hospitality service, salon transitions and clinical support. These are reviewed components; whole-room composition, six-species fitting and game adoption still require the recovered host and further testing.' if 'The catalogue now contains 77 unique authored component designs' in line else line) for line in s.split('\n'))
if '## Batch15 shared-crew rest and privacy' not in s:s+='''\n## Batch15 shared-crew rest and privacy\n\nFour original designs extend the practical staff family with shaped single-place bedding and frame, a supported side curtain with constant-length geometric folds, useful open storage with a hollow moving drawer, and a joined reading-light/shelf module. The relative QA pair repeats those four assets; it is not a new cabin or population allocation.\n\nThe actual shared-room reference and preserved D03 programme guide material restraint, personal privacy and storage. Final room dimensions, the player’s shared-home identity and all six-species body/environment fitting remain unresolved. The source photo’s bunk option is not claimed implemented by two independent frames. The 77-row index retains every earlier record. See batches/batch15/STATUS.md for actual export, motion, collision and ordinary-height review scope.\n'''
p.write_text(s);print('Coverage77 and complete Staff source family updated')
