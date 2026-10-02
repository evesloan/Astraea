"""Count each existing artistic design once in a practical primary category."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
cat=json.loads((ROOT/'catalogue_manifest.json').read_text());by_id={r['catalogue_id']:r for r in cat['assets']}
A='architecture_transitions';F='furnishings';L='fixtures';E='equipment';P='purposeful_props'
groups=[
 ('guest_day_use','Guest day-use / reveals',{A:['AST-VR-01-H','AST-VR-01-S','AST-VR-01-J','AST-VR-01-T'],F:['AST-FUR-001','AST-FUR-002','AST-FUR-003']},'Fitted room transitions and personal-use variants selected for actual district layouts'),
 ('library','Library',{A:['AST-LIB-STR-001','AST-LIB-STR-002','AST-LIB-STR-003'],F:['AST-LIB-STUDY-01','AST-LIB-STUDY-02'],P:['AST-LIB-006','AST-LIB-007']},'Joined collection/study transitions and purposeful stock variety matched to district sections'),
 ('staff_service','Staff / service',{A:['AST-STF-001','AST-STF-002','AST-STF-003'],E:['AST-STF-004','AST-STF-005'],L:['AST-STF-006'],F:['AST-STF-007']},'Workplace storage/use details and alternative practical fixture mounts'),
 ('botanical','Botanical / planted edges',{A:['AST-BOT-004','AST-BOT-005','AST-BOT-006'],P:['AST-BOT-001','AST-BOT-002','AST-BOT-003']},'Denser and different plant silhouettes; branching or stepped edge interfaces'),
 ('aquatic','Aquatic leisure',{A:['AST-AQU-003','AST-AQU-004','AST-AQU-005'],F:['AST-AQU-001','AST-AQU-002'],E:['AST-AQU-006']},'Wet-area fixtures, towel/hydration/support details and complementary entry interfaces'),
 ('engineering','Engineering utilities',{E:[f'AST-ENG-{i:03d}' for i in range(1,7)]},'Additional supported connections, maintenance interfaces and distinct useful equipment'),
 ('hospitality','Hospitality service',{A:['AST-HSP-001','AST-HSP-002'],E:['AST-HSP-003','AST-HSP-004'],F:['AST-HSP-005','AST-HSP-006']},'Service/task fixtures, guest presentation details and meaningful stock variants'),
]
# Add the next reviewed family members only when the whole declared expansion is present.
expansion_ids={'AST-GST-001','AST-GST-002','AST-GST-003','AST-LIB-008','AST-LIB-009','AST-LIB-010'}
if expansion_ids.intersection(by_id):
 assert expansion_ids.issubset(by_id), 'Partial reviewed expansion in catalogue'
 groups[0][2][L]=['AST-GST-001','AST-GST-002']
 groups[0][2][F]+=['AST-GST-003']
 groups[1][2][L]=['AST-LIB-008']
 groups[1][2][F]+=['AST-LIB-009']
 groups[1][2][E]=['AST-LIB-010']
salon_ids={f'AST-SAL-{i:03d}' for i in range(1,7)}
if salon_ids.intersection(by_id):
 assert salon_ids.issubset(by_id), 'Partial salon kit in catalogue'
 groups.append(('public_salon','Public salon transitions',{A:sorted(salon_ids)},'Host-specific placement and join revisions after recovered geometry review; paired landing interfaces guided by district planning'))
landing_ids={f'AST-LND-{i:03d}' for i in range(1,5)}
if landing_ids.intersection(by_id):
 assert landing_ids.issubset(by_id), 'Partial landing kit in catalogue'
 groups[0][2][A]+=['AST-LND-001']
 groups[0][2][F]+=['AST-LND-002']
 groups[2][2][A]+=['AST-LND-003']
 groups[2][2][F]+=['AST-LND-004']
clinical_ids={f'AST-MED-{i:03d}' for i in range(1,5)}
if clinical_ids.intersection(by_id):
 assert clinical_ids.issubset(by_id), 'Partial clinical kit in catalogue'
 groups.append(('clinical_care','Clinical care support',{A:['AST-MED-001'],F:['AST-MED-003','AST-MED-004'],E:['AST-MED-002']},'Species-specific body/support and host privacy/access reconciliation; no new clinical capacity'))
count=len(by_id)
rows=[];seen=[];totals={k:0 for k in (A,F,L,E,P)}
for key,title,entries,gap in groups:
 ids=[i for v in entries.values() for i in v];assert all(i in by_id for i in ids);seen+=ids
 counts={k:len(entries.get(k,[])) for k in totals}
 for k,v in counts.items():totals[k]+=v
 rows.append({'family':key,'title':title,'primary_category_asset_ids':entries,'primary_category_counts':counts,'unique_designs':len(ids),'next_useful_coverage':gap})
assert len(seen)==len(set(seen))==len(by_id)==count and set(seen)==set(by_id)
ledger={'revision':'catalogue-category-coverage-02','scope':'Primary functional categories for balanced expansion of existing families; inventory only, not completed rooms or engine adoption','total_unique_artistic_designs':count,'derived_representations_counted_as_new_designs':False,'game_adoptions':0,'category_totals':totals,'families':rows,'quality_baseline':{'status':'user_supported_demonstrated_asset_quality_baseline','source_message_id':'Sentinel_1f1516ffa9a08191a5f37800301a001c','source_utc':'2026-10-02T16:08:00Z','quote':'this is a quality threshold I feel genuinely comfortable getting behind for a large scale asset delivery. I suggest we expand each family categorically, growing our collections while we continue the restore path.','scope_limit':'Approval of the demonstrated catalogue asset-quality threshold, not the whole ship, room integration, gameplay, physics or native performance.'},'expansion_rules':['Choose useful form/activity/mount/interface differences; no recolor-only count inflation','Integrated subparts and derived mirrors/closures/stock layouts/LODs are not separately counted designs','Use categories where purpose fits; zero does not demand an arbitrary asset','Retain distinct guest/public/staff/technical character and the full relevant reference set','Editable source, actual export review, independent checks and durable backup remain gates','Upcoming kits respond to documented district purpose, proportions, section and material character, rather than independent generic category filling','Real-room and neighborhood manual reviews resume when the original game is available']}
ledger['governing_canon']={'decks':18,'guest_units':1000,'luxury_units_within_guest_total':{'deluxe':50,'premium':25,'royalty':5,'supreme':1},'passenger_hard_cap':2000,'normal_passenger_occupancy':[1200,2000],'crew_including_player':400,'player_room':'Shared with an existing crew member within the same 400; roommate story remains deferred','canonical_species':['Koblin','Mantelid','Human','Baelin','Munko','Mindo'],'source_priority':'Latest user decisions override older blueprint or design-document capacity/private-player-room labels. Catalogue components do not assign rooms, berths or persons.'}
(ROOT/'CATEGORY_COVERAGE.json').write_text(json.dumps(ledger,indent=2)+'\n')
lines=['# Catalogue category coverage','','The demonstrated catalogue quality is the user-supported baseline for larger asset delivery (2 October 2026, 16:08 UTC; message `Sentinel_1f1516ffa9a08191a5f37800301a001c`). This supports expanding the collections while recovery continues. It does not approve a finished ship, installed room, gameplay or native performance.','',f'Each of the {count} designs has one primary planning category. Integrated subparts and derivative copies are not counted again. These counts measure coverage, not completion.','','| Existing family | Architecture / transitions | Furnishings | Fixtures | Equipment | Purposeful props | Total |','|---|---:|---:|---:|---:|---:|---:|']
for row in rows:
 c=row['primary_category_counts'];lines.append('| '+row['title']+' | '+' | '.join(str(c[k]) for k in totals)+' | '+str(row['unique_designs'])+' |')
lines += ['| Total | '+' | '.join(str(totals[k]) for k in totals)+' | '+str(count)+' |','','## Useful gaps for successive batches','']
for row in rows:lines.append('- **'+row['title']+':** '+row['next_useful_coverage']+'.')
lines += ['','These directions support district-specific needs, not mechanical filling of every category. The user clarified at 16:50 UTC on 2 October that assets and district planning must work together (Sentinel_8f46f68ad3c88191b3568d463bcc0e91). Variants must change useful silhouette, activity, mounting, reach, privacy or connection decisions. Recoloring, extra tessellation and repeated stock do not create new designs. Preserve the coordinated vessel language and the difference between guest comfort and practical staff spaces.','','The Batch08 readiness archive is durably backed up. Each subsequent bounded batch retains editable Blender source, actual GLB review, independent checks and durable backup. The eventual real-room and neighborhood passes remain necessary. Exact IDs, classifications and approval provenance are in `CATEGORY_COVERAGE.json`.']
lines += ['','## Governing programme','', 'Use the latest user decisions over older diagram labels: 18 decks; 1,000 guest units including 50 deluxe, 25 premium, 5 royalty and 1 supreme; a hard 2,000-passenger onboard cap with normal occupancy 1,200–2,000; and 400 crew including the player. The player shares with an existing crew member within that total, while roommate story remains deferred. Koblin, Mantelid, Human, Baelin, Munko and Mindo remain the six species. Component counts assign no rooms, berths or population.']
(ROOT/'CATEGORY_COVERAGE.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'unique_designs':count,'primary_category_totals':totals},indent=2))
