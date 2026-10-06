"""Parent-approved scratch-only two-thread Court A source build, no exports/imports."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time,resource,datetime
R=Path(__file__).resolve().parent;D=R/'printed_materials001';G=Path('/workspace/shared/astraea-godot-production-20261003');C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');P=C/'assets/grand_lantern_theater_section';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected={'COURT_A_GEOMETRY_CONTRACT.json':'d1ea220667cf6c381aa875df099bbda083d18096c8d757c6456659e2206a67e9','COURT_A_PURE_SCREEN.json':'17793a52b40cbf649010b48e9466b29ecc34ec5d2740f337c467609c3c8fad2a','FULLER_REAR_MASS_CANDIDATE.json':'c3965e00e3745d685804bf40f9de2c127e921131de79edb78fbb5e6498136c60','printed_materials001/build_court_A_source_printed_DRAFT.py':'0577a0336d26b8999bd86d97261e3b56d8623d695fb4003affd463047c06673c','PARENT_SOURCE_BUILD_GATE.json':'8324a7b105c0fa46550d48f9b1ed76ca582834eb4de93214eeaa484623cd1cfc'}
for rel,h in expected.items():assert sha(R/rel)==h,rel
contract=json.loads((R/'COURT_A_GEOMETRY_CONTRACT.json').read_text());inputs=contract['input_sha256'].copy()
for row in contract['retained_instances']:inputs[row['source']]=row['source_sha256']
for p in [P/'source/firstpass_001/firstpass_common.py',P/'source/firstpass_001/build_firstpass_assembly.py',C/'assets/furniture/AST-FUR-001_day_window_bench.blend',C/'assets/furniture/AST-FUR-002_day_reading_chair.blend',C/'assets/botanical_planter/AST-BOT-004.blend',C/'assets/botanical_understory/source/AST-BOT-002.blend']:
 inputs[str(p)]=sha(p)
for rel,h in expected.items():inputs[str(R/rel)]=h
for p,h in inputs.items():assert sha(p)==h,p
# Source/job outputs cannot overlap any protected input or the production trees.
output=D/'authored_preview001'/contract['standalone_source_proposal'];assert not output.exists();assert str(output).startswith('/workspace/scratch/')
run=R/'source_build_run001';run.mkdir(exist_ok=False);env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='1',MALLOC_ARENA_MAX='2')
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:p=run/sub;p.mkdir();env[key]=str(p)
def game_snapshot():return {str(p.relative_to(G)):sha(p)for p in G.rglob('*')if p.is_file()and not any(x in {'.git','.godot','artifacts','__pycache__'}for x in p.relative_to(G).parts)}
before=game_snapshot();(run/'INPUT_PINS.json').write_text(json.dumps({'source_inputs':inputs,'game':before},indent=2)+'\n')
script=D/'build_court_A_source_printed_DRAFT.py';expr='import sys,runpy;sys.dont_write_bytecode=True;sys.argv='+repr([str(script),'--','--build'])+';runpy.run_path('+repr(str(script))+',run_name="__main__")'
receipt={'status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'threads':2,'builder_sha256':sha(script),'output':str(output),'production_writes':False,'renders':False};(run/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');start=time.monotonic()
with(run/'blender.log').open('x')as log:
 result=subprocess.run(['blender','-b','-t','2','--factory-startup','--python-expr',expr],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
text=(run/'blender.log').read_text(errors='replace');errors=[line for line in text.splitlines()if 'Traceback'in line or'Error:'in line or'AssertionError'in line or'Segmentation fault'in line]
unchanged=all(sha(p)==h for p,h in inputs.items())and game_snapshot()==before
report=D/'authored_preview001/BUILD_REPORT.json';passed=result.returncode==0 and not errors and report.exists()and output.exists()and unchanged
receipt.update(status='PASS_SOURCE_BUILD_REOPEN_PENDING'if passed else'FAILED_PRESERVED',returncode=result.returncode,seconds=round(time.monotonic()-start,3),errors=errors,inputs_unchanged=unchanged,game_input_count=len(before),peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,source_sha256=sha(output)if output.exists()else None,report_sha256=sha(report)if report.exists()else None);(run/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));sys.exit(0 if passed else 1)
