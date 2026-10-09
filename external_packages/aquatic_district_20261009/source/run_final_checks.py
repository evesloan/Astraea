"""Serialize final bounded construction checks; no host import or mutation."""
import subprocess,json,datetime,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];B=r'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe';rows=[]
steps=[('final_native',[B,'-b','--python',str(P/'source/finish_entry_native.py')]),('geometry',[sys.executable,str(P/'source/validate_delivery.py')]),('supports',[sys.executable,str(P/'source/verify_supports.py')]),('godot',[sys.executable,str(P/'source/check_import.py')]),('source_views',[B,'-b','--python',str(P/'source/render_source.py')])]
for phase,args in steps:
 r=subprocess.run(args,capture_output=True,text=True,timeout=120)
 out=r.stdout+'\n'+r.stderr;(P/'qa'/('final_'+phase+'.log')).write_text(out)
 errors=[q for q in out.splitlines() if 'Traceback' in q or 'SCRIPT ERROR:' in q]
 rows.append({'phase':phase,'exit_code':r.returncode,'errors':errors,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 (P/'qa/final_checks_execution.json').write_text(json.dumps(rows,indent=2));print(phase,r.returncode,errors,flush=True)
 assert r.returncode==0 and not errors,phase
