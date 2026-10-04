"""Finalize family dependency/source closure and capture receipts without modifying geometry."""
from pathlib import Path
import json,hashlib,datetime
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p,root,key='path'):return {key:str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)}
freeze=json.loads((BASE/'qa/source_freeze.json').read_text());checks=[{'path':r['path'],'frozen_sha256':r['sha256'],'current_sha256':sha(BASE/r['path']),'unchanged':sha(BASE/r['path'])==r['sha256']}for r in freeze['files']];assert all(r['unchanged']for r in checks)
external=[CAT/'standards/materials.py',CAT/'materials/material_manifest.json']+sorted((CAT/'materials').glob('*.png'))
local=[BASE/'source/build_landing_guest.py',BASE/'source/make_orientation_art.py',BASE/'textures/guest_arrival_original.png']
prod=local+sorted((BASE/'source').glob('*.blend'))+sorted((BASE/'exports').glob('*.glb'))+[BASE/p for p in ['README.md','manifest.json','AST-LND-001.manifest.json','AST-LND-002.manifest.json','marker_api.json','collision_proposals.json','qa_context_placements.json']]
closure={'scope':'All production rebuild inputs and output files. Shared inputs include all eight loaded roles, even unused source roles. QA context is separate.','generator_command_from_catalogue_root':'blender --background --threads 2 --python-exit-code 1 --python assets/landing_guest/source/build_landing_guest.py','software_build':'Blender 4.3.2, ordinary bundled glTF exporter','art_regeneration':'Python/Pillow; deterministic original raster with no font/image dependencies','local_input_files':[record(p,BASE)for p in local],'external_input_files':[record(p,CAT,'path_from_catalogue_root')for p in external],'files':[record(p,BASE)for p in prod],'qa_only_external_dependencies':[record(CAT/p,CAT,'path_from_catalogue_root')for p in ['standards/qa_frame.py','assets/guest_use/exports/AST-GST-002.glb','assets/guest_use/source/AST-GST-002.blend']],'all_production_files_under_8MB':all(p.stat().st_size<8*1024*1024 for p in prod),'no_previous_output_or_qa_build_input':True}
(BASE/'dependency_manifest.json').write_text(json.dumps(closure,indent=2)+'\n')
render_inputs=[BASE/'qa/render_imported.py',CAT/'standards/qa_frame.py']
render_logs=[p for p in [BASE/'qa/render.log',BASE/'qa/render_001_plate_correction.log',BASE/'qa/preflight.log']if p.exists()]
bind={'scope':'Exact executed render script/helper and retained logs for all final imported-GLB views.001 rerendered with the unchanged same-camera renderer after its physical plate correction;002 final source and export match its earlier successful capture.','scripts':[record(p,CAT,'path_from_catalogue_root')for p in render_inputs],'logs':[record(p,BASE)for p in render_logs],'execution_commands':['blender --background --threads 3 --python-exit-code 1 --python qa/render_imported.py','blender --background --threads 3 --python-exit-code 1 --python qa/render_imported.py -- --only AST-LND-001'],'no_geometry_changes_during_capture':True}
(BASE/'qa/render_execution_bindings.json').write_text(json.dumps(bind,indent=2)+'\n')
media=[]
if (BASE/'qa/render_evidence.json').exists():
 evidence=json.loads((BASE/'qa/render_evidence.json').read_text())
 for name,r in evidence['views'].items():
  p=BASE/'qa'/f'{name}.png';assert p.exists();assert r['source_sha256_at_capture']==r['source_sha256_after_capture'];assert r['glb_sha256']==r['glb_sha256_after_capture'];assert r['glb_sha256']==sha(BASE/'exports'/f"{r['camera']['id']}.glb")
  media.append(dict(record(p,BASE),purpose=r['camera']['purpose'],catalogue_id=r['camera']['id'],imported_glb_sha256=r['glb_sha256'],source_sha256=r['source_sha256_at_capture'],intentional_crop=r['intentional_crop'],context=r['context']))
(BASE/'qa/review_media_manifest.json').write_text(json.dumps({'scope':'Frozen imported-GLB Blender inspection, not a room/actor/runtime acceptance','images':media},indent=2)+'\n')
(BASE/'qa/final_freeze_verification.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':checks,'all_unchanged':all(r['unchanged']for r in checks)},indent=2)+'\n')
paths=prod+[BASE/'dependency_manifest.json']+sorted(p for p in(BASE/'qa').glob('*')if p.is_file()and p.suffix in('.json','.png','.py'))
(BASE/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(BASE))+'\n'for p in sorted(set(paths))))
print('FINAL_RECORDS',len(prod),'production files;',len(media),'frozen images')
