from pathlib import Path
import json,hashlib,shutil,subprocess,zipfile
D=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';E=Path('/workspace/astraea-protected-integration-evidence-20261012');sha=lambda b:hashlib.sha256(b).hexdigest();assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()=='1dea2c7531d3dee7d00cac8057e5812da6456eb5';assert not subprocess.check_output(['git','-C',str(R),'diff','HEAD','--name-only']).strip();assert json.loads((E/'vesper_candidate325.json').read_text())['passed'];d=json.loads((D/'CANDIDATE_RUNTIME325.json').read_text());assert d['status']=='PASS'and not d['unexplained_contacts']and not d['new_floor_preimages'];assert json.loads((D/'NATIVE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS');pre=json.loads((D/'STAGED_LOADER_PREIMAGES.json').read_text())
for n,pin in pre.items():assert sha((G/n).read_bytes())==pin,n
writes={}
with zipfile.ZipFile(D/'CANDIDATE_OVERLAY.zip')as z:
 for n in z.namelist():
  b=z.read(n)
  if (G/n).exists()and n not in pre:assert (G/n).read_bytes()==b,n
  writes[n]=b
(D/'INSTALLATION_PREIMAGES.json').write_text(json.dumps({n:sha((G/n).read_bytes())if(G/n).exists()else None for n in writes},indent=2)+'\n')
for n,b in writes.items():p=G/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
B=R/'BlenderCatalogue/assets/vesper_service_receiving_20261015';B.mkdir(parents=True,exist_ok=True)
for p in list((D/'native').glob('*.blend'))+list((D/'import/Game/assets/vesper_service_receiving_20261015').glob('*.glb'))+list(D.glob('*.py'))+list(D.glob('*.json')):shutil.copyfile(p,B/p.name)
shutil.copytree(D/'visual_review',B/'visual_review',dirs_exist_ok=True)
shutil.copyfile(D/'CANDIDATE_OVERLAY.zip',D/'INSTALLED_OVERLAY.zip');shutil.copyfile(D/'CANDIDATE_OVERLAY.zip',D.parent/'VESPER_SERVICE_ADOPTION_OVERLAY.zip');(D/'INSTALLED_FILES.json').write_text(json.dumps({n:{'bytes':len(b),'sha256':sha(b)}for n,b in writes.items()},indent=2)+'\n');print('ADOPTED_VERIFIED_VESPER',len(writes))
