"""Materialize a bounded list of pinned Git objects, never touch the live checkout."""
import hashlib, json, subprocess, sys
from pathlib import Path
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
G=P/'retention/canonical_git'
revision=sys.argv[2] if len(sys.argv)>2 else None
assert revision in [None,'9d6f85']
D=P/('dependencies/canonical_9d6f85' if revision else 'dependencies/canonical_77a745')
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def git(*a, input=None):
    return subprocess.run(['git','-C',str(G),*a],input=input,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
tree_file=P/('qa/canonical_tree_9d6f85.json' if revision else 'qa/canonical_tree.json')
record_file=P/('qa/materialized_9d6f85.json' if revision else 'qa/materialized_canonical.json')
tree=json.loads(tree_file.read_text(encoding='utf-8'))
request=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
paths={r['path']:r['sha1'] for r in tree['files']}
record=json.loads(record_file.read_text(encoding='utf-8')) if record_file.exists() else {'commit':tree['commit'],'files':[]}
done={r['path']:r for r in record['files']}
pending=[]
def save(s,h,b,method):
    assert blob(b)==h,s
    out=D/s;out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():assert out.read_bytes()==b, 'Refuse overwrite: '+s
    else:out.write_bytes(b)
    done[s]={'path':s,'git_blob':h,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'method':method}
for s in request:
    h=paths[s]
    if s in done:
        assert blob((D/s).read_bytes())==h,s
        continue
    found=False
    for candidate in [ROOT/s,P/'dependencies/canonical_77a745'/s,ROOT/'external_packages/shopping_promenade_20261009/dependencies'/s,ROOT/'external_packages/aquatic_district_20261009/dependencies'/s]:
        if not candidate.is_file():continue
        b=candidate.read_bytes()
        if blob(b)==h:save(s,h,b,'existing exact bytes');found=True;break
        n=b.replace(b'\r\n',b'\n')
        if blob(n)==h:save(s,h,n,'existing CRLF normalized to exact pinned bytes');found=True;break
    if not found:pending.append((s,h))
if pending:
    objects=sorted(set(h for _,h in pending))
    git('-c','fetch.negotiationAlgorithm=noop','fetch','origin','--no-tags','--no-write-fetch-head','--recurse-submodules=no','--filter=blob:none','--stdin',input=('\n'.join(objects)+'\n').encode())
    for s,h in pending:save(s,h,git('cat-file','blob',h),'bounded fetch exact pinned object')
record['files']=sorted(done.values(),key=lambda r:r['path'])
record_file.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'requested':len(request),'fetched':len(pending),'total':len(done)}))
