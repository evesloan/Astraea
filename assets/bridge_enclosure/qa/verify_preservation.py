from pathlib import Path
import json,hashlib
C=Path(__file__).resolve().parents[3];R=C/'assets/bridge_enclosure';P=C/'assets/bridge_platform';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((R/'qa/prior_003_parts.json').read_text());after=json.loads((P/'source/geometry_parts.json').read_text())['parts'];allow=set(before['allowlist_assemblies']);changed=[];unchanged=[]
assert len(after)==len(before['parts'])==3394
for part in after:
 old=before['parts'][part['name']];h=hashlib.sha256(json.dumps(part,sort_keys=True).encode()).hexdigest()
 if h==old['sha256']:unchanged.append(part['name']);continue
 assert part['assembly']in allow,part['name'];a=old['world_aabb'];b=part['world_aabb'];assert all(a[k]==b[k]for k in[0,1,4,5]);assert b[2:4]==([107.08,107.12]if '_GuardCap_'in part['assembly']else[106.45,107.1]),part['name'];changed.append({'name':part['name'],'assembly':part['assembly'],'before_aabb':a,'after_aabb':b,'before_record_sha256':old['sha256'],'after_record_sha256':h})
assert set(p['assembly']for p in changed)==allow
D=json.loads((P/'source/section_contract.json').read_text());assert D['windows']==before['windows'];assert D['light_markers']==before['light_markers'];assert len(D['windows'])==24 and len(D['light_markers'])==20
files=json.loads((R/'qa/prior_file_hashes.json').read_text());diff=[]
for f,h in files.items():
 if f.startswith('assets/bridge_platform/') or f=='catalogue_manifest.json':continue
 assert (C/f).is_file() and sha(C/f)==h,f
M=json.loads((C/'catalogue_manifest.json').read_text());prior=json.loads(__import__('subprocess').check_output(['git','show','dc8b89d8d25bb6b973961a1fff27d27b0aa839e6:catalogue_manifest.json'],cwd=C));a={x['catalogue_id']:x for x in M['assets']};b={x['catalogue_id']:x for x in prior['assets']};assert all(a[k]==v for k,v in b.items()if k!='AST-CMD-003')
report={'pass':True,'003_before_part_count':3394,'003_after_part_count':len(after),'changed_part_count':len(changed),'unchanged_part_count':len(unchanged),'allowed_changed_assemblies':sorted(allow),'changed_parts':changed,'unchanged_part_names':unchanged,'all24_bypass_window_records_unchanged':True,'all20_fixture_records_unchanged':True,'all_nonallowlisted_part_records_byte_exact':True,'other161_catalogue_records_unchanged':True,'unrelated_files_byte_exact':True,'protected_unrelated_file_count':sum(not(f.startswith('assets/bridge_platform/')or f=='catalogue_manifest.json')for f in files),'method':'Canonical per-part full-record SHA256 including all vertices, role, group and bounds; exact catalogue records and protected-file bytes; exact triangle proof separately.'}
(R/'qa/preservation_comparison.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items()if k not in ['changed_parts','unchanged_part_names']})
