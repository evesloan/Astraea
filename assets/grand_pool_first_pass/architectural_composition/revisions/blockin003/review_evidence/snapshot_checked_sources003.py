"""Read-only two-thread evaluated snapshots of the three checked architecture sources."""
import json,hashlib,subprocess,datetime
from pathlib import Path
S=Path(__file__).resolve().parent/'export003';A=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_pool_first_pass/architectural_composition');build=json.loads((A/'revisions/blockin003/qa/BUILD_RECEIPT.json').read_text());assert json.loads((A/'qa/SOURCE_JOB_003.json').read_text())['status']=='BLOCKIN003_REOPEN_RETAINED_CONTACT_AND_ROOTED_SUPPORT_PASS';rows=[]
for row in build['sources']:
 p=Path(row['source']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['source_sha256'];out=S/(row['group']+'_snapshot.json');log=S/(row['group']+'_snapshot.log');assert not out.exists()and not log.exists()
 with log.open('x')as f:r=subprocess.run(['blender','--background','--threads','2','--python-exit-code','1','--python',str(S/'snapshot_source.py'),'--','--kind','architecture','--source',str(p),'--output',str(out)],stdout=f,stderr=subprocess.STDOUT,timeout=120)
 assert r.returncode==0,log;assert hashlib.sha256(p.read_bytes()).hexdigest()==row['source_sha256'];rows.append(dict(group=row['group'],snapshot_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),source_sha256=row['source_sha256']));print(row['group'],'snapshot pass',flush=True)
(S/'SNAPSHOT_RECEIPT.json').write_text(json.dumps(dict(status='THREE_INDEPENDENT_EVALUATED_SNAPSHOTS_PASS',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources=rows),indent=2)+'\n')
