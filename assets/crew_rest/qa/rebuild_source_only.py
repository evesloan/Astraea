"""Clean reconstruction uses dependency manifest inputs only, no blend/GLB/QA as build input."""
from pathlib import Path
import json,hashlib,shutil,subprocess,time
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((BASE/'dependency_manifest.json').read_text());stage=BASE/'qa/source_only_stage/catalogue';assert not stage.exists(),'Fresh stage required; preserve earlier attempt and choose a new stage'
for row in manifest['source_only_inputs']:
 src=CAT/row['path'];assert sha(src)==row['sha256'];dst=stage/row['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
staged=stage/'assets/crew_rest';assert not(staged/'exports').exists();assert not list((staged/'source').glob('*.blend'))
proc=subprocess.run(['/usr/bin/blender','--background','--threads','1','--python',str(staged/'source/build_crew_rest.py')],capture_output=True,text=True);(BASE/'qa/source_only_build.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0 and 'CREW_REST_BUILD_OK'in proc.stdout
matches=[]
for f in sorted((BASE/'exports').glob('*.glb')):
 g=staged/'exports'/f.name;matches.append({'file':f.name,'original_sha256':sha(f),'rebuilt_sha256':sha(g),'identical_bytes':f.read_bytes()==g.read_bytes()})
metadata=[]
for n in('interface_api.json','collision_proposals.json','pose_contract.json'):
 metadata.append({'file':n,'identical_bytes':(BASE/n).read_bytes()==(staged/n).read_bytes()})
report={'clean_start_no_previous_outputs':True,'source_input_count':len(manifest['source_only_inputs']),'copied_inputs':manifest['source_only_inputs'],'builder_exit_code':proc.returncode,'glb_comparisons':matches,'interface_comparisons':metadata,'all_passed':all(r['identical_bytes']for r in matches+metadata),'scope':'Actual source-only reconstruction in fresh isolated catalogue path. Source .blend binary differs by paths/serialization; geometric identity supplied by exact exported bytes and independent source signatures.'};(BASE/'qa/source_only_rebuild.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
