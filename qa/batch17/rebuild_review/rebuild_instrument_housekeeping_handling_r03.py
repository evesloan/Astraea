"""Read instrumentation for fresh builds; preserve traces even on failure. Never render."""
from pathlib import Path
import sys,runpy,json,hashlib,traceback,subprocess
sys.dont_write_bytecode=True
args=sys.argv[sys.argv.index('--')+1:]
generator,stage,catalogue,out=map(lambda x:Path(x).resolve(),args[:4])
events=[];witnesses=[];failure=None;child_runs=[]
original_subprocess_run=subprocess.run
def instrument_child(argv,*pos,**kw):
    if isinstance(argv,(list,tuple))and len(argv)>=2 and Path(str(argv[0])).name.startswith('python')and str(argv[1]).endswith('.py')and Path(argv[1]).resolve().is_relative_to(stage):
        target=Path(argv[1]).resolve();child_out=out.with_name(out.stem+f'_child{len(child_runs)+1}.json')
        modified=[str(argv[0]),str(Path(__file__).resolve()),'--',str(target),str(stage),str(catalogue),str(child_out)]+[str(x)for x in argv[2:]]
        child_runs.append({'original_argv':[str(x)for x in argv],'instrumented_argv':modified,'trace':str(child_out)})
        return original_subprocess_run(modified,*pos,**kw)
    return original_subprocess_run(argv,*pos,**kw)
subprocess.run=instrument_child
def audit(event,args):
    if event!='open' or not args or not isinstance(args[0],str):return
    path=Path(args[0]).resolve()
    if path.is_relative_to(stage):where='stage';name=str(path.relative_to(stage))
    elif path.is_relative_to(catalogue):where='outside_stage_catalogue';name=str(path.relative_to(catalogue))
    else:return
    mode=args[1]if len(args)>1 else None
    events.append({'scope':where,'path':name,'mode':str(mode),'flags':args[2]if len(args)>2 else None})
def images(reason):
    try:import bpy
    except ImportError:return
    for im in bpy.data.images:
        p=Path(bpy.path.abspath(im.filepath)).resolve() if im.filepath else None
        if p and (p.is_relative_to(stage)or p.is_relative_to(catalogue)):
            witnesses.append({'reason':reason,'path':str(p.relative_to(stage))if p.is_relative_to(stage)else str(p.relative_to(catalogue)),'scope':'stage'if p.is_relative_to(stage)else'outside_stage_catalogue','image':im.name,'exists':p.exists(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()if p.exists()else None,'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest()if im.packed_file else None})
sys.addaudithook(audit)
try:
    import bpy
    @bpy.app.handlers.persistent
    def observe_save(_):images('save_pre')
    bpy.app.handlers.save_pre.append(observe_save)
except ImportError:pass
try:
    sys.argv=[str(generator)]+args[4:]
    runpy.run_path(str(generator),run_name='__main__')
except BaseException:
    failure=traceback.format_exc()
finally:
    images('final')
    payload={'python_open_events':events.copy(),'actual_blender_image_files':witnesses,'child_python_runs':child_runs,'failure':failure,'scope':'Python-level catalogue open attempts plus native Blender image bytes at source saves and final scene; not a complete OS syscall trace. Direct source Python subprocesses are transparently instrumented too. System Blender/Python dependencies are environment inputs.'}
    out.write_text(json.dumps(payload,indent=2)+'\n')
if failure:raise RuntimeError(failure)
