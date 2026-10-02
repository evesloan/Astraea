"""Stage only declared generator inputs, then rebuild with no existing outputs or QA inputs."""
import json,hashlib,shutil,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];stage=BASE/'qa/source_only_stage_final/catalogue'
assert not stage.exists(), 'Use a fresh stage; do not reuse existing outputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mat=json.loads((CAT/'materials/botanical/manifest.json').read_text());inputs=['assets/botanical_cluster/source/build_botanical_cluster.py','standards/botanical_materials.py','materials/botanical/manifest.json']+['materials/botanical/'+r['file']for r in mat['materials'].values()]
rows=[]
for rel in inputs:
 src=CAT/rel;out=stage/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out);rows.append({'catalogue_relative_path':rel,'sha256':sha(src),'staged_sha256':sha(out),'role':'source generator'if rel.endswith('build_botanical_cluster.py')else 'opened generator dependency'})
initial=[str(p.relative_to(stage))for p in stage.rglob('*')if p.is_file()];assert sorted(initial)==sorted(inputs)
with (BASE/'qa/source_only_build.log').open('w')as f:code=subprocess.call(['blender','--background','--threads','1','--python-exit-code','1','--python',str(stage/'assets/botanical_cluster/source/build_botanical_cluster.py')],stdout=f,stderr=subprocess.STDOUT)
assert code==0
staged=stage/'assets/botanical_cluster';assets=[]
for live in sorted(BASE.glob('AST-BOT-*.manifest.json')):
 a=json.loads(live.read_text());b=json.loads((staged/live.name).read_text());lo=BASE/a['export'];so=staged/b['export'];assets.append({'catalogue_id':a['catalogue_id'],'live_source_sha256':a['source_sha256'],'rebuilt_source_sha256':sha(staged/b['source']),'live_glb_sha256':sha(lo),'rebuilt_glb_sha256':sha(so),'glb_byte_identical':sha(lo)==sha(so),'bounds_match':a['bounds_blender_z_up']==b['bounds_blender_z_up'],'joins_match':a['joins']==b['joins'],'markers_match':a['physical_and_proposal_markers']==b['physical_and_proposal_markers'],'source_editable_part_names_match':a['semantic_parts']==b['semantic_parts'],'source_bytes_note':'Blender container bytes can differ by save path/session; exact native GLB and semantic/geometry records bind reproduced appearance'})
receipt={'fresh_stage':str(stage.relative_to(BASE)),'initial_files':initial,'preexisting_outputs':False,'preexisting_qa_inputs':False,'generator_inputs':rows,'blender_exit_code':code,'assets':assets,'passes':code==0 and all(a['glb_byte_identical']and a['bounds_match']and a['joins_match']and a['markers_match']and a['source_editable_part_names_match']for a in assets)}
(BASE/'qa/source_only_rebuild_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['passes'])
(BASE/'dependency_manifest.json').write_text(json.dumps({'generator':'source/build_botanical_cluster.py','all_opened_generator_inputs':rows,'unused_loaded_material_roles_included':True,'qa_helpers':[{'catalogue_relative_path':str(p.relative_to(CAT)),'sha256':sha(p)}for p in sorted((BASE/'qa').glob('*.py'))]+[{'catalogue_relative_path':'standards/qa_frame.py','sha256':sha(CAT/'standards/qa_frame.py')}],'material_library_unchanged':True},indent=2)+'\n')
