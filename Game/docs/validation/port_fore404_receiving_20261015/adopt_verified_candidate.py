from pathlib import Path
import json,hashlib,shutil,subprocess
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';E=Path('/workspace/astraea-protected-integration-evidence-20261012');sha=lambda b:hashlib.sha256(b).hexdigest();assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()=='e2126433d2f4b949237e254303c616bfcc4d0622';assert not subprocess.check_output(['git','-C',str(R),'diff','HEAD','--name-only']).strip();assert json.loads((E/'port_fore404_candidate315.json').read_text())['passed'];assert json.loads((D/'CANDIDATE_RUNTIME315.json').read_text())['status']=='PASS';assert json.loads((D/'NATIVE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS');assert json.loads((D/'OUTSIDE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS');pre=json.loads((D/'STAGED_LOADER_PREIMAGES.json').read_text());
for path,pin in pre.items():assert sha((G/path).read_bytes())==pin,path
writes={}
for p in(D/'import/Game').rglob('*'):
 rel=p.relative_to(D/'import/Game').as_posix()
 if p.is_file()and rel.startswith(('assets/','data/','scripts/','tests/','.godot/imported/')):
  if(G/rel).exists()and rel not in pre:assert(G/rel).read_bytes()==p.read_bytes(),rel
  writes[rel]=p.read_bytes()
(D/'INSTALLATION_PREIMAGES.json').write_text(json.dumps({p:sha((G/p).read_bytes())if(G/p).exists()else None for p in writes},indent=2)+'\n')
for path,b in writes.items():p=G/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
B=R/'BlenderCatalogue/assets/port_fore404_receiving_20261015';B.mkdir(parents=True,exist_ok=True);shutil.copytree(D/'retained_source',B/'retained_source',dirs_exist_ok=True)
assert json.loads((D/'SINGLE_ROOT_NATIVE_DELTA_VERIFICATION.json').read_text())['all_referenced_packed_image_payloads_identical']
for p in(D/'native').glob('*.blend'):shutil.copyfile(p,B/p.name)
for p in(D/'import/Game/assets/port_fore404_receiving_20261015').glob('*.glb'):shutil.copyfile(p,B/p.name)
for p in D.iterdir():
 if p.is_file()and p.suffix in['.json','.py','.gd','.log']:shutil.copyfile(p,B/p.name)
shutil.copyfile(D/'CANDIDATE_OVERLAY.zip',D/'INSTALLED_OVERLAY.zip');shutil.copyfile(D/'CANDIDATE_OVERLAY.zip',D.parent/'PORT_FORE404_ADOPTION_OVERLAY.zip');(D/'INSTALLED_FILES.json').write_text(json.dumps({p:{'bytes':len(b),'sha256':sha(b)}for p,b in writes.items()},indent=2)+'\n');print('ADOPTED_VERIFIED_PORT_FORE404',len(writes))
