"""Inventory the new source-only package; never copy to catalogue or Game."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');assert str(R)=='/workspace/scratch/375c2e438292/engineering-dense-bays'
root='assets/secondary_engineering_section/dense_bays_candidate';assert not (C/root).exists(),'An existing candidate must never be overwritten'
exclude={'COPY_ALLOWLIST.json','DELIVERY_HASHES.json','DELIVERY_HASHES.sha256'}
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or p.name in exclude or '__pycache__'in p.parts:continue
 assert not p.is_symlink();relative=str(p.relative_to(R));files.append({'relative_path':relative,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
inventory={'scope':'Frozen reusable equipment source; flat-room direction superseded. No runtime or visual adoption.','files':files,'count':len(files),'total_bytes':sum(f['bytes'] for f in files)}
(R/'DELIVERY_HASHES.json').write_text(json.dumps(inventory,indent=2)+'\n');(R/'DELIVERY_HASHES.sha256').write_text(''.join(f["sha256"]+'  '+f['relative_path']+'\n' for f in files))
allow={'scope':'Proposed exact new-source copy only after parent approval and protected write permission. Destination absent when inventoried. No copy performed; never overwrite original AST-ENG-008, essentials, registry or Game.','package_root':str(R),'proposed_new_root':root,'catalogue_id':'AST-ENG-008','family':'secondary_engineering_section','derivative':'dense_bays','copy_files':[dict(source=str(R/f['relative_path']),proposed_catalogue_destination=root+'/'+f['relative_path'],**f) for f in files]}
for name in ['DELIVERY_HASHES.json','DELIVERY_HASHES.sha256']:
 p=R/name;allow['copy_files'].append({'source':str(p),'relative_path':name,'proposed_catalogue_destination':root+'/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(R/'COPY_ALLOWLIST.json').write_text(json.dumps(allow,indent=2)+'\n');print(json.dumps({'files':len(files),'total_bytes':inventory['total_bytes'],'copy_allowlist_sha256':hashlib.sha256((R/'COPY_ALLOWLIST.json').read_bytes()).hexdigest()},indent=2))
