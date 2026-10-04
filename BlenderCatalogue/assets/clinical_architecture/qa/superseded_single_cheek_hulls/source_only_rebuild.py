"""Fresh source-only reconstruction: no new .blend, GLB, local textures or QA data as inputs."""
from pathlib import Path
import subprocess,shutil,json,hashlib,sys
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];STAGE=BASE/'qa/source_only_stage/catalogue';OUT=STAGE/'assets/clinical_architecture'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not STAGE.exists(),'Use a fresh named stage, never conceal a prior failed stage'
inputs=[CAT/'standards/materials.py',CAT/'standards/care_materials.py',CAT/'materials/material_manifest.json',CAT/'materials/care/source/generate_care_materials.py',BASE/'source/build_clinical_architecture.py',BASE/'source/make_clinical_textures.py']
inputs.extend(CAT/'materials'/r['base_color_file']for r in json.loads((CAT/'materials/material_manifest.json').read_text())['materials'].values())
for p in inputs:
 dest=STAGE/p.relative_to(CAT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(OUT/'qa').mkdir(parents=True,exist_ok=True)
initial=[str(p.relative_to(STAGE))for p in STAGE.rglob('*')if p.is_file()];assert not any(p.endswith(('.blend','.glb'))or '/qa/'in p or '/textures/'in p for p in initial)
commands=[[sys.executable,str(STAGE/'materials/care/source/generate_care_materials.py')],[sys.executable,str(OUT/'source/make_clinical_textures.py')],['blender','--background','--threads','2','--python-exit-code','1','--python',str(OUT/'source/build_clinical_architecture.py')]]
runs=[]
for idx,cmd in enumerate(commands):
 result=subprocess.run(cmd,cwd=STAGE,capture_output=True,text=True);log=BASE/'qa'/f'source_only_step_{idx}.log';log.write_text(result.stdout+result.stderr);runs.append({'argv':cmd,'exit_code':result.returncode,'log_sha256':sha(log)});assert result.returncode==0
comparisons=[]
for p in sorted((BASE/'exports').glob('*.glb')):
 other=OUT/'exports'/p.name;comparisons.append({'file':str(p.relative_to(BASE)),'original_sha256':sha(p),'rebuilt_sha256':sha(other),'byte_identical':sha(p)==sha(other)})
textures=[]
for folder,target in[(BASE/'textures',OUT/'textures'),(CAT/'materials/care',STAGE/'materials/care')]:
 for p in sorted(folder.glob('*.png')):
  q=target/p.name;textures.append({'source':str(p.relative_to(CAT)),'original_sha256':sha(p),'rebuilt_sha256':sha(q),'byte_identical':sha(p)==sha(q)})
metadata=[]
for name in('marker_api.json','collision_proposals.json'):
 a=BASE/name;b=OUT/name;metadata.append({'file':name,'original_sha256':sha(a),'rebuilt_sha256':sha(b),'byte_identical':sha(a)==sha(b)})
receipt={'scope':'Fresh generation from authoring scripts, original existing shared source maps, and care pixel generator. No new existing output or QA input opened. Bpy bundled font only; no external font or reference image input during build.','stage':str(STAGE.relative_to(BASE)),'initial_files':initial,'inputs':[{'path':str(p.relative_to(CAT)),'sha256':sha(p)}for p in inputs],'executed_commands':runs,'glb_binary_comparisons':comparisons,'fresh_texture_comparisons':textures,'interface_and_collision_comparisons':metadata,'blend_binary_note':'Fresh .blend saved with a different stage path; byte identity is not required. Actual regenerated GLB geometry/material/markers and source part tree establish reproducibility.','passed':all(x['byte_identical']for x in comparisons+textures+metadata),'runner_sha256':sha(Path(__file__))}
(BASE/'qa/source_only_rebuild_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
