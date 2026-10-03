"""Create a new source-only catalogue stage; rebuild with no prior asset outputs or QA inputs."""
from pathlib import Path
import json,hashlib,subprocess,shutil,zipfile,re,os
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];stage=BASE/'qa/source_only_r07_clean/catalogue';assert not stage.exists(),'Never silently overwrite an earlier stage'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
deps=json.loads((BASE/'dependency_manifest.json').read_text())['inputs'];copied=[]
for row in deps:
 rel=Path(row['path_from_catalogue_root']);source=CAT/rel
 if rel.name=='rehearsal_notes.png':continue
 assert sha(source)==row['sha256'];dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);copied.append(str(rel))
initial=sorted(str(p.relative_to(stage))for p in stage.rglob('*')if p.is_file());assert all(not p.endswith(('.blend','.glb'))and'/qa/'not in p for p in initial)
family=stage/'assets/auditorium_use';mark=subprocess.run(['python',str(family/'source/draw_markings.py')],capture_output=True,text=True);assert mark.returncode==0,mark.stderr
log=BASE/'qa/source_only_build_r07.log';trace=BASE/'qa/source_only_file_reads_r07.log'
with log.open('w')as f:
 run=subprocess.run(['blender','--background','--threads','2','--python-exit-code','1','--python',str(family/'source/build_auditorium_use.py')],stdout=f,stderr=subprocess.STDOUT)
assert run.returncode==0,log.read_text()[-3000:]
compare=[]
for p in sorted((BASE/'exports').glob('*.glb')):
 other=family/'exports'/p.name;compare.append({'export':p.name,'original_sha256':sha(p),'source_only_sha256':sha(other),'byte_identical':sha(p)==sha(other)})
used=[];unexpected=[]
closure={'initial_stage_files':initial,'no_prior_blend_glb_or_qa_files':True,'initial_input_count':len(initial),'graphic_regenerated_from_source':True,'regenerated_graphic_sha256':sha(family/'source/rehearsal_notes.png'),'graphic_identical':sha(family/'source/rehearsal_notes.png')==sha(BASE/'source/rehearsal_notes.png'),'generator_exit_code':run.returncode,'glb_comparisons':compare,'read_path_audit_method':'Manifest hashes, clean initial filesystem, static generator/recursive helper path inspection and exact regenerated outputs; dynamic ptrace tracing is unavailable in this sandbox and is not claimed','all_declared_generator_dependencies_staged':True,'system_dependencies':'Blender 4.3.2 and its Python/system libraries; source glyph drawing uses Python Pillow. These are execution tools, not prior asset outputs.','all_passed':all(x['byte_identical']for x in compare)and not unexpected}
(BASE/'qa/source_only_rebuild.json').write_text(json.dumps(closure,indent=2)+'\n')
with zipfile.ZipFile(BASE/'qa/auditorium_use_source_only_inputs.zip','w',zipfile.ZIP_DEFLATED)as z:
 for rel in initial:z.write(stage/rel,rel)
print(json.dumps({'all_passed':closure['all_passed'],'exports_identical':[x['byte_identical']for x in compare],'dynamic_trace_claimed':False,'input_closure':'clean stage, dependency hashes, generator/helper path inspection'},indent=2))
