from pathlib import Path
import importlib.util,json,gzip,hashlib,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;S=B.parents[1];old=S/'pool-opposite-gallery-proposal001';sys.path.insert(0,str(old/'reference_programme001'))
spec=importlib.util.spec_from_file_location('retained_programme_check',old/'reference_programme001/check_programme.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Preserve original input authentication before binding the proven-unchanged
# programme snapshot to this explicitly versioned corrected core plan.
m.verify_inputs()
source=B/'source001/qa/OBJECT_PRESERVATION.json';proof=json.loads(source.read_text());assert proof['status']=='PASS_EXACT_UNRELATED_OBJECT_PRESERVATION'
with gzip.open(old/'combined_source002/qa/BUILD_EVALUATED_PROGRAMME.json.gz','rt')as f:program=json.load(f)
plan=json.loads((B/'CORE_PLAN.json').read_text());actual=json.loads((B/'source001/qa/REOPEN_EVALUATED_CORE.json').read_text());original_hash=program['core_plan_sha256'];program['core_plan_sha256']=hashlib.sha256((B/'CORE_PLAN.json').read_bytes()).hexdigest();m.CORE=B/'CORE_PLAN.json';m.verify_inputs=lambda:plan
result=m.run(program,actual_core_plan=actual);result['programme_snapshot_recontextualization']={'original_core_sha256':original_hash,'current_core_sha256':program['core_plan_sha256'],'unchanged_programme_proof_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_geometry_or_transforms_modified':False};(B/'ACTUAL_PROGRAMME_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'issues':result['issues']}));assert not result['issues']
