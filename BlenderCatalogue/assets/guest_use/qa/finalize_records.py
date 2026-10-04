"""Freeze production and review-media hashes; never alter source or GLB geometry."""
from pathlib import Path
import json,hashlib
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
validation=json.loads((BASE/'qa/glb_validation.json').read_text());byfile={r['file']:r for r in validation['results']};records=[]
for p in sorted(BASE.glob('AST-GST-*.manifest.json')):
 rec=json.loads(p.read_text());v=byfile[rec['export']];rec['exported_triangles']=v['triangle_count'];rec['evaluated_triangles']=v['triangle_count'];rec['runtime_material_group_meshes']=v['runtime_mesh_count'];rec['runtime_primitive_count']=v['runtime_primitive_count'];rec['bounds_gltf_y_up']=v['bounds_gltf_y_up'];rec['source_sha256']=sha(BASE/rec['source']);rec['glb_sha256']=sha(BASE/rec['export']);rec['generator_sha256']=sha(BASE/rec['generator']);p.write_text(json.dumps(rec,indent=2)+'\n');records.append(rec)
(BASE/'manifest.json').write_text(json.dumps({'family':'guest_use','revision':'guest-use-01','assets':records},indent=2)+'\n')
inputs=[CAT/'standards/materials.py',CAT/'materials/material_manifest.json']+[CAT/'materials'/r['base_color_file']for r in json.loads((CAT/'materials/material_manifest.json').read_text())['materials'].values()]
prod=[p for p in BASE.rglob('*')if p.is_file()and 'qa'not in p.relative_to(BASE).parts and p.name not in ('dependency_manifest.json','SHA256SUMS.txt')]
dep={'scope':'Production package and source-only rebuild dependencies; review images and QA scripts excluded from production inputs','generator_command_from_catalogue_root':'blender --background --threads 2 --python-exit-code 1 --python assets/guest_use/source/build_guest_use.py','external_input_files':[{'path_from_catalogue_root':str(p.relative_to(CAT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in inputs],'files':[{'path':str(p.relative_to(BASE)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(prod)],'all_under_8MB':all(p.stat().st_size<8_000_000 for p in prod+inputs)}
(BASE/'dependency_manifest.json').write_text(json.dumps(dep,indent=2)+'\n')
evidence=BASE/'qa/render_evidence.json'
if evidence.exists():
 ev=json.loads(evidence.read_text());media=[]
 for name,r in ev['views'].items():
  p=BASE/'qa'/f'{name}.png'
  if p.exists():media.append({'path':str(p.relative_to(BASE)),'sha256':sha(p),'bytes':p.stat().st_size,'source_sha256':r['source_sha256_at_capture'],'glb_sha256':r['glb_sha256'],'camera':r['camera'],'intentional_crop':r['intentional_crop']})
 (BASE/'qa/review_media_manifest.json').write_text(json.dumps({'scope':'Labelled actual imported-GLB Blender component evidence, not game screenshots','files':media},indent=2)+'\n')
files=sorted(p for p in BASE.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt'and p.suffix not in('.log','.pyc')and '__pycache__'not in p.parts)
(BASE/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(BASE))+'\n'for p in files))
print('PRODUCTION_FROZEN',len(prod),'FILES',[(r['catalogue_id'],r['exported_triangles'])for r in records])
