from pathlib import Path
import json,zipfile,shutil,hashlib
D=Path(__file__).resolve().parent;G=D/'runtime_import/Game';r=json.loads((D/'NATIVE_RECEIVER_VERIFICATION.json').read_text());stem=Path(r['file']).stem;writes={}
assert json.loads((D/'BATCH_GEOMETRY_VERIFICATION.json').read_text())['status'].startswith('PASS')
for folder in ['assets/dining_service_receiving_20261015','.godot/imported']:
 for p in (G/folder).rglob('*'):
  if p.is_file()and p.name.startswith(stem):writes[str(p.relative_to(G))]=p.read_bytes()
writes['scripts/dining_service_receiving_20261015/package.gd']=(D/'receiver_package.gd').read_bytes();writes['data/dining_service_receiving_20261015/NATIVE_RECEIVER_VERIFICATION.json']=(D/'NATIVE_RECEIVER_VERIFICATION.json').read_bytes();path=D/'SERVICE_CANDIDATE_OVERLAY.zip'
if path.exists()and not(D/'SERVICE_CANDIDATE_OVERLAY_failed267.zip').exists():shutil.copyfile(path,D/'SERVICE_CANDIDATE_OVERLAY_failed267.zip')
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for name,data in writes.items():z.writestr(name,data)
 z.write(D/'native_import/Game/assets/dining_service_receiving_20261015'/r['raw_authoring_file'],'validation/dining_service_receiving_20261015/'+r['raw_authoring_file'])
(D/'CANDIDATE_RUNTIME_FILES.json').write_text(json.dumps({name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}for name,data in writes.items()},indent=2)+'\n');print('PASS_CANDIDATE_PACKAGED',r['file'],len(writes),path.stat().st_size)
