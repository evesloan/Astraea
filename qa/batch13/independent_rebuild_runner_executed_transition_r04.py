"""Reviewer-controlled fresh source-only generation, actual file-read trace and semantic equivalence."""
from pathlib import Path
import sys,json,hashlib,subprocess,shutil,re,os,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';family=sys.argv[1];revision=sys.argv[2]if len(sys.argv)>2 else'r01'
assert family in ['botanical_cluster','botanical_transition']
stage=OUT/f'independent_rebuild_stage_{family}_{revision}';assert not stage.exists(),'Never overwrite a previous rebuild stage';stage.mkdir();source=ROOT/'assets'/family
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
seeds={'standards/botanical_materials.py','materials/botanical/manifest.json'}|{'materials/botanical/'+x['file']for x in json.loads((ROOT/'materials/botanical/manifest.json').read_text())['materials'].values()}|{str(p.relative_to(ROOT))for p in (source/'source').glob('*.py')}
if family=='botanical_transition':seeds|={'standards/materials.py','materials/material_manifest.json'}|{'materials/'+x['base_color_file']for x in json.loads((ROOT/'materials/material_manifest.json').read_text())['materials'].values()}
assert not any('/qa/'in p or p.endswith(('.blend','.glb','.blend1'))for p in seeds)
for name in sorted(seeds):
 dst=stage/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
for name in ['source','exports','qa']:(stage/'assets'/family/name).mkdir(parents=True,exist_ok=True)
initial=sorted(str(p.relative_to(stage))for p in stage.rglob('*')if p.is_file());assert initial==sorted(seeds)
generator=stage/'assets'/family/'source'/('build_'+family+'.py');trace=OUT/f'independent_rebuild_{family}_{revision}_reads.json';log=OUT/f'independent_rebuild_{family}_{revision}.log';instrument=OUT/'independent_rebuild_instrument.py';cmd=['blender','--background','--threads','1','--python',str(instrument),'--',str(generator),str(trace)]
env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
with log.open('w')as f:run=subprocess.run(cmd,cwd=stage,env=env,stdout=f,stderr=subprocess.STDOUT)
if run.returncode:raise RuntimeError('Source-only generation failed; see '+str(log))
tr=json.loads(trace.read_text());reads=sorted(set(x['path']for x in tr['python_open_events']if x['mode'].startswith('r'))|{x['path']for x in tr['actual_blender_image_files']});generated_reads=[p for p in reads if p.startswith('assets/'+family+'/')and p.endswith(('.blend','.glb'))];unexpected=[p for p in reads if p not in seeds and p not in generated_reads and not p.endswith('.pyc')];assert not unexpected,unexpected
produced=[]
for gp in sorted((source/'exports').glob('AST-*.glb')):
 rebuilt=stage/gp.relative_to(ROOT);produced.append({'current':bind(gp),'rebuilt':bind(rebuilt),'byte_identical':sha(gp)==sha(rebuilt)})
paths=sorted((stage/'assets'/family/'source').glob('AST-*.blend'));prefix=f'independent_rebuilt_{family}_{revision}_';audit_log=OUT/f'independent_rebuilt_audit_{family}_{revision}.log';audit_cmd=['blender','--background','--threads','1','--python',str(OUT/'independent_source_review.py'),'--','--prefix',prefix]+[str(p)for p in paths]
with audit_log.open('w')as f:check=subprocess.run(audit_cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
assert check.returncode==0
results=[]
for p in paths:
 ident=p.stem;original=source/'source'/p.name;sp=OUT/f'independent_source_{ident}.json';rp=OUT/f'{prefix}source_{ident}.json';s=json.loads(sp.read_text());r=json.loads(rp.read_text());assert s['sha256']==sha(original)and r['sha256']==sha(p)
 fields=['name','type','parent','matrix_world','properties','editable_mesh_sha256','modifier_settings'];sig=lambda x:[{k:o.get(k)for k in fields}for o in sorted(x['objects'],key=lambda o:o['name'])];geo1=np.load(ROOT/s['geometry_cache']);geo2=np.load(ROOT/r['geometry_cache']);geometry=all(np.array_equal(geo1[k],geo2[k])for k in ['triangles','object_names','material_names']);semantic=sig(s)==sig(r);mats=s['units']==r['units']and s['used_materials']==r['used_materials']and {x['packed_sha256']for x in s['used_images']}=={x['packed_sha256']for x in r['used_images']}
 results.append({'catalogue_id':ident,'source':bind(original),'rebuilt_source':bind(p),'source_audits':[bind(sp),bind(rp)],'evaluated_geometry_equal':geometry,'editable_mesh_hierarchy_uv_material_modifier_properties_equal':semantic,'units_material_graph_image_bytes_equal':mats,'pass':geometry and semantic and mats})
receipt={'passed':all(x['byte_identical']for x in produced)and all(x['pass']for x in results),'family':family,'revision':revision,'fresh_input_only_stage':True,'source_only_build_duplicated_by_reviewer':True,'stage':str(stage.relative_to(ROOT)),'production_inputs':[bind(ROOT/p)for p in sorted(seeds)],'seed_files':initial,'observed_catalogue_read_paths':reads,'unexpected_catalogue_reads':unexpected,'freshly_generated_outputs_reopened_for_hashing':generated_reads,'all_helper_loaded_material_roles_included':True,'command':cmd,'returncode':run.returncode,'build_log':bind(log),'file_read_instrumentation':bind(trace),'instrumentation_script':bind(instrument),'source_audit_command':audit_cmd,'source_audit_log':bind(audit_log),'exports':produced,'assets':results,'executed_script_sha256':sha(Path(__file__)),'limits':'Python open events are observed attempts, not guaranteed successful reads; native image witnesses bind existing loaded image bytes. Blender/system add-on, Python and renderer resources are execution environment dependencies; catalogue Python opens are instrumented and all actual native-loaded Blender image datablocks are bound. OS ptrace tracing was unavailable; the unsuccessful r01 trace is retained. This is not claimed as a system-call-complete trace. No pre-existing new source/export, QA input or author receipt was seeded. Blender binary equality is not required because stored paths differ; actual editable signatures and evaluated geometry are compared.'}
(OUT/f'independent_rebuild_{family}_{revision}.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('INDEPENDENT_REBUILD',family,receipt['passed'],'seed count',len(seeds),'actual reads',len(reads),'exports',[x['byte_identical']for x in produced],flush=True)
