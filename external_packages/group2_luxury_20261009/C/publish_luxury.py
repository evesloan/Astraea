"""Owner-approved additive Group2 source milestone on one unique private branch."""
import pathlib,subprocess,json,hashlib,sys,datetime
R=pathlib.Path(__file__).resolve().parent;repo=R/'read_repository';verify=R/'remote_verification';URL='https://github.com/evesloan/Astraea.git';BRANCH='handoff/group2-luxury-c-20261009';BASE='9311ce52e625a5ef797770931a598dd78fb3c66e';archive=pathlib.Path(sys.argv[1]).resolve();assert archive.is_relative_to((R/'deliveries').resolve()) and archive.suffix=='.zip';summary=archive.with_suffix('.json');assert summary.exists();assert json.loads(summary.read_text())['archive_sha256']==hashlib.sha256(archive.read_bytes()).hexdigest()
def git(args,cwd=repo,data=None):
 result=subprocess.run(['git',*args],cwd=cwd,input=data,capture_output=True);assert result.returncode==0,result.stderr.decode(errors='replace');return result.stdout.decode().strip()
git(['config','user.name','Astraea Group2 C']);git(['config','user.email','group2-c@local.invalid']);local_proc=subprocess.run(['git','show-ref','--verify','--hash','refs/heads/'+BRANCH],cwd=repo,capture_output=True);local=local_proc.stdout.decode().strip() if local_proc.returncode==0 else BASE;remote=git(['ls-remote',URL,'refs/heads/'+BRANCH]);remote_sha=remote.split()[0] if remote else None
if remote_sha:assert remote_sha==local,'Handoff branch changed externally; no overwrite'
git(['read-tree',local]);targets=[]
coord=R/'delivery_coordination'/archive.stem;coord.mkdir(parents=True,exist_ok=True)
files=[(archive,'deliveries/'+archive.name),(summary,'deliveries/'+summary.name)]
for name in ['GROUP2_GROUP7_BOUNDARY_SHEET.json','GROUP2_STATUS.json']:
 snapshot=coord/name
 if not snapshot.exists():snapshot.write_bytes((R/name).read_bytes())
 files.append((snapshot,name))
for file,target_relative in files:
 assert file.exists();path='external_packages/group2_luxury_20261009/C/'+target_relative;oid=git(['hash-object','--no-filters','-w',str(file)]);git(['update-index','--add','--cacheinfo','100644',oid,path]);targets.append({'path':path,'git_blob':oid,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
tree=git(['write-tree','--missing-ok']);commit=git(['commit-tree',tree,'-p',local],data=('Group2 luxury source milestone: '+archive.stem+'\n').encode());changed=git(['diff-tree','--no-commit-id','--name-only','-r',local,commit]).splitlines();assert set(changed)<=set(x['path'] for x in targets);git(['update-ref','refs/heads/'+BRANCH,commit]);git(['push',URL,commit+':refs/heads/'+BRANCH]);assert git(['ls-remote',URL,'refs/heads/'+BRANCH]).split()[0]==commit
verify.mkdir(exist_ok=True)
if not (verify/'.git').exists():git(['init'],cwd=verify)
git(['fetch','--depth=1','--filter=blob:none',URL,'refs/heads/'+BRANCH],cwd=verify);assert git(['rev-parse','FETCH_HEAD'],cwd=verify)==commit
for t in targets:
 entry=git(['ls-tree',commit,t['path']],cwd=verify);assert entry.split()[2]==t['git_blob'];raw=subprocess.check_output(['git','cat-file','blob',t['git_blob']],cwd=verify);assert len(raw)==t['bytes'] and hashlib.sha256(raw).hexdigest()==t['sha256']
receipt={'branch':BRANCH,'commit':commit,'independent_fresh_remote_download':True,'files':targets,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'main_written':False,'credentials_changed':False,'shared_live_registry_changed':False,'only_allowlisted_additive_delivery_and_coordination_files':changed};(R/(archive.stem+'_REMOTE_RECEIPT.json')).write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
