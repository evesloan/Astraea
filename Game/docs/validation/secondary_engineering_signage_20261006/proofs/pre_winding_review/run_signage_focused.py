#!/usr/bin/env python3
"""Approved sign-only import precision and serial standard focused checks.
Run only after the parent releases the checkpoint boundary and exact apply passed.
"""
from pathlib import Path
import argparse,hashlib,json,datetime,subprocess,sys,time
O=Path(__file__).parent;G=Path('/workspace/shared/astraea-godot-production-20261003');M=O/'FINAL_APPLY_ALLOWLIST.json';MH='83bf5dbdfe893a1c69c21af78efb77dded013ffc415eb3979bb6fba08420aa6e'
BASE='assets/models/AST-ENG-008_cell_restriction_signage_004';IMPORT=BASE+'.glb.import'
GENERATED={IMPORT,BASE+'_staff_label.png',BASE+'_staff_label.png.import',BASE+'_staff_rubber.png',BASE+'_staff_rubber.png.import','scripts/engineering_cell_signage.gd.uid','tests/engineering_signage_capture_successor.gd.uid','tests/engineering_signage_source_guard.gd.uid'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def pins():return {str(p.relative_to(G)):sha(p) for p in G.rglob('*') if p.is_file() and not any(x in p.relative_to(G).parts for x in ['.git','.godot','artifacts','__pycache__']) and p.suffix!='.pyc'}
def quiet():
 active=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:name=(p/'comm').read_text().strip().lower()
  except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  if name.startswith('godot'):active.append((p.name,name))
 assert not active,('Existing Game process; cannot start another engine',active)
def check_all_pins(expected,stage,allow_new=False):
 actual=pins();bad={p:{'before':h,'after':actual.get(p)} for p,h in expected.items() if actual.get(p)!=h};added=set(actual)-set(expected)
 assert not bad,('Existing portable source changed',stage,bad)
 assert (added<=GENERATED if allow_new else not added),('Unexpected generated source',stage,sorted(added))
 return actual
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--expected-head',required=True);ap.add_argument('--run-id',required=True);ap.add_argument('--execute',action='store_true');a=ap.parse_args();assert a.run_id.replace('_','').replace('-','').isalnum();assert sha(M)==MH;m=json.loads(M.read_text());apply=json.loads((O/'LIVE_APPLY_RECEIPT.json').read_text());assert apply['status']=='EXACT_TEN_FILE_SIGNAGE_TRIAL_APPLIED';assert apply['base_head']==a.expected_head and subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD']).decode().strip()==a.expected_head
for row in m['files']:assert sha(G/row['path'])==row['sha256'],('Applied target drift',row['path'])
for rel,h in m['required_unchanged_game_sha256'].items():assert sha(G/rel)==h
assert not (G/IMPORT).exists(),'This runner requires a fresh first import; preserve any earlier attempt instead of silently repeating'
if not a.execute:print('READ_ONLY_RUN_PREFLIGHT_PASS');raise SystemExit
quiet();R=O/a.run_id;R.mkdir(exist_ok=False);baseline=pins();write(R/'SOURCE_START.json',baseline);report={'status':'RUNNING','started_utc':now(),'base_head':a.expected_head,'baseline_pins':len(baseline),'checks':[],'first_pass_accepted':False,'readability_accepted':False};write(R/'PROGRESS.json',report)
def run(check):
 quiet();command=[sys.executable,str(G/'tools/validate.py'),'--only',check];start=time.monotonic();log=R/(str(len(report['checks'])+1).zfill(2)+'_'+check+'.log');p=subprocess.Popen(command,cwd=G,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 with log.open('w')as f:
  for line in p.stdout:f.write(line);f.flush()
 code=p.wait();record={'check':check,'exit_code':code,'wall_seconds':round(time.monotonic()-start,3),'log_sha256':sha(log),'finished_utc':now()};report['checks'].append(record);write(R/'PROGRESS.json',report)
 receipt=G/'artifacts'/('validation_'+check+'_fixed60.json');assert receipt.exists();(R/(check+'_validation.json')).write_bytes(receipt.read_bytes());assert code==0,(check,code,'inspect preserved log',str(log));r=json.loads(receipt.read_text());assert all(row['passed']for row in r['checks']),r;print(json.dumps(record),flush=True)
try:
 run('import');imported=check_all_pins(baseline,'initial import',True);write(R/'SOURCE_AFTER_INITIAL_IMPORT.json',imported);assert IMPORT in imported and IMPORT not in baseline
 original=(G/IMPORT).read_bytes();old='meshes/force_disable_compression=false\n';new='meshes/force_disable_compression=true\n';text=original.decode();assert text.count(old)==1 and new not in text;corrected=text.replace(old,new).encode();assert corrected.replace(new.encode(),old.encode())==original;quiet();(R/'NEW_ASSET_IMPORT_PREIMAGE.import').write_bytes(original);(G/IMPORT).write_bytes(corrected);assert (G/IMPORT).read_bytes()==corrected
 precision={'path':IMPORT,'before_sha256':hashlib.sha256(original).hexdigest(),'after_sha256':sha(G/IMPORT),'exact_change':{'from':old.strip(),'to':new.strip()},'scope':'Only newly created sign asset import; old imports unchanged; source ink0.2mm, precision/memory tradeoff without target-GPU claim'};write(R/'IMPORT_PRECISION_CORRECTION.json',precision);expected=dict(imported);expected[IMPORT]=sha(G/IMPORT);check_all_pins(expected,'new asset precision edit')
 run('secondary_engineering_cell');settled=check_all_pins(expected,'cell import-first physical check',True)
 for name in ['engineering_signage_imported_source.json','engineering_signage_triangles.float32','engineering_signage_uv.float32']:(R/name).write_bytes((G/'artifacts'/name).read_bytes())
 command=[sys.executable,str(O/'compare_imported_signage.py'),'--artifact-dir',str(R),'--output',str(R/'NATIVE_SOURCE_EQUIVALENCE.json')];comparison=subprocess.run(command,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(R/'NATIVE_SOURCE_EQUIVALENCE.log').write_text(comparison.stdout);assert comparison.returncode==0,('Actual imported source mismatch; preserve failed evidence',comparison.stdout[-3000:])
 for check in ['secondary_engineering_access','secondary_engineering_essentials']:
  run(check);check_all_pins(settled,check)
 report.update(status='FOCUSED_SIGNAGE_PHYSICAL_AND_SOURCE_CHECKS_PASS_CAPTURE_PENDING',finished_utc=now(),unrelated_source_drift=[],generated_source_files={p:h for p,h in settled.items()if p not in baseline},import_precision_correction=precision,normal_capture_readability='PENDING');write(R/'PROGRESS.json',report);print(json.dumps(report,indent=2))
except Exception as e:
 report.update(status='FAILED_PRESERVE_EVIDENCE',failure=str(e),finished_utc=now());write(R/'PROGRESS.json',report);raise
