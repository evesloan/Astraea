"""Parent-controlled UNVERIFIED_IMPORT_EQUIVALENCE visual-study runner. Default is read-only prepared-input check.
Freeze only after engineering/theater release; no automatic import or repair.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys, threading, time
S=Path(__file__).resolve().parent
GAME=Path('/workspace/shared/astraea-godot-production-20261003')
FREEZE=S/'FINAL_CURRENT_FREEZE.json'
EXCLUDED={'.git','.godot','artifacts','__pycache__'}
PREPARED=['visual_import.gd','trial.gd','run_trial.py','HANDOFF.md','NATIVE_INPUTS.json','parent_graphical.sh']
def require(ok,msg):
    if not ok:raise RuntimeError(msg)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write_new(p,value):
    with Path(p).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def tree_snapshot(root,exclude=()):
    require(root.is_dir(),'Missing expected tree '+str(root));result={}
    for directory,dirs,names in os.walk(root):
        dirs[:]=sorted(d for d in dirs if d not in exclude)
        for d in dirs:require(not (Path(directory)/d).is_symlink(),'Symlink directory cannot be certified')
        for name in sorted(names):
            p=Path(directory)/name;require(not p.is_symlink(),'Symlink file cannot be certified')
            if p.is_file():result[str(p.relative_to(root))]=sha(p)
    return result
def byte_diffs(before,after):
    return [{'path':p,'kind':'added' if p not in before else 'removed' if p not in after else 'changed','before_sha256':before.get(p),'after_sha256':after.get(p)} for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)]
def inputs():
    d=read(S/'NATIVE_INPUTS.json')
    require(d['status']=='PREPARED_UNINSTALLED_NATIVE_CHECK_NOT_RUN' and not d['installed'],'Wrong prepared scope')
    require(len(d['assets'])==7,'Need seven accepted sources')
    for p,h in d['pins'].items():require(sha(p)==h,'Pinned input changed: '+p)
    require(read(S.parent/'pool-feature-export-preparation001/runs/feature002/CORRECTION_RUN_RECEIPT.json')['status']=='PASS_EXACT_TRANSLATION_COPY_AND_UNCHANGED_STRICT_EQUIVALENCE','Correction gate absent')
    return d
def no_engine():
    p=subprocess.run(['pgrep','-x','godot'],capture_output=True,text=True)
    require(p.returncode==1,'Another Godot process exists or process status is uncertain')
    require(not list(Path('/workspace/shared/astraea-review-queue').glob('*.request')),'A coordinated review request has priority')
def verify_frozen():
    d=inputs();f=read(FREEZE)
    require(f['status']=='PARENT_RELEASED_FINAL_CURRENT_FREEZE' and f['engineering_theater_released'],'No final-current release freeze')
    require(sha(S/'NATIVE_INPUTS.json')==f['native_inputs_sha256'],'Native inputs changed after freeze')
    for p,h in f['prepared_files'].items():require(sha(S/p)==h,'Prepared tool changed after freeze: '+p)
    require(tree_snapshot(GAME,EXCLUDED)==f['game_source'],'Current Game bytes changed; reconcile and prepare a new freeze, do not use stale baseline')
    require(tree_snapshot(GAME/'.godot')==f['game_cache'],'Existing Godot cache changed; reconcile before launch, never auto-import')
    require(sha(f['engine_path'])==f['engine_sha256'],'Pinned existing engine binary changed; no switch authorized')
    return d,f

def main():
    require(not sys.flags.optimize,'Python optimization forbidden')
    ap=argparse.ArgumentParser();mode=ap.add_mutually_exclusive_group();mode.add_argument('--freeze',action='store_true');mode.add_argument('--run',action='store_true')
    ap.add_argument('--parent-released-engineering-theater',action='store_true');ap.add_argument('--release-reference');ap.add_argument('--parent-approved-game-slot',action='store_true');args=ap.parse_args()
    d=inputs()
    if args.freeze:
        require(args.parent_released_engineering_theater and args.release_reference,'Freeze needs the actual parent release reference; flags do not grant authority')
        require(not FREEZE.exists(),'Preserve prior freeze. Review/reconcile in a new preparation revision instead of overwriting')
        require(not (S/'launcher_run001').exists() and not (S/'output').exists(),'Preserve prior trial output')
        no_engine();engine=shutil.which('godot');require(engine is not None,'Existing Godot binary missing; no install/switch')
        before=tree_snapshot(GAME,EXCLUDED);cache=tree_snapshot(GAME/'.godot');no_engine()
        require(tree_snapshot(GAME,EXCLUDED)==before and tree_snapshot(GAME/'.godot')==cache,'Game changed while freezing')
        f={'status':'PARENT_RELEASED_FINAL_CURRENT_FREEZE','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'release_reference':args.release_reference,'engineering_theater_released':True,'verification':'UNVERIFIED_IMPORT_EQUIVALENCE','geometry_acceptance':False,'physical_acceptance':False,'final_acceptance':False,'installed':False,'production_changes':False,'full_suite':False,'native_inputs_sha256':sha(S/'NATIVE_INPUTS.json'),'prepared_files':{p:sha(S/p) for p in PREPARED},'engine_path':str(Path(engine).resolve()),'engine_sha256':sha(engine),'game_source':before,'game_cache':cache}
        write_new(FREEZE,f);print(json.dumps({'status':f['status'],'source_file_count':len(before),'cache_files':len(cache),'freeze_sha256':sha(FREEZE),'engine_launched':False,'installed':False}));return
    if not args.run:
        if FREEZE.exists():_,f=verify_frozen();status='FROZEN_READ_ONLY_PREFLIGHT_PASS'
        else:status='PREPARED_ACCEPTED_INPUTS_PASS_GAME_FREEZE_PENDING'
        print(json.dumps({'status':status,'accepted_glbs':7,'native_geometry':'NOT_RUN','engines_launched':False,'verification':'UNVERIFIED_IMPORT_EQUIVALENCE','geometry_acceptance':False,'physical_acceptance':False,'final_acceptance':False,'installed':False,'production_changes':False}));return
    require(args.parent_approved_game_slot,'Parent must already own the approved Game slot')
    require(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'),'Use parent existing graphical terminal; no alternate display')
    _,f=verify_frozen();no_engine()
    R=S/'launcher_run001';require(not R.exists() and not(S/'output').exists(),'Preserve previous attempt and screenshots');R.mkdir()
    env=os.environ.copy()
    for key,name in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('TMPDIR','tmp')]:
        p=R/name;p.mkdir();env[key]=str(p)
    env['ASTRAEA_POOL_NATIVE_TRIAL_RUN']='parent_guarded_unsaved'
    receipt={'status':'RUNNING_VISUAL_STUDY_UNVERIFIED_IMPORT_EQUIVALENCE','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verification':'UNVERIFIED_IMPORT_EQUIVALENCE','geometry_acceptance':False,'physical_acceptance':False,'final_acceptance':False,'installed':False,'production_changes':False,'full_suite':False,'visual_acceptance':False,'freeze_sha256':sha(FREEZE),'game_source_before_files':len(f['game_source']),'game_cache_before_files':len(f['game_cache']),'command':[f['engine_path'],'--audio-driver','Dummy','--path',str(GAME),'--resolution','1280x720','--script',str(S/'trial.gd')]}
    rp=R/'RECEIPT.json';write_new(rp,receipt);start=time.monotonic();errors=[];lines=[];proc=None;timer=None
    try:
        with (R/'engine.log').open('x') as log:
            proc=subprocess.Popen(receipt['command'],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            timer=threading.Timer(600,proc.kill);timer.start()
            for line in proc.stdout:
                log.write(line);log.flush();lines.append(line)
                if any(x in line for x in ['ERROR:','Assertion failed','Parse Error']):
                    errors.append(line.rstrip())
                    if proc.poll() is None:proc.terminate()
            proc.wait();timer.cancel()
        require(proc.returncode==0 and not errors and 'VISUAL_STUDY004_COMPLETE_UNVERIFIED_IMPORT_EQUIVALENCE' in ''.join(lines),'Trial stopped; see preserved engine log')
        verify_frozen()
        result=read(S/'output/RESULT.json')
        require(result['installed'] is False and result['geometry_acceptance'] is False and result['physical_acceptance'] is False and result['verification']=='UNVERIFIED_IMPORT_EQUIVALENCE' and result['budget']==8 and result['candidate_limit']==32 and len(result['captures'])==16,'Incomplete bounded trial result')
        receipt.update(status='VISUAL_STUDY_CAPTURE_COMPLETE_UNVERIFIED_IMPORT_EQUIVALENCE',verification='UNVERIFIED_IMPORT_EQUIVALENCE',geometry_acceptance=False,physical_acceptance=False,final_acceptance=False,primary_selection_satisfied=result['primary_selection_satisfied'],result_sha256=sha(S/'output/RESULT.json'))
    except Exception as e:
        receipt.update(status='STOPPED_PRESERVE_UNINSTALLED_EVIDENCE',error=str(e));raise
    finally:
        if timer:timer.cancel()
        if proc and proc.poll() is None:proc.terminate();proc.wait(timeout=10)
        after=tree_snapshot(GAME,EXCLUDED);cache_after=tree_snapshot(GAME/'.godot')
        write_new(R/'GAME_SOURCE_AFTER.json',after);write_new(R/'GAME_CACHE_AFTER.json',cache_after)
        diffs={'verification':'UNVERIFIED_IMPORT_EQUIVALENCE','geometry_acceptance':False,'physical_acceptance':False,'final_acceptance':False,'installed':False,'game_source':byte_diffs(f['game_source'],after),'project_godot':byte_diffs(f['game_cache'],cache_after),'strict_policy':'No project cache exclusions; only command-local XDG/TMPDIR output is operational','scratch_operational_output_roots':[str(R/x) for x in ['config','data','cache','tmp']]}
        write_new(R/'EXPLICIT_BYTE_DIFFS.json',diffs)
        unchanged=after==f['game_source'] and cache_after==f['game_cache']
        receipt.update(returncode=proc.returncode if proc else None,errors=errors,seconds=round(time.monotonic()-start,3),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_game_and_cache_bytes_unchanged=unchanged,game_source_after_sha256=sha(R/'GAME_SOURCE_AFTER.json'),game_cache_after_sha256=sha(R/'GAME_CACHE_AFTER.json'),explicit_diffs_sha256=sha(R/'EXPLICIT_BYTE_DIFFS.json'),source_diff_count=len(diffs['game_source']),project_cache_diff_count=len(diffs['project_godot']))
        if not unchanged:receipt['status']='STOPPED_GAME_OR_CACHE_MUTATION_REQUIRES_REVIEW';receipt['production_changes']='UNEXPECTED_DIFFERENCE_REQUIRES_REVIEW'
        rp.write_text(json.dumps(receipt,indent=2)+'\n')
        require(unchanged,'Unexpected Game/cache change; never claim no-production-change, preserve and review')
    print(json.dumps(receipt))
if __name__=='__main__':main()
