#!/usr/bin/env python3
"""Queue once through the existing graphical runner, or archive its terminal result."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil,subprocess,time
O=Path(__file__).parent;G=Path('/workspace/shared/astraea-godot-production-20261003');Q=Path('/workspace/shared/astraea-review-queue');R=O/'capture_engineering_signage_installed_001';ID='engineering-signage-installed-001'
LABELS=['visitor','maintenance_diagnostic','control_diagnostic','workbay_diagnostic','guest_north_side','guest_south_side','cell_threshold_open','cell_lower_service_open','cell_restriction_closed']
SUFFIXES=['world_capture','processed_world_capture','presentation_capture','clear_world_capture','clear_processed_world_capture','clear_presentation_capture']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def pins():return {str(p.relative_to(G)):sha(p)for p in G.rglob('*')if p.is_file()and not any(x in p.relative_to(G).parts for x in ['.git','.godot','artifacts','__pycache__'])and p.suffix!='.pyc'}
def quiet():
 active=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:name=(p/'comm').read_text().strip().lower()
  except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  if name.startswith('godot'):active.append((p.name,name))
 assert not active,('No competing Game process allowed',active)
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--expected-head',required=True);ap.add_argument('--focused-run-id',default='focused001');ap.add_argument('--enqueue',action='store_true');ap.add_argument('--archive',action='store_true');a=ap.parse_args();assert a.enqueue!=a.archive;assert subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD']).decode().strip()==a.expected_head
focused=json.loads((O/a.focused_run_id/'PROGRESS.json').read_text());assert focused['status']=='FOCUSED_SIGNAGE_PHYSICAL_AND_SOURCE_CHECKS_PASS_CAPTURE_PENDING' and focused['base_head']==a.expected_head
if a.enqueue:
 assert not R.exists(),'Existing evidence directory; inspect rather than duplicate';assert not any((Q/(ID+s)).exists()for s in ['.request','.completed-request','.result.json','.log','.request.tmp']);assert not list(Q.glob('*.request')) and not (Q/'STOP').exists();quiet()
 runner=json.loads((Q/'runner.json').read_text());assert runner['project']==str(G)and runner['display_present'];pid=int(runner['pid']);os.kill(pid,0);assert b'run_capture_queue.py'in Path(f'/proc/{pid}/cmdline').read_bytes()
 source=pins();assert source.get('scripts/presentation.gd')=='aabcfa21a0dd0ab763ef08bc7a0ba3422bea1df9f9383e5b2999e4dfa1198c51';R.mkdir();write(R/'SOURCE_START.json',source)
 selector=G/'artifacts/capture_view_group.txt';old=selector.read_bytes()if selector.exists()else None
 if old is not None:(R/'PREVIOUS_SELECTOR.txt').write_bytes(old)
 selector.write_text('secondary_engineering\n');receipt={'status':'QUEUED','queued_utc':now(),'queued_epoch':time.time(),'request_id':ID,'base_head':a.expected_head,'runner_pid_verified':pid,'view_group':'secondary_engineering','expected_views':9,'expected_pngs':54,'original_eight_preserved':True,'ninth':'Supported normal-eye west approach with the real inherited gate closed; no hidden walls, focus zoom, renderer or audio change.','portable_source_pins':len(source),'prior_selector_sha256':hashlib.sha256(old).hexdigest()if old is not None else None};write(R/'ENQUEUED.json',receipt);temp=Q/(ID+'.request.tmp');temp.write_text(json.dumps({'kind':'capture_current_ship'})+'\n');os.replace(temp,Q/(ID+'.request'));print(json.dumps(receipt,indent=2))
else:
 e=json.loads((R/'ENQUEUED.json').read_text());assert (Q/(ID+'.completed-request')).exists()and not(Q/(ID+'.request')).exists();quiet();result=json.loads((Q/(ID+'.result.json')).read_text());assert not(R/'CAPTURE_RECEIPT.json').exists();shutil.copy2(Q/(ID+'.result.json'),R/'RUNNER_RESULT.json');shutil.copy2(Q/(ID+'.log'),R/'RUNNER.log');before=json.loads((R/'SOURCE_START.json').read_text());actual=pins();assert actual==before,'Source drift during capture';assert result['status']=='passed'and result['exit_code']==0 and not result['errors'],result
 images=R/'images';images.mkdir(exist_ok=False);records=[]
 for label in LABELS:
  for suffix in SUFFIXES:
   name='secondary_engineering_'+label+'_'+suffix+'.png';p=G/'artifacts'/name;assert p.exists() and p.stat().st_mtime>=e['queued_epoch']-1,('Missing or stale native image',name);q=images/name;shutil.copy2(p,q);assert sha(q)==sha(p);records.append({'file':name,'sha256':sha(q),'bytes':q.stat().st_size,'captured_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()})
 old=R/'PREVIOUS_SELECTOR.txt'
 if old.exists():(G/'artifacts/capture_view_group.txt').write_bytes(old.read_bytes())
 report={'status':'ACTUAL_NINE_VIEW_CAPTURE_ARCHIVED_REQUIRES_VISUAL_REVIEW','finished_utc':now(),'request_id':ID,'base_head':a.expected_head,'runner_result':result,'source_pins':len(before),'unrelated_source_drift':[],'pngs':54,'images':records,'first_pass_accepted':False,'sign_readability_accepted':False};write(R/'CAPTURE_RECEIPT.json',report);print(json.dumps({k:v for k,v in report.items()if k!='images'},indent=2))
