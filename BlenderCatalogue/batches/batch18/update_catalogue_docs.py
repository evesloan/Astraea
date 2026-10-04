"""Publish reviewed retail coverage and a complete standalone source family."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
assert json.loads((ROOT/'qa/batch18/independent_final_review.json').read_text())['passed']
p=ROOT/'CATEGORY_COVERAGE.json';j=json.loads(p.read_text())
j['families']=[row for row in j['families'] if row['family']!='retail_display_work']
j['families'].append({'family':'retail_display_work','title':'Retail display / work','primary_category_asset_ids':{'architecture_transitions':['AST-RTL-001'],'furnishings':['AST-RTL-002','AST-RTL-003'],'purposeful_props':['AST-RTL-004']},'next_useful_coverage':'Recovered-shop threshold/support and activity-slot fitting, distinct merchandise families and authored shop compositions; no automatic100-shop rollout or transaction system'})
for row in j['families']:
 row['primary_category_counts']={key:len(row['primary_category_asset_ids'].get(key,[])) for key in j['category_totals']}
 row['unique_designs']=sum(row['primary_category_counts'].values())
j['category_totals']={key:sum(row['primary_category_counts'][key] for row in j['families']) for key in j['category_totals']}
j['total_unique_artistic_designs']=sum(j['category_totals'].values());assert j['total_unique_artistic_designs']==89
p.write_text(json.dumps(j,indent=2)+'\n')
p=ROOT/'CATEGORY_COVERAGE.md';s=p.read_text().replace('Each of the 85 designs','Each of the 89 designs')
s=s.replace('| Total | 31 | 21 | 7 | 18 | 8 | 85 |','| Retail display / work | 1 | 2 | 0 | 0 | 1 | 4 |\n| Total | 32 | 23 | 7 | 18 | 9 | 89 |')
if '- **Retail display / work:**' not in s:s=s.replace('These directions support district-specific needs','- **Retail display / work:** Recovered-shop threshold/support and activity-slot fitting, distinct merchandise families and authored shop compositions; no automatic100-shop rollout or transaction system.\n\nThese directions support district-specific needs')
p.write_text(s)
p=ROOT/'standards/source_package_groups.json';j=json.loads(p.read_text());j['revision']='source-family-delivery-11';j['groups']=[row for row in j['groups'] if row['name']!='Retail_Display'];j['groups'].append({'name':'Retail_Display','asset_directories':['retail_display','retail_work']});p.write_text(json.dumps(j,indent=2)+'\n')
p=ROOT/'catalogue_manifest.json';j=json.loads(p.read_text());record={'path':'materials/retail/manifest.json','scope':'Original recessed public-retail terracotta enamel; prior public materials unchanged','revision':'retail-original-01'}
if not any(row['path']==record['path'] for row in j['material_libraries']):j['material_libraries'].append(record)
p.write_text(json.dumps(j,indent=2)+'\n')
p=ROOT/'README.md';s=p.read_text().replace('contains 85 unique authored component designs','contains 89 unique authored component designs').replace('Batch17 adds four housekeeping and laundry workplace components.','Batch18 adds four retail display and work components.')
if '## Batch18 retail display and work' not in s:s+='''\n## Batch18 retail display and work\n\nFour original designs add an authored recessed wall-display bay, stepped island, wrapping/service bench and one coordinated reusable small-goods case. The partial source-level arrangement is grounded in the explicitly mapped historical R070 Kind Curios /070 allocation. Supported repeated case placements count as instances, and derivative handling states remain the same design.\n\nThe100 addressed small shops remain distinct from the ten larger D09 destinations and the separate forward Orchard market. Historical outer containment and ordinary-height component pictures do not recover actual door pockets, supports, activity-slot ownership or finished shop architecture. Payment, stock, staff assignment, persistence and engine use are unimplemented. See batches/batch18/STATUS.md and the frozen source/export review.\n'''
p.write_text(s)
print('Coverage89 and complete retail source family updated')
