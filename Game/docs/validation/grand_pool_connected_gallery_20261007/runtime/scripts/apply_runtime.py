"""Reviewed bounded east-gallery installation. No engine/import/commit from this script."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,stat,subprocess,sys
assert not sys.flags.optimize
S=Path(__file__).resolve().parent
G=Path('/workspace/shared/astraea-godot-production-20261003');B=Path('/workspace/shared/astraea-github-backup')
M=S/'FINAL_APPLY_MANIFEST.json';EXPECTED_MANIFEST='e15ddd0611fd59ce133570b5ab0debdb799d3de42286c369366853523f844dae'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def read(p):return json.loads(Path(p).read_text())
def snapshot():
 out={}
 for directory,dirs,names in os.walk(G):
  dirs[:]=sorted(d for d in dirs if d not in {'.git','.godot'})
  for d in dirs:need(not (Path(directory)/d).is_symlink(),'Symlink directory in source tree')
  for n in sorted(names):
   p=Path(directory)/n;need(not p.is_symlink(),'Symlink source file')
   if p.is_file():out[str(p.relative_to(G))]=sha(p)
 return out
def git(*args):return subprocess.check_output(['git','-C',str(G),*args],text=True).strip()
def quiet():
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:cmd=(proc/'cmdline').read_bytes().split(b'\0')
  except (FileNotFoundError,ProcessLookupError,PermissionError):continue
  if cmd and Path(os.fsdecode(cmd[0])).name.lower().startswith('godot'):raise RuntimeError('A Godot process is active: '+proc.name)
 need(not list(Path('/workspace/shared/astraea-review-queue').glob('*.request')),'A queued review job has priority')
need(sha(M)==EXPECTED_MANIFEST,'Reviewed manifest changed');m=read(M)
need(m['status']=='FROZEN_REVIEWED_CANDIDATE_UNINSTALLED','Manifest has wrong scope')
need(git('rev-parse','HEAD')==m['game_head'],'Game HEAD changed; preserve and rebase')
need(sha(G/'.git/index')==m['index_sha256'],'Existing Game index changed')
quiet();before=snapshot();need(before==m['source_before'],'Game source changed since reviewed boundary')
need(sha(S/'INDEPENDENT_PREIMAGE_PROOF.json')==m['preimage_proof_sha256'],'Preimage proof changed')
proof=read(S/'INDEPENDENT_PREIMAGE_PROOF.json')
need(proof['status']=='PASS_ALL_MUTATION_PREIMAGES_INDEPENDENTLY_RETAINED','Missing preimage protection')
cp=subprocess.check_output(['git','-C',str(B),'show',proof['remote_commit']+':CHECKPOINT.json']);need(hashlib.sha256(cp).hexdigest()==proof['checkpoint_sha256'],'Retained checkpoint changed')
checkpoint=json.loads(cp)
for row in proof['files']:
 p=row['path'];need(before[p]==row['sha256']and sha(B/'Game'/p)==row['sha256']and checkpoint['projects']['Godot']['files'][p]==row['sha256'],'Modified-file preimage differs from retained exact version: '+p)
 need(sha(S/'preimages'/p)==row['sha256'],'Local preserved preimage missing or changed')
retained={x['path']:x['sha256']for x in proof['retained_catalogue_files']}
for rel,digest in retained.items():
 need(sha(Path('/workspace/shared/astraea-catalogue-continuation-20261002')/rel)==digest,'Retained gallery source changed')
 need(checkpoint['projects']['Blender']['files'][rel]==digest,'Retained source is not in immutable independently verified checkpoint')
seen=set();changes={}
for row in m['files']:
 rel=Path(row['target']);src=Path(row['source']);dst=G/rel
 need(not rel.is_absolute()and '..'not in rel.parts and str(rel)not in seen,'Unscoped/duplicate target');seen.add(str(rel))
 need(src.is_file()and not src.is_symlink()and src.resolve().is_relative_to(S.parent),'Unsafe staged source')
 need(sha(src)==row['sha256']and src.stat().st_size==row['bytes'],'Staged candidate changed')
 for parent in dst.parents:
  if parent==G.parent:break
  need(not parent.is_symlink(),'Symlink target ancestor')
 if row['kind']=='modify':
  need(dst.is_file()and not dst.is_symlink()and sha(dst)==row['before_sha256'],'Modified preimage changed')
  need(stat.S_IMODE(dst.stat().st_mode)==row['mode'],'Existing target mode changed')
  need(before[str(rel)]==row['before_sha256'],'Unpinned existing target')
 else:need(row['kind']=='new'and not dst.exists()and not dst.is_symlink()and str(rel)not in before,'New-only target already exists')
 if row.get('retained_export_path'):
  need(retained[row['retained_export_path']]==row['sha256'],'Export is not exact independently retained artifact')
  ep=row['retained_export_path'];need(sha(Path('/workspace/shared/astraea-catalogue-continuation-20261002')/ep)==row['sha256']and sha(B/'BlenderCatalogue'/ep)==row['sha256'],'Retained export live/mirror bytes changed')
 changes[str(rel)]=row['sha256']
need(len(changes)==m['file_count'],'Reviewed file count mismatch')
a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');args=a.parse_args()
if not args.apply:
 print(json.dumps({'status':'READ_ONLY_RUNTIME_PREFLIGHT_PASS','file_count':len(changes),'existing_source_files':len(before),'new':sum(x['kind']=='new'for x in m['files']),'modified':sum(x['kind']=='modify'for x in m['files']),'manifest_sha256':EXPECTED_MANIFEST,'engine_started':False}));sys.exit(0)
quiet();need(snapshot()==before,'Game changed during preflight')
tag=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');R=S/'apply_receipts'/tag;R.mkdir(parents=True,exist_ok=False)
receipt={'status':'APPLYING_CHECKED_CONNECTED_CURVED_POOL_GALLERY_CANDIDATE','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':EXPECTED_MANIFEST,'written':[],'existing_modes_preserved':True,'new_modes':'Actual restrictive process umask; no chmod or settings changes','engine_started':False,'validated_installed_candidate':False}
def save():(R/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
save()
try:
 for row in m['files']:
  src=Path(row['source']);dst=G/row['target'];need(sha(src)==row['sha256'],'Staged bytes changed just before write');dst.parent.mkdir(parents=True,exist_ok=True)
  if row['kind']=='new':
   need(not dst.exists()and not dst.is_symlink(),'New target appeared')
   with dst.open('xb')as f:f.write(src.read_bytes());f.flush();os.fsync(f.fileno())
  else:
   need(sha(dst)==row['before_sha256']and stat.S_IMODE(dst.stat().st_mode)==row['mode'],'Existing preimage changed just before write')
   with dst.open('r+b')as f:f.seek(0);f.write(src.read_bytes());f.truncate();f.flush();os.fsync(f.fileno())
   need(stat.S_IMODE(dst.stat().st_mode)==row['mode'],'Existing permissions changed')
  need(sha(dst)==row['sha256'],'Written bytes do not match reviewed target');receipt['written'].append(row['target']);save()
 after=snapshot();expected=dict(before);expected.update(changes);drift=[p for p in sorted(set(expected)|set(after))if expected.get(p)!=after.get(p)];need(not drift,'Unexpected source drift: '+str(drift))
 need(git('rev-parse','HEAD')==m['game_head']and sha(G/'.git/index')==m['index_sha256'],'Git HEAD/index changed')
 receipt.update(status='INSTALLED_CONNECTED_CURVED_POOL_GALLERY_CANDIDATE_IMPORT_AND_FOCUSED_CHECK_PENDING',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),written_count=len(changes),unrelated_source_files_unchanged=len(before)-sum(x['kind']=='modify'for x in m['files']),unexpected_changes=drift,head_and_index_unchanged=True);save();print(json.dumps(receipt))
except BaseException as error:
 receipt.update(status='STOPPED_PRESERVE_EXACT_PARTIAL_STATE',error=repr(error),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save();raise
