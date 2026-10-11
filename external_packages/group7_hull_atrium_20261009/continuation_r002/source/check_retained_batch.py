"""Verify the first delivery byte-for-byte, including its original manifest."""
from pathlib import Path
import hashlib,json,subprocess,datetime
P=Path(__file__).resolve().parents[1];OLD=P.parent;EXPECTED='ef789ac9a669e337389c46c83562ca14bee6ba54ac9fda7d528d407606f785eb'
raw=(OLD/'RESOURCE_HASHES.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
files=json.loads(raw)['files']
for n,r in files.items():assert hashlib.sha256((OLD/n).read_bytes()).hexdigest()==r['sha256'],n
host=OLD.parents[1]
def git(*a):return subprocess.run(['git','-C',str(host),*a],capture_output=True,text=True,check=True).stdout.strip()
assert git('rev-parse','HEAD')=='a36c3c36a171b63a4f4a19efef6450d11520004a'
(P/'qa').mkdir(parents=True,exist_ok=True)
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_delivery_commit':'e6abd8100af7c56587dcf7dfb6eb85450dbcd1fe','first_delivery_manifest_sha256':EXPECTED,'first_delivery_files_checked':len(files)+1,'host_head':git('rev-parse','HEAD'),'host_branch':git('branch','--show-current'),'passed':True,'scope':'Only continuation_r002 may be authored; all first-delivery resources and manifest untouched'}
(P/'qa/retention_check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
