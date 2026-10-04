"""Private GitHub checkpoint mirror. Never rewrites production Git histories.

Authentication lives outside all source/mirror trees. Remote divergence, oversized
files and uncertain writes stop the service; no force pushes or blind retries.
"""
from pathlib import Path
import argparse, datetime, fcntl, hashlib, json, os, re, shutil, subprocess, time
from automatic_backup import inventory, safe_name, atomic_json, digest, SnapshotChanged

TOKEN = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|AKIA[A-Z0-9]{16})')
TEXT = {'.py','.json','.md','.gd','.txt','.yml','.yaml','.cfg','.ini','.sh','.ps1'}

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def command(args, cwd, env=None):
    return subprocess.check_output(args, cwd=cwd, env=env, stderr=subprocess.PIPE, timeout=600).decode().strip()

def git(config, *args):
    env=os.environ.copy();env['GH_CONFIG_DIR']=config['auth_directory']
    return command(['git','-c','credential.helper=','-c','credential.helper=!gh auth git-credential',*args],config['mirror'],env)

def remote_head(config):
    row=git(config,'ls-remote','origin','refs/heads/main')
    if not row:raise RuntimeError('Expected remote main is missing')
    return row.split()[0]

def verify_private(config):
    env=os.environ.copy();env['GH_CONFIG_DIR']=config['auth_directory']
    info=json.loads(command(['gh','api','repos/'+config['repository']],config['mirror'],env))
    if info.get('full_name')!=config['repository'] or info.get('private') is not True:
        raise RuntimeError('Backup destination identity/private visibility not verified; no upload')

def eligible(path, name):
    if not safe_name(name) or path.is_symlink():raise RuntimeError('Unsafe backup path: '+name)
    if path.stat().st_size>95*1024*1024:raise RuntimeError('File exceeds conservative Git size ceiling; review LFS/storage: '+name)
    if path.suffix.lower() in TEXT and TOKEN.search(path.read_bytes()):raise RuntimeError('Credential-like text requires review: '+name)

def sync_project(project, info, mirror):
    prefix=project['prefix'];assert prefix in {'Game','BlenderCatalogue'}
    src=Path(project['root']);dst=mirror/prefix;hashes={}
    for name,size,mtime in info['entries']:
        origin=src/name;eligible(origin,name);h=digest(origin);hashes[name]=h;target=dst/name
        if not target.exists() or digest(target)!=h:
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(origin,target)
        if digest(target)!=h:raise RuntimeError('Stable copy hash mismatch: '+name)
    # Only the generated mirror is pruned, never source or retained history.
    for target in dst.rglob('*'):
        if target.is_file() and target.relative_to(dst).as_posix() not in hashes:target.unlink()
    if inventory(project)['signature']!=info['signature']:
        raise SnapshotChanged('Source changed during checkpoint; no upload attempted')
    return hashes

def run_once(config, force=False):
    state_path=Path(config['state']);state=json.loads(state_path.read_text())
    if state.get('blocked'):raise RuntimeError('Recorded backup blocker requires review')
    infos={p['name']:inventory(p) for p in config['projects']}
    changed=any(state.get('projects',{}).get(n,{}).get('signature')!=i['signature'] for n,i in infos.items())
    if not changed:return False
    committed=any(state.get('projects',{}).get(n,{}).get('head')!=i['head'] for n,i in infos.items())
    elapsed=time.time()-state.get('last_verified_epoch',0)
    if not force and not committed and elapsed<config.get('wip_interval_seconds',900):return False
    mirror=Path(config['mirror']);verify_private(config)
    expected=state['remote_commit'];actual=remote_head(config)
    if actual!=expected:raise RuntimeError('Remote main changed outside this publisher; preserve both histories and review')
    if git(config,'rev-parse','HEAD')!=expected:raise RuntimeError('Mirror has an unpublished commit; inspect before retrying')
    checkpoint={'created_utc':now(),'scope':'Source checkpoint; WIP may be untested','projects':{}}
    for p in config['projects']:
        info=infos[p['name']];hashes=sync_project(p,info,mirror)
        checkpoint['projects'][p['name']]={'head':info['head'],'signature':info['signature'],'work_in_progress':info['dirty'],'prefix':p['prefix'],'files':hashes}
        git(config,'fetch',p['root'],info['head']+':refs/heads/source/'+p['name'].lower())
    for p in config['projects']:
        if inventory(p)['signature']!=infos[p['name']]['signature']:raise SnapshotChanged('Source changed before commit; no upload attempted')
    atomic_json(mirror/'CHECKPOINT.json',checkpoint)
    # Keep hourly checks small: the full hash manifest is for local audits.
    summary={'schema':1,'checkpoint_created_utc':checkpoint['created_utc'],
             'manifest_sha256':digest(mirror/'CHECKPOINT.json'),
             'projects':{n:{'head':p['head'],'work_in_progress':p['work_in_progress'],
                            'file_count':len(p['files']),'prefix':p['prefix']}
                         for n,p in checkpoint['projects'].items()},
             'scope':'Source checkpoint metadata. Verify remote refs separately; no release or final-art acceptance implied.',
             'workshop_copy_verified':False}
    atomic_json(mirror/'BACKUP_STATUS.json',summary)
    git(config,'add','-f','--','Game','BlenderCatalogue','CHECKPOINT.json','BACKUP_STATUS.json')
    git(config,'-c','user.name=Higgins','-c','user.email=higgins@localhost','commit','-q','-m','Automatic source checkpoint '+checkpoint['created_utc'])
    intended=git(config,'rev-parse','HEAD')
    state.update(status='uploading',pending_commit=intended,attempted_utc=now());atomic_json(state_path,state)
    try:git(config,'push','--atomic','origin','main','source/godot','source/blender')
    except Exception:
        # A failed transport may have completed remotely. Read before deciding.
        if remote_head(config)!=intended:raise RuntimeError('Push failed or remains unverified; no blind retry')
    if remote_head(config)!=intended:raise RuntimeError('Remote commit mismatch after push')
    state.update(status='healthy',remote_commit=intended,verified_utc=now(),last_verified_epoch=time.time(),projects={n:{'head':i['head'],'signature':i['signature'],'work_in_progress':i['dirty']}for n,i in infos.items()})
    state.pop('pending_commit',None);atomic_json(state_path,state)
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True,type=Path);ap.add_argument('--watch',action='store_true');ap.add_argument('--force',action='store_true',help='Checkpoint changed WIP now without changing its regular cadence');args=ap.parse_args();c=json.loads(args.config.read_text());runtime=Path(c['state']).parent
    if args.watch and args.force:ap.error('A watcher must respect the regular WIP cadence')
    with (runtime/'github.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        while True:
            atomic_json(runtime/'github_runner.json',{'pid':os.getpid(),'heartbeat_utc':now(),'config':str(args.config)})
            try:
                changed=run_once(c,args.force)
                if changed:print('Verified GitHub checkpoint',flush=True)
            except SnapshotChanged:
                state=json.loads(Path(c['state']).read_text());state.update(status='waiting_for_stable_source');atomic_json(Path(c['state']),state)
            except Exception as e:
                state=json.loads(Path(c['state']).read_text());state.update(status='blocked',blocked=True,error=str(e),failed_utc=now());atomic_json(Path(c['state']),state);raise
            if not args.watch:break
            time.sleep(c.get('poll_seconds',15))

if __name__=='__main__':main()
