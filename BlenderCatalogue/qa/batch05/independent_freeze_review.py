from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports=json.loads((OUT/'independent_glb_report.json').read_text());manifest_checks=json.loads((OUT/'independent_manifest_checks.json').read_text());source_reports=[r for p in OUT.glob('independent_aquatic_*_blend_report.json') for r in json.loads(p.read_text())]
assets=[{'path':str(Path(r['path']).relative_to(ROOT)),'sha256':sha(Path(r['path'])),'reviewed_sha256':r['sha256'],'matches_review':sha(Path(r['path']))==r['sha256']} for r in reports+source_reports]
assert all(r['matches_review'] for r in assets)
(OUT/'independent_reviewed_assets_sha256.json').write_text(json.dumps({'status':'PASS frozen reviewed aquatic source/export bytes','assets':assets},indent=2)+'\n')
paths=set()
for folder in ['assets/aquatic_lounge','assets/aquatic_edges','assets/aquatic_float','materials/aquatic','qa/batch05/arrangement','qa/batch05/cabinet_metadata_revision']:
 for p in (ROOT/folder).rglob('*'):
  if not p.is_file() or p.suffix not in ['.blend','.glb','.png','.json','.py','.md','.txt','.log']:continue
  if any(x=='initial_rejected' or x.startswith('before_') or x=='__pycache__' for x in p.parts):continue
  paths.add(p)
for p in OUT.glob('independent_*'):
 if p.is_file() and p.name!='independent_reviewed_files.json':paths.add(p)
for rel in ['standards/aquatic_materials.py','standards/COORDINATE_CONTRACT.md','standards/coordinate_compatibility.json','tools/generate_aquatic_materials.py','batches/batch05/CONTRACT.md','batches/batch05/reference_manifest.json','references/aquatic/image(20261001-035517).png']:
 paths.add(ROOT/rel)
for rel in json.loads((OUT/'independent_authorized_metadata_exception.json').read_text())['paths']:paths.add(ROOT/rel)
for r in json.loads((OUT/'independent_visual_review.json').read_text())['reviews']:
 for im in r['images']:paths.add(ROOT/im['path'])
files=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(paths)]
(OUT/'independent_reviewed_files.json').write_text(json.dumps({'review_status':'PASS independent component and coordinate review','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_commit':'11936f59ff9a9c31392105ff81bf8feef8688496','scope':'Final aquatic artifacts/evidence and authorized cabinet metadata correction. Historical files listed only when preserved evidence was reviewed. This is a review inventory, not the durable-backup receipt.','file_count':len(files),'files':files},indent=2)+'\n');print(json.dumps({'source_export_files':len(assets),'source_export_hashes_match':True,'frozen_reviewed_files':len(files),'review':'qa/batch05/independent_review.md'},indent=2))
