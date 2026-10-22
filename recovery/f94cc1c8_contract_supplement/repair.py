"""Restore only missing frozen contract inputs; Python 3.9+, standard library."""
import argparse,hashlib,json,sys
from pathlib import Path

def digest(data): return hashlib.sha256(data).hexdigest()
def inside(root,relative):
    p=root/relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or root.resolve() not in (p.resolve(), *p.resolve().parents):
        raise ValueError('Unsafe path: '+relative)
    return p

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',required=True,type=Path)
    ap.add_argument('--apply',action='store_true',help='Write missing files after complete preflight; otherwise inspect only')
    args=ap.parse_args();repo=args.repo.resolve();here=Path(__file__).resolve().parent
    data=json.loads((here/'SUPPLEMENT.json').read_text(encoding='utf-8'))
    manifest=inside(repo,data['contract_manifest']);raw=manifest.read_bytes()
    if digest(raw)!=data['contract_manifest_sha256']:raise ValueError('Frozen manifest mismatch; no files written')
    contracts=json.loads(raw);expected={r['path']:r for r in contracts};missing=[]
    for row in contracts:
        p=inside(repo,'Game/'+row['path'].removeprefix('res://'))
        if p.exists():
            if not p.is_file() or digest(p.read_bytes())!=row['sha256']:raise ValueError('Existing mismatch: '+row['path']+'; no files written')
        else:missing.append(row['path'])
    supplemental={r['path']:r for r in data['files']}
    unexpected=set(missing)-set(supplemental)
    if unexpected:raise ValueError('Missing files outside supplement: '+str(sorted(unexpected)))
    pending=[];sources={}
    for path in missing:
        row=supplemental[path]
        if row['sha256']!=expected[path]['sha256'] or row['bytes']!=expected[path]['bytes']:raise ValueError('Supplement/manifest disagreement: '+path)
        if 'payload' in row:blob=inside(here,row['payload']).read_bytes()
        else:
            name=row['source']
            if name not in sources:
                b=inside(repo,name).read_bytes()
                if digest(b)!=row['source_sha256']:raise ValueError('Retained GLB mismatch: '+name)
                sources[name]=b
            b=sources[name];blob=b[row['offset']:row['offset']+row['length']]
        if len(blob)!=row['bytes'] or digest(blob)!=row['sha256']:raise ValueError('Recovered bytes mismatch: '+path)
        pending.append((inside(repo,'Game/'+path.removeprefix('res://')),blob))
    if args.apply:
        for p,blob in pending:
            p.parent.mkdir(parents=True,exist_ok=True)
            # Exclusive creation: a concurrent survivor is never overwritten.
            with p.open('xb') as f:f.write(blob)
        for row in contracts:
            if digest(inside(repo,'Game/'+row['path'].removeprefix('res://')).read_bytes())!=row['sha256']:raise ValueError('Post-write verification failed: '+row['path'])
    print(json.dumps({'status':'PASS' if args.apply or not missing else 'READY_TO_MATERIALIZE','contracts':len(contracts),'missing_before':len(missing),'written':len(pending)if args.apply else 0,'all_contracts_match':args.apply or not missing,'existing_files_overwritten':0,'frozen_manifest_changed':False}))
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError) as e:print('REFUSED: '+str(e),file=sys.stderr);sys.exit(2)
