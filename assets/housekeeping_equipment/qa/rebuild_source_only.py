"""Author clean source-only reconstruction, exact declared originals; independent review is separate."""
from pathlib import Path
import json,hashlib,shutil,subprocess
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stage=BASE/'qa/source_only_r08/catalogue'
if stage.exists():raise RuntimeError('Refuse to reuse seeded stage; choose a new empty revision')
stage.mkdir(parents=True);inputs=json.loads((BASE/'dependency_manifest.json').read_text())['inputs'];copied=[]
for row in inputs:
 p=CAT/row['path_from_catalogue_root'];assert sha(p)==row['sha256'];dst=stage/row['path_from_catalogue_root'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);copied.append({'path':row['path_from_catalogue_root'],'sha256':sha(dst)})
seed_files=[str(p.relative_to(stage))for p in stage.rglob('*')if p.is_file()];assert len(seed_files)==len(copied);log=BASE/'qa/source_only_build_r08.log'
with log.open('w')as f:r=subprocess.run(['blender','--background','--threads','1','--python-exit-code','1','--python',str(stage/'assets/housekeeping_equipment/source/build_housekeeping_equipment.py')],stdout=f,stderr=subprocess.STDOUT)
assert r.returncode==0
rebuilt=stage/'assets/housekeeping_equipment';outputs=[]
for rel in ['marker_api.json','collision_proposals.json','actor_proxies/body_collision_subset.json','source/cloth_controls.png','source/rack_controls.png']+[str(p.relative_to(BASE))for p in sorted((BASE/'exports').glob('*.glb'))]:
 outputs.append({'path':rel,'original_sha256':sha(BASE/rel),'rebuilt_sha256':sha(rebuilt/rel),'byte_identical':sha(BASE/rel)==sha(rebuilt/rel)})
result={'inputs':copied,'seed_files':seed_files,'seed_count':len(seed_files),'prior_generated_geometry_or_art_seeds':False,'generator_exit':r.returncode,'outputs':outputs,'all_outputs_byte_identical':all(r['byte_identical']for r in outputs),'scope':'Actual isolated reconstruction from original13 input files; source semantics independently reloaded by reviewer, not byte identity of compressed blend timestamps/path metadata'}
(BASE/'qa/source_only_rebuild.json').write_text(json.dumps(result,indent=2)+'\n');print(result['all_outputs_byte_identical'])
