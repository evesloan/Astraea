from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path.cwd();G=R/'Game';O=R/'recovery/exact_contact_sharing_20261026';E=R.parent/'Astraea-resume-20261025'
for name in ['performance-live-owner-cost-001','performance-contact-sharing-002','performance-contact-sharing-003','performance-contact-sharing-004','performance-contact-invalidation-001','performance-contact-production-001','performance-contact-production-002','performance-contact-contracts-001']:
 src=E/name;dst=O/'evidence'/name;dst.mkdir(parents=True,exist_ok=True)
 for p in src.iterdir():
  if p.is_file():shutil.copy2(p,dst/p.name)
rows=json.loads((G/'scripts/runtime_contracts_20261022/SOURCE_CONTRACTS.json').read_bytes());bad=[]
for row in rows:
 p=G/row['path'].removeprefix('res://');data=p.read_bytes() if p.exists() else b''
 if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:bad.append(row['path'])
(O/'CONTRACT_VERIFICATION.json').write_text(json.dumps({'count':len(rows),'mismatches':bad},indent=2));print({'contracts':len(rows),'mismatch_count':len(bad),'mismatches':bad[:10]})
