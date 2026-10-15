from pathlib import Path
import json,hashlib,shutil,zipfile
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';T=D/'import/Game';sha=lambda b:hashlib.sha256(b).hexdigest();prior=json.loads((D/'INSTALLED_FILES.json').read_text());writes={p:(G/p).read_bytes()for p in prior}
for path,row in prior.items():assert sha(writes[path])==row['sha256'],path
assert'ERROR:'not in(D/'IMPORT002.log').read_text();assert json.loads((D/'NATIVE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS');assert json.loads((D/'OUTSIDE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS')
for p in T.rglob('*'):
 rel=p.relative_to(T).as_posix()
 if p.is_file()and rel.startswith(('assets/','scripts/','data/','.godot/imported/')):writes[rel]=p.read_bytes()
(D/'INSTALLATION_R002_PREIMAGES.json').write_text(json.dumps({p:sha((G/p).read_bytes())if(G/p).exists()else None for p in writes},indent=2)+'\n')
for path,b in writes.items():p=G/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
B=R/'BlenderCatalogue/assets/arrivals_staff_receiving_20261015'
for p in D.iterdir():
 if p.is_file()and p.suffix in['.py','.json','.glb']:
  dest=B/p.name
  if dest.exists()and dest.read_bytes()!=p.read_bytes()and not(B/(p.stem+'_r001'+p.suffix)).exists():shutil.copyfile(dest,B/(p.stem+'_r001'+p.suffix))
  shutil.copyfile(p,dest)
for p in(D/'native').glob('*.blend'):shutil.copyfile(p,B/p.name)
for p in(T/'assets/arrivals_staff_receiving_20261015').glob('*.glb'):shutil.copyfile(p,B/p.name)
with zipfile.ZipFile(D/'INSTALLED_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for path,b in writes.items():z.writestr(path,b)
shutil.copyfile(D/'INSTALLED_OVERLAY.zip',D.parent/'ARRIVALS_STAFF_ADOPTION_OVERLAY.zip');shutil.copyfile(D/'INSTALLED_FILES.json',D/'INSTALLED_FILES_r001.json');(D/'INSTALLED_FILES.json').write_text(json.dumps({p:{'bytes':len(b),'sha256':sha(b)}for p,b in writes.items()},indent=2)+'\n');print('INSTALLED_R002_PENDING',len(writes))
