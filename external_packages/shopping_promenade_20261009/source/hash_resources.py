from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1]
files={}
for f in sorted(P.rglob('*')):
 r=f.relative_to(P)
 if r.parts[:2]==('preview','exports'):continue
 if not f.is_file() or any(k in r.parts for k in ['retention','.godot','__pycache__']) or f.suffix in ['.blend1','.pyc','.import'] or str(r)=='RESOURCE_HASHES.json':continue
 files[r.as_posix()]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
(P/'RESOURCE_HASHES.json').write_text(json.dumps({'algorithm':'sha256','scope':'Bounded shopping delivery; caches and independent Git store excluded','files':files},indent=2)+'\n',encoding='utf-8')
print('HASHED',len(files))
