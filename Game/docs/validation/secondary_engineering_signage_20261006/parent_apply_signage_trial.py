#!/usr/bin/env python3
"""Install only the reviewed retained sign trial at the settled exclusive Game boundary."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess
O=Path(__file__).parent;G=Path('/workspace/shared/astraea-godot-production-20261003');C=Path('/workspace/shared/astraea-catalogue-continuation-20261002');B=Path('/workspace/shared/astraea-github-backup')
M=O/'FINAL_APPLY_ALLOWLIST.json';MH='83bf5dbdfe893a1c69c21af78efb77dded013ffc415eb3979bb6fba08420aa6e'
EXACT={'data/architecture/ENGINEERING_CELL_SIGNAGE_RUNTIME.json','docs/ENGINEERING_SIGNAGE_CAPTURE_ADOPTION.json','scripts/engineering_cell_signage.gd','scripts/presentation.gd','scripts/secondary_engineering_cell.gd','tests/engineering_signage_capture_successor.gd','tests/engineering_signage_source_guard.gd','tests/secondary_engineering_additive_guard.gd','tests/validate_secondary_engineering_cell.gd','assets/models/AST-ENG-008_cell_restriction_signage_004.glb'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(*args):return subprocess.check_output(['git','-C',str(G),*args])
def pins():return {str(p.relative_to(G)):sha(p) for p in G.rglob('*') if p.is_file() and not any(x in p.relative_to(G).parts for x in ['.git','.godot','artifacts','__pycache__']) and p.suffix!='.pyc'}
def quiet():
 active=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  try:name=(p/'comm').read_text().strip().lower()
  except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  if name.startswith('godot'):active.append({'pid':p.name,'name':name})
 assert not active,('Existing Game process; wait for terminal boundary',active)
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--expected-head',required=True);ap.add_argument('--apply',action='store_true');opts=ap.parse_args();assert len(opts.expected_head)==40 and all(c in '0123456789abcdef' for c in opts.expected_head)
assert sha(M)==MH;m=json.loads(M.read_text());rows=m['files'];assert len(rows)==10 and {r['path'] for r in rows}==EXACT
receipt=O/'LIVE_APPLY_RECEIPT.json'
def preflight():
 assert sha(M)==MH
 assert git('rev-parse','HEAD').decode().strip()==opts.expected_head,'Settled checkpoint HEAD mismatch'
 assert not git('diff','--cached','--name-only','-z'),'Preserve occupied index and stop'
 for row in rows:
  rel=row['path'];p=G/rel;s=Path(row['source']);assert not p.is_symlink() and not s.is_symlink()
  assert all(not parent.is_symlink() for parent in p.parents if parent!=G.parent)
  assert (sha(p) if p.exists() else None)==row['pre_sha256'],('Target preimage changed',rel)
  assert sha(s)==row['sha256'] and s.stat().st_size==row['bytes'],('Staged bytes changed',rel)
 for rel,h in m['required_unchanged_game_sha256'].items():assert sha(G/rel)==h,('Companion changed',rel)
 import_path=G/'assets/models/AST-ENG-008_cell_restriction_signage_004.glb.import';assert not import_path.exists(),'New asset import must not overwrite any previous import'
 retained=Path(m['retention_receipt_path']);assert sha(retained)==m['retention_receipt_sha256'];r=json.loads(retained.read_text());assert r['commit']==m['retained_commit'] and r['parent_independent_remote_confirmation']['status']=='CONFIRMED' and len(r['files'])==66
 for row in r['files']:
  rel=row['path'];assert sha(C/rel)==row['sha256'],('Retained catalogue bytes changed',rel)
  blob=subprocess.check_output(['git','-C',str(B),'show',m['retained_commit']+':BlenderCatalogue/'+rel])
  assert hashlib.sha256(blob).hexdigest()==row['sha256'],('Retained mirror blob mismatch',rel)
 return {'retained_files':66,'source_sha256':r['source_sha256'],'export_sha256':r['export_sha256']}
retention=preflight();report={'status':'READ_ONLY_PREFLIGHT_PASS','utc':now(),'files':10,'manifest_sha256':MH,'base_head':opts.expected_head,'retention':retention,'controls_v3_audio_listener_included':False,'first_pass_accepted':False,'sign_readability_accepted':False,'engines':'NOT_RUN'}
if not opts.apply:print(json.dumps(report,indent=2));raise SystemExit
assert not receipt.exists(),'Inspect existing receipt rather than retrying blindly';quiet();preflight();start=pins();write(O/'SOURCE_START.json',start);index_before=git('diff','--cached','--name-only','-z');saved=O/'APPLY_PREIMAGES';saved.mkdir(exist_ok=False)
for row in rows:
 if row['pre_sha256'] is not None:
  dest=saved/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(G/row['path'],dest);assert sha(dest)==row['pre_sha256']
report.update(status='PREFLIGHT_COMPLETE',portable_source_pins=len(start),applied=[]);write(receipt,report)
try:
 quiet();preflight()
 # Add dependencies first; change the existing builder last. No engine may run mid-apply.
 by_path={r['path']:r for r in rows};order=[r['path'] for r in rows if r['pre_sha256'] is None]+['tests/secondary_engineering_additive_guard.gd','tests/validate_secondary_engineering_cell.gd','scripts/presentation.gd','scripts/secondary_engineering_cell.gd'];assert len(order)==len(set(order))==10 and set(order)==EXACT
 for rel in order:
  row=by_path[rel];p=G/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(row['source'],p);assert sha(p)==row['sha256'];report['applied'].append({'path':rel,'sha256':row['sha256']});write(receipt,report)
 expected=dict(start);expected.update({r['path']:r['sha256'] for r in rows});assert pins()==expected,'Unexpected unrelated portable-source drift during apply'
 assert git('diff','--cached','--name-only','-z')==index_before and git('rev-parse','HEAD').decode().strip()==opts.expected_head
 report.update(status='EXACT_TEN_FILE_SIGNAGE_TRIAL_APPLIED',finished_utc=now(),unrelated_source_drift=[],index_unchanged=True,next='Standard import; disable compression only on the newly generated sign import; standard import-first cell check, imported raw triangle/UV proof, retained tests and actual normal capture.');write(receipt,report);print(json.dumps(report,indent=2))
except Exception as e:
 report.update(status='FAILED_PRESERVE_STATE_AND_INSPECT',failure=str(e));write(receipt,report);raise
