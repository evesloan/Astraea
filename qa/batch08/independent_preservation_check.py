"""Bind Batch08 to the delivered Batch07 git snapshot; never rewrite baseline assets."""
from pathlib import Path
import hashlib, json, subprocess, datetime

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'qa/batch08'
BASE='66dcaf10f105958c5cadb421d5aca15b054b98ed'
def sha(b): return hashlib.sha256(b).hexdigest()
def frozen(path):
    p=Path(path)
    return ((path.startswith('assets/') and p.suffix.lower() in {'.blend','.glb','.png','.jpg','.jpeg','.exr','.hdr'})
            or path.startswith('materials/')
            or path.startswith('standards/') and p.suffix=='.py')
snapshot=OUT/'independent_baseline_hashes.json'
if not snapshot.exists():
    rows=[]
    entries=subprocess.check_output(['git','ls-tree','-r','-z',BASE],cwd=ROOT).split(b'\0')
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    for entry in entries:
        if not entry: continue
        head,path=entry.split(b'\t',1);mode,kind,oid=head.split();path=path.decode()
        if kind!=b'blob': continue
        proc.stdin.write(oid+b'\n');proc.stdin.flush()
        header=proc.stdout.readline().split();size=int(header[-1]);content=proc.stdout.read(size);assert proc.stdout.read(1)==b'\n'
        rows.append({'path':path,'git_blob':oid.decode(),'bytes':size,'sha256':sha(content),'visual_material_source_frozen':frozen(path)})
    proc.stdin.close();proc.wait()
    snapshot.write_text(json.dumps({'baseline_commit':BASE,'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Exact bytes from durably delivered Batch07 commit, including every tracked prior file. Existing visual .blend/.glb/image assets, all material files and original standards helpers are frozen. Any metadata-only source/export exception requires explicit path and change scope plus independent semantic preservation evidence.','files':rows},indent=2)+'\n')
base=json.loads(snapshot.read_text());assert base['baseline_commit']==BASE
changed=[];missing=[]
for r in base['files']:
    p=ROOT/r['path']
    if not p.is_file():missing.append(r['path']);continue
    current=sha(p.read_bytes())
    if current!=r['sha256']:changed.append({**r,'current_sha256':current,'current_bytes':p.stat().st_size})
exceptions_path=OUT/'independent_scoped_exceptions.json'
exceptions=json.loads(exceptions_path.read_text()) if exceptions_path.exists() else {'exceptions':[]}
by_path={e['path']:e for e in exceptions['exceptions']}
for r in changed:
    r['scoped_exception']=by_path.get(r['path'])
result={'baseline_commit':BASE,'baseline_receipt_sha256':sha(snapshot.read_bytes()),'compared_files':len(base['files']),'frozen_visual_material_source_file_count':sum(r['visual_material_source_frozen'] for r in base['files']),'changed_prior_files':changed,'missing_prior_files':missing,'no_frozen_visual_material_source_changes':not any(r['visual_material_source_frozen'] for r in changed),'unapproved_frozen_changes':[r['path'] for r in changed if r['visual_material_source_frozen'] and not r['scoped_exception']],'scope':'Scope review of changed nonvisual metadata is a separate interface/collision gate; this report does not infer blanket permission from a filename.'}
(OUT/'independent_preservation_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='changed_prior_files'},indent=2))
print('Changed prior files:',*[r['path'] for r in changed],sep='\n')
