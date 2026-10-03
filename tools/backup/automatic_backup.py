"""Astraea checkpoint/WIP retention through the unmodified official Library helper.

No credentials are stored. The session supervisor must supply a freshly obtained
helper path. This runner is deliberately fail-closed after an uncertain upload.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys, tempfile, time, zipfile
import fcntl

EXCLUDED = {'.git','.godot','__pycache__','node_modules','Library','Temp','obj','bin'}
SECRETS = {'.env','.env.local','credentials.json','secrets.json','id_rsa','id_ed25519'}

class SnapshotChanged(RuntimeError):
    pass

def atomic_json(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.new')
    temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.PIPE)

def safe_name(name):
    p=Path(name)
    return not p.is_absolute() and '..' not in p.parts and not set(p.parts)&EXCLUDED and p.name not in SECRETS and not p.name.endswith(('.blend1','.pem','.key'))

def inventory(project):
    root=Path(project['root']);head=git(root,'rev-parse','HEAD').decode().strip()
    tracked=git(root,'ls-files','-z').decode().rstrip('\0').split('\0')
    others=git(root,'ls-files','--others','--exclude-standard','-z').decode().rstrip('\0').split('\0')
    allowed={'assets','scripts','scenes','shaders','data','tools','tests','docs','materials','standards','references','batches'}
    new=[n for n in others if n and (Path(n).parts[0] in allowed or (len(Path(n).parts)==1 and Path(n).suffix in {'.md','.json','.gd','.godot','.py'}))]
    names=sorted(set(tracked+new));entries=[];missing=[]
    for name in names:
        if not safe_name(name):continue
        p=root/name
        if not p.exists():missing.append(name);continue
        if p.is_symlink():raise ValueError('Symlink not eligible for backup: '+name)
        if not p.is_file():continue
        stat=p.stat();entries.append((name,stat.st_size,stat.st_mtime_ns))
    dirty=git(root,'status','--porcelain','--untracked-files=normal').decode()
    signature=hashlib.sha256(json.dumps([head,entries,missing],sort_keys=True).encode()).hexdigest()
    return {'head':head,'entries':entries,'missing':missing,'dirty':bool(dirty),'signature':signature}

def selected_files(project, info):
    # Full portable production source every time. Historical QA/reference files
    # remain in the retained Git baseline; include any changed/uncommitted ones.
    names=[x[0] for x in info['entries']]
    if project['kind']=='godot':return names
    root=Path(project['root'])
    dirty=set(git(root,'diff','--name-only','HEAD','-z').decode().rstrip('\0').split('\0'))
    dirty.update(git(root,'ls-files','--others','--exclude-standard','-z').decode().rstrip('\0').split('\0'))
    return [n for n in names if n in dirty or (not set(Path(n).parts)&{'qa','references'} and not n.endswith(('.log','.pdf','.mp4','.gif')))]

def snapshot(project, info, output, retained, part_limit=20*1024*1024):
    root=Path(project['root']);output.mkdir(parents=True,exist_ok=True)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    stem=f"Astraea_AUTO_{project['name']}_{stamp}_{info['head'][:8]}"
    stage=Path(tempfile.mkdtemp(prefix='stage-',dir=output));files={}
    try:
        for name in selected_files(project,info):
            src=root/name;dest=stage/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
            files['source/'+name]=dest
        base=retained.get('head')
        if base != info['head']:
            bundle=stage/'history.bundle'
            revision=base+'..HEAD' if base else '--all'
            if base:subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',base,info['head']],check=True,capture_output=True)
            subprocess.run(['git','-C',str(root),'bundle','create',str(bundle),revision],check=True,capture_output=True)
            subprocess.run(['git','-C',str(root),'bundle','verify',str(bundle)],check=True,capture_output=True)
            files['history.bundle']=bundle
        after=inventory(project)
        if after['signature'] != info['signature']:raise SnapshotChanged('Source changed during snapshot; no upload attempted')
        hashes={n:digest(p) for n,p in files.items()}
        manifest={'schema':1,'project':project['name'],'head':info['head'],'work_in_progress':info['dirty'],
                  'source_signature':info['signature'],'files':hashes,'deleted_tracked_files':info['missing'],
                  'history_prerequisite':base,'parent_retained_library_ids':retained.get('library_file_ids',[]),
                  'scope':'Full portable production source; historical catalogue QA/references live in retained history and reference archives. No runnable/final-art acceptance implied.'}
        groups=[];current=[];size=0
        for name,path in files.items():
            n=path.stat().st_size
            if current and size+n>part_limit:groups.append(current);current=[];size=0
            current.append((name,path));size+=n
        if current:groups.append(current)
        result=[]
        for i,group in enumerate(groups):
            target=output/f'{stem}_part{i+1:02}.zip'
            with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
                for name,path in group:z.write(path,name)
                part=dict(manifest,part=i+1,parts=len(groups),files={n:hashes[n] for n,p in group})
                z.writestr('MANIFEST.json',json.dumps(part,indent=2)+'\n')
                z.writestr('READ_ME.txt','Extract every part of this checkpoint into one empty folder. The source folder contains the current portable production files. Work-in-progress checkpoints may be untested. Git history can be incremental; see manifest prerequisites. Do not delete previous retained checkpoints or reference archives.\n')
            with zipfile.ZipFile(target) as z:
                if z.testzip() is not None:raise ValueError('Archive CRC failed')
                for name,path in group:
                    if hashlib.sha256(z.read(name)).hexdigest()!=hashes[name]:raise ValueError('Archive hash mismatch')
            result.append({'path':str(target),'sha256':digest(target),'bytes':target.stat().st_size})
        return result
    finally:shutil.rmtree(stage)

def upload(helper, archives, log):
    if not Path(helper).is_file():raise RuntimeError('Current official upload helper unavailable; no independent backup claimed')
    request={'uploads':[{'local_path':a['path'],'purpose':'create_library_file','library_artifact_type':'other'} for a in archives]}
    result=subprocess.run([sys.executable,helper],input=json.dumps(request),text=True,capture_output=True,timeout=600)
    # Tool output can contain private transfer details. Keep it local, never archive it.
    log.write_text(result.stdout+'\n'+result.stderr)
    payload=None
    for line in reversed(result.stdout.splitlines()):
        try:
            candidate=json.loads(line)
            if isinstance(candidate,dict) and 'results' in candidate:payload=candidate;break
        except json.JSONDecodeError:pass
    if result.returncode or payload is None:raise RuntimeError('Upload outcome failed or uncertain; automatic retries are stopped')
    rows=payload['results']
    if len(rows)!=len(archives):raise RuntimeError('Incomplete upload result; automatic retries are stopped')
    for expected,row in zip(archives,rows):
        if row.get('local_path')!=expected['path'] or row.get('status')!='succeeded' or not row.get('library_file_id') or not row.get('local_metadata_applied'):
            raise RuntimeError('One or more files were not fully retained; automatic retries are stopped')
    return [{'library_file_id':r['library_file_id'],'file_id':r.get('file_id'),'version':r.get('current_version_number'),**a} for r,a in zip(rows,archives)]

def run_once(config, force=False):
    state_path=Path(config['state']);state=json.loads(state_path.read_text()) if state_path.exists() else {'projects':{}}
    if state.get('blocked'):raise RuntimeError('Backup service is blocked pending review of its recorded failure')
    output=Path(config['output']);output.mkdir(parents=True,exist_ok=True)
    with (output/'service.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return {'status':'busy'}
        for project in config['projects']:
            info=inventory(project);prior=state['projects'].get(project['name'],project.get('retained_baseline',{}))
            if not force and prior.get('signature')==info['signature']:continue
            state['active_project']=project['name'];state['status']='packaging';state['heartbeat_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();atomic_json(state_path,state)
            try:
                archives=snapshot(project,info,output,project.get('retained_baseline',prior),config.get('part_limit_bytes',20*1024*1024))
                state['status']='uploading';state['pending_archives']=archives;atomic_json(state_path,state)
                rows=upload(config['upload_helper'],archives,output/(project['name']+'_last_upload.private.log'))
                receipt={'head':info['head'],'signature':info['signature'],'work_in_progress':info['dirty'],
                         'library_file_ids':[r['library_file_id'] for r in rows],'archives':rows,
                         'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                         'archive_integrity_verified':True,'independent_retention_verified':True,'workshop_copy_verified':False}
                state['projects'][project['name']]=receipt;state['status']='healthy';state.pop('pending_archives',None);state.pop('active_project',None)
                atomic_json(state_path,state)
                atomic_json(output/(project['name']+'_last_verified_receipt.json'),receipt)
            except SnapshotChanged:
                state['status']='waiting_for_stable_source';atomic_json(state_path,state)
                return {'status':'retry_pending'}
            except Exception as error:
                state.update(status='blocked',blocked=True,error=str(error),failed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
                atomic_json(state_path,state);raise
        state['heartbeat_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();atomic_json(state_path,state)
        return {'status':state.get('status','unchanged'),'projects':{k:v.get('verified_utc') for k,v in state['projects'].items()}}

def install_hooks(config_path,config):
    command=Path(__file__).resolve()
    import shlex
    for project in config['projects']:
        root=Path(project['root']);hook=root/'.git/hooks/post-commit'
        marker='# Astraea automatic backup request hook v1'
        if hook.exists() and marker not in hook.read_text():raise RuntimeError('Existing post-commit hook preserved: '+str(hook))
        hook.write_text('#!/bin/sh\n'+marker+'\n'+shlex.quote(sys.executable)+' '+shlex.quote(str(command))+' request --config '+shlex.quote(str(config_path))+'\n')
        hook.chmod(0o755)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['once','watch','request','install-hooks','status'])
    parser.add_argument('--config',required=True,type=Path);parser.add_argument('--force',action='store_true')
    args=parser.parse_args();config=json.loads(args.config.read_text());request=Path(config['output'])/'checkpoint.request'
    if args.action=='request':request.parent.mkdir(parents=True,exist_ok=True);request.touch();return
    if args.action=='install-hooks':install_hooks(args.config.resolve(),config);print('Hooks installed');return
    if args.action=='status':print(Path(config['state']).read_text());return
    if args.action=='once':print(json.dumps(run_once(config,args.force)));return
    last=time.monotonic();request.parent.mkdir(parents=True,exist_ok=True)
    atomic_json(Path(config['output'])/'runner.json',{'pid':os.getpid(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'config':str(args.config.resolve())})
    while not (Path(config['output'])/'STOP').exists():
        due=request.exists() or time.monotonic()-last>=config.get('wip_interval_seconds',900)
        if due:
            # Do not consume a later request that arrives during retention.
            mtime=request.stat().st_mtime_ns if request.exists() else None
            try:
                outcome=run_once(config);print(json.dumps(outcome),flush=True)
                if outcome['status']=='retry_pending':
                    request.touch();time.sleep(config.get('poll_seconds',15));continue
            except Exception as error:print('BACKUP_BLOCKED: '+str(error),flush=True);return
            if request.exists() and request.stat().st_mtime_ns==mtime:request.unlink()
            last=time.monotonic()
        time.sleep(config.get('poll_seconds',15))

if __name__=='__main__':main()
