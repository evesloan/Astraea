from pathlib import Path
import json,hashlib,shutil,zipfile,datetime
E=Path('/workspace/ship-delivery-20261019');R=Path('/workspace/Astraea');D=E/'Astraea-Integrated-Construction';V=R/'Game/docs/validation/ship_delivery_20261019'
for n in ['SCENE_INCLUSION.json','PACK_SOURCE_INTEGRITY.json','PACK_RESOURCE_INTEGRITY.json','PACK_IMPORT_METADATA.json','PACK_SCENE_INCLUSION.json']:
 assert json.loads((E/n).read_text())['status']=='PASS',n
 shutil.copy2(E/n,D/n);shutil.copy2(E/n,V/n)
for n in ['export.log','pack-inclusion.log','PACK_SOURCE_PINS.json','verify_pack.gd','finalize_package.py','repack_with_sources.gd','repack.log','REPACK_RECEIPT.json','EXPORTED_RESOURCE_PINS.json','IMPORT_METADATA_PINS.json']:shutil.copy2(E/n,V/n)
assert hashlib.sha256((R/'Game/project.godot').read_bytes()).hexdigest()=='42dfd175fd8135e51094d66347802a51f6622475a06b4b2c11227af29884bdc0'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
files=[{'path':str(p.relative_to(D)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(D.rglob('*'))if p.is_file()and p.name!='DELIVERY_MANIFEST.json']
m={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'construction_base_commit':'32268435ecbb5380f81e96e695c5103212a07139','engine':'Godot 4.6.3 stable official','package_kind':'Portable integrated construction runtime; existing default main scene, Windows and Linux x64 launchers','source_scene_checks':1892,'pack_scene_checks':len(json.loads((E/'PACK_SCENE_INCLUSION.json').read_text())['checks']),'pack_exact_source_files':15118,'native_sources':'Retained unchanged in private GitHub production history; not duplicated into runtime archive','acceptance':'Construction inclusion only. No final graphics, Windows device, structural/physics/gameplay acceptance. D17 placement unapproved.','files':files}
(D/'DELIVERY_MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n');shutil.copy2(D/'DELIVERY_MANIFEST.json',V/'DELIVERY_MANIFEST.json')
assert 'SCRIPT ERROR:' not in (E/'pack-inclusion.log').read_text() and 'ERROR:' not in (E/'pack-inclusion.log').read_text()
a=E/'Astraea-Integrated-Construction-20261019.zip';assert not a.exists()
with zipfile.ZipFile(a,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True)as z:
 for p in sorted(D.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(E))
with zipfile.ZipFile(a)as z:
 assert z.testzip()is None
 assert len(z.infolist())==len(files)+1
receipt={'archive_name':a.name,'bytes':a.stat().st_size,'sha256':sha(a),'zip_crc_integrity':'PASS','files':len(files)+1,'manifest_sha256':sha(D/'DELIVERY_MANIFEST.json'),'construction_base_commit':m['construction_base_commit']}
(E/'ARCHIVE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');shutil.copy2(E/'ARCHIVE_RECEIPT.json',V/'ARCHIVE_RECEIPT.json');print(json.dumps(receipt,indent=2))
