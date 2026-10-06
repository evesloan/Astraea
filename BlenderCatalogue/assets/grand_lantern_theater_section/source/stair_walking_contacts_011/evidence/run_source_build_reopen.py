"""PREPARED, NOT RUN. Bounded scratch-only sequential build/reopen/QA, Blender 2 threads.
Run only after the parent coordinates the source lane. Never writes Game/Catalogue.
Usage: python THIS --output /workspace/scratch/375c2e438292/NEW_RUN_DIR
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,signal,subprocess,sys,time
R=Path(__file__).resolve().parent
MANIFEST_SHA='63784a5ae6160aec41123696f76a4745a91e086094b5141bd7f21e405031b5d9'
SCRATCH=Path('/workspace/scratch/375c2e438292').resolve()
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    output=args.output.absolute()
    assert output.parent.exists() and output.parent.resolve().is_relative_to(SCRATCH)
    assert not output.exists() and not output.is_symlink(), 'New-only output directory required; keep prior attempts'
    assert output.name not in ['', '.', '..']
    manifest=R/'SOURCE_EXECUTION_PINS.json';assert digest(manifest)==MANIFEST_SHA,'Execution pin manifest changed'
    pins=json.loads(manifest.read_text())
    def verify_pins():
        for name,pin in pins['immutable_sha256'].items():assert digest(name)==pin,'Immutable source/input changed: '+name
    verify_pins()
    assert pins['blender_path']=='/usr/bin/blender' and pins['threads']==2
    output.mkdir(exist_ok=False);output=output.resolve()
    assert output.is_relative_to(SCRATCH)
    env=os.environ.copy()
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:env[key]='2'
    env['PYTHONDONTWRITEBYTECODE']='1'
    for key,folder in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('BLENDER_USER_CONFIG','blender_config'),('BLENDER_USER_SCRIPTS','blender_scripts')]:
        path=output/'state'/folder;path.mkdir(parents=True,exist_ok=False);env[key]=str(path)
    source=R.parent/'source';blend=output/'authored/AST-CUL-005_stair_walking_contacts_011.blend';export=output/'REOPENED_CONTACTS.json';qa=output/'SOURCE_REOPEN_QA.json'
    common=[pins['blender_path'],'--background','--factory-startup','--threads','2','--disable-autoexec','--python-exit-code','1']
    jobs=[('build',120,common+['--python',str(source/'build_stair_walking_contacts.py'),'--','--output',str(output/'authored')]),('reopen',120,common+['--python',str(source/'reopen_export_contacts.py'),'--','--blend',str(blend),'--output',str(export)]),('independent_qa',60,[sys.executable,'-B',str(source/'verify_source_contacts.py'),'--reopened',str(export),'--output',str(qa)])]
    receipt={'status':'RUNNING_SOURCE_ONLY','started_utc':now(),'execution_manifest_sha256':MANIFEST_SHA,'wrapper_sha256':digest(__file__),'threads':2,'sequential_blender_processes':2,'phases':[],'original_sources_unchanged':False,'runtime_installation':False,'godot_launched':False}
    try:
        for label,limit,command in jobs:
            verify_pins();started=time.monotonic()
            with (output/(label+'.log')).open('xb')as log:
                process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,cwd=str(output),env=env,start_new_session=True)
                try:code=process.wait(timeout=limit)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGTERM)
                    try:process.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=5)
                    raise RuntimeError(label+' exceeded '+str(limit)+' seconds; attempt preserved')
            receipt['phases'].append({'phase':label,'returncode':code,'seconds':round(time.monotonic()-started,3),'timeout_seconds':limit,'log_sha256':digest(output/(label+'.log'))})
            assert code==0,label+' failed; preserve attempt and inspect its log before retry'
            verify_pins()
        proof=json.loads(qa.read_text());built=json.loads((output/'authored/BUILD_RECEIPT.json').read_text());reopened=json.loads(export.read_text())
        assert proof['status']=='PASS_REOPENED_SOURCE_CONTACTS' and proof['reopened_test_run']
        assert proof['contacts']==8 and proof['literal_treads_preserved']==90 and proof['width_m']==3.2 and proof['vertical_thickness_m']==.04 and proof['margin_m']==.001
        assert proof['max_reopened_vertex_error_m']<=.00002 and not proof['load_certification']
        assert proof['blend_sha256']==reopened['blend_sha256']==built['blend_sha256']==digest(blend)
        assert proof['reopened_export_sha256']==digest(export)
        assert built['builder_sha256']==pins['immutable_sha256'][str(source/'build_stair_walking_contacts.py')]
        assert reopened['reopen_exporter_sha256']==pins['immutable_sha256'][str(source/'reopen_export_contacts.py')]
        assert proof['input_sha256']['verifier']==pins['immutable_sha256'][str(source/'verify_source_contacts.py')]
        verify_pins();receipt['original_sources_unchanged']=True;receipt['status']='PASS_SOURCE_BUILD_REOPEN_QA_RUNTIME_UNINSTALLED'
        receipt['source_outputs_sha256']={str(p.relative_to(output)):digest(p)for p in [blend,output/'authored/BUILD_RECEIPT.json',export,qa]}
    except BaseException as error:
        receipt['status']='FAILED_SOURCE_ONLY_PRESERVED_ATTEMPT';receipt['error_type']=type(error).__name__;receipt['error']=str(error)
        try:verify_pins();receipt['original_sources_unchanged']=True
        except BaseException as pin_error:receipt['immutable_pin_failure']=str(pin_error)
        raise
    finally:
        receipt['finished_utc']=now()
        with (output/'SOURCE_RUN_RECEIPT.json').open('x')as f:json.dump(receipt,f,indent=2);f.write('\n')
    print(receipt['status']);print(output/'SOURCE_RUN_RECEIPT.json')
if __name__=='__main__':main()
