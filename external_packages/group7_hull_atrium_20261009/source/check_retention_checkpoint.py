"""Verify retained inputs and earlier deliveries without operating their Git stores."""
from pathlib import Path
import hashlib,json,subprocess,datetime
P=Path(__file__).resolve().parents[1];host=P.parents[1]
initial=json.loads((P/'qa/initial_retention.json').read_text())
counts={'earlier_package_files_reverified':0,'earlier_manifests_reverified':0,'pinned_inputs_reverified':0}
for package,record in initial['completed_package_retention'].items():
 d=P.parent/package
 assert hashlib.sha256((d/'RESOURCE_HASHES.json').read_bytes()).hexdigest()==record['manifest_sha256'],package
 counts['earlier_manifests_reverified']+=1
 for name,h in record['files'].items():
  assert hashlib.sha256((d/name).read_bytes()).hexdigest()==h,(package,name)
  counts['earlier_package_files_reverified']+=1
for name,dep in [('materialized_canonical.json','canonical_77a745'),('materialized_9d6f85.json','canonical_9d6f85')]:
 for r in json.loads((P/'qa'/name).read_text())['files']:
  assert hashlib.sha256((P/'dependencies'/dep/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
  counts['pinned_inputs_reverified']+=1
def git(*a):return subprocess.run(['git','-C',str(host),*a],capture_output=True,text=True,check=True).stdout.strip()
head=git('rev-parse','HEAD');branch=git('branch','--show-current')
assert head==initial['host_head'] and branch==initial['host_branch']
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host_head':head,'host_branch':branch,**counts,'source_ownership':'Only owned Group7 package changed; no host reset/restore/fetch, import, engine run or competing backup worker'}
(P/'qa/checkpoint_retention.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
