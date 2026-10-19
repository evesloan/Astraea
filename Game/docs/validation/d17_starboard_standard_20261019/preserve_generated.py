from pathlib import Path
import subprocess,shutil,json,hashlib
R=Path('/workspace/Astraea');E=Path('/workspace/d17-starboard-integration');paths=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines();rows=[]
for f in paths:
 if 'd17_starboard'in f.lower()or f=='Game/docs/validation/CONSTRUCTION_OMISSIONS_20261019.json':continue
 p=R/f;assert p.suffix in ['.uid','.import','.png'],f
 dest=E/'generated-import-artifacts'/f;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();rows.append({'path':f,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size});shutil.move(p,dest)
(E/'GENERATED_ARTIFACTS_PRESERVED.json').write_text(json.dumps({'method':'Unrelated newly generated Godot imports/UIDs moved to external evidence; no existing tracked source removed','files':rows},indent=2)+'\n');print('preserved',len(rows))
