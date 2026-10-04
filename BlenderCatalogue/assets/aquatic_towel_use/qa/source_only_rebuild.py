"""Start an empty, declared-input-only catalogue and compare fresh exports."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
dep=json.loads((ROOT/'dependency_manifest.json').read_text());stage=ROOT/'qa'/('source_only_stage_collision_refined' if '--collision-refined' in sys.argv else 'source_only_stage')/'catalogue'
if stage.exists():raise RuntimeError('Preserve earlier rebuild; choose a fresh stage explicitly')
stage.mkdir(parents=True)
for r in dep['inputs']:
 src=CAT/r['path_from_catalogue_root'];assert sha(src)==r['sha256'];dst=stage/r['path_from_catalogue_root'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
inputs=[str(p.relative_to(stage)) for p in stage.rglob('*') if p.is_file()]
assert not any('/qa/' in p or '/exports/' in p or p.endswith('.blend') for p in inputs)
generator=stage/'assets/aquatic_towel_use/source/build_towel_use.py'
run=subprocess.run(['blender','-b','-t','2','--python',str(generator)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(ROOT/'qa/source_only_build.log').write_text(run.stdout)
assert run.returncode==0,run.stdout[-1000:]
fresh=stage/'assets/aquatic_towel_use';comparisons=[]
for p in sorted((ROOT/'exports').glob('*.glb')):
 q=fresh/'exports'/p.name
 comparisons.append({'file':p.name,'author_sha256':sha(p),'fresh_sha256':sha(q),'byte_identical':p.read_bytes()==q.read_bytes()})
sources=[]
for p in sorted((ROOT/'source').glob('*.blend')):
 q=fresh/'source'/p.name;sources.append({'file':p.name,'fresh_source_exists':q.is_file(),'fresh_source_size':q.stat().st_size,'fresh_source_sha256':sha(q)})
collisions=[{'file':p.name,'author_sha256':sha(p),'fresh_sha256':sha(fresh/p.name),'byte_identical':p.read_bytes()==(fresh/p.name).read_bytes()} for p in sorted(ROOT.glob('*.collision_proposal.json'))]
report={'method':'Fresh empty catalogue, copied only the declared20 inputs; no QA, source blend or pre-existing output present before generator run','stage':str(stage.relative_to(ROOT)),'input_files_before_build':inputs,'dependency_manifest_sha256':sha(ROOT/'dependency_manifest.json'),'build_returncode':run.returncode,'glb_comparisons':comparisons,'collision_comparisons':collisions,'fresh_editable_sources':sources,'passed':all(r['byte_identical'] for r in comparisons+collisions) and all(r['fresh_source_exists'] for r in sources)}
(ROOT/'qa/source_only_rebuild.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
