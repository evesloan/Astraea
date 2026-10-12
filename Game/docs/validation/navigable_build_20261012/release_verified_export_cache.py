import zipfile,pathlib,hashlib,json,time
r=pathlib.Path('/workspace/astraea-protected-integration-20261012/Game');o=pathlib.Path('/workspace/astraea-windows-build-evidence-20261012');p=o/'Astraea_Runtime_3210f55.zip';removed=[];kept=[]
with zipfile.ZipFile(p)as z:
 names=set(z.namelist())
 for f in (r/'.godot/imported').iterdir():
  if not f.is_file():continue
  key=str(f.relative_to(r))
  if key not in names or z.getinfo(key).file_size!=f.stat().st_size:kept.append(key);continue
  b=f.read_bytes();sha=hashlib.sha256(b).hexdigest()
  if hashlib.sha256(z.read(key)).hexdigest()!=sha:kept.append(key);continue
  removed.append({'path':key,'bytes':len(b),'sha256':sha,'retained_exactly_in':str(p)});f.unlink()
report={'scope':'Task-owned reproducible engine import cache only;source/originals/receipts/backups untouched','removed_count':len(removed),'removed_bytes':sum(x['bytes']for x in removed),'exact_bytes_retained_in_verified_export':True,'removed':removed,'kept_count':len(kept),'kept':kept};(o/'GENERATED_CACHE_RELEASE_RECEIPT.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k not in ['removed','kept']})
