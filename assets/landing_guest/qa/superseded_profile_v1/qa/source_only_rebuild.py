"""Fresh source-only rebuild; no existing new .blend, export, manifest or QA input."""
from pathlib import Path
import json,hashlib,shutil,subprocess,time
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];STAGE=BASE/'qa/source_only_stage';SCAT=STAGE/'catalogue';SB=SCAT/'assets/landing_guest'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not STAGE.exists(),'Fresh stage required; do not silently reuse earlier outputs'
local=['source/build_landing_guest.py','textures/guest_arrival_original.png']
shared=['standards/materials.py','materials/material_manifest.json']+['materials/'+p.name for p in sorted((CAT/'materials').glob('*.png'))]
inputs=[]
for root,relative,destroot in [(BASE,x,SB)for x in local]+[(CAT,x,SCAT)for x in shared]:
 src=root/relative;dst=destroot/relative;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);inputs.append({'origin_from_catalogue_root':str(src.relative_to(CAT)),'staged_relative_path':str(dst.relative_to(STAGE)),'bytes':src.stat().st_size,'sha256':sha(src)})
initial=sorted(str(p.relative_to(STAGE))for p in STAGE.rglob('*')if p.is_file())
assert not any(x.endswith(('.blend','.glb'))or'/qa/'in x for x in initial)
cmd=['blender','--background','--threads','2','--python-exit-code','1','--python',str(SB/'source/build_landing_guest.py')]
r=subprocess.run(cmd,capture_output=True,text=True);(BASE/'qa/source_only_build.log').write_text(r.stdout+r.stderr);assert r.returncode==0
results=[]
for ident in('AST-LND-001','AST-LND-002'):
 cur=json.loads((BASE/f'{ident}.manifest.json').read_text());fresh=json.loads((SB/f'{ident}.manifest.json').read_text());cp=BASE/cur['export'];np=SB/fresh['export'];results.append({'catalogue_id':ident,'current_glb_sha256':sha(cp),'rebuilt_glb_sha256':sha(np),'glb_binary_identical':sha(cp)==sha(np),'current_source_sha256':sha(BASE/cur['source']),'rebuilt_source_sha256':sha(SB/fresh['source']),'bounds_equal':cur['bounds_blender_z_up']==fresh['bounds_blender_z_up'],'triangles_equal':cur['evaluated_source_triangles']==fresh['evaluated_source_triangles'],'semantic_parts_equal':cur['semantic_parts']==fresh['semantic_parts'],'marker_records_equal':cur['physical_and_proposal_markers']==fresh['physical_and_proposal_markers'],'joins_equal':cur['joins']==fresh['joins']})
# QA is introduced only after successful source-only build. It is not a build input.
(SB/'qa').mkdir(exist_ok=True);shutil.copy2(BASE/'qa/check_sources.py',SB/'qa/check_sources.py')
v=subprocess.run(['blender','--background','--threads','1','--python-exit-code','1','--python',str(SB/'qa/check_sources.py')],capture_output=True,text=True);(BASE/'qa/source_only_reload.log').write_text(v.stdout+v.stderr)
checks=json.loads((SB/'qa/source_reload_checks.json').read_text());ok=v.returncode==0 and checks['all_passed']and all(all(x[k]for k in ('glb_binary_identical','bounds_equal','triangles_equal','semantic_parts_equal','marker_records_equal','joins_equal'))for x in results)
receipt={'scope':'Fresh generator/material/art input only; no pre-existing new outputs or QA read during build. Rebuilt .blend then independently reloaded after build. .blend binaries may vary with file metadata; exact export bytes and semantic records are compared.','staged_initial_files':initial,'source_inputs':inputs,'build_command':cmd,'build_exit_code':r.returncode,'postbuild_reload_exit_code':v.returncode,'postbuild_reload_all_passed':checks['all_passed'],'assets':results,'all_passed':ok}
(BASE/'qa/source_only_rebuild_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SOURCE_ONLY_REBUILD_PASS',ok);assert ok
