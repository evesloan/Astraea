"""Compare every prior file with read-only Batch07 start receipt."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch07'
b=json.loads((OUT/'independent_start_baseline.json').read_text());changes=[];missing=[]
for r in b['files']:
 p=ROOT/r['path']
 if not p.is_file():missing.append(r);continue
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=r['sha256']:changes.append({**r,'current_sha256':h})
# Lead authorization: append-only cost/follow-up documentation, no asset/helper mutation.
append_path='standards/PERFORMANCE_FOLLOWUPS.md'
old=subprocess.check_output(['git','show',b['baseline_commit']+':'+append_path],cwd=ROOT)
now=(ROOT/append_path).read_bytes();append_ok=now.startswith(old) and b'399' in now[len(old):] and b'263' in now[len(old):]
for r in changes:
 if r['path']==append_path and append_ok:r['protected']=False;r['allowed_lead_bookkeeping']=True;r['authorized_exception']='Lead-approved append-only Batch07 performance follow-up; prior prefix unchanged'
out={'baseline_commit' :b['baseline_commit'],'compared_files':len(b['files']),'frozen_asset_material_and_coordinate_files':sum(r['protected'] for r in b['files']),'changed_prior_files':changes,'missing_prior_files':missing,'no_frozen_changes':not any(r['protected'] for r in changes+missing),'all_other_changes_authorized':not missing and all(r['allowed_lead_bookkeeping'] for r in changes),'scope':b['scope'],'lead_append_only_performance_followup':append_ok}
(OUT/'independent_preservation_report.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['compared_files','frozen_asset_material_and_coordinate_files','no_frozen_changes','all_other_changes_authorized']},indent=2))
