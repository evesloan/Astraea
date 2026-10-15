from pathlib import Path
import json,hashlib,subprocess,zipfile,shutil
D=Path(__file__).parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';E=Path('/workspace/astraea-protected-integration-evidence-20261012');sha=lambda b:hashlib.sha256(b).hexdigest();assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()=='a42c632fa94364f837eaa9b82878d11f4529ed59';assert not subprocess.check_output(['git','-C',str(R),'diff','HEAD','--name-only']).strip();writes={}
for V,name,sub,pack in [(D,'vesper_fixture_support329','vesper_service_receiving_20261015','VESPER_SERVICE_ADOPTION_OVERLAY.zip'),(D/'orchard','orchard_fixture_support330','orchard_external_receiving_20261015','ORCHARD_RECEIVING_ADOPTION_OVERLAY.zip')]:
 assert json.loads((E/(name+'.json')).read_text())['passed'];r=json.loads((V/('FIXTURE_SUPPORT_RUNTIME329.json'if V==D else'FIXTURE_SUPPORT_RUNTIME330.json')).read_text());assert r['status']=='PASS';assert json.loads((V/'NATIVE_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS');assert json.loads((V/'ALL_REFERENCED_IMAGE_PAYLOADS.json').read_text())['status'].startswith('PASS')
 with zipfile.ZipFile(V/'CANDIDATE_OVERLAY.zip')as z:
  for n in z.namelist():
   b=z.read(n)
   if (G/n).exists()and n!='data/'+sub+'/NATIVE_VERIFICATION.json':assert(G/n).read_bytes()==b,n
   writes[n]=b
 path=D.parent/pack
 with zipfile.ZipFile(path)as z:merged={n:z.read(n)for n in z.namelist()}
 with zipfile.ZipFile(V/'CANDIDATE_OVERLAY.zip')as z:merged.update({n:z.read(n)for n in z.namelist()})
 with zipfile.ZipFile(V/'MERGED_ADOPTION_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
  for n,b in merged.items():z.writestr(n,b)
 shutil.copyfile(V/'MERGED_ADOPTION_OVERLAY.zip',path)
(D/'INSTALLATION_PREIMAGES.json').write_text(json.dumps({n:sha((G/n).read_bytes())if(G/n).exists()else None for n in writes},indent=2)+'\n')
for n,b in writes.items():p=G/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
B=R/'BlenderCatalogue/assets/receiving_fixture_support_20261015';B.mkdir(parents=True,exist_ok=True)
for V,sub in [(D,'vesper'),(D/'orchard','orchard')]:
 dest=B/sub;dest.mkdir(exist_ok=True)
 for p in list((V/'native').glob('*.blend'))+list(V.glob('*.py'))+list(V.glob('*.json'))+list(V.glob('*.log'))+list((V/'import/Game/assets').rglob('*.glb')):shutil.copyfile(p,dest/p.name)
shutil.copyfile(D.parent/'vesper_service_receiving_20261015/visual_review/LIBRARY_DELIVERY_RECEIPT.json',B/'R001_LIBRARY_DELIVERY_RECEIPT.json');(D/'INSTALLED_FILES.json').write_text(json.dumps({n:{'bytes':len(b),'sha256':sha(b)}for n,b in writes.items()},indent=2)+'\n');print('ADOPTED_TWO_SUPPORTED_FIXTURE_VARIANTS',len(writes))
