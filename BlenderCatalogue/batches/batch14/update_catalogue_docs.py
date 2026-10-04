"""Update category/source-package coverage only after bounded acceptance."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];assert json.loads((R/'qa/batch14/independent_final_review_receipt.json').read_text())['passed']
p=R/'CATEGORY_COVERAGE.json';j=json.loads(p.read_text());f=next(x for x in j['families'] if x['family']=='aquatic')
for category,ids in [('architecture_transitions',['AST-AQU-007']),('equipment',['AST-AQU-008']),('fixtures',['AST-AQU-009','AST-AQU-010'])]:
 for aid in ids:
  if aid not in f['primary_category_asset_ids'].setdefault(category,[]):f['primary_category_asset_ids'][category].append(aid)
for family in j['families']:
 family['primary_category_counts']={key:len(family['primary_category_asset_ids'].get(key,[])) for key in j['category_totals']};family['unique_designs']=sum(family['primary_category_counts'].values())
f['next_useful_coverage']='Recovered-host wet/dry thresholds, drainage/utility joins and genuinely species-specific support after spatial review'
j['category_totals']={key:sum(x['primary_category_counts'][key] for x in j['families']) for key in j['category_totals']};j['total_unique_artistic_designs']=sum(j['category_totals'].values());assert j['total_unique_artistic_designs']==73;p.write_text(json.dumps(j,indent=2)+'\n')
p=R/'CATEGORY_COVERAGE.md';s=p.read_text().replace('Each of the 69 designs','Each of the 73 designs').replace('| Aquatic leisure | 3 | 2 | 0 | 1 | 0 | 6 |','| Aquatic leisure | 4 | 2 | 2 | 2 | 0 | 10 |').replace('| Total | 28 | 16 | 4 | 13 | 8 | 69 |','| Total | 29 | 16 | 6 | 14 | 8 | 73 |').replace('Wet-area fixtures, towel/hydration/support details and complementary entry interfaces.','Recovered-host wet/dry thresholds, drainage/utility joins and genuinely species-specific support after spatial review.');p.write_text(s)
p=R/'standards/source_package_groups.json';j=json.loads(p.read_text());j['revision']='source-family-delivery-07';g=next(x for x in j['groups'] if x['name']=='Aquatic_Leisure')
for folder in ['aquatic_towel_use','aquatic_wet_use']:
 if folder not in g['asset_directories']:g['asset_directories'].append(folder)
p.write_text(json.dumps(j,indent=2)+'\n')
p=R/'README.md';s=p.read_text().replace('The catalogue now contains 69 unique authored component designs','Batch14 adds four aquatic arrival/use designs. The catalogue now contains 73 unique authored component designs').replace('- `assets/aquatic_float`: purpose-shaped leisure float with seat and grip proposals','- `assets/aquatic_float`: purpose-shaped leisure float with seat and grip proposals\n- `assets/aquatic_towel_use`: protected dry supply and guarded used return with a removable receiver\n- `assets/aquatic_wet_use`: optional refreshment and supported rinse-control housings')
if '## Batch14 aquatic arrival and use' not in s:s+='''\n## Batch14 aquatic arrival and use\n\nFour original designs add distinct clean retrieval, used return and optional wet-fixture purposes to the aquatic collection. The dry niche and guarded receiver use original markings, while the wheeled container and rear service plates retain purposeful native hierarchies. Capped connections and supported controls communicate intended use without implementing fluid, laundry or gameplay behavior.\n\nThe historical D08 changing allocation and farther-aft towel/care allocation are separate. The supplied blueprint and later facility evidence guide this component kit, without inventing their missing connection, room polygons or species fitting. Actual imported closed/withdrawn and wet/service examples remain studio QA. The current 73-row index preserves all 69 earlier records. See batches/batch14/STATUS.md and its exact independent receipt for source/export, collision and capture limits.\n'''
p.write_text(s);print('Coverage73 and complete Aquatic source family updated')
