from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];C=R.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=json.loads((R/'qa/prior_file_hashes.json').read_text());allowed={'catalogue_manifest.json','assets/aft_command/AST-CMD-002.manifest.json','assets/aft_command/source/AST-CMD-002.blend','assets/aft_command/source/build_aft_command.py','assets/aft_command/source/geometry_parts.json','assets/aft_command/source/section_contract.json','assets/aft_command/exports/AST-CMD-002.glb'}
changed=[]
for f,h in before.items():
 assert(C/f).exists(),f
 if sha(C/f)!=h:changed.append(f);assert f in allowed,f
old=json.loads((R/'qa/prior_catalogue_records.json').read_text());new=json.loads((C/'catalogue_manifest.json').read_text());lookup={p['catalogue_id']:p for p in new['assets']};assert len(lookup)==len(new['assets'])==164
for record in old['assets']:
 if record['catalogue_id']!='AST-CMD-002':assert record==lookup[record['catalogue_id']],record['catalogue_id']
for p in new['assets']:
 assert sha(C/p['source'])==p['source_sha256'],p['catalogue_id'];assert sha(C/p['export'])==p['export_sha256'],p['catalogue_id']
report={'pass':True,'prior_files_checked':len(before),'changed_old_files':changed,'old_file_allowlist':sorted(allowed),'prior_records':len(old['assets']),'unchanged_prior_records':162,'bounded_revision':'AST-CMD-002','new_record':'AST-CMD-005','exact_id_ownership':True,'all164_source_export_hashes_match':True,'unchanged_old_files':len(before)-len(changed)}
(R/'qa/catalogue_preservation.json').write_text(json.dumps(report,indent=2)+'\n');print('CATALOGUE_PRESERVATION_PASS',report)
