"""Bounded serial source job; requires the parent's released two-thread source slot."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,datetime
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from fixture_recipe import read,sha,write_new
assert '--source-slot-released' in sys.argv,'Wait for parent source slot release'
manifest=read(R/'EXECUTION_MANIFEST.json')
for p,h in manifest['pins'].items():assert sha(Path(p))==h,('Changed job input',p)
assert not(R/'SOURCE_JOB_RECEIPT.json').exists()
env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',BLIS_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
record={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blender_threads':2,'serial_processes':True,'runtime_writes':False,'godot_launched':False,'rendering_performed':False,'phases':[]}
for phase,cmd,limit in [('build',['/usr/bin/blender','-b','--factory-startup','-t','2','--python-exit-code','9','--python',str(R/'build_source.py')],120),('reopen',['/usr/bin/blender','-b','--factory-startup','-t','2','--python-exit-code','9','--python',str(R/'reopen_source.py')],120),('geometry_qa',[sys.executable,str(R/'check_geometry.py'),'REOPENED_GEOMETRY.json','SOURCE_GEOMETRY_QA.json'],90)]:
 log=R/(phase+'.log');start=time.monotonic()
 with log.open('x')as out:proc=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,env=env,timeout=limit)
 result={'phase':phase,'returncode':proc.returncode,'seconds':round(time.monotonic()-start,3),'log_sha256':sha(log)};record['phases'].append(result);print(result,flush=True)
 if proc.returncode:record['status']='FAILED_'+phase.upper();break
else:
 for p,h in manifest['original_input_pins'].items():assert sha(Path(p))==h,('Original input changed',p)
 record['status']='PASS_SCRATCH_SOURCE_BUILD_REOPEN_GEOMETRY_QA';record['original_inputs_unchanged']=True
 record['outputs_sha256']={p.name:sha(p)for p in [R/'AST-CUL-005_inward_stair_channels_020.blend',R/'ACTUAL_SOURCE_RECIPE.json',R/'BUILD_RECEIPT.json',R/'REOPENED_GEOMETRY.json',R/'SOURCE_REOPEN_REPORT.json',R/'SOURCE_GEOMETRY_QA.json']}
record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write_new(R/'SOURCE_JOB_RECEIPT.json',record);print(record['status'],flush=True)
if not record['status'].startswith('PASS'):raise SystemExit(1)
