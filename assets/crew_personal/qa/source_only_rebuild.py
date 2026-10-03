"""Stage only all declared opened inputs; reproduce native exports and collision records."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,zipfile
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
dep=json.loads((BASE/'dependency_manifest.json').read_text());name=sys.argv[1]if len(sys.argv)>1 else'source_only_stage';stage=BASE/'qa'/name/'catalogue'
if stage.exists():raise RuntimeError('Prior rebuild retained; use a fresh stage name')
stage.mkdir(parents=True)
for r in dep['inputs']:
 src=CAT/r['path_from_catalogue_root'];assert sha(src)==r['sha256'];dst=stage/r['path_from_catalogue_root'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
inputs=sorted(str(p.relative_to(stage))for p in stage.rglob('*')if p.is_file());assert not any('/qa/'in p or'/exports/'in p or p.endswith('.blend')for p in inputs)
gen=stage/'assets/crew_personal/source/build_crew_personal.py';run=subprocess.run(['blender','-b','-t','2','--python-exit-code','1','--python',str(gen)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(BASE/'qa'/f'{name}_build.log').write_text(run.stdout);assert run.returncode==0,run.stdout[-1200:]
fresh=stage/'assets/crew_personal';checks=[]
for p in list(sorted((BASE/'exports').glob('*.glb')))+[BASE/'collision_proposals.json',BASE/'marker_api.json',BASE/'mount_contract.json']:
 q=fresh/p.relative_to(BASE);checks.append({'file':str(p.relative_to(BASE)),'original_sha256':sha(p),'fresh_sha256':sha(q),'byte_identical':p.read_bytes()==q.read_bytes()})
sources=[{'file':p.name,'fresh_source_exists':(fresh/'source'/p.name).is_file(),'fresh_source_sha256':sha(fresh/'source'/p.name)}for p in sorted((BASE/'source').glob('*.blend'))]
with zipfile.ZipFile(BASE/'qa/crew_personal_source_only_inputs.zip','w',zipfile.ZIP_DEFLATED)as z:
 for r in dep['inputs']:z.write(CAT/r['path_from_catalogue_root'],r['path_from_catalogue_root'])
report={'method':'Fresh stage has only declared generator/helper/manifest/9 opened textures; no blend, export, QA, reference or metadata outputs initially','stage':str(stage.relative_to(BASE)),'input_files_before_build':inputs,'dependency_manifest_sha256':sha(BASE/'dependency_manifest.json'),'source_input_zip_sha256':sha(BASE/'qa/crew_personal_source_only_inputs.zip'),'build_returncode':run.returncode,'comparisons':checks,'fresh_sources':sources,'passed':all(c['byte_identical']for c in checks)and all(c['fresh_source_exists']for c in sources)};(BASE/'qa/source_only_rebuild.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
