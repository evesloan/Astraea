"""Reviewed exact two-file test successor, followed by one standard registered cell check."""
from pathlib import Path
import argparse,json,hashlib,datetime,subprocess,shutil,os,tempfile,time
O=Path(__file__).resolve().parent;G=Path('/workspace/shared/astraea-godot-production-20261003');A=O/'FINAL_TWO_FILE_ALLOWLIST.json'
MANIFEST='b074dd5829ddd9d495dd534f4841c5897cba644923554e4f1c92ef17f1d7db6f'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def snap():return{str(p.relative_to(G)):sha(p)for p in sorted(G.rglob('*'))if p.is_file()and not{'.git','.godot','artifacts','__pycache__'}.intersection(p.relative_to(G).parts)}
def idle():
 for p in Path('/proc').iterdir():
  if p.name.isdigit():
   try:n=(p/'comm').read_text().strip().lower()
   except OSError:continue
   assert not n.startswith('godot'),('Competing local Godot process',p.name)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--approved-game-boundary',action='store_true');ap.add_argument('--execute',action='store_true');args=ap.parse_args();assert sha(A)==MANIFEST;m=json.loads(A.read_text());assert subprocess.check_output(['git','-C',str(G),'rev-parse','HEAD'],text=True).strip()==m['expected_head'];assert len(m['files'])==2
 for r in m['files']:assert sha(G/r['path'])==r['pre_sha256']and sha(O/r['source'])==r['sha256'],r['path']
 for p,h in m['unchanged_proofs'].items():assert sha(G/p)==h,p
 assert sha(O/m['validated_candidate_receipt'])==m['validated_candidate_receipt_sha256'];assert json.loads((O/m['validated_candidate_receipt']).read_text())['status']=='PASS_FULL_CANDIDATE_SEQUENCE';assert sha(O/'STATIC_CHANGE_AUDIT.json')==m['static_audit_sha256']
 if not args.execute:print(json.dumps({'status':'READ_ONLY_PREFLIGHT_PASS','manifest_sha256':MANIFEST,'files':m['files']},indent=2));return
 assert args.approved_game_boundary;idle();run=O/'registered_cell_run001';assert not run.exists();run.mkdir();before=snap();save(run/'SOURCE_BEFORE_APPLY.json',before);report={'status':'APPLYING','started_utc':now(),'manifest_sha256':MANIFEST,'expected_head':m['expected_head'],'source_pin_count':len(before),'runtime_edits':False}
 try:
  for r in m['files']:
   target=G/r['path'];shutil.copy2(target,run/(target.name+'.preimage'));fd,tmp=tempfile.mkstemp(prefix='.carry_test_apply_',dir=target.parent)
   with os.fdopen(fd,'wb')as f:f.write((O/r['source']).read_bytes())
   os.chmod(tmp,target.stat().st_mode&0o777);os.replace(tmp,target);assert sha(target)==r['sha256']
  after=snap();expected={r['path']:r['sha256']for r in m['files']};assert set(before)==set(after);assert {p for p in before if before[p]!=after[p]}==set(expected);assert all(after[p]==h for p,h in expected.items());save(run/'SOURCE_START.json',after);report.update(status='APPLIED_EXACT_TWO_FILES',applied_utc=now(),changes={r['path']:{'old':r['pre_sha256'],'new':r['sha256']}for r in m['files']});save(run/'APPLY_RECEIPT.json',report)
  start=time.monotonic()
  with(run/'secondary_engineering_cell.log').open('w')as log:r=subprocess.run(['python','tools/validate.py','--only','secondary_engineering_cell'],cwd=G,stdout=log,stderr=subprocess.STDOUT,timeout=720)
  for src,dest in [('artifacts/validation_secondary_engineering_cell_fixed60.json','VALIDATION.json'),('artifacts/secondary_engineering_cell_validation.json','CELL_RECEIPT.json')]:
   if(G/src).exists():shutil.copy2(G/src,run/dest)
  final=snap();drift={p:{'before':after.get(p),'after':final.get(p)}for p in set(after)|set(final)if after.get(p)!=final.get(p)};save(run/'SOURCE_DRIFT.json',drift);v=json.loads((run/'VALIDATION.json').read_text())if(run/'VALIDATION.json').exists()else{};report.update(status='PASS_STANDARD_REGISTERED_CELL'if r.returncode==0 and not drift else'FAILED_PRESERVE_EVIDENCE',finished_utc=now(),wall_seconds=round(time.monotonic()-start,4),exit_code=r.returncode,source_drift=drift,validation=v);save(run/'RUN_RECEIPT.json',report);print(json.dumps(report,indent=2));raise SystemExit(0 if report['status']=='PASS_STANDARD_REGISTERED_CELL'else 1)
 except Exception as exc:
  report.update(status='FAILED_PRESERVE_EVIDENCE',finished_utc=now(),failure=str(exc));save(run/'RUN_RECEIPT.json',report);raise
if __name__=='__main__':main()
