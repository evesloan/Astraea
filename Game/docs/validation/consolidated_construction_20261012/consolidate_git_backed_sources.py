import pathlib,json,subprocess,hashlib,os
R=pathlib.Path('/workspace/astraea-protected-integration-20261012');O=pathlib.Path(__file__).parent;S='/workspace/astraea-readonly-interface-review-20261012/remote_only_20261012T000749Z.git';base='affc5c807087ff87da29f3642c2d6e418241b896';snap=json.loads((O/'EIGHT_OWNER_SOURCE_SNAPSHOT.json').read_text())
def git(repo,*a):
 cmd=['git','-C',str(repo),*a]
 try:return subprocess.check_output(cmd)
 except subprocess.CalledProcessError:return subprocess.check_output(cmd)
def tree(repo,ref):
 out={}
 for entry in git(repo,'ls-tree','-r','-z',ref).split(b'\0'):
  if not entry:continue
  h,p=entry.split(b'\t',1);mode,kind,blob=h.decode().split();out[p.decode()]={'mode':mode,'kind':kind,'blob':blob}
 return out
current=tree(R,'HEAD');baseline=tree(S,base);known={};summary={};index_paths={}
for p,row in current.items():
 if row['kind']=='blob':known.setdefault(row['blob'],{'storage_path':p})
for file in R.glob('RetainedConstruction/group*/SOURCE_MAP.json'):
 for row in json.loads(file.read_text())['files']:known[row['source_git_blob']]={'storage_path':row['storage_path'],'bytes':row['bytes'],'sha256':row['sha256']}
for group,info in snap.items():
 source=tree(S,info['commit']);rows=[];counts={'existing_exact':0,'deduplicated':0,'held_new':0,'held_collision':0};materialized=0;git_backed=0
 for p,item in source.items():
  if item==baseline.get(p):continue
  assert item['kind']=='blob'and not pathlib.PurePosixPath(p).is_absolute()and'..'not in pathlib.PurePosixPath(p).parts
  blob=item['blob'];state='held_collision'if(R/p).exists()else'held_new';storage=f'RetainedConstruction/group{group}/revisions/{info["commit"][:12]}/'+p+('.declared_symlink'if item['mode']=='120000'else'')
  if p in current and current[p]['blob']==blob:storage=p;state='existing_exact'
  elif(R/p).is_file()and git(R,'hash-object','--',p).decode().strip()==blob:storage=p;state='existing_exact'
  elif blob in known:storage=known[blob]['storage_path'];state='deduplicated'
  dest=R/storage;cached=known.get(blob,{})
  if cached.get('sha256')and cached.get('storage_path')==storage:
   length=cached['bytes'];h=cached['sha256']
  elif dest.is_file():
   assert git(R,'hash-object','--',storage).decode().strip()==blob,storage;length=dest.stat().st_size;digest=hashlib.sha256()
   with dest.open('rb')as f:
    for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
   h=digest.hexdigest()
  else:
   length=int(git(S,'cat-file','-s',blob));digest=hashlib.sha256();objecthash=hashlib.sha1(b'blob '+str(length).encode()+b'\0');read=0
   process=subprocess.Popen(['git','-C',S,'cat-file','blob',blob],stdout=subprocess.PIPE)
   while True:
    chunk=process.stdout.read(1024*1024)
    if not chunk:break
    digest.update(chunk);objecthash.update(chunk);read+=len(chunk)
   assert process.wait()==0 and read==length and objecthash.hexdigest()==blob,p;h=digest.hexdigest()
   # Retain small contracts locally; large inactive payloads stay in the same
   # consolidated Git tree, without a second working-copy binary transfer.
   if length<128*1024:
    data=git(S,'cat-file','blob',blob);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  exists=dest.is_file();materialized+=int(exists);git_backed+=int(not exists);counts[state]+=1
  known[blob]={'storage_path':storage,'bytes':length,'sha256':h}
  if storage not in current:index_paths[storage]={'git_blob_sha':blob,'bytes':length,'sha256':h,'mode':'100644'if item['mode']=='120000'else item['mode'],'materialized':exists}
  rows.append({'source_path':p,'source_git_blob':blob,'source_mode':item['mode'],'storage_path':storage,'bytes':length,'sha256':h,'retention_state':state,'materialized':exists,'activation':'Source retention only;installed selected revisions listed in eight-group inventory'})
  if len(rows)%250==0:print(f'Group{group}: {len(rows)} exact entries;{git_backed} Git-backed inactive files',flush=True)
 source_map={'group':int(group),'source_commit':info['commit'],'source_tree':info['tree'],'baseline':base,'files':rows,'counts':counts,'materialized_files':materialized,'git_backed_inactive_files':git_backed,'worker_snapshot_has_no_original_deletions':all(p in source for p in baseline)}
 path=R/f'RetainedConstruction/group{group}/SOURCE_MAP.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(source_map,indent=2)+'\n');summary[group]={k:v for k,v in source_map.items()if k!='files'};print('GROUP COMPLETE',group,counts,flush=True)
report={'snapshots':summary,'index_paths':index_paths,'source_entries':sum(sum(x['counts'].values())for x in summary.values()),'one_working_branch':'construction/group1-tidal-d15-20261010','no_held_runtime_imports':True,'large_inactive_payloads':'Exactly indexed Git-backed storage in same branch;source-map locations remain visible in working copy','source_objects_store':S,'new_branch_created':False}
(O/'OWNER_SOURCE_CONSOLIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print('COMPLETE',report['source_entries'],len(index_paths))
