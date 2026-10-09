"""Reconcile installed descriptors with exact-source focused receipts."""
from pathlib import Path
import json,datetime,hashlib
G=Path(__file__).resolve().parents[1];p=G/'docs/RECEIVED_SECTION_INTEGRATION_STATUS.json';d=json.loads(p.read_text());defs=json.loads((G/'data/architecture/received_sections.json').read_text());sections={s['programme_key']:s for s in defs['sections']};passed=0
completion_path=G/'docs/RECEIVED_SECTION_INTEGRATION_COMPLETION.json'
completion=json.loads(completion_path.read_text()) if completion_path.exists() else {}
combined_current=bool(completion) and all((G/path).is_file() and hashlib.sha256((G/path).read_bytes()).hexdigest()==sha for path,sha in completion.get('source_pins',{}).items())
for row in d['rows']:
 key=row['programme_key']
 if key not in sections:continue
 source=sections[key];paths=[G/f'artifacts/received_entry_{key}.json']
 if key=='D02_directory_09':paths.append(G/'artifacts/solar_entry_walk.json')
 if key=='D02_directory_10':paths.append(G/'artifacts/inspection_entry_walk.json')
 receipts=[p for p in paths if p.exists()]
 assert receipts,('Missing receipt',key)
 receipt=json.loads(receipts[0].read_text());assert receipt.get('status')=='PASS',(key,receipt)
 if 'source_sha256' in receipt:assert receipt['source_sha256']==source['source_sha256']
 row.update(status='installed_focused_entry_return_pass_combined_check_pending',fresh_runtime_pass=False,focused_runtime_pass=True,evidence=str(receipts[0].relative_to(G)),final_art_approved=False);passed+=1
 if combined_current:row.update(status='installed_focused_walk_and_combined_entry_fitment_pass',fresh_runtime_pass=True,combined_evidence='artifacts/received_sections_combined.json')
 d['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
d.update(new_candidates=len(sections),focused_passes=passed,not_yet_installed=60-2-len(sections));p.write_text(json.dumps(d,indent=2)+'\n');print({'focused':passed,'existing':2,'remaining':d['not_yet_installed']})
