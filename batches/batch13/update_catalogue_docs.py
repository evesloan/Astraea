"""Update coverage and compact source grouping after independent acceptance."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2]
assert json.loads((R/'qa/batch13/independent_final_review.json').read_text())['passed']
p=R/'CATEGORY_COVERAGE.json';j=json.loads(p.read_text());f=next(x for x in j['families'] if x['family']=='botanical')
for cat,ids in [('architecture_transitions',['AST-BOT-010']),('purposeful_props',['AST-BOT-007','AST-BOT-008','AST-BOT-009'])]:
 for aid in ids:
  if aid not in f['primary_category_asset_ids'][cat]:f['primary_category_asset_ids'][cat].append(aid)
for family in j['families']:
 family['primary_category_counts']={key:len(family['primary_category_asset_ids'].get(key,[])) for key in j['category_totals']};family['unique_designs']=sum(family['primary_category_counts'].values())
f['next_useful_coverage']='Host-specific planting composition, economical distant silhouettes and distinct habitat planting after actual volume review'
j['category_totals']={key:sum(x['primary_category_counts'][key] for x in j['families']) for key in j['category_totals']};j['total_unique_artistic_designs']=sum(j['category_totals'].values());assert j['total_unique_artistic_designs']==69
p.write_text(json.dumps(j,indent=2)+'\n')
p=R/'CATEGORY_COVERAGE.md';s=p.read_text().replace('Each of the 65 designs','Each of the 69 designs').replace('| Botanical / planted edges | 3 | 0 | 0 | 0 | 3 | 6 |','| Botanical / planted edges | 4 | 0 | 0 | 0 | 6 | 10 |').replace('| Total | 27 | 16 | 4 | 13 | 5 | 65 |','| Total | 28 | 16 | 4 | 13 | 8 | 69 |').replace('Denser and different plant silhouettes; branching or stepped edge interfaces.','Host-specific planting composition, economical distant silhouettes and distinct habitat planting after actual volume review.');p.write_text(s)
p=R/'standards/source_package_groups.json';j=json.loads(p.read_text());j['revision']='source-family-delivery-06';g=next(x for x in j['groups'] if x['name']=='Botanical')
for folder in ['botanical_cluster','botanical_transition']:
 if folder not in g['asset_directories']:g['asset_directories'].append(folder)
p.write_text(json.dumps(j,indent=2)+'\n')
p=R/'README.md';s=p.read_text().replace('Batch12 adds four forward care-support designs. The catalogue now contains 65 unique authored component designs','Batch12 adds four forward care-support designs. Batch13 adds three contrasting botanical forms and one raised planted-seat transition. The catalogue now contains 69 unique authored component designs');s=s.replace('- `assets/botanical_planter`: straight, curved and closed planted-seat edges','- `assets/botanical_planter`: straight, curved and closed planted-seat edges\n- `assets/botanical_cluster`: pleated fan crown, rearward trailing cluster and upright flowering bank\n- `assets/botanical_transition`: raised planted-seat end with supported lower/upper soil cells')
if '## Batch13 botanical edge expansion' not in s:s+='''\n## Batch13 botanical edge expansion\n\nFour original designs expand the sparse first botanical collection with different crown, trailing and flowering rhythms. The partial imported arrangement joins the existing straight seat/closure to a raised end transition, retaining a useful sitting ribbon and declared front, seated-view and rear maintenance spaces. This is component inspection, not an installed commons or finished receiving courtyard.\n\nEditable branches/leaves remain in Blender. Static plant exports use 4/4/5 material-role meshes, with purposeful markers retained; there is no claimed runtime improvement without the game. Every visible flowering clump has its own verified soil contact instead of an artificial exposed connector. The transition preserves the original seam and uses supported retaining profiles, with simplified collision limits recorded rather than implied certification. The current 69-row interface index preserves all 65 earlier records. See batches/batch13/STATUS.md and its final independent review for exact source/export and capture scope.\n'''
p.write_text(s)
print('Coverage69, botanical10, complete Botanical source group updated')
